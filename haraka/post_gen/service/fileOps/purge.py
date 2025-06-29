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
    protected:
      - runConfigurations
    services:
      kafka:
        - src/kafka/**
        - configs/kafka.yaml

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


class ResourcePurger:
    """Filesystem cleaner driven by variant manifest files."""

    def __init__(self, fops: FileOps, logger: Logger | None = None) -> None:
        self._f = fops
        self._log = logger or Logger("ResourcePurger")
        self._log.debug("ResourcePurger initialized with FileOps instance and Logger.")
        self._protected_dirs: List[str] = []

    def purge(self, variant: str, project_dir: Path, enabled_services: List[str] = []) -> None:
        """
        Remove everything outside the manifest’s `keep:` patterns.

        Parameters
        ----------
        variant
            Variant key, e.g. ``PyFast`` or ``GoUltraFast``.
        project_dir
            Root of the freshly generated Cookiecutter project.
        enabled_services
            Optional list of enabled services to include in keep patterns.
        """
        variant = variant.lower()
        self._log.info(f"Starting purge for variant: {variant}")
        manifest = config.load_manifest(variant)  # assumes full manifest dict

        raw_keep = manifest.get("keep", []) or []
        raw_protected = manifest.get("protected", []) or []
        service_patterns = manifest.get("services", {}) or {}

        keep_patterns = [p.rstrip("/") for p in raw_keep]
        self._protected_dirs = [p.rstrip("/") for p in raw_protected]

        for service in enabled_services:
            if service in service_patterns:
                self._log.debug(f"✅ Including service paths for: {service}")
                keep_patterns.extend(p.rstrip("/") for p in service_patterns[service])
            else:
                self._log.warn(f"⚠️ No manifest section for enabled service: {service}")

        spec = config.build_spec(keep_patterns)
        self._log.debug(f"Built PathSpec for keep patterns. Total: {len(keep_patterns)}")
        for pattern in keep_patterns:
            self._log.debug(f"Keep pattern: {pattern}")

        all_paths = self._walk_tree(project_dir)

        matched, non_matched_dirs, non_matched_files, directories_skipped = \
            self.classify_paths(all_paths, project_dir, spec)

        self._purge_unrelated(
            project_dir,
            matched,
            non_matched_dirs,
            non_matched_files,
            directories_skipped
        )

        self._log.debug(f"Finished purging unrelated paths in project directory: {project_dir}")
        divider("Project tree after purge…")
        self._f.print_tree(project_dir)

    def _walk_tree(self, root: Path) -> List[Path]:
        paths = list(root.rglob("*"))
        self._log.debug(f"📋 All paths under {root} (total {len(paths)}):")
        for p in paths:
            self._log.debug(f"   {p.relative_to(root)}")
        return paths

    def classify_paths(
        self,
        paths: List[Path],
        root: Path,
        spec: PathSpec,
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        matched: List[str] = []
        non_matched_files: List[str] = []
        non_matched_dirs: List[str] = []
        directories_skipped: List[str] = []

        matched_set = set()

        for path in paths:
            rel = path.relative_to(root).as_posix()

            if spec.match_file(rel):
                self._log.debug(f"✅ KEEP      {rel}")
                matched.append(rel)
                matched_set.add(rel)
                continue

            if path.is_dir():
                if rel in self._protected_dirs:
                    self._log.debug(f"⏭️  SKIPPING DELETE: Protected directory: {rel}")
                    directories_skipped.append(rel)
                else:
                    self._log.debug(f"❌ DELETE DIR: {rel}")
                    non_matched_dirs.append(rel)
            else:
                self._log.debug(f"❌ DELETE FILE: {rel}")
                non_matched_files.append(rel)

        return matched, non_matched_dirs, non_matched_files, directories_skipped

    def _print_section(self, title: str, items: List[str]) -> None:
        self._log.info(f"{title} — {len(items)}")
        if items:
            for p in sorted(items):
                self._log.info(f"  • {p}")
        else:
            self._log.info("  (none)")
        self._log.info("-" * 70)

    def _dir_batch_delete(self, items: List[str], root: Path) -> None:
        for p in sorted(items):
            if p in self._protected_dirs:
                self._log.debug(f"  🛡️  PROTECTED DIRECTORY: {p}")
            else:
                full_path = root / Path(p)
                self._f.remove_dir(full_path)

    def _file_batch_delete(self, items: List[str], root: Path) -> None:
        for p in sorted(items):
            full_path = root / Path(p)
            self._f.remove_file(full_path)

    def _purge_unrelated(
        self,
        root: Path,
        matched: List[str],
        non_matched_dirs: List[str],
        non_matched_files: List[str],
        directories_skipped: List[str],
    ) -> None:
        self._log.info("\n" + "=" * 70)
        self._print_section("✅ MATCHED (keep)", matched)
        self._log.info("=" * 70)

        self._log.info("\n" + "=" * 70)
        self._print_section("⏭️  SKIPPED PROTECTED DIRECTORIES", directories_skipped)
        self._log.info("=" * 70)

        self._log.info("\n" + "=" * 70)
        self._print_section("🗂️  NON-MATCHED DIRECTORIES (delete)", non_matched_dirs)
        self._dir_batch_delete(non_matched_dirs, root)
        self._log.info("=" * 70)

        self._log.info("\n" + "=" * 70)
        self._print_section("📄 NON-MATCHED FILES (delete)", non_matched_files)
        self._file_batch_delete(non_matched_files, root)
        self._log.info("=" * 70)
