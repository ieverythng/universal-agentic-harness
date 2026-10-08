from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil
import subprocess
import sys


ROOT = Path(sys.argv[1])
SOURCE = ROOT / "scripts/precommit_cache.py"
if not SOURCE.exists():
    print("BASELINE_UNAVAILABLE: precommit_cache.py")
    raise SystemExit(0)

with TemporaryDirectory(prefix="uah-standards-push-") as temp:
    repo = Path(temp)
    (repo / "scripts").mkdir()
    shutil.copy2(SOURCE, repo / "scripts/precommit_cache.py")

    def git(*args):
        return subprocess.run(
            ("git", *args), cwd=repo, check=True, capture_output=True, text=True
        )

    def cache(command):
        return subprocess.run(
            (sys.executable, "scripts/precommit_cache.py", command),
            cwd=repo,
            capture_output=True,
            text=True,
        )

    git("init", "-q")
    git("config", "user.name", "Synthetic reviewer")
    git("config", "user.email", "synthetic@example.invalid")
    good = "RESULT = 42\n"
    (repo / "source.py").write_text(good)
    git("add", ".")
    git("commit", "-q", "-m", "synthetic valid baseline")
    compile(good, "source.py", "exec")
    assert cache("record").returncode == 0
    (repo / "source.py").write_text("RESULT = (\n")
    git("add", "source.py")
    (repo / "source.py").write_text(good)
    git("commit", "-q", "-m", "synthetic broken outgoing commit")
    outgoing = git("show", "HEAD:source.py").stdout
    try:
        compile(outgoing, "outgoing/source.py", "exec")
        outgoing_status = "valid"
    except SyntaxError:
        outgoing_status = "SyntaxError"
    checked = cache("check")
    print(
        json.dumps(
            {
                "outgoing_commit": outgoing_status,
                "covered_worktree": "valid",
                "pre_push_check_exit": checked.returncode,
                "pre_push_message": checked.stdout.strip(),
                "dirty_worktree": bool(git("status", "--porcelain").stdout),
            }
        )
    )
