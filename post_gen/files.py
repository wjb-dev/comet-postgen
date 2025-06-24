import shutil
from pathlib import Path
from .utils import Logger

class FileOps:
    """Filesystem helpers: remove files/dirs, print tree, nice dividers."""
    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    # -------- removal -------------------------------------------------- #
    def remove_file(self, path: Path) -> None:
        try:
            if path.is_file():
                path.unlink()
                self.logger.info(f"Removed file: {path.relative_to(Path.cwd())}")
            elif path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                self.logger.info(f"Removed directory (expected file): {path.relative_to(Path.cwd())}")
        except Exception as e:
            self.logger.warn(f"Could not remove {path}: {e}")

    def remove_dir(self, path: Path) -> None:
        if path.exists():
            try:
                shutil.rmtree(path, ignore_errors=True)
                self.logger.info(f"Removed directory: {path.relative_to(Path.cwd())}")
            except Exception as e:
                self.logger.warn(f"Could not remove directory {path}: {e}")

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
