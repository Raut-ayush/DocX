#!/usr/bin/env python3
"""
scan_project.py — deterministic recon for the ai-project-docs skill.

Scans ONE project directory and gathers raw, factual signals: tech stack
hints from manifest files, git activity, existing docs, TODO/FIXME markers,
and a rough file tree. It does NOT judge completion or write prose — that's
the AI assistant's job, using this JSON plus the actual README/doc contents.

Usage:
    python3 scan_project.py [path]

    If no path is given, it defaults to the current working directory —
    run it from the project root. This script always skips its own tool
    folder when walking the tree (based on its own file location), no
    matter what that folder is named or where it's been copied to.

Output: JSON to stdout.
"""

import sys
import os
import re
import json
import fnmatch
import subprocess
from pathlib import Path

# This script lives at <tool_root>/scripts/scan_project.py. Whatever the
# tool's root folder is named (DocX, or renamed by whoever cloned it) and
# wherever it's been copied to (project root, or .claude/skills/DocX/ after
# install.py), we never want to walk into it when scanning the project.
SCRIPT_DIR = Path(__file__).resolve().parent
TOOL_ROOT = SCRIPT_DIR.parent
# Default scan target: the current working directory. Callers should run
# this from the project root (both the standalone workflow and the
# installed Claude Code skill do this), or pass an explicit path.

IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__",
    "dist", "build", ".next", ".nuxt", "target", ".cache", ".idea",
    ".vscode", "vendor", ".mypy_cache", ".pytest_cache", "coverage",
    "docs",  # avoid re-scanning our own generated docs as source
    # Fallback name-based exclusion: after install.py runs, the original
    # DocX/ clone can still be sitting at the project root alongside the
    # installed copy in .claude/skills/. The path-based self-exclusion
    # below only catches the copy actually running, not this leftover.
    "DocX",
}

# Files matching these patterns are never walked into, read, or included
# in output — even their names aren't listed. Best-effort, filename-based;
# not a substitute for keeping secrets out of git in the first place.
SENSITIVE_FILE_PATTERNS = [
    ".env", ".env.*", "*.pem", "*.key", "*.pfx", "*.p12", "*.keystore",
    "id_rsa", "id_rsa.pub", "id_ed25519", "id_ed25519.pub",
    "credentials.json", "credentials.yml", "credentials.yaml",
    "secrets.json", "secrets.yml", "secrets.yaml",
    "service-account*.json", "service_account*.json",
    ".npmrc", ".pypirc", ".netrc",
]

# Regex patterns for common secret formats. Applied to any free-text content
# (README, TODO lines, manifest snippets) before it's ever included in the
# scan output, as a defense-in-depth safety net on top of the filename
# exclusions above — those catch whole sensitive files, this catches a
# stray key pasted into an otherwise-normal file.
SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),                                    # AWS access key ID
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),                          # GitHub tokens
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),                        # Slack tokens
    re.compile(r"(?is)-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9\-_\.]{10,}"),                # Bearer tokens
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password|passwd|pwd)\b\s*[:=]\s*['\"]?[A-Za-z0-9\-_\.\/+=]{8,}['\"]?"),
]


def redact_secrets(text):
    """Best-effort redaction of common secret formats from free text before
    it's included in scan output. Returns (clean_text, was_redacted)."""
    if not text:
        return text, False
    redacted = False
    for pattern in SECRET_PATTERNS:
        new_text = pattern.sub("[REDACTED]", text)
        if new_text != text:
            redacted = True
        text = new_text
    return text, redacted


def is_sensitive_file(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in SENSITIVE_FILE_PATTERNS)


def load_gitignore_patterns(root: Path):
    """Lightweight, best-effort .gitignore parser — not full gitignore
    semantics (no nested .gitignore files, simplified negation), but enough
    to keep custom-named build/output folders out of the scan."""
    gi = root / ".gitignore"
    patterns = []
    if gi.exists():
        try:
            for line in gi.read_text(errors="ignore").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                patterns.append(line)
        except Exception:
            pass
    return patterns


def gitignore_matches(rel_path: str, is_dir: bool, patterns) -> bool:
    if not patterns:
        return False
    name = rel_path.rsplit("/", 1)[-1]
    ignored = False
    for pat in patterns:
        p = pat
        negate = p.startswith("!")
        if negate:
            p = p[1:]
        dir_only = p.endswith("/")
        if dir_only:
            p = p.rstrip("/")
        p = p.lstrip("/")
        matched = (
            fnmatch.fnmatch(rel_path, p)
            or fnmatch.fnmatch(name, p)
            or fnmatch.fnmatch(rel_path, p + "/*")
            or rel_path.startswith(p + "/")
        )
        if matched:
            if dir_only and not is_dir:
                continue
            ignored = not negate
    return ignored


MANIFEST_PARSERS = {
    "package.json": "node",
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "setup.py": "python",
    "Cargo.toml": "rust",
    "go.mod": "go",
    "pom.xml": "java",
    "build.gradle": "java",
    "Gemfile": "ruby",
    "composer.json": "php",
}

EXT_LANGUAGE = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".rb": "Ruby", ".php": "PHP",
    ".c": "C", ".cpp": "C++", ".h": "C/C++ Header", ".cs": "C#",
    ".swift": "Swift", ".kt": "Kotlin", ".html": "HTML",
    ".css": "CSS", ".scss": "SCSS", ".vue": "Vue", ".sql": "SQL",
    ".sh": "Shell",
}


def find_manifests(path: Path):
    found = []
    for fname, tech in MANIFEST_PARSERS.items():
        if (path / fname).exists():
            found.append({"file": fname, "hints_tech": tech})
    return found


def parse_package_json(path: Path):
    fpath = path / "package.json"
    if not fpath.exists():
        return None
    try:
        data = json.loads(fpath.read_text(errors="ignore"))
        return {
            "name": data.get("name"),
            "version": data.get("version"),
            "scripts": list(data.get("scripts", {}).keys()),
            "dependencies": list(data.get("dependencies", {}).keys()),
            "devDependencies": list(data.get("devDependencies", {}).keys()),
        }
    except Exception:
        return None


def parse_requirements_txt(path: Path):
    fpath = path / "requirements.txt"
    if not fpath.exists():
        return None
    try:
        lines = [l.strip() for l in fpath.read_text(errors="ignore").splitlines()]
        return [l for l in lines if l and not l.startswith("#")]
    except Exception:
        return None


def parse_pyproject_toml(path: Path):
    fpath = path / "pyproject.toml"
    if not fpath.exists():
        return None
    try:
        text = fpath.read_text(errors="ignore")[:1500]
        text, _ = redact_secrets(text)
        return text
    except Exception:
        return None


def git_info(path: Path):
    if not (path / ".git").exists():
        return None

    def run(args):
        try:
            r = subprocess.run(
                ["git", "-C", str(path)] + args,
                capture_output=True, text=True, timeout=10
            )
            return r.stdout.strip() if r.returncode == 0 else None
        except Exception:
            return None

    last_commit_date = run(["log", "-1", "--format=%cI"])
    first_commit_date = run(["log", "--reverse", "--format=%cI", "-1"])
    commit_count = run(["rev-list", "--count", "HEAD"])
    branch = run(["rev-parse", "--abbrev-ref", "HEAD"])
    remote = run(["remote", "get-url", "origin"])
    status = run(["status", "--porcelain"])
    uncommitted_changes = len(status.splitlines()) if status else 0
    last_commit_msgs = run(["log", "-8", "--format=%s"])
    recent_commits_raw = run(["log", "-30", "--format=%H|%cI|%s"])
    recent_commits = []
    if recent_commits_raw:
        for line in recent_commits_raw.splitlines():
            parts = line.split("|", 2)
            if len(parts) == 3:
                recent_commits.append({
                    "hash": parts[0][:10],
                    "date": parts[1],
                    "subject": parts[2],
                })

    return {
        "first_commit_date": first_commit_date,
        "last_commit_date": last_commit_date,
        "commit_count": int(commit_count) if commit_count and commit_count.isdigit() else None,
        "current_branch": branch,
        "remote_url": remote,
        "uncommitted_changes": uncommitted_changes,
        "recent_commit_messages": last_commit_msgs.splitlines() if last_commit_msgs else [],
        "recent_commits": recent_commits,
    }


def walk_files(path: Path, gitignore_patterns, max_files=6000):
    files = []
    lang_counts = {}
    for root, dirs, fnames in os.walk(path):
        rel_root = Path(root).relative_to(path)
        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_DIRS
            and not d.startswith(".")
            and (Path(root) / d).resolve() != TOOL_ROOT
            and not gitignore_matches(
                str((rel_root / d).as_posix()) if str(rel_root) != "." else d,
                True, gitignore_patterns
            )
        ]
        for f in fnames:
            if len(files) >= max_files:
                break
            if is_sensitive_file(f):
                continue
            rel = (rel_root / f).as_posix() if str(rel_root) != "." else f
            if gitignore_matches(rel, False, gitignore_patterns):
                continue
            files.append(rel)
            ext = Path(f).suffix.lower()
            if ext in EXT_LANGUAGE:
                lang = EXT_LANGUAGE[ext]
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
    return files, lang_counts


def find_docs(files):
    return sorted([f for f in files if f.lower().endswith((".md", ".rst"))])


def find_existing_ai_docs(path: Path):
    """Check for our own previously-generated doc set, so the workflow knows
    whether this is a first run or an update."""
    docs_dir = path / "docs"
    names = ["project.md", "PRD.md", "architecture.md", "state.md", "tasks.md", "decisions.md", "changes.md"]
    existing = {}
    for name in names:
        fpath = docs_dir / name
        if fpath.exists():
            try:
                existing[name] = fpath.read_text(errors="ignore")
            except Exception:
                existing[name] = None
    return existing


def count_todos(path: Path, files, max_scan=1500):
    count = 0
    examples = []
    scanned = 0
    any_redacted = False
    for rel in files:
        ext = Path(rel).suffix.lower()
        if ext not in EXT_LANGUAGE and ext not in {".md"}:
            continue
        if scanned >= max_scan:
            break
        scanned += 1
        fpath = path / rel
        try:
            text = fpath.read_text(errors="ignore")
        except Exception:
            continue
        for marker in ("TODO", "FIXME", "XXX"):
            if marker in text:
                n = text.count(marker)
                count += n
                if len(examples) < 10:
                    for line in text.splitlines():
                        if marker in line:
                            clean_line, was_redacted = redact_secrets(line.strip()[:120])
                            any_redacted = any_redacted or was_redacted
                            examples.append(f"{rel}: {clean_line}")
                            break
    return count, examples[:10], any_redacted


def read_readme(path: Path):
    for name in ("README.md", "README.rst", "README.txt", "README"):
        fpath = path / name
        if fpath.exists():
            try:
                text = fpath.read_text(errors="ignore")[:8000]
                text, was_redacted = redact_secrets(text)
                return text, was_redacted
            except Exception:
                pass
    return None, False


def detect_new_project(total_files: int, manifests_found: list, git_data) -> bool:
    """Best-effort heuristic: is there basically nothing here yet? Used to
    offer switching into planning mode instead of documenting existing
    code — the caller should always confirm with the user before acting
    on this, never switch modes silently."""
    file_signal = total_files <= 3
    manifest_signal = len(manifests_found) == 0
    commit_signal = True
    if git_data:
        commit_signal = (git_data.get("commit_count") or 0) <= 1
    return file_signal and manifest_signal and commit_signal


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    path = Path(target).expanduser().resolve()
    if not path.exists():
        print(json.dumps({"error": f"path does not exist: {path}"}))
        sys.exit(1)

    gitignore_patterns = load_gitignore_patterns(path)
    files, lang_counts = walk_files(path, gitignore_patterns)
    top_level = sorted([
        p.name + ("/" if p.is_dir() else "")
        for p in path.iterdir()
        if p.name not in IGNORE_DIRS
        and not p.name.startswith(".")
        and not is_sensitive_file(p.name)
        and not gitignore_matches(p.name, p.is_dir(), gitignore_patterns)
    ])
    todo_count, todo_examples, todo_redacted = count_todos(path, files)
    readme_content, readme_redacted = read_readme(path)
    manifests_found = find_manifests(path)
    git_data = git_info(path)

    result = {
        "name": path.name,
        "path": str(path),
        "top_level_entries": top_level,
        "total_files_scanned": len(files),
        "language_file_counts": lang_counts,
        "manifests_found": manifests_found,
        "package_json": parse_package_json(path),
        "requirements_txt": parse_requirements_txt(path),
        "pyproject_toml_snippet": parse_pyproject_toml(path),
        "git": git_data,
        "doc_files_in_repo": find_docs(files),
        "readme_content": readme_content,
        "todo_fixme_count": todo_count,
        "todo_fixme_examples": todo_examples,
        "existing_ai_docs": find_existing_ai_docs(path),
        "secrets_redacted": bool(readme_redacted or todo_redacted),
        "gitignore_respected": bool(gitignore_patterns),
        "likely_new_project": detect_new_project(len(files), manifests_found, git_data),
    }
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
