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
import json
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
        return fpath.read_text(errors="ignore")[:1500]
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

    return {
        "first_commit_date": first_commit_date,
        "last_commit_date": last_commit_date,
        "commit_count": int(commit_count) if commit_count and commit_count.isdigit() else None,
        "current_branch": branch,
        "remote_url": remote,
        "uncommitted_changes": uncommitted_changes,
        "recent_commit_messages": last_commit_msgs.splitlines() if last_commit_msgs else [],
    }


def walk_files(path: Path, max_files=6000):
    files = []
    lang_counts = {}
    for root, dirs, fnames in os.walk(path):
        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_DIRS
            and not d.startswith(".")
            and (Path(root) / d).resolve() != TOOL_ROOT
        ]
        for f in fnames:
            if len(files) >= max_files:
                break
            fpath = Path(root) / f
            rel = fpath.relative_to(path)
            files.append(str(rel))
            ext = fpath.suffix.lower()
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
    names = ["project.md", "PRD.md", "architecture.md", "state.md", "tasks.md"]
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
                            examples.append(f"{rel}: {line.strip()[:120]}")
                            break
    return count, examples[:10]


def read_readme(path: Path):
    for name in ("README.md", "README.rst", "README.txt", "README"):
        fpath = path / name
        if fpath.exists():
            try:
                return fpath.read_text(errors="ignore")[:8000]
            except Exception:
                pass
    return None


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    path = Path(target).expanduser().resolve()
    if not path.exists():
        print(json.dumps({"error": f"path does not exist: {path}"}))
        sys.exit(1)

    files, lang_counts = walk_files(path)
    top_level = sorted([
        p.name + ("/" if p.is_dir() else "")
        for p in path.iterdir()
        if p.name not in IGNORE_DIRS and not p.name.startswith(".")
    ])
    todo_count, todo_examples = count_todos(path, files)

    result = {
        "name": path.name,
        "path": str(path),
        "top_level_entries": top_level,
        "total_files_scanned": len(files),
        "language_file_counts": lang_counts,
        "manifests_found": find_manifests(path),
        "package_json": parse_package_json(path),
        "requirements_txt": parse_requirements_txt(path),
        "pyproject_toml_snippet": parse_pyproject_toml(path),
        "git": git_info(path),
        "doc_files_in_repo": find_docs(files),
        "readme_content": read_readme(path),
        "todo_fixme_count": todo_count,
        "todo_fixme_examples": todo_examples,
        "existing_ai_docs": find_existing_ai_docs(path),
    }
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
