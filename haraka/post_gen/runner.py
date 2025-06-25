from post_gen.gen_ascii.ascii_art import goLang

from haraka.art.create import Create
from haraka.art.ascii.assets import *
from .config import PostGenConfig
from haraka.utils import divider, Logger
from haraka.post_gen.service.command import CommandRunner
from haraka.post_gen.service.files import FileOps
from haraka.post_gen.service.purge import ResourcePurger
from haraka.post_gen.service.gitops import GitOps


def main(cfg: PostGenConfig) -> None:

    _logger = Logger(cfg.variant)
    logger = _logger.start_logger()

    try:
        cmd = CommandRunner(logger)
        fops = FileOps(logger)
        purge = ResourcePurger(fops, logger)
        git = GitOps(cmd, logger)
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise

    divider("1️⃣  / 4️⃣  – Purge template junk")
    purge.purge(cfg.variant, cfg.project_dir)
    logger.info("Skipping git repo creation (steps 2-4)...")

    if cfg.create_repo:

        divider("2️⃣  / 4️⃣  – Initialise Git repo")
        git.init_repo(cfg.project_dir)

        divider("3️⃣  / 4️⃣  – Commit scaffold")
        git.stage_commit(cfg.project_dir)

        divider("4️⃣  / 4️⃣  – Create GitHub repo & push")
        git.push_to_github(cfg.project_dir, cfg.author, cfg.project_slug, cfg.description)

    divider("🎉 Project generation complete 🎉")

    if cfg.variant == "go-grpc-protoc":
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
        Create.ascii(go_performance_mode)
        Create.logo(go_fast)
