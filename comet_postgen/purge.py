from pathlib import Path
from .files import FileOps
from .utils import divider
from .utils import Logger
from .utils import LANGUAGE_ASSETS, GLOBAL_ASSETS


class ResourcePurger:
    """Delete template artefacts not relevant to the selected language."""

    def __init__(self, fops: FileOps, logger: Logger) -> None:
        self._f = fops
        self._log = logger

    def purge(self, language: str, project_dir: Path) -> None:
        """
        Purge all files and directories not relevant to the selected language,
        but always preserve global assets.
        """
        language = language.lower()
        if language not in LANGUAGE_ASSETS:
            self._log.warn(f"Unrecognized language '{language}'; skipping purge.")
            return

        self._log.info(f"Starting purge for language: {language}")

        # Merge language-specific assets with global assets
        assets_to_keep = LANGUAGE_ASSETS[language].union(GLOBAL_ASSETS)

        # Purge unrelated directories and files
        self._purge_unrelated_assets(project_dir, assets_to_keep)

        divider("Project tree after purge...")
        self._f.print_tree(project_dir)

    def _purge_unrelated_assets(self, root: Path, assets_to_keep: set) -> None:
        """
        Remove all files and directories not listed in assets_to_keep.
        """
        for path in root.rglob("*"):  # Recursively iterate through all files/directories
            # Get the relative path for comparison
            relative_path = path.relative_to(root).as_posix()

            if relative_path not in assets_to_keep:
                # Remove file or directory if it's not in the keep list
                if path.is_file():
                    self._f.remove_file(path)  # Remove file
                    self._log.info(f"Removed file: {relative_path}")
                elif path.is_dir():
                    self._f.remove_dir(path)  # Remove directory
                    self._log.info(f"Removed directory: {relative_path}")
