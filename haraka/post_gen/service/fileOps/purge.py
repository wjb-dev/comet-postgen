#!/usr/bin/env python3
"""
haraka.post_gen.utils.purge

Delete all template artefacts that are **not** required for the chosen
variant, as defined by a YAML manifest in `haraka/manifests/<variant>.yml`.

Manifest format (git-wildmatch globs):

    variant: PyFast
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
from typing import Tuple, List

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
        self._protected_dirs: List[str] = []

    # ------------------------------ public API ----------------------------- #
    def purge(self, variant: str, project_dir: Path) -> None:
        """
        Remove everything outside the manifest’s `keep:` patterns.

        Parameters
        ----------
        variant
            Variant key, e.g. ``PyFast`` or ``GoUltraFast``.
        project_dir
            Root of the freshly generated Cookiecutter project.
        """
        variant = variant.lower()
        self._log.info(f"Starting purge for variant: {variant}")
        self._log.debug(f"Loaded variant for purge: {variant}")

        raw_patterns, raw_protected_dirs = config.load_manifest(variant)
        keep_patterns = [p.rstrip("/") for p in raw_patterns]
        self._protected_dirs = [p.rstrip("/") for p in raw_protected_dirs]

        self._log.debug(f"Loaded manifest for variant '{variant}': {keep_patterns}")

        spec = config.build_spec(keep_patterns)
        self._log.debug(f"Built PathSpec for keep patterns. Total patterns: {len(keep_patterns)}")

        self._log.info(f"Keeping {len(keep_patterns)} pattern(s)")
        for pattern in keep_patterns:
            self._log.debug(f"Keep pattern: {pattern}")

        all_paths = self._walk_tree(project_dir)

        matched, non_matched_dirs, non_matched_files, directories_skipped = \
            self.classify_paths(all_paths, project_dir, spec)

        self._purge_unrelated(
            project_dir,
            matched,
            non_matched_dirs,
            non_matched_files
        )

        self._log.debug(f"Finished purging unrelated paths in project directory: {project_dir}")

        divider("Project tree after purge…")
        self._f.print_tree(project_dir)


    # ----------------------------- internals ------------------------------ #

    def _walk_tree(self, root: Path) -> List[Path]:
        """Return every file/dir under *root*, logging the walk."""
        paths = list(root.rglob("*"))
        self._log.debug(f"📋 All paths under {root} (total {len(paths)}:")
        for p in paths:
            self._log.debug(f"   {p.relative_to(root)}")
        return paths


    # --------------------------------------------------------------------------- #
    # Classification helpers                                                      #
    # --------------------------------------------------------------------------- #

    def classify_paths(
            self,
            paths: List[Path],
            root: Path,
            spec: PathSpec,
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Split paths into keep/delete buckets."""
        matched: List[str] = []
        non_matched_files: List[str] = []
        non_matched_dirs: List[str] = []
        directories_skipped: List[str] = []

        for path in paths:
            rel = path.relative_to(root).as_posix()

            if spec.match_file(rel):
                self._log.debug(f"✅ KEEP      {rel}")
                matched.append(rel)
                continue

            if path.is_dir():
                # skip deletion if this dir is exactly in protected list
                if rel in self._protected_dirs:
                    self._log.debug(f"⏭️  SKIPPING DELETE: Protected ancestor found: {path}")
                    directories_skipped.append(rel)
                else:
                    self._log.debug(f"❌ DELETE DIR: {rel}")
                    non_matched_dirs.append(rel)
            else:
                non_matched_files.append(rel)

        return matched, non_matched_dirs, non_matched_files, directories_skipped

    # --------------------------------------------------------------------------- #
    # Summary printing helpers                                                    #
    # --------------------------------------------------------------------------- #
    def _print_matches(self, title: str, items: List[str]) -> None:
        self._log.info(f"{title} — {len(items)}")
        if items:
            for p in sorted(items):
                self._log.info(f"  • {p}")
        else:
            self._log.info("  (none)")
        self._log.info("-" * 70)

    def _dir_batch_delete(self, title: str, items: List[str], root: Path) -> None:
        self._log.info(f"{title} — {len(items)}")
        if items:
            for p in sorted(items):
                # only protect exact matches
                if p in self._protected_dirs:
                    self._log.debug(f"  🛡️  PROTECTED DIRECTORY  DIR {p}")
                else:
                    full_path = root / Path(p)
                    self._f.remove_dir(full_path)
        else:
            self._log.info("  (none)")
        self._log.info("-" * 70)

    def _file_batch_delete(self, title: str, items: List[str], root: Path) -> None:
        self._log.info(f"{title} — {len(items)}")
        if items:
            for p in sorted(items):
                full_path = root / Path(p)
                self._f.remove_file(full_path)
        else:
            self._log.info("  (none)")
        self._log.info("-" * 70)

    def _purge_unrelated(
            self,
            root: Path,
            matched: List[str],
            non_matched_dirs: List[str],
            non_matched_files: List[str]
    ) -> None:
        """Human-friendly digest of keep/delete results."""
        self._log.info("\n" + "=" * 70)
        self._print_matches("✅ MATCHED (keep)", matched)
        self._dir_batch_delete("🗂️  NON-MATCHED DIRECTORIES (delete)", non_matched_dirs, root)
        self._file_batch_delete("📄 NON-MATCHED FILES (delete)", non_matched_files, root)
        self._log.info("=" * 70)
