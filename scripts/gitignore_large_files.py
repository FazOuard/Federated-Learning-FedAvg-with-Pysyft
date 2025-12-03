"""
Find files larger than a threshold and append their relative paths to .gitignore.
Usage:
    python scripts/gitignore_large_files.py --threshold 50MB [--dry-run]

This script is safe: by default it shows what it would add. Use without --dry-run to append.
"""
import argparse
import os
from pathlib import Path

IGNORED_DIRS = {".git", ".venv", "venv", "env", "node_modules", "__pycache__"}


def human_readable(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P"]:
        if abs(num) < 1024.0:
            return f"{num:.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}P{suffix}"


def find_large_files(root: Path, threshold_bytes: int):
    for dirpath, dirnames, filenames in os.walk(root):
        # filter out ignored dirs
        parts = Path(dirpath).parts
        if any(p in IGNORED_DIRS for p in parts):
            continue
        for f in filenames:
            fp = Path(dirpath) / f
            try:
                size = fp.stat().st_size
            except OSError:
                continue
            if size >= threshold_bytes:
                yield fp, size


def append_to_gitignore(gitignore_path: Path, entries: list[str]):
    existing = set()
    if gitignore_path.exists():
        existing = set([line.rstrip('\n') for line in gitignore_path.read_text(encoding='utf8').splitlines()])

    to_add = [e for e in entries if e not in existing]
    if not to_add:
        return []
    with gitignore_path.open("a", encoding="utf8") as f:
        for e in to_add:
            f.write(e + "\n")
    return to_add


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", default="50MB", help="Size threshold, e.g. 50MB, 1GB")
    parser.add_argument("--path", default='.', help="Repo root path")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be added")
    args = parser.parse_args()

    multipliers = {"B": 1, "K": 1024, "KB": 1024, "M": 1024**2, "MB": 1024**2, "G": 1024**3, "GB": 1024**3}
    s = args.threshold.strip().upper()
    num = ''.join(ch for ch in s if (ch.isdigit() or ch == '.'))
    unit = ''.join(ch for ch in s if not (ch.isdigit() or ch == '.')).strip()
    unit = unit or 'B'
    threshold_bytes = int(float(num) * multipliers.get(unit, 1))

    root = Path(args.path).resolve()
    gitignore_path = root / '.gitignore'

    matches = []
    for fp, size in find_large_files(root, threshold_bytes):
        # create relative path pattern for gitignore
        rel = fp.relative_to(root)
        # For files under directories like data/ or tmp/, ignore directory pattern instead of file.
        parts = rel.parts
        if len(parts) >= 2 and parts[0].lower() in ('data', 'tmp'):
            pattern = f"{parts[0]}/"  # ignore directory
        else:
            pattern = str(rel).replace('\\', '/')
        matches.append((pattern, fp, size))

    # deduplicate patterns
    patterns = []
    seen = set()
    for p, fp, size in matches:
        if p not in seen:
            seen.add(p)
            patterns.append((p, fp, size))

    if not patterns:
        print("No files larger than", human_readable(threshold_bytes), "found.")
        return

    print("Files/dirs detected (will be added to .gitignore):")
    for p, fp, size in patterns:
        print(f"  {p}  — {human_readable(size)}  ({fp})")

    if args.dry_run:
        print('\nDry run, nothing changed.')
        return

    to_add = append_to_gitignore(gitignore_path, [p for p, _, _ in patterns])
    if to_add:
        print('\nAppended to .gitignore:')
        for t in to_add:
            print('  ', t)
    else:
        print('\nNothing new to add to .gitignore.')


if __name__ == '__main__':
    main()
