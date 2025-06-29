from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Tuple
import yaml
from pathspec import PathSpec


class ManifestDrivenCleaner:
    """
    A class to perform manifest-driven keep/delete checks for a project tree.

    1. Loads “keep” and “protected” globs from a YAML manifest.
    2. Optionally includes service-specific paths based on enabled services.
    3. Walks every path under a root directory.
    4. Classifies paths into keep / delete (files & dirs).
    5. Prints a tidy summary.
    """

    def __init__(self, manifest_path: Path, project_dir: Path, enabled_services: List[str] = []) -> None:
        self.manifest_path = manifest_path
        self.project_dir = project_dir
        self.enabled_services = enabled_services
        self.keep_patterns: List[str] = []
        self._protected_dirs: List[str] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format="%(levelname)-5s %(message)s")

    def load_keep_patterns(self) -> Tuple[List[str], List[str]]:
        with self.manifest_path.open() as f:
            cfg = yaml.safe_load(f)

        raw_keep_patterns = cfg.get("keep", []) or []
        raw_protected_dirs = cfg.get("protected", []) or []
        self.raw_services = cfg.get("services", {}) or {}

        # Start with the unconditional keep patterns
        self.keep_patterns = [p.rstrip("/") for p in raw_keep_patterns]
        self._protected_dirs = [p.rstrip("/") for p in raw_protected_dirs]

        # Add service-specific patterns if enabled
        for service in self.enabled_services:
            if service in self.raw_services:
                self.logger.debug("✅ Including service paths for: %s", service)
                self.keep_patterns.extend(p.rstrip("/") for p in self.raw_services[service])
            else:
                self.logger.warning("⚠️ No manifest section for enabled service: %s", service)

        return self.keep_patterns, self._protected_dirs

    def build_pathspec(self, patterns: List[str]) -> PathSpec:
        return PathSpec.from_lines("gitwildmatch", patterns)

    def walk_tree(self) -> List[Path]:
        paths = list(self.project_dir.rglob("*"))
        self.logger.debug("📋 All paths under %s (total %d):", self.project_dir, len(paths))
        for p in paths:
            self.logger.debug("   %s", p.relative_to(self.project_dir))
        return paths

    def classify_paths(
            self,
            paths: List[Path],
            root: Path,
            spec: PathSpec
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        matched: List[str] = []
        non_matched_files: List[str] = []
        non_matched_dirs: List[str] = []
        directories_skipped: List[str] = []

        matched_set = set()

        # First pass: collect all explicitly matched paths
        for path in paths:
            rel = path.relative_to(self.project_dir).as_posix()
            if spec.match_file(rel):
                self.logger.debug("✅ KEEP      %s", rel)
                matched.append(rel)
                matched_set.add(rel)

                # Also mark parent directories
                parent = Path(rel)
                while parent != Path("."):
                    parent = parent.parent
                    matched_set.add(parent.as_posix())

        # Second pass: classify remaining paths
        for path in paths:
            rel = path.relative_to(self.project_dir).as_posix()

            if rel in matched_set:
                # Don't duplicate log for already added paths
                continue

            if path.is_dir():
                if rel in self._protected_dirs:
                    self.logger.debug("⏭️  SKIPPED: Protected directory: %s", rel)
                    directories_skipped.append(rel)
                elif rel in matched_set:
                    self.logger.debug("✅ KEEP IMPLIED DIR: %s", rel)
                    matched.append(rel)
                else:
                    self.logger.debug("⚠️  CLASSIFIED FOR DELETION (DIR): %s", rel)
                    non_matched_dirs.append(rel)
            else:
                self.logger.debug("⚠️  CLASSIFIED FOR DELETION (FILE): %s", rel)
                non_matched_files.append(rel)

        return sorted(set(matched)), non_matched_dirs, non_matched_files, directories_skipped

    def _print_section(self, title: str, items: List[str]) -> None:
        self.logger.info("%s — %d", title, len(items))
        if items:
            for p in sorted(items):
                if p in self._protected_dirs:
                    self.logger.debug(f"  🛡️  PROTECTED DIRECTORY: DIR {p}")
                else:
                    self.logger.info("  • %s", p)
        else:
            self.logger.info("  (none)")
        self.logger.info("-" * 70)

    def print_summary(
        self,
        matched: List[str],
        non_matched_dirs: List[str],
        non_matched_files: List[str]
    ) -> None:
        self.logger.info("\n" + "=" * 70)
        self._print_section("✅  MATCHED ITEMS (keep)", matched)
        self.logger.info("=" * 70)

        self.logger.info("\n" + "=" * 70)
        self._print_section("🗂️  NON-MATCHED DIRECTORIES (delete)", non_matched_dirs)
        self.logger.info("=" * 70)

        self.logger.info("\n" + "=" * 70)
        self._print_section("📑  NON-MATCHED FILES (delete)", non_matched_files)
        self.logger.info("=" * 70)

    def scan_empty_subdirs(self, directory: Path) -> None:
        self.logger.debug(f"Scanning for empty subdirectories in: {directory}")
        for subdir in directory.iterdir():
            self.logger.debug(f"  🗑️  SCANNING  {subdir}")
            if subdir.is_dir():
                self.scan_empty_subdirs(subdir)
                if not any(subdir.iterdir()):
                    self.logger.debug(f"  🔍 WOULD DELETE EMPTY SUBDIRECTORY: {subdir}")

    def run(self) -> None:
        self.load_keep_patterns()
        spec = self.build_pathspec(self.keep_patterns)

        all_paths = self.walk_tree()
        self.logger.debug("Completed directory walk.")

        matched, non_matched_dirs, non_matched_files, directories_skipped = self.classify_paths(
            all_paths, self.project_dir, spec
        )

        self.print_summary(matched, non_matched_dirs, non_matched_files)


if __name__ == "__main__":
    MANIFEST_PATH = Path("/Users/will/Projects/comet-postgen/haraka/utils/manifests/PyFast.yml")
    ROOT_PATH = Path("/Users/will/Projects/junk2/test-template")

    cleaner = ManifestDrivenCleaner(
        manifest_path=MANIFEST_PATH,
        project_dir=ROOT_PATH,
        enabled_services=["kafka"]  # ← toggle this list
    )
    cleaner.run()
