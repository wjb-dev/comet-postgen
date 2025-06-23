from pathlib import Path
from .files import FileOps

class ResourcePurger:
    """Delete template artefacts not relevant to the selected language."""

    def __init__(self, fops: FileOps) -> None:
        self._f = fops

    def purge(self, language: str, project_dir: Path) -> None:
        language = language.lower()
        if language == "cpp":
            self._purge_cpp(project_dir)
        elif language == "go":
            self._purge_go(project_dir)
        else:
            self._f._warn(f"Unrecognised language '{language}'; skipping purge.")
            return

        self._f.divider("Project tree after purge")
        self._f.print_tree(project_dir)

    # ------------------------------------------------------------------ #
    def _purge_cpp(self, root: Path) -> None:
        self._f.remove_dir(root / "src" / "go")
        for f in ("Dockerfile", "Dockerfile.go", "Makefile.go"):
            self._f.remove_file(root / f)

    def _purge_go(self, root: Path) -> None:
        self._f.remove_dir(root / "src")
        self._f.remove_dir(root / "tests")
        for f in ("Dockerfile.cpp", "Makefile.cpp"):
            self._f.remove_file(root / f)
