from .utils.config      import PostGenConfig
from .utils             import divider
from .utils             import Logger, get_label
from .command           import CommandRunner
from .files             import FileOps
from .purge             import ResourcePurger
from .gitops            import GitOps
from .gen_ascii         import gen

def main(cfg: PostGenConfig) -> None:

    logger = init_logger(cfg.language)
    cmd = CommandRunner(logger)
    fops  = FileOps(logger)
    purge = ResourcePurger(fops, logger)
    git   = GitOps(cmd, logger)

    divider("1️⃣  / 4️⃣  – Purge template junk")
    purge.purge(cfg.language, cfg.project_dir)

    divider("2️⃣  / 4️⃣  – Initialise Git repo")
    git.init_repo(cfg.project_dir)

    divider("3️⃣  / 4️⃣  – Commit scaffold")
    git.stage_commit(cfg.project_dir)

    divider("4️⃣  / 4️⃣  – Create GitHub repo & push")
    git.push_to_github(cfg.project_dir, cfg.author, cfg.project_slug, cfg.description)

    divider("🎉 Project generation complete 🎉")
    if cfg.language == "go" and not cfg.swagger:
        gen.print_go_performance_mode_art()

def init_logger(lang) -> Logger:
    label = get_label(lang)
    return Logger(label)

