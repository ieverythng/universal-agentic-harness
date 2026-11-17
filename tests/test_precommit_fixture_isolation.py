import os
from pathlib import Path
import stat
import subprocess

import pytest

from test_precommit_cache import _prepare_disposable_repo


def _private_git_environment(root: Path) -> dict[str, str]:
    home = root / "home"
    xdg_config = root / "xdg-config"
    xdg_data = root / "xdg-data"
    xdg_cache = root / "xdg-cache"
    precommit_home = root / "pre-commit-home"
    git_templates = root / "git-templates"
    temporary = root / "tmp"
    git_config = root / "git-config"
    home.mkdir()
    xdg_config.mkdir()
    xdg_data.mkdir()
    xdg_cache.mkdir()
    precommit_home.mkdir()
    git_templates.mkdir()
    temporary.mkdir()
    git_config.mkdir()
    system_config = git_config / "system"
    global_config = git_config / "global"
    system_config.write_text("", encoding="utf-8")
    global_config.write_text("", encoding="utf-8")

    inherited = {
        name: os.environ[name]
        for name in (
            "PATH",
            "LANG",
            "LC_ALL",
            "SYSTEMROOT",
            "WINDIR",
            "PATHEXT",
        )
        if name in os.environ
    }
    return inherited | {
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(xdg_config),
        "XDG_DATA_HOME": str(xdg_data),
        "XDG_CACHE_HOME": str(xdg_cache),
        "PRE_COMMIT_HOME": str(precommit_home),
        "GIT_TEMPLATE_DIR": str(git_templates),
        "GIT_ALLOW_PROTOCOL": "file",
        "GIT_CONFIG_NOSYSTEM": "1",
        "TMPDIR": str(temporary),
        "TMP": str(temporary),
        "TEMP": str(temporary),
        "GIT_CONFIG_SYSTEM": str(system_config),
        "GIT_CONFIG_GLOBAL": str(global_config),
        "GIT_OPTIONAL_LOCKS": "0",
    }


def _install_process_environment(
    monkeypatch: pytest.MonkeyPatch, env: dict[str, str]
) -> None:
    for name in tuple(os.environ):
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)


def _git(
    env: dict[str, str], repo: Path, *args: str
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ("git", "-C", str(repo), *args),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, f"git {args!r} failed: {result.stderr}"
    return result


def _git_output(env: dict[str, str], repo: Path, *args: str) -> str:
    return _git(env, repo, *args).stdout.strip()


def _snapshot_path(path: Path) -> tuple[str, int, bytes | str] | None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None

    mode = stat.S_IMODE(info.st_mode)
    if stat.S_ISLNK(info.st_mode):
        return "symlink", mode, os.readlink(path)
    if stat.S_ISDIR(info.st_mode):
        return "directory", mode, b""
    return "file", mode, path.read_bytes()


def _snapshot_tree(root: Path) -> dict[str, tuple[str, int, bytes | str] | None]:
    paths = (root, *sorted(root.rglob("*")))
    return {
        "." if path == root else path.relative_to(root).as_posix(): _snapshot_path(path)
        for path in paths
    }


def _victim_snapshot(
    common_git_dir: Path, linked_git_dir: Path, linked_worktree: Path
) -> dict[str, object]:
    return {
        "common Git directory": _snapshot_tree(common_git_dir),
        "linked-worktree Git directory": _snapshot_tree(linked_git_dir),
        "linked-worktree .git file": _snapshot_path(linked_worktree / ".git"),
    }


def _changed_paths(before: dict[str, object], after: dict[str, object]) -> list[str]:
    changed: list[str] = []
    for area in before:
        before_tree = before[area]
        after_tree = after[area]
        if isinstance(before_tree, dict) and isinstance(after_tree, dict):
            changed.extend(
                f"{area}/{path}"
                for path in sorted(before_tree.keys() | after_tree.keys())
                if before_tree.get(path) != after_tree.get(path)
            )
        elif before_tree != after_tree:
            changed.append(area)
    return changed


def test_disposable_fixture_git_commands_do_not_mutate_inherited_linked_worktree(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    private_root = tmp_path / "private-environment"
    private_root.mkdir()
    clean_env = _private_git_environment(private_root)
    _install_process_environment(monkeypatch, clean_env)

    victim = private_root / "victim"
    victim.mkdir()
    _git(clean_env, victim, "init", "--initial-branch=main")
    _git(clean_env, victim, "config", "user.name", "Private Victim")
    _git(clean_env, victim, "config", "user.email", "victim@example.invalid")
    _git(clean_env, victim, "config", "extensions.worktreeConfig", "true")
    (victim / "tracked.txt").write_text("private baseline\n", encoding="utf-8")
    _git(clean_env, victim, "add", "tracked.txt")
    _git(clean_env, victim, "commit", "-m", "private baseline")

    linked_worktree = private_root / "victim-linked"
    _git(clean_env, victim, "worktree", "add", "-b", "linked", str(linked_worktree))
    _git(
        clean_env,
        linked_worktree,
        "config",
        "--worktree",
        "victim.marker",
        "private linked config",
    )
    common_git_dir = Path(
        _git_output(
            clean_env,
            linked_worktree,
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        )
    ).resolve()
    linked_git_dir = Path(
        _git_output(clean_env, linked_worktree, "rev-parse", "--absolute-git-dir")
    ).resolve()
    victim_hook = common_git_dir / "hooks" / "pre-commit"
    victim_hook.parent.mkdir(parents=True, exist_ok=True)
    victim_hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    victim_hook.chmod(0o751)

    before = _victim_snapshot(common_git_dir, linked_git_dir, linked_worktree)

    # Reproduce an inherited linked-worktree selector while keeping every Git
    # config source and the victim repository itself inside this tmp_path.
    inherited_linked_env = clean_env | {"GIT_DIR": str(linked_git_dir)}
    _install_process_environment(monkeypatch, inherited_linked_env)
    fixture_root = tmp_path / "disposable-fixture"
    fixture_root.mkdir()

    fixture: tuple[Path, Path, dict[str, str]] | None = None
    fixture_error: Exception | None = None
    try:
        fixture = _prepare_disposable_repo(fixture_root)
    except Exception as error:
        # Inspect the private victim after a partial setup too; a Git failure
        # must not hide an already-observed mutation of its metadata.
        fixture_error = error

    after = _victim_snapshot(common_git_dir, linked_git_dir, linked_worktree)
    changed = _changed_paths(before, after)
    assert not changed, (
        "disposable fixture creation mutated private victim Git metadata: "
        + ", ".join(changed)
    )
    assert fixture_error is None, f"disposable fixture setup failed: {fixture_error!r}"
    assert fixture is not None

    fixture_repo, remote, _fixture_env = fixture
    fixture_git_dir = Path(
        _git_output(clean_env, fixture_repo, "rev-parse", "--absolute-git-dir")
    ).resolve()
    assert fixture_git_dir.is_relative_to(fixture_repo.resolve())
    assert fixture_git_dir != linked_git_dir
    assert remote.is_dir()
    assert remote.resolve().is_relative_to(fixture_root.resolve())
