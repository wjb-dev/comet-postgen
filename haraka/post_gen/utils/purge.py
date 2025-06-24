# haraka/post_gen/utils/purge.py
from pathlib import Path
from typing import Dict, Set

from .files import FileOps
from haraka.utils import Logger, divider
from haraka.post_gen.utils.assets import LANGUAGE_ASSETS, GLOBAL_ASSETS


class ResourcePurger:
    """Delete template artefacts not relevant to the selected language."""

    def __init__(self, fops: FileOps, logger: Logger | None = None) -> None:
        self._f = fops
        self._log = logger or Logger("ResourcePurger")

        # Build a quick lookup: language → {"files": set, "dirs": set}
        self._index: Dict[str, Dict[str, Set[str]]] = {
            spec["language"]: {
                "files": set(spec["files"]),
                # store directory names *without* trailing “/”
                "dirs": {d.rstrip("/") for d in spec["dirs"]},
            }
            for spec in LANGUAGE_ASSETS
        }

    # ------------------------------------------------------------------ #
    # public API                                                          #
    # ------------------------------------------------------------------ #
    def purge(self, language: str, project_dir: Path) -> None:
        language = language.lower()
        if language not in self._index:
            self._log.warn(f"Unrecognised language '{language}'; skipping purge.")
            return

        self._log.info(f"Starting purge for language: {language}")

        keep_files = self._index[language]["files"] | set(GLOBAL_ASSETS["files"])
        keep_dirs  = self._index[language]["dirs"]  | {
            d.rstrip("/") for d in GLOBAL_ASSETS["dirs"]
        }

        self._log.info(f"Keeping {len(keep_files)} files & {len(keep_dirs)} dirs")

        self._purge_unrelated(project_dir, keep_files, keep_dirs)

        divider("Project tree after purge…")
        self._f.print_tree(project_dir)

    # ------------------------------------------------------------------ #
    # internals                                                           #
    # ------------------------------------------------------------------ #
    def _purge_unrelated(
        self,
        root: Path,
        keep_files: Set[str],
        keep_dirs: Set[str],
    ) -> None:
        for path in root.rglob("*"):
            rel = path.relative_to(root).as_posix()

            inside_kept_dir = any(rel.startswith(d + "/") for d in keep_dirs)

            if rel in keep_files or rel in keep_dirs or inside_kept_dir:
                continue  # safe

            if path.is_dir():
                self._f.remove_dir(path)
            else:
                self._f.remove_file(path)
