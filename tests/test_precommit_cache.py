import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from scripts import precommit_cache


def test_successful_precommit_records_signature(monkeypatch, tmp_path):
    cache_path = tmp_path / "precommit-success.json"
    monkeypatch.setattr(precommit_cache, "CACHE_PATH", cache_path)
    monkeypatch.setattr(precommit_cache, "_candidate_paths", lambda: (b"file.py",))
    monkeypatch.setattr(precommit_cache, "_repo_signature", lambda *_args: "signature-1")
    monkeypatch.setattr(precommit_cache, "_checked_worktree_tree", lambda: "tree-1")
    monkeypatch.setattr(
        precommit_cache.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 0),
    )

    assert precommit_cache.run() == 0
    assert precommit_cache.check() == 0
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    assert cache["checked_tree"] == "tree-1"


def test_changed_repository_state_invalidates_precommit_cache(
    monkeypatch, tmp_path
):
    cache_path = tmp_path / "precommit-success.json"
    cache_path.write_text('{"signature": "old"}\n', encoding="utf-8")
    monkeypatch.setattr(precommit_cache, "CACHE_PATH", cache_path)
    monkeypatch.setattr(precommit_cache, "_repo_signature", lambda: "current")

    assert precommit_cache.check() == 1


def test_repository_signature_is_independent_of_git_listing_order(
    monkeypatch, tmp_path
):
    (tmp_path / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    (tmp_path / "new.txt").write_text("new\n", encoding="utf-8")
    listing = b"tracked.txt\0new.txt\0"
    monkeypatch.setattr(precommit_cache, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(precommit_cache, "_git", lambda *_args: listing)

    before_staging = precommit_cache._repo_signature()
    listing = b"new.txt\0tracked.txt\0"
    after_staging = precommit_cache._repo_signature()

    assert after_staging == before_staging


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ("git", "-C", str(repo), *args),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode:
        raise AssertionError(f"git {args!r} failed: {result.stderr}")
    return result


def _run(repo: Path, command: tuple[str, ...], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=repo,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _precommit_binary() -> str:
    sibling = Path(sys.executable).with_name("pre-commit")
    binary = sibling if sibling.is_file() else shutil.which("pre-commit")
    if binary is None:
        pytest.skip("the disposable hook integration requires pre-commit")
    return str(binary)


def _ruff_binary() -> str | None:
    sibling = Path(sys.executable).with_name("ruff")
    binary = sibling if sibling.is_file() else shutil.which("ruff")
    return str(binary) if binary is not None else None


def _prepare_disposable_repo(
    tmp_path: Path,
    *,
    source_import_hook: bool = False,
    source_test_hook: bool = False,
) -> tuple[Path, Path, dict[str, str]]:
    repo = tmp_path / "repo"
    repo.mkdir()
    source_root = precommit_cache.REPO_ROOT
    for relative in (
        "scripts/precommit_cache.py",
        "scripts/run_repo_python.sh",
        "scripts/run_precommit.sh",
        "scripts/setup_dev_tools.sh",
        "scripts/pre_push_guard.sh",
    ):
        source = source_root / relative
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    (repo / ".gitignore").write_text(
        ".venv/\n__pycache__/\n", encoding="utf-8"
    )
    ruff_binary = _ruff_binary()
    ruff_hook = ""
    if ruff_binary is not None:
        ruff_hook = (
            "      - id: check-python-with-ruff\n"
            "        name: check Python with Ruff\n"
            "        entry: ./scripts/run_repo_python.sh -m ruff check --output-format concise\n"
            "        language: system\n"
            "        files: ^src/.*\\.py$\n"
            "        types: [python]\n"
            "        stages: [pre-commit]\n"
        )
    source_import = ""
    if source_import_hook:
        source_import = (
            "      - id: check-source-import\n"
            "        name: check source import\n"
            f"        entry: {sys.executable} -c 'import sys; sys.path.insert(0, \"src\"); from checked import value'\n"
            "        language: system\n"
            "        always_run: true\n"
            "        pass_filenames: false\n"
            "        stages: [pre-commit]\n"
        )
    source_test = ""
    if source_test_hook:
        source_test = (
            "      - id: source-tests\n"
            "        name: source-aware test suite\n"
            "        entry: ./scripts/run_repo_python.sh -m pytest -q\n"
            "        language: system\n"
            "        pass_filenames: false\n"
            "        always_run: true\n"
            "        stages: [pre-commit]\n"
        )
    (repo / ".pre-commit-config.yaml").write_text(
        "minimum_pre_commit_version: \"4.0.0\"\n"
        "default_install_hook_types: [pre-commit, pre-push]\n\n"
        "repos:\n"
        "  - repo: local\n"
        "    hooks:\n"
        "      - id: pre-commit-control\n"
        "        name: pre-commit control\n"
        "        entry: \"true\"\n"
        "        language: system\n"
        "        always_run: true\n"
        "        stages: [pre-commit]\n"
        + source_import
        + source_test
        + ruff_hook
        + "      - id: check-precommit-cache\n"
        "        name: require a fresh pre-commit state\n"
        "        entry: ./scripts/run_repo_python.sh scripts/precommit_cache.py check\n"
        "        language: system\n"
        "        pass_filenames: false\n"
        "        always_run: true\n"
        "        stages: [pre-push]\n",
        encoding="utf-8",
    )
    (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src" / "checked.py").write_text("value = 1\n", encoding="utf-8")

    _git(repo, "init", "--initial-branch=main")
    _git(repo, "config", "user.name", "Hook Test")
    _git(repo, "config", "user.email", "hook-test@example.invalid")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "baseline")

    remote = tmp_path / "remote.git"
    subprocess.run(("git", "init", "--bare", str(remote)), check=True, capture_output=True)
    _git(repo, "remote", "add", "origin", str(remote))
    legacy_hook = repo / ".git" / "hooks" / "pre-push"
    legacy_hook.write_text(
        "#!/usr/bin/env bash\nprintf 'called\\n' >> .git/pre-push-legacy-called\n",
        encoding="utf-8",
    )
    legacy_hook.chmod(0o755)

    precommit = _precommit_binary()
    venv_bin = repo / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    fake_python = venv_bin / "python"
    fake_python.write_text(
        "#!/usr/bin/env python3\n"
        "import os, sys\n"
        f"REAL_PYTHON = {sys.executable!r}\n"
        f"PRE_COMMIT = {precommit!r}\n"
        "args = sys.argv[1:]\n"
        "if args[:2] == ['-m', 'pip']:\n"
        "    raise SystemExit(0)\n"
        "if args[:2] == ['-m', 'pre_commit']:\n"
        "    os.execv(PRE_COMMIT, [PRE_COMMIT, *args[2:]])\n"
        "if args and args[0] == '-mpre_commit':\n"
        "    os.execv(PRE_COMMIT, [PRE_COMMIT, *args[1:]])\n"
        "os.execv(REAL_PYTHON, [REAL_PYTHON, *args])\n",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)
    env = os.environ.copy()
    setup = _run(repo, ("./scripts/setup_dev_tools.sh",), env)
    assert setup.returncode == 0, setup.stdout + setup.stderr
    guard = repo / ".git" / "hooks" / "pre-push"
    delegate = repo / ".git" / "hooks" / "pre-push.pre-commit"
    assert guard.is_file() and os.access(guard, os.X_OK)
    assert delegate.is_file() and os.access(delegate, os.X_OK)
    assert (repo / ".git" / "hooks" / "pre-push.legacy").is_file()

    # Re-running setup must refresh the guard without moving it into its own delegate.
    setup_again = _run(repo, ("./scripts/setup_dev_tools.sh",), env)
    assert setup_again.returncode == 0, setup_again.stdout + setup_again.stderr
    assert guard.is_file() and delegate.is_file()
    return repo, remote, env


def _run_precommit(repo: Path, env: dict[str, str]) -> None:
    result = _run(repo, ("./scripts/run_precommit.sh",), env)
    assert result.returncode == 0, result.stdout + result.stderr


def _commit(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)


def _remote_ref(remote: Path, ref: str) -> str | None:
    result = subprocess.run(
        ("git", "--git-dir", str(remote), "rev-parse", "--verify", ref),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def test_pre_push_guard_cannot_skip_cache_with_python_override(tmp_path):
    no_op = shutil.which("true")
    if no_op is None:
        pytest.skip("the interpreter-override regression requires true")
    repo, remote, env = _prepare_disposable_repo(tmp_path)
    bypass_env = env | {
        "UAH_PYTHON_BIN": no_op,
        "SKIP": "check-precommit-cache",
    }

    attempted = _run(repo, ("git", "push", "-u", "origin", "main"), bypass_env)

    assert attempted.returncode != 0, attempted.stdout + attempted.stderr
    assert "No pre-commit success record" in attempted.stdout + attempted.stderr
    assert _remote_ref(remote, "refs/heads/main") is None


def test_pre_push_guard_binds_checked_tree_and_rejects_unsupported_updates(tmp_path):
    repo, remote, env = _prepare_disposable_repo(tmp_path)

    # A complete checked tree can be committed and pushed.
    (repo / "tracked.txt").write_text("checked\n", encoding="utf-8")
    _run_precommit(repo, env)
    assert _git(repo, "diff", "--cached", "--quiet").returncode == 0
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-m", "checked content")
    green = _run(repo, ("git", "push", "-u", "origin", "main"), env)
    assert green.returncode == 0, green.stdout + green.stderr
    remote_main = _remote_ref(remote, "refs/heads/main")
    assert remote_main == _git(repo, "rev-parse", "HEAD").stdout.strip()
    assert (repo / ".git" / "pre-push-legacy-called").read_text() == "called\n"

    # Restore checked worktree bytes after committing different outgoing content.
    (repo / "tracked.txt").write_text("checked\n", encoding="utf-8")
    _run_precommit(repo, env)
    (repo / "tracked.txt").write_text("unchecked\n", encoding="utf-8")
    _commit(repo, "unchecked outgoing content")
    (repo / "tracked.txt").write_text("checked\n", encoding="utf-8")
    red = _run(repo, ("git", "push", "origin", "main"), env)
    assert red.returncode != 0
    assert "outgoing commit tree differs" in red.stderr
    assert _remote_ref(remote, "refs/heads/main") == remote_main

    # A deleted baseline path is rejected even if checked worktree bytes return.
    _git(repo, "rm", "-f", "tracked.txt")
    _git(repo, "commit", "-m", "unchecked deletion")
    (repo / "tracked.txt").write_text("checked\n", encoding="utf-8")
    deleted = _run(repo, ("git", "push", "origin", "main"), env)
    assert deleted.returncode != 0
    assert "outgoing commit tree differs" in deleted.stderr
    assert _remote_ref(remote, "refs/heads/main") == remote_main

    # Reset only this disposable repo, then reject a multi-ref push atomically.
    _git(repo, "reset", "--hard", remote_main)
    _run_precommit(repo, env)
    _git(repo, "branch", "other")
    _git(repo, "commit", "--allow-empty", "-m", "checked same-tree advance")
    multi = _run(repo, ("git", "push", "origin", "main", "other"), env)
    assert multi.returncode != 0
    assert "multi-ref pushes are unsupported" in multi.stderr
    assert _remote_ref(remote, "refs/heads/main") == remote_main
    assert _remote_ref(remote, "refs/heads/other") is None

    # Tags, deletions, and a non-current branch are explicitly unsupported.
    _git(repo, "tag", "v1")
    tag = _run(repo, ("git", "push", "origin", "refs/tags/v1"), env)
    assert tag.returncode != 0
    assert "tags are rejected" in tag.stderr
    assert _remote_ref(remote, "refs/tags/v1") is None
    deletion = _run(repo, ("git", "push", "origin", ":refs/heads/main"), env)
    assert deletion.returncode != 0
    assert "ref deletions are unsupported" in deletion.stderr
    assert _remote_ref(remote, "refs/heads/main") == remote_main
    non_head = _run(repo, ("git", "push", "origin", "other"), env)
    assert non_head.returncode != 0
    assert "current checked-out branch tip" in non_head.stderr
    assert _remote_ref(remote, "refs/heads/other") is None

    # A fetched remote tip that is not an ancestor is rejected even with --force.
    writer = tmp_path / "remote-writer"
    subprocess.run(("git", "clone", "--branch", "main", str(remote), str(writer)), check=True, capture_output=True)
    _git(writer, "config", "user.name", "Remote Writer")
    _git(writer, "config", "user.email", "remote-writer@example.invalid")
    (writer / "tracked.txt").write_text("remote only\n", encoding="utf-8")
    _git(writer, "add", "tracked.txt")
    _git(writer, "commit", "-m", "remote advance")
    _git(writer, "push", "origin", "main")
    _git(repo, "fetch", "origin", "main")
    forced = _run(repo, ("git", "push", "--force", "origin", "main"), env)
    assert forced.returncode != 0
    assert "non-fast-forward updates are unsupported" in forced.stderr
    assert _remote_ref(remote, "refs/heads/main") != remote_main


def test_pre_push_rejects_checked_new_dependency_omitted_from_tip(tmp_path):
    repo, remote, env = _prepare_disposable_repo(
        tmp_path, source_import_hook=True
    )
    checked = repo / "src" / "checked.py"
    required = repo / "src" / "required_new.py"
    checked.write_text(
        "from required_new import value\nRESULT = value\n", encoding="utf-8"
    )
    required.write_text("value = 2\n", encoding="utf-8")

    _run_precommit(repo, env)
    _git(repo, "add", "src/checked.py")
    # Build the adversarial partial tip after the successful manual gate.
    _git(
        repo,
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "-m",
        "depend on a new module",
    )

    omitted = _run(repo, ("git", "push", "-u", "origin", "main"), env)
    assert omitted.returncode != 0
    assert "outgoing commit tree differs" in omitted.stderr
    assert _remote_ref(remote, "refs/heads/main") is None

    # Once the checked dependency is included in the outgoing tree, the same
    # recorded tree is an acceptable push candidate.
    _run_precommit(repo, env)
    _git(repo, "add", "src/required_new.py")
    _git(repo, "commit", "-m", "include the checked dependency")
    complete = _run(repo, ("git", "push", "-u", "origin", "main"), env)
    assert complete.returncode == 0, complete.stdout + complete.stderr
    assert _remote_ref(remote, "refs/heads/main") == _git(repo, "rev-parse", "HEAD").stdout.strip()



def test_manual_gate_rejects_untracked_invalid_python(tmp_path):
    if _ruff_binary() is None:
        pytest.skip("the untracked Python coverage test requires Ruff")
    repo, _remote, env = _prepare_disposable_repo(tmp_path)
    invalid = repo / "src" / "untracked_invalid.py"
    invalid.write_text("missing_name()\n", encoding="utf-8")

    # Reproduce the old false green: --all-files omits an untracked Python file.
    old_gate = repo / "scripts" / "run_precommit.sh"
    old_gate.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        ".venv/bin/python -m pre_commit run --all-files\n"
        ".venv/bin/python scripts/precommit_cache.py record\n",
        encoding="utf-8",
    )
    old_gate.chmod(0o755)
    false_green = _run(repo, ("./scripts/run_precommit.sh",), env)
    assert false_green.returncode != 0
    assert "invalid choice" in false_green.stderr
    assert not (repo / ".git" / "precommit-success.json").exists()
    cached = _run(
        repo,
        ("./scripts/run_repo_python.sh", "scripts/precommit_cache.py", "check"),
        env,
    )
    assert cached.returncode != 0

    source = precommit_cache.REPO_ROOT / "scripts" / "run_precommit.sh"
    shutil.copy2(source, old_gate)
    covered = _run(repo, ("./scripts/run_precommit.sh",), env)
    assert covered.returncode != 0
    assert "untracked_invalid.py" in covered.stdout + covered.stderr
    assert "F821" in covered.stdout + covered.stderr
    assert not (repo / ".git" / "precommit-success.json").exists()
    stale_check = _run(
        repo,
        ("./scripts/run_repo_python.sh", "scripts/precommit_cache.py", "check"),
        env,
    )
    assert stale_check.returncode != 0


def test_manual_gate_ignores_hostile_pre_commit_module_on_pythonpath(tmp_path):
    if _ruff_binary() is None:
        pytest.skip("the hostile-import regression test requires Ruff")
    repo, _remote, env = _prepare_disposable_repo(tmp_path)
    invalid = repo / "src" / "hostile_invalid.py"
    invalid.write_text("missing_name()\n", encoding="utf-8")

    hostile = tmp_path / "hostile-pythonpath"
    hostile.mkdir()
    marker = tmp_path / "hostile-pre-commit-imported"
    (hostile / "pre_commit.py").write_text(
        "from pathlib import Path\n"
        "import os\n"
        "Path(os.environ['HOSTILE_PRE_COMMIT_MARKER']).write_text('imported')\n"
        "raise SystemExit(0)\n",
        encoding="utf-8",
    )
    hostile_env = env | {
        "PYTHONPATH": str(hostile),
        "HOSTILE_PRE_COMMIT_MARKER": str(marker),
    }

    result = _run(repo, ("./scripts/run_precommit.sh",), hostile_env)

    assert result.returncode != 0, result.stdout + result.stderr
    assert "hostile_invalid.py" in result.stdout + result.stderr
    assert "F821" in result.stdout + result.stderr
    assert not marker.exists()
    assert not (repo / ".git" / "precommit-success.json").exists()


def test_manual_gate_and_pre_push_ignore_hostile_sitecustomize(tmp_path):
    if _ruff_binary() is None:
        pytest.skip("the hostile-startup regression test requires Ruff")
    repo, remote, env = _prepare_disposable_repo(tmp_path)
    hostile = tmp_path / "hostile-pythonpath"
    hostile.mkdir()
    marker = tmp_path / "hostile-sitecustomize-imported"
    (hostile / "sitecustomize.py").write_text(
        "import os\n"
        "import subprocess\n"
        "from pathlib import Path\n"
        "_original_run = subprocess.run\n"
        "def _intercept(command, *args, **kwargs):\n"
        "    if '-m' in command and 'pre_commit' in command:\n"
        "        Path(os.environ['HOSTILE_STARTUP_MARKER']).write_text('bypassed')\n"
        "        return subprocess.CompletedProcess(command, 0)\n"
        "    return _original_run(command, *args, **kwargs)\n"
        "subprocess.run = _intercept\n",
        encoding="utf-8",
    )
    hostile_env = env | {
        "PYTHONPATH": str(hostile),
        "HOSTILE_STARTUP_MARKER": str(marker),
    }
    invalid = repo / "src" / "hostile_startup_invalid.py"
    invalid.write_text("missing_name()\n", encoding="utf-8")

    rejected = _run(repo, ("./scripts/run_precommit.sh",), hostile_env)

    assert rejected.returncode != 0, rejected.stdout + rejected.stderr
    assert "F821" in rejected.stdout + rejected.stderr
    assert not marker.exists()
    assert not (repo / ".git" / "precommit-success.json").exists()

    invalid.unlink()
    _run_precommit(repo, env)
    pushed = _run(repo, ("git", "push", "-u", "origin", "main"), hostile_env)

    assert pushed.returncode == 0, pushed.stdout + pushed.stderr
    assert not marker.exists()
    assert _remote_ref(remote, "refs/heads/main") == _git(repo, "rev-parse", "HEAD").stdout.strip()
    assert (repo / ".git" / "pre-push-legacy-called").read_text() == "called\n"


def test_manual_gate_ignores_pytest_addopts_selection_override(tmp_path):
    repo, _remote, env = _prepare_disposable_repo(
        tmp_path,
        source_test_hook=True,
    )
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_gate.py").write_text(
        "def test_gate_must_execute():\n"
        "    assert 1 == 2\n",
        encoding="utf-8",
    )

    normal = _run(repo, ("./scripts/run_precommit.sh",), env)

    assert normal.returncode != 0, normal.stdout + normal.stderr
    assert "1 failed" in normal.stdout + normal.stderr
    assert not (repo / ".git" / "precommit-success.json").exists()

    bypass_env = env | {"PYTEST_ADDOPTS": "--collect-only"}
    bypass = _run(repo, ("./scripts/run_precommit.sh",), bypass_env)

    assert bypass.returncode != 0, bypass.stdout + bypass.stderr
    assert "1 failed" in bypass.stdout + bypass.stderr
    assert not (repo / ".git" / "precommit-success.json").exists()



def test_manual_gate_ignores_hostile_pytest_plugin_selection(tmp_path):
    repo, _remote, env = _prepare_disposable_repo(
        tmp_path,
        source_test_hook=True,
    )
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_gate.py").write_text(
        "def test_gate_must_execute():\n"
        "    assert 1 == 2\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "review_gate_plugin.py").write_text(
        "import pytest\n\n"
        "def pytest_collection_modifyitems(items):\n"
        "    for item in items:\n"
        "        item.add_marker(pytest.mark.skip(reason='ambient plugin'))\n",
        encoding="utf-8",
    )

    hostile_env = env | {"PYTEST_PLUGINS": "scripts.review_gate_plugin"}
    result = _run(repo, ("./scripts/run_precommit.sh",), hostile_env)
    output = result.stdout + result.stderr

    assert result.returncode != 0, output
    assert "1 failed" in output, output
    assert not (repo / ".git" / "precommit-success.json").exists()

    cached = _run(
        repo,
        (
            "./scripts/run_repo_python.sh",
            "scripts/precommit_cache.py",
            "check",
        ),
        hostile_env,
    )
    assert cached.returncode != 0, cached.stdout + cached.stderr
    assert "No pre-commit success record" in cached.stdout + cached.stderr


def test_manual_gate_cannot_skip_required_hooks(tmp_path):
    if _ruff_binary() is None:
        pytest.skip("the skipped-hook regression test requires Ruff")
    no_op = shutil.which("true")
    if no_op is None:
        pytest.skip("the interpreter-override regression requires true")
    repo, _remote, env = _prepare_disposable_repo(tmp_path)
    invalid = repo / "src" / "untracked_invalid.py"
    invalid.write_text("missing_name()\n", encoding="utf-8")
    skip_env = env | {
        "SKIP": "check-python-with-ruff,source-tests",
        "UAH_PYTHON_BIN": no_op,
    }

    result = _run(repo, ("./scripts/run_precommit.sh",), skip_env)

    assert result.returncode != 0, result.stdout + result.stderr
    assert "F821" in result.stdout + result.stderr
    assert not (repo / ".git" / "precommit-success.json").exists()
