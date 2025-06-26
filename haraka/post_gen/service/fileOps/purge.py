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

    # ----------------------------- internals ------------------------------ #
    def _purge_unrelated(self, root: Path, spec: PathSpec) -> None:
        """
        Walk the project tree; delete every path NOT matched by *spec*.

        Updated to align with the `test_java_manifest` logic for cleaner organization.
        """

        # Dictionaries to separate matches and non-matches for logging

        # 1) Dump every path under root or state what was found
        all_paths = list(root.rglob("*"))
        if self._log.evm:
            self._log.debug(f"📋 All paths under {root} (total {len(all_paths)}):")
            for p in all_paths:
                print(f"{p.relative_to(root)}")
        else:
            self._log.debug(f"Found {len(all_paths)} paths under {root})")

        matches, non_matched_files, directories_skipped, non_matched_dirs = [], [], [], []
        for path in all_paths:
            self._log.debug(f"\nScanning path: {path}")
            rel = path.relative_to(root).as_posix()
            self._log.debug(f"Relative path for inspection: {rel}")
            # Match file against the PathSpec
            if spec.match_file(rel):
                self._log.debug(f"✅ KEEP: Path matches keep patterns: {rel}")
                matches.append(path)  # Collect paths to keep
            else:
                if path.is_dir():
                    if self._is_dir_protected(rel, spec):
                        self._log.debug(f"{"⏭️ SKIPPING DELETE: Protected ancestor found: %s", path}")
                        directories_skipped.append(rel)
                    else:
                        self._log.debug(f"{"❌ DELETE DIR: %s", rel}")
                        non_matched_dirs.append(rel)
                else:
                    non_matched_files.append(rel)
                    self._f.remove_file(path)
                    self._log.debug(f"{"❌ DELETE FILE: %s", rel}")



            # Non-matching paths: collect and delete
            self._log.debug(f"❌ DELETE: Path does not match keep patterns: {rel}")

            if path.is_dir():
                directories_skipped.append(path)
                self._log.debug(f"⏭️ SKIPPING DELETE: Path is a directory: {path}")

        # Print results cleanly for debugging/logging purposes
        self._log.info("\nMATCHED PATHS:")
        self._log.info("=" * 80)
        for match in matches:
            self._log.info(f"✅ {match}")

        self._log.info("\nNOT MATCHED PATHS:")
        self._log.info("=" * 80)
        for non_match in non_matched_files:
            self._log.info(f"❌ {non_match}")

    @staticmethod
    def _is_dir_protected(relative_path: str, spec: PathSpec) -> bool:
        """
        Walks from `path` up to `root`, and returns True if any ancestor
        is matched by the spec.
        """
        if spec.match_file(relative_path):
            return True
        return False