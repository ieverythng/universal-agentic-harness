#!/usr/bin/env python3
"""Record and verify the repository state covered by pre-commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _git(*args: str) -> bytes:
    return subprocess.check_output(("git", *args), cwd=REPO_ROOT)


def _git_dir() -> Path:
    path = Path(_git("rev-parse", "--git-dir").decode().strip())
    return path if path.is_absolute() else REPO_ROOT / path


CACHE_PATH = _git_dir() / "precommit-success.json"


def _repo_signature() -> str:
    digest = hashlib.sha256()
    paths = _git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    encoded_paths = sorted(path for path in paths.split(b"\0") if path)
    for encoded_path in encoded_paths:
        path = Path(encoded_path.decode("utf-8", errors="surrogateescape"))
        absolute = REPO_ROOT / path
        digest.update(b"path\0")
        digest.update(encoded_path)
        digest.update(b"\0")
        if not absolute.is_file():
            digest.update(b"missing\0")
            continue
        digest.update(str(absolute.stat().st_mode & 0o777).encode())
        digest.update(b"\0")
        digest.update(absolute.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def record() -> int:
    CACHE_PATH.write_text(
        json.dumps(
            {
                "head": _git("rev-parse", "HEAD").decode().strip(),
                "recorded_at": int(time.time()),
                "signature": _repo_signature(),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Recorded successful pre-commit state in {CACHE_PATH}")
    return 0


def check() -> int:
    if not CACHE_PATH.exists():
        print(
            "No pre-commit success record. Run ./scripts/run_precommit.sh.",
            file=sys.stderr,
        )
        return 1
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    if cache.get("signature") != _repo_signature():
        print(
            "The pre-commit success record is stale. "
            "Run ./scripts/run_precommit.sh.",
            file=sys.stderr,
        )
        return 1
    print("The pre-commit success record matches the current repository state.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("record", "check"))
    args = parser.parse_args()
    return record() if args.command == "record" else check()


if __name__ == "__main__":
    raise SystemExit(main())
