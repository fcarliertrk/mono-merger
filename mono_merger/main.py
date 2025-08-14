import asyncio
from mono_merger.config import AppConfig, parse_args, load_config_async
from mono_merger.merge_repos import RepoMerger


async def main(config: AppConfig) -> None:
    mono_merger = RepoMerger(config)
    await mono_merger.prepare_mono_repo()
    await mono_merger.clone_repo_branches()


async def bootstrap() -> None:
    args = parse_args()
    config = await load_config_async(args.config)
    await main(config)


if __name__ == "__main__":
    asyncio.run(bootstrap())
