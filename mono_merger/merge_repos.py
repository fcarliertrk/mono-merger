import asyncio
import aiofiles

from mono_merger.config import AppConfig, RepoConfig
from mono_merger.async_git import AsyncGitRepo


class RepoMerger:
    def __init__(self, config: AppConfig):
        self.config: AppConfig = config
        self.mono_repo: AsyncGitRepo = AsyncGitRepo(self.config.output_dir)

    async def prepare_mono_repo(self) -> None:
        """Initialize a new repo at the directory specified in the config and prepare for merging"""
        self.mono_repo.repo_path.mkdir(parents=True, exist_ok=True)
        await self.mono_repo.init()

        readme_path = self.mono_repo.repo_path / "README.md"
        async with aiofiles.open(readme_path, mode="w") as f:
            await f.write("# Monolith\n")
            await f.write("This file was created automatically by mono_merger\n")

        await self.mono_repo.add("README.md")
        await self.mono_repo.commit("first commit")

    async def clone_repo_branches(self) -> None:
        """Clone the specified branches from a repo into their own sub directories, grouped together by domain"""
        repo_idx = 0
        while repo_idx < len(self.config.repos):
            repos = self.config.repos[repo_idx : repo_idx + 5]
            tasks = [self._subtree_add_branches(repo) for repo in repos]
            await asyncio.gather(*tasks)
            repo_idx += 5

    async def _subtree_add_branches(self, repo: RepoConfig):
        branch_idx = 0
        while branch_idx < len(repo.branches):
            branches = repo.branches[branch_idx : branch_idx + 5]
            tasks = [
                self.mono_repo.subtree_add(
                    f"{branch.domain}/{branch.name}", repo.url, branch.name, True
                )
                for branch in branches
            ]
            await asyncio.gather(*tasks)
            branch_idx += 5
        pass
