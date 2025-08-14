import aiofiles

from mono_merger.config import AppConfig
from mono_merger.async_git import AsyncGitRepo


class RepoMerger:
    def __init__(self, config: AppConfig):
        self.config: AppConfig = config
        self.mono_repo: AsyncGitRepo = AsyncGitRepo(self.config.output_dir)

    async def prepare_mono_repo(self) -> None:
        """Initialize a new repo at the directory specified in the config and prepare for merging"""
        self.mono_repo.repo_path.mkdir(parents=True, exist_ok=True)
        await self.mono_repo.run_git_command("init")

        readme_path = self.mono_repo.repo_path / "README.md"
        async with aiofiles.open(readme_path, mode="w") as f:
            await f.write("# Monolith")
            await f.write("This file was created automatically by mono_merger")

        await self.mono_repo.run_git_command("add", "README.md")
        await self.mono_repo.run_git_command("commit")

        # stdout = await self.mono_repo.run_git_command()

    # def clone_repo_branches(self, repo: Repo, target_dir: str) -> bool:
    #     """Clone the specified branches from a repo into their own sub directories, grouped together by domain"""
