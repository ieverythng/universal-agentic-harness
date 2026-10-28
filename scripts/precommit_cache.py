#!/usr/bin/env python3
"""Record a successful pre-commit run and qualify the outgoing branch tip.

Coverage is tip-only. The outgoing tip tree must equal the complete checked
worktree snapshot. Intermediate commits in the range are not inspected.
Tags, deletions, multi-ref pushes, cross-ref pushes, detached heads, and
non-fast-forward updates are rejected explicitly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _git(*args: str) -> bytes:
    return subprocess.check_output(("git", *args), cwd=REPO_ROOT)


def _git_dir() -> Path:
    path = Path(_git("rev-parse", "--git-dir").decode().strip())
    return path if path.is_absolute() else REPO_ROOT / path


CACHE_PATH = _git_dir() / "precommit-success.json"


def _candidate_paths() -> tuple[bytes, ...]:
    paths = _git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    return tuple(sorted(path for path in paths.split(b"\0") if path))


def _repo_signature(paths: tuple[bytes, ...] | None = None) -> str:
    digest = hashlib.sha256()
    encoded_paths = _candidate_paths() if paths is None else paths
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


def _checked_worktree_tree() -> str:
    """Build a tree from current files without changing the real index."""
    with tempfile.TemporaryDirectory(prefix="uah-precommit-index-") as directory:
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(Path(directory) / "index")
        subprocess.run(
            ("git", "read-tree", "HEAD"),
            cwd=REPO_ROOT,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            ("git", "add", "-A", "--", "."),
            cwd=REPO_ROOT,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return subprocess.check_output(
            ("git", "write-tree"), cwd=REPO_ROOT, env=env
        ).decode().strip()


def run() -> int:
    """Run pre-commit on the same candidate paths recorded by the cache."""
    try:
        CACHE_PATH.unlink(missing_ok=True)
        paths = _candidate_paths()
        signature = _repo_signature(paths)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Unable to determine pre-commit candidate paths: {exc}", file=sys.stderr)
        return 1

    command = [sys.executable, "-I", "-m", "pre_commit", "run", "--files"]
    command.extend(os.fsdecode(path) for path in paths)
    precommit_env = os.environ.copy()
    for name in tuple(precommit_env):
        if name.startswith("PYTEST_"):
            precommit_env.pop(name)
    precommit_env.pop("SKIP", None)
    precommit_env.pop("UAH_PYTHON_BIN", None)
    precommit_env.pop("PYTHONPATH", None)
    # Required-suite plugin policy belongs to the repository, not caller env.
    precommit_env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    result = subprocess.run(
        command, cwd=REPO_ROOT, env=precommit_env, check=False
    )
    if result.returncode != 0:
        return result.returncode

    try:
        checked_tree = _checked_worktree_tree()
        paths_after = _candidate_paths()
        signature_after = _repo_signature(paths_after)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Unable to record the checked worktree tree: {exc}", file=sys.stderr)
        return 1
    if paths_after != paths or signature_after != signature:
        print(
            "Repository contents changed during pre-commit; no success was recorded.",
            file=sys.stderr,
        )
        return 1

    CACHE_PATH.write_text(
        json.dumps(
            {
                "checked_tree": checked_tree,
                "recorded_at": int(time.time()),
                "signature": signature,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Recorded successful pre-commit state in {CACHE_PATH}")
    return 0


def _reject_push(reason: str) -> int:
    print(
        "Pre-push validation failed: "
        f"{reason} Run ./scripts/run_precommit.sh before pushing.",
        file=sys.stderr,
    )
    return 1


def _check_outgoing_ref(cache: dict[str, object], payload: bytes) -> int:
    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError:
        return _reject_push("Git supplied malformed ref-update data.")

    lines = text.splitlines()
    if not lines or any(not line.strip() for line in lines):
        return _reject_push("expected exactly one branch ref update.")
    if len(lines) != 1:
        return _reject_push("multi-ref pushes are unsupported; push one branch at a time.")

    fields = lines[0].split()
    if len(fields) != 4:
        return _reject_push("Git supplied a malformed ref update.")
    local_ref, local_sha, remote_ref, remote_sha = fields
    if local_ref == "(delete)" or local_sha == "0" * len(local_sha):
        return _reject_push("ref deletions are unsupported.")
    if not local_ref.startswith("refs/heads/"):
        return _reject_push("only branch ref updates are supported; tags are rejected.")
    if local_ref != remote_ref:
        return _reject_push("source and destination branch names must match.")

    try:
        head = _git("rev-parse", "HEAD").decode().strip()
        current_ref = _git("symbolic-ref", "--quiet", "HEAD").decode().strip()
        local_type = _git("cat-file", "-t", local_sha).decode().strip()
    except subprocess.CalledProcessError:
        return _reject_push("the outgoing branch or commit cannot be resolved locally.")
    if local_ref != current_ref or local_sha != head or local_type != "commit":
        return _reject_push("only the current checked-out branch tip may be pushed.")

    checked_tree = cache.get("checked_tree")
    if not isinstance(checked_tree, str) or not checked_tree:
        return _reject_push("the success record has no checked worktree tree; rerun pre-commit.")
    try:
        outgoing_tree = _git("rev-parse", f"{local_sha}^{{tree}}").decode().strip()
    except subprocess.CalledProcessError:
        return _reject_push("the outgoing commit tree cannot be resolved locally.")
    if outgoing_tree != checked_tree:
        return _reject_push(
            "the outgoing commit tree differs from the complete checked worktree snapshot."
        )

    object_length = len(head)
    if len(remote_sha) != object_length or any(
        character not in "0123456789abcdef" for character in remote_sha
    ):
        return _reject_push("the remote ref update has an unsupported object id.")
    zero_sha = "0" * object_length
    if remote_sha != zero_sha:
        try:
            remote_type = _git("cat-file", "-t", remote_sha).decode().strip()
        except subprocess.CalledProcessError:
            return _reject_push("the remote tip is not available locally; fetch and retry.")
        if remote_type != "commit":
            return _reject_push("the remote branch tip is not a commit.")
        ancestry = subprocess.run(
            ("git", "merge-base", "--is-ancestor", remote_sha, local_sha),
            cwd=REPO_ROOT,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if ancestry.returncode != 0:
            return _reject_push("non-fast-forward updates are unsupported.")

    print(f"Outgoing tip {local_ref} matches the complete checked worktree tree.")
    return 0


def check(push_input: Path | None = None) -> int:
    if not CACHE_PATH.exists():
        print(
            "No pre-commit success record. Run ./scripts/run_precommit.sh.",
            file=sys.stderr,
        )
        return 1
    try:
        cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"The pre-commit success record is unreadable: {exc}", file=sys.stderr)
        return 1
    if cache.get("signature") != _repo_signature():
        print(
            "The pre-commit success record is stale. "
            "Run ./scripts/run_precommit.sh.",
            file=sys.stderr,
        )
        return 1
    if push_input is not None:
        try:
            payload = push_input.read_bytes()
        except OSError as exc:
            return _reject_push(f"unable to read Git ref updates: {exc}.")
        return _check_outgoing_ref(cache, payload)
    print("The pre-commit success record matches the current repository state.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("--push-input", type=Path)
    args = parser.parse_args()
    if args.command == "run":
        if args.push_input is not None:
            parser.error("--push-input is only valid with check")
        return run()
    return check(args.push_input)


if __name__ == "__main__":
    raise SystemExit(main())
