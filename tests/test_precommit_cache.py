import json

from scripts import precommit_cache


def test_recorded_precommit_signature_is_accepted(monkeypatch, tmp_path):
    cache_path = tmp_path / "precommit-success.json"
    monkeypatch.setattr(precommit_cache, "CACHE_PATH", cache_path)
    monkeypatch.setattr(precommit_cache, "_repo_signature", lambda: "signature-1")
    monkeypatch.setattr(precommit_cache, "_git", lambda *_args: b"head-1\n")

    assert precommit_cache.record() == 0
    assert precommit_cache.check() == 0
    assert json.loads(cache_path.read_text(encoding="utf-8"))["head"] == "head-1"


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
