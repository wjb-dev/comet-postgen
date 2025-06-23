from pathlib import Path
from .config import PostGenConfig
from .command import CommandRunner
from .files   import FileOps
from .purge   import ResourcePurger
from .gitops  import GitOps
from .generate_ascii import gen

def main() -> None:
    cfg = PostGenConfig(
        language     = "go",
        project_slug = "{{ cookiecutter.project_slug }}",
        author       = "{{ cookiecutter.author }}",
        description  = "{{ cookiecutter.description }}",
        project_dir  = Path.cwd(),
        swagger      = False
    )

    cmd   = CommandRunner()
    fops  = FileOps()
    purge = ResourcePurger(fops)
    git   = GitOps(cmd, fops)

    fops.divider("Stage 1  –  Purge template junk")
    purge.purge(cfg.language, cfg.project_dir)

    fops.divider("Stage 2  –  Initialise Git repo")
    git.init_repo(cfg.project_dir)

    fops.divider("Stage 3  –  Commit scaffold")
    git.stage_commit(cfg.project_dir)

    fops.divider("Stage 4  –  Create GitHub repo & push")
    git.push_to_github(cfg.project_dir, cfg.author, cfg.project_slug, cfg.description)

    fops.divider("Project generation complete 🎉")
    if cfg.language == "go" and not cfg.swagger:
        gen.print_go_performance_mode_art()
