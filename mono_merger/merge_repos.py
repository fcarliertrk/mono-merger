import asyncio
import aiofiles
import aiofiles.os

from mono_merger.config import AppConfig, RepoConfig, logger
from mono_merger.async_git import AsyncGitRepo


class RepoMerger:
    def __init__(self, config: AppConfig, mono_repo: AsyncGitRepo):
        self.config: AppConfig = config
        self.mono_repo: AsyncGitRepo = mono_repo

        total_branches = sum(len(repo.branches) for repo in config.repos)
        logger.info(
            "RepoMerger initialized with %s repositories, %s total branches", len(config.repos), total_branches
        )
        logger.debug("Domain mapping: %s", config.domain_mapping)

    async def prepare_mono_repo(self) -> None:
        """Initialize a new repo at the directory specified in the config and prepare for merging"""
        logger.info("Preparing mono repository at: %s", self.config.output_dir)

        logger.debug("Creating output directory")
        await aiofiles.os.makedirs(self.config.output_dir, exist_ok=True)

        logger.debug("Initializing git repository")
        await self.mono_repo.init()

        logger.debug("Creating README.md file")
        readme_path = self.mono_repo.repo_path / "README.md"
        async with aiofiles.open(readme_path, mode="w") as f:
            await f.write("# Monolith\n")
            await f.write("This file was created automatically by mono_merger\n")

        logger.debug("Adding README.md to staging and creating initial commit")
        await self.mono_repo.add("README.md")
        await self.mono_repo.commit("first commit")

        logger.info("Mono repository preparation completed successfully")

    async def clone_repo_branches(self) -> None:
        """Clone the specified branches from a repo into their own sub directories, grouped together by domain"""
        total_repos = len(self.config.repos)
        logger.info(
            "Starting repository branch cloning for %s repositories", total_repos
        )

        repo_idx = 0
        batch_num = 1

        while repo_idx < total_repos:
            batch_end = min(repo_idx + 5, total_repos)
            repos = self.config.repos[repo_idx:batch_end]

            logger.info(
                "Processing repository batch %s (%s repositories): %s-%s of %s", batch_num, len(repos), repo_idx + 1, batch_end, total_repos
            )

            tasks = [self._subtree_add_branches(repo) for repo in repos]
            await asyncio.gather(*tasks)

            repo_idx += 5
            batch_num += 1

        logger.info("All repository branches cloned successfully")

    async def _subtree_add_branches(self, repo: RepoConfig):
        """Copies a repo and it's specified branch using subtree add"""
        total_branches = len(repo.branches)
        logger.info("Processing repository: %s (%s branches)", repo.url, total_branches)

        branch_idx = 0

        while branch_idx < total_branches:
            batch_end = min(branch_idx + 5, total_branches)
            branches = repo.branches[branch_idx:batch_end]

            logger.debug(
                "Processing branch batch for %s: %s-%s of %s", repo.url, branch_idx + 1, batch_end, total_branches
            )

            tasks = []
            for branch in branches:
                prefix = f"{branch.domain}/{branch.name}"
                logger.debug(
                    "Preparing subtree add: %s:%s -> %s", repo.url, branch.name, prefix
                )

                task = self.mono_repo.subtree_add(prefix, repo.url, branch.name, True)
                tasks.append(task)

            await asyncio.gather(*tasks)

            logger.info(
                "Completed branch batch for %s: %s branches added", repo.url, len(branches)
            )
            branch_idx += 5

        logger.info(
            "Completed processing repository: %s (all %s branches)", repo.url, total_branches
        )
