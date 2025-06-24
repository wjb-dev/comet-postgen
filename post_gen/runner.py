from .utils.config      import PostGenConfig
from .utils             import divider
from .utils             import logger
from .command           import CommandRunner
from .files             import FileOps
from .purge             import ResourcePurger
from .gitops            import GitOps
from .gen_ascii         import gen
from .utils.common.globals import label

def main(cfg: PostGenConfig) -> None:
    global label
    cmd   = CommandRunner()
    label = logger.get_label(cfg.language)
    fops  = FileOps()
    purge = ResourcePurger()
    git   = GitOps(cmd)

    divider("1️⃣/ 4️⃣–  Purge template junk")
    purge.purge(cfg.language, cfg.project_dir)

    divider("2️⃣/ 4️⃣–  Initialise Git repo")
    git.init_repo(cfg.project_dir)

    divider("3️⃣/ 4️⃣–  Commit scaffold")
    git.stage_commit(cfg.project_dir)

    divider("4️⃣/ 4️⃣–  Create GitHub repo & push")
    git.push_to_github(cfg.project_dir, cfg.author, cfg.project_slug, cfg.description)

    divider("Project generation complete 🎉")
    if cfg.language == "go" and not cfg.swagger:
        gen.print_go_performance_mode_art()
