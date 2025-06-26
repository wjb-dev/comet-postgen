import shutil
import sys
from pathlib import Path
from haraka.post_gen.service.command import CommandRunner
import subprocess
from haraka.utils import Logger

class GitOps:
    """Git-related operations: init, commit, create remote, push."""

    def __init__(self, runner: CommandRunner, logger: Logger) -> None:
        self._r = runner
        self._log = logger

    # ------------- public API ----------------------------------------- #
    def init_repo(self, project_dir: Path) -> None:
        self._log.debug(f"Checking if {project_dir}/.git exists…")
        if not (project_dir / ".git").exists():

            self._log.info("Initializing Git repository…")
            self._log.debug(f"Running 'git init' in {project_dir}…")

            self._r.run(["git", "init"], cwd=project_dir)
            self._log.debug("Git repository initialized successfully.")

            self._log.debug("Setting default branch to 'main'…")
            self._r.run(["git", "branch", "-M", "main"], cwd=project_dir)
            self._log.debug("Default branch set successfully.")
        else:
            self._log.warn(f"{project_dir}/.git already exists; skipping git init.")

    def stage_commit(self, project_dir: Path) -> None:
        self._log.info("Staging files…")
        self._log.debug(f"Running 'git add .' in {project_dir}…")

        self._r.run(["git", "add", "."], cwd=project_dir)
        self._log.debug("Files staged successfully.")

        self._log.debug("Committing changes with message: 'Initial commit'…")
        res = self._r.run(["git", "commit", "-m", "Initial commit"],
                          cwd=project_dir, check=False)
        if not res or res.returncode:
            self._log.error("'git commit' failed (perhaps nothing to commit); continuing…", file=sys.stderr)
        else:
            self._log.debug("'git commit' executed successfully.")

    def push_to_github(self, project_dir: Path, author: str,
                       slug: str, description: str) -> None:
        self._log.debug("Checking if GitHub CLI ('gh') is installed…")
        if not self._has_gh():
            self._log.warn("GitHub CLI ('gh') not found; skipping.")
            return
        self._log.debug(f"Checking existing remotes in {project_dir}…")
        if "origin" in self._current_remotes(project_dir):
            self._log.debug("Remote 'origin' already exists; skipping creation.")
            self._log.warn("Remote 'origin' already exists; skipping create.")
            return
        self._log.debug("No existing 'origin' found; proceeding to create a new GitHub repo.")
        repo = f"{author}/{slug}"
        self._log.debug(f"Prepared repository slug: {repo}")

        self._log.info(f"Creating GitHub repo {repo} & pushing…")
        self._log.debug(f"Running 'gh repo create' for {repo} with description: '{description}'…")
        self._r.run([
            "gh", "repo", "create", repo,
            "--public", "--description", description,
            "--source", ".", "--remote", "origin", "--push", "--confirm"
        ], cwd=project_dir)
        self._log.debug(f"GitHub repo {repo} created and code pushed successfully.")

    # ------------- internals ------------------------------------------ #
    def _current_remotes(self, project_dir: Path):
        try:
            self._log.debug(f"Fetching remotes for repository at {project_dir}…")
            res = subprocess.run(["git", "remote"], cwd=project_dir,
                                 check=True, text=True,
                                 stdout=subprocess.PIPE)
            remotes = [r.strip() for r in res.stdout.splitlines()]
            self._log.debug(f"Found remotes: {remotes}")
            return remotes
        except subprocess.CalledProcessError:
            self._log.warn("Failed to fetch remotes; returning an empty list.")
            return []

    def _has_gh(self) -> bool:
        result = shutil.which("gh") is not None
        self._log.debug(f"'gh' command found: {result}")
        return result
