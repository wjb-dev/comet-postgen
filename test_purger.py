# test_purger.py
from pathlib import Path
import pytest

from haraka.post_gen.utils.assets import LANGUAGE_ASSETS, GLOBAL_ASSETS
from haraka.post_gen.utils.purge import ResourcePurger
from haraka.post_gen.utils.files import FileOps
from haraka.utils import Logger


# ------------------------------------------------------------------ #
# helper functions                                                    #
# ------------------------------------------------------------------ #
def _expand_parents(path: str) -> list[str]:
    """Return parent directories (without trailing slash)."""
    parts = Path(path).parts
    return [str(Path(*parts[:i])) for i in range(1, len(parts))]


def _lookup_for(lang: str) -> dict[str, set[str]]:
    spec = next(x for x in LANGUAGE_ASSETS if x["language"] == lang)
    files = set(spec["files"]) | set(GLOBAL_ASSETS["files"])
    dirs  = {d.rstrip("/") for d in spec["dirs"]} | {
        d.rstrip("/") for d in GLOBAL_ASSETS["dirs"]
    }

    # Ensure every parent dir is included
    for p in files | dirs:
        dirs.update(_expand_parents(p))

    return {"files": files, "dirs": dirs}


def _materialise(tmp_path: Path, assets: dict[str, set[str]]) -> None:
    """Create the fake project tree."""
    for d in assets["dirs"]:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    for f in assets["files"]:
        fp = tmp_path / f
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.touch()


def _run_purge_and_assert(tmp_path: Path, lang: str) -> None:
    assets = _lookup_for(lang)
    _materialise(tmp_path, assets)

    purger = ResourcePurger(FileOps(test_mode=True), Logger("test"))
    purger.purge(lang, tmp_path)

    # Assert every required file exists
    for f in assets["files"]:
        assert (tmp_path / f).exists(), f"Missing file after purge: {f}"

    # Assert every required directory exists
    for d in assets["dirs"]:
        assert (tmp_path / d).is_dir(), f"Missing dir after purge: {d}"


# ------------------------------------------------------------------ #
# Three independent tests                                            #
# ------------------------------------------------------------------ #
def test_purger_keeps_go(tmp_path: Path):
    _run_purge_and_assert(tmp_path, "go")


def test_purger_keeps_python(tmp_path: Path):
    _run_purge_and_assert(tmp_path, "python")


def test_purger_keeps_java(tmp_path: Path):
    _run_purge_and_assert(tmp_path, "java")
