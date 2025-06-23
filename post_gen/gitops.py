import shutil
from pathlib import Path
from .command import CommandRunner
from .files import FileOps
import subprocess

class GitOps:
    """Git-related operations: init, commit, create remote, push."""

    def __init__(self, runner: CommandRunner, fops: FileOps) -> None:
        self._r = runner
        self._f = fops

    # ------------- public API ----------------------------------------- #
    def init_repo(self, project_dir: Path) -> None:
        if not (project_dir / ".git").exists():
            self._f._log("Initializing Git repository…")
            self._r.run(["git", "init"], cwd=project_dir)
            self._r.run(["git", "branch", "-M", "main"], cwd=project_dir)
        else:
            self._f._log(".git already exists; skipping git init.")

    def stage_commit(self, project_dir: Path) -> None:
        self._f._log("Staging files…")
        self._r.run(["git", "add", "."], cwd=project_dir)
        res = self._r.run(["git", "commit", "-m", "Initial commit"],
                          cwd=project_dir, check=False)
        if not res or res.returncode:
            self._f._warn("'git commit' failed (maybe nothing to commit); continuing…")

    def push_to_github(self, project_dir: Path, author: str,
                       slug: str, description: str) -> None:
        if not self._has_gh():
            return
        if "origin" in self._current_remotes(project_dir):
            self._f._log("Remote 'origin' already exists; skipping create.")
            return
        repo = f"{author}/{slug}"
        self._f._log(f"Creating GitHub repo {repo} & pushing…")
        self._r.run([
            "gh", "repo", "create", repo,
            "--public", "--description", description,
            "--source", ".", "--remote", "origin", "--push", "--confirm"
        ], cwd=project_dir)

    # ------------- internals ------------------------------------------ #
    @staticmethod
    def _current_remotes(project_dir: Path):
        try:
            res = subprocess.run(["git", "remote"], cwd=project_dir,
                                 check=True, text=True,
                                 stdout=subprocess.PIPE)
            return [r.strip() for r in res.stdout.splitlines()]
        except subprocess.CalledProcessError:
            return []

    @staticmethod
    def _has_gh() -> bool:
        return shutil.which("gh") is not None
