import os, shutil, sys
from pathlib import Path

class FileOps:
    """Filesystem helpers: remove files/dirs, print tree, nice dividers."""

    # -------- removal -------------------------------------------------- #
    def remove_file(self, path: Path) -> None:
        try:
            if path.is_file():
                path.unlink()
                self._log(f"Removed file: {path.relative_to(Path.cwd())}")
            elif path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                self._log(f"Removed directory (expected file): {path.relative_to(Path.cwd())}")
        except Exception as e:
            self._warn(f"Could not remove {path}: {e}")

    def remove_dir(self, path: Path) -> None:
        if path.exists():
            try:
                shutil.rmtree(path, ignore_errors=True)
                self._log(f"Removed directory: {path.relative_to(Path.cwd())}")
            except Exception as e:
                self._warn(f"Could not remove directory {path}: {e}")

    # -------- pretty printing ------------------------------------------ #
    def divider(self, title: str, *, char: str = "=") -> None:
        width = self._term_width()
        print("\n" + char * width)
        print(title)
        print(char * width + "\n")

    def print_tree(self, path: Path, prefix: str = "") -> None:
        if not path.exists():
            self._warn(f"Path does not exist: {path}")
            return
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        for i, entry in enumerate(entries):
            branch = "└── " if i == len(entries) - 1 else "├── "
            print(prefix + branch + entry.name)
            if entry.is_dir():
                ext = "    " if i == len(entries) - 1 else "│   "
                self.print_tree(entry, prefix + ext)

    # -------- internals ------------------------------------------------ #
    @staticmethod
    def _term_width() -> int:
        try:
            return os.get_terminal_size().columns
        except OSError:
            return 60

    @staticmethod
    def _log(msg: str) -> None:
        print(f"[post_gen] {msg}")

    @staticmethod
    def _warn(msg: str) -> None:
        print(f"[post_gen] Warning: {msg}", file=sys.stderr)
