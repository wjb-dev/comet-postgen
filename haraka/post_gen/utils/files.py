import shutil
from pathlib import Path
from haraka.utils import Logger

class FileOps:
    """Filesystem helpers: remove files/dirs, print tree, nice dividers."""
    def __init__(self, logger: Logger = Logger("⚙️️️️️️️️️️️️Testing⚙️"), test_mode=False) -> None:
        self.logger = logger
        self.test_mode = test_mode

    def _relpath(self, path: Path) -> str:
        try:
            return str(path.relative_to(Path.cwd()))
        except ValueError:
            return str(path) if self.test_mode else f"<non-project-path>: {path}"

    def remove_file(self, path: Path) -> None:
        try:
            if path.is_file():
                path.unlink()
                self.logger.info(f"Removed file: {self._relpath(path)}")
            elif path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                self.logger.info(f"Removed directory (expected file): {self._relpath(path)}")
        except Exception as e:
            self.logger.warn(f"Could not remove {self._relpath(path)}: {e}")

    def remove_dir(self, path: Path) -> None:
        if path.exists():
            try:
                shutil.rmtree(path, ignore_errors=True)
                self.logger.info(f"Removed directory: {self._relpath(path)}")
            except Exception as e:
                self.logger.warn(f"Could not remove directory {self._relpath(path)}: {e}")

    def print_tree(self, path: Path, prefix: str = "") -> None:
        if not path.exists():
            self.logger.warn(f"Path does not exist: {path}")
            return
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        for i, entry in enumerate(entries):
            branch = "└── " if i == len(entries) - 1 else "├── "
            print(prefix + branch + entry.name)
            if entry.is_dir():
                ext = "    " if i == len(entries) - 1 else "│   "
                self.print_tree(entry, prefix + ext)
