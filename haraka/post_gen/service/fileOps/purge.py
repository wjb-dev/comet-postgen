#!/usr/bin/env python3
"""
haraka.post_gen.utils.purge

Delete all template artefacts that are **not** required for the chosen
variant, as defined by a YAML manifest in `haraka/manifests/<variant>.yml`.

Manifest format (git-wildmatch globs):

    variant: python-fastapi
    keep:
      - src/app/**
      - tests/**
      - Dockerfile
      - chart/**

Anything matching a `keep:` pattern survives. Everything else is removed.

Requires:  pip install pathspec PyYAML
"""
from __future__ import annotations

from pathlib import Path

from pathspec import PathSpec

from haraka.post_gen.service.fileOps.files import FileOps
from haraka.utils import Logger, divider
from haraka.post_gen.config import config

_MANIFEST_DIR = Path(__file__).resolve().parent.parent.parent / "manifests"


# --------------------------------------------------------------------------- #
# main purger                                                                 #
# --------------------------------------------------------------------------- #
class ResourcePurger:
    """Filesystem cleaner driven by variant manifest files."""

    def __init__(self, fops: FileOps, logger: Logger | None = None) -> None:
        self._f = fops
        self._log = logger or Logger("ResourcePurger")
        self._log.debug("ResourcePurger initialized with FileOps instance and Logger.")

    # ------------------------------ public API ----------------------------- #
    def purge(self, variant: str, project_dir: Path) -> None:
        """
        Remove everything outside the manifest’s `keep:` patterns.

        Parameters
        ----------
        variant
            Variant key, e.g. ``python-fastapi`` or ``go-grpc-protoc``.
        project_dir
            Root of the freshly generated Cookiecutter project.
        """
        variant = variant.lower()
        self._log.info(f"Starting purge for variant: {variant}")
        self._log.debug(f"Loaded variant for purge: {variant}")

        raw_patterns = config.load_manifest(variant)
        keep_patterns = [p.rstrip("/") for p in raw_patterns]

        self._log.debug(f"Loaded manifest for variant '{variant}': {keep_patterns}")

        spec = config.build_spec(keep_patterns)
        self._log.debug(f"Built PathSpec for keep patterns. Total patterns: {len(keep_patterns)}")

        self._log.info(f"Keeping {len(keep_patterns)} pattern(s)")
        for pattern in keep_patterns:
            self._log.debug(f"Keep pattern: {pattern}")

        self._purge_unrelated(project_dir, spec)
        self._log.debug(f"Finished purging unrelated paths in project directory: {project_dir}")

        divider("Project tree after purge…")
        self._f.print_tree(project_dir)

    # --------------------------------------------------------------------------- #
    # internals                                                                   #
    # --------------------------------------------------------------------------- #
    def _purge_unrelated(self, root: Path, spec: PathSpec) -> None:
        """
        Walk *root* recursively and delete every path **not** matched by *spec*.
        A directory is preserved if **it or any ancestor** is matched.
        """
        all_paths = list(root.rglob("*"))
        self._log.debug("📋 Scanning %d paths under %s", len(all_paths), root)

        keep: list[str] = []
        delete_files: list[str] = []
        delete_dirs: list[str] = []

        for path in all_paths:
            rel = path.relative_to(root).as_posix()

            if spec.match_file(rel):
                keep.append(rel)
                continue

            if path.is_dir():
                if self._dir_has_kept_ancestor(rel, spec):
                    self._log.debug("⏭️  SKIP DIR (kept ancestor): %s", rel)
                else:
                    self._log.debug("❌ DELETE DIR: %s", rel)
                    delete_dirs.append(rel)
            else:
                self._log.debug("❌ DELETE FILE: %s", rel)
                delete_files.append(rel)

        # -- perform deletions -------------------------------------------------- #
        for f in delete_files:
            self._f.remove_file(root / f)

        # delete directories bottom-up to avoid “directory not empty” errors
        for d in sorted(delete_dirs, key=lambda p: p.count("/"), reverse=True):
            (root / d).rmdir()

        # -- summary ------------------------------------------------------------ #
        self._log.info("✅ kept  : %d", len(keep))
        self._log.info("🗂️ dirs  : %d deleted", len(delete_dirs))
        self._log.info("📄 files : %d deleted", len(delete_files))

    @staticmethod
    def _dir_has_kept_ancestor(rel: str, spec: PathSpec) -> bool:
        """
        Return True if *rel* **or any of its ancestors** is matched by *spec*.
        """
        parts = rel.split("/")
        return any(spec.match_file("/".join(parts[: i + 1])) for i in range(len(parts)))
