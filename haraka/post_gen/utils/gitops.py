import shutil
import sys
from pathlib import Path
from .command import CommandRunner
import subprocess
from haraka.utils import Logger

class GitOps:
    """Git-related operations: init, commit, create remote, push."""

    def __init__(self, runner: CommandRunner, logger: Logger) -> None:
        self._r = runner
        self._log = logger

    # ------------- public API ----------------------------------------- #
    def init_repo(self, project_dir: Path) -> None:
        if not (project_dir / ".git").exists():
            self._log.info("Initializing Git repository…")
            self._r.run(["git", "init"], cwd=project_dir)
            self._r.run(["git", "branch", "-M", "main"], cwd=project_dir)
        else:
            self._log.warn(".git already exists; skipping git init.")

    def stage_commit(self, project_dir: Path) -> None:
        self._log.info("Staging files…")
        self._r.run(["git", "add", "."], cwd=project_dir)
        res = self._r.run(["git", "commit", "-m", "Initial commit"],
                          cwd=project_dir, check=False)
        if not res or res.returncode:
            self._log.error("'git commit' failed (maybe nothing to commit); continuing…", file=sys.stderr)

    def push_to_github(self, project_dir: Path, author: str,
                       slug: str, description: str) -> None:
        if not self._has_gh():
            return
        if "origin" in self._current_remotes(project_dir):
            self._log.warn("Remote 'origin' already exists; skipping create.")
            return
        repo = f"{author}/{slug}"
        self._log.info(f"Creating GitHub repo {repo} & pushing…")
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
