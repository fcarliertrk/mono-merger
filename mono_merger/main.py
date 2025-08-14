import asyncio
from mono_merger.config import AppConfig, parse_args, load_config_async, logger
from mono_merger.merge_repos import RepoMerger
from mono_merger.async_git import AsyncGitRepo


async def main(config: AppConfig, async_git_svc: AsyncGitRepo) -> None:
    logger.info("Starting mono-merger workflow")
    logger.info("Output directory: %s", str(config.output_dir))
    logger.info("Processing %s repositories", len(config.repos))

    mono_merger = RepoMerger(config, async_git_svc)

    logger.info("Preparing mono repository")
    await mono_merger.prepare_mono_repo()

    logger.info("Starting repository branch cloning")
    await mono_merger.clone_repo_branches()

    logger.info("Mono-merger workflow completed successfully")


async def bootstrap() -> None:
    try:
        logger.info("Starting mono-merger application")

        args = parse_args()
        logger.info("Loading configuration from: %s", args.config)

        config: AppConfig = await load_config_async(args.config)
        logger.info("Configuration loaded successfully")

        async_git: AsyncGitRepo = AsyncGitRepo(config.output_dir)
        await main(config, async_git)

    except Exception as e:
        logger.exception("Application failed with error: %s", e)
        raise


if __name__ == "__main__":
    asyncio.run(bootstrap())
