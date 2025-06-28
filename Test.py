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
    2. Walks every path under a root directory.
    3. Classifies paths into keep / delete (files & dirs).
    4. Prints a tidy summary.
    """

    def __init__(self, manifest_path: Path, project_dir: Path) -> None:
        self.manifest_path = manifest_path
        self.project_dir = project_dir
        self.keep_patterns: List[str] = []
        self._protected_dirs: List[str] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)-5s %(message)s")

    # --------------------------------------------------------------------------- #
    # I/O helpers                                                                 #
    # --------------------------------------------------------------------------- #
    def load_keep_patterns(self) -> Tuple[List[str], List[str]]:
        """Loads keep-globs and protected-globs from YAML, normalized (no trailing ‘/’)."""
        with self.manifest_path.open() as f:
            cfg = yaml.safe_load(f)

        raw_keep_patterns = cfg.get("keep", [])
        raw_protected_dirs = cfg.get("protected", [])

        self.keep_patterns = [p.rstrip("/") for p in raw_keep_patterns]
        self._protected_dirs = [p.rstrip("/") for p in raw_protected_dirs]

        self.logger.debug("Normalized keep patterns:")
        for pat in self.keep_patterns:
            self.logger.debug("   %s", pat)

        self.logger.debug("Normalized protected patterns:")
        for pat in self._protected_dirs:
            self.logger.debug("   %s", pat)

        return self.keep_patterns, self._protected_dirs

    def build_pathspec(self, patterns: List[str]) -> PathSpec:
        """Build a PathSpec from gitwildmatch lines."""
        return PathSpec.from_lines("gitwildmatch", patterns)

    def walk_tree(self) -> List[Path]:
        """Return every file/dir under the root_path, logging the walk."""
        paths = list(self.project_dir.rglob("*"))
        self.logger.debug("📋 All paths under %s (total %d):", self.project_dir, len(paths))
        for p in paths:
            self.logger.debug("   %s", p.relative_to(self.project_dir))
        return paths

    # --------------------------------------------------------------------------- #
    # Classification helpers                                                      #
    # --------------------------------------------------------------------------- #
    def is_dir_protected(self, rel: str, spec: PathSpec) -> bool:
        """True if *rel* (or an ancestor) is matched by the protected spec."""
        return spec.match_file(rel)

    def classify_paths(
            self,
            paths: List[Path],
            root: Path,
            spec: PathSpec
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Split paths into keep/delete buckets."""
        matched: List[str] = []
        non_matched_files: List[str] = []
        non_matched_dirs: List[str] = []
        directories_skipped: List[str] = []

        for path in paths:
            rel = path.relative_to(self.project_dir).as_posix()

            if spec.match_file(rel):
                self.logger.debug("✅ KEEP      %s", rel)
                matched.append(rel)
                continue

            if path.is_dir():
                if rel in self._protected_dirs:
                    self.logger.debug("⏭️  SKIPPING DELETE: Protected ancestor found: %s", path)
                    directories_skipped.append(rel)
                else:
                    self.logger.debug("❌ DELETE DIR: %s", rel)
                    non_matched_dirs.append(rel)
            else:
                non_matched_files.append(rel)

        return matched, non_matched_dirs, non_matched_files, directories_skipped

    # --------------------------------------------------------------------------- #
    # Summary printing helpers                                                    #
    # --------------------------------------------------------------------------- #
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
        """Human-friendly digest of keep/delete results."""
        self.logger.info("\n" + "=" * 70)
        self._print_section("✅  MATCHED ITEMS (keep)", matched)
        self.logger.info("=" * 70)

        self.logger.info("\n" + "=" * 70)
        self._print_section("🗂️  NON-MATCHED DIRECTORIES (delete)", non_matched_dirs)
        self.logger.info("=" * 70)

        self.logger.info("\n" + "=" * 70)
        self._print_section("📑  NON-MATCHED FILES (delete)", non_matched_files)
        self.logger.info("=" * 70)



    def delete_empty_subdirs(self, directory: Path) -> None:
        """
        Deletes only empty subdirectories within a given directory.

        Args:
            directory (Path): The directory to check for empty subdirectories.
        """
        for subdir in directory.iterdir():
            self.logger.debug(f"  🗑️  SCANNING  {subdir}")
            if subdir.is_dir():  # Ensure it's a directory
                self.delete_empty_subdirs(subdir)  # Recursively process subdirectories
                # If the subdirectory is empty after recursion, delete it
                if not any(subdir.iterdir()):  # Check if it's empty
                    self.logger.debug(f"  🗑️  DELETING EMPTY SUBDIRECTORY {subdir}")
                    subdir.rmdir()

    # --------------------------------------------------------------------------- #
    # Main driver                                                                 #
    # --------------------------------------------------------------------------- #
    def run(self) -> None:
        # Step 1: Load patterns
        project = self.project_dir
        self.load_keep_patterns()
        spec = self.build_pathspec(self.keep_patterns)

        # Step 2: Walk the tree
        all_paths = self.walk_tree()

        # Step 3: Classify paths
        matched, non_matched_dirs, non_matched_files, directories_skipped = self.classify_paths(
            all_paths, project, spec)

        # Step 4: Print the summary
        self.print_summary(matched, non_matched_dirs, non_matched_files)


if __name__ == "__main__":
    MANIFEST_PATH = Path(
        "/Users/will/Projects/comet-postgen/haraka/utils/manifests/PyFast.yml"
    )
    ROOT_PATH = Path("/Users/will/Projects/junk2/test-template")

    cleaner = ManifestDrivenCleaner(MANIFEST_PATH, ROOT_PATH)
    cleaner.run()
