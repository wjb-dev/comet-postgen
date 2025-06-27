from haraka.art.create import Create
from haraka.art.ascii.assets import *
from .config import PostGenConfig
from haraka.utils import divider, Logger
from haraka.post_gen.service.command import CommandRunner
from haraka.post_gen.service.fileOps.files import FileOps
from haraka.post_gen.service.fileOps.purge import ResourcePurger
from haraka.post_gen.service.gitOps.gitops import GitOps


def main(cfg: PostGenConfig) -> None:

    _logger = Logger(cfg.variant)

    logger = _logger.start_logger(cfg.verbose)
    logger.debug("Logger instance created for variant: {cfg.variant}")
    logger.debug(f"Logger started with verbosity: {cfg.verbose}")

    try:
        cmd = CommandRunner(logger)
        logger.debug("CommandRunner initialized")

        fops = FileOps(logger)
        logger.debug("FileOps initialized")

        purge = ResourcePurger(fops, logger)
        logger.debug("ResourcePurger initialized with FileOps")

        git = GitOps(cmd, logger)
        logger.debug("GitOps initialized with CommandRunner")
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise

    divider("1️⃣  / 4️⃣  – Purge template junk")
    logger.debug("Starting template junk purge")

    purge.purge(cfg.variant, cfg.project_dir)
    logger.debug(f"Purge completed for variant: {cfg.variant} in directory: {cfg.project_dir}")

    if cfg.use_git:

        divider("2️⃣  / 4️⃣  – Initialise Git repo")
        logger.debug("Starting Git repository initialization")

        git.init_repo(cfg.project_dir)
        logger.debug(f"Git repository initialized in directory: {cfg.project_dir}")

        divider("3️⃣  / 4️⃣  – Commit scaffold")
        logger.debug("Starting staging and initial commit")

        git.stage_commit(cfg.project_dir)
        logger.debug(f"Initial commit completed in directory: {cfg.project_dir}")

        if cfg.confirm_remote and cfg.author_gh:
            divider("4️⃣  / 4️⃣  – Create GitHub repo & push")
            logger.debug("Starting GitHub repository creation and push")

            git.push_to_github(cfg.project_dir, cfg.author_gh, cfg.project_slug, cfg.description)
            logger.debug(f"Pushed to GitHub: Author: {cfg.author_gh}, Slug: {cfg.project_slug}, Description: {cfg.description}")
        else:
            logger.info("Skipping create remote (step 4)...")
            logger.debug(f"Configuration for confirm_remote: {cfg.confirm_remote}")
    else:
        logger.info("Skipping git repo creation (steps 2-4)...")
        logger.debug(f"Configuration for use_git: {cfg.use_git}")

    divider("🎉 Project generation complete 🎉")
    logger.debug("Project generation completed")

    if cfg.variant == "go-grpc-protoc":
        logger.debug(f"Detected variant: {cfg.variant}, beginning Go-specific steps")
        go_emoji_logo = [emoji["go"]]
        go_performance_mode = [
            goLang, divider_xl, performance_mode, divider_l, tools, divider_s,
            gRPC, divider_mono, protoC, divider_mono, autoMaxProcs, divider_mono,
            ants, divider_mono, zeroLog,
        ]
        go_fast = [
            goFast, gRpc_ProtoBuf, server,
            by, wjb_dev
        ]
        Create.emoji(go_emoji_logo)
        logger.debug("Generated Go emoji logo")

        Create.ascii(go_performance_mode)
        logger.debug("Generated Go performance mode ASCII art")

        Create.logo(go_fast)
        logger.debug("Generated Go fast ASCII logo")
