import asyncio
from mono_merger.config import AppConfig, parse_args, load_config_async
from mono_merger.merge_repos import RepoMerger
from mono_merger.async_git import AsyncGitRepo


async def main(config: AppConfig, async_git_svc: AsyncGitRepo) -> None:
    mono_merger = RepoMerger(config, async_git_svc)
    await mono_merger.prepare_mono_repo()
    await mono_merger.clone_repo_branches()


async def bootstrap() -> None:
    args = parse_args()
    config: AppConfig = await load_config_async(args.config)
    async_git: AsyncGitRepo = AsyncGitRepo(config.output_dir)
    await main(config, async_git)


if __name__ == "__main__":
    asyncio.run(bootstrap())
