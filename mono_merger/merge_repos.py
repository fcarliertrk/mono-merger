import asyncio
import aiofiles
import aiofiles.os

from mono_merger.config import AppConfig, RepoConfig, BranchConfig, logger
from mono_merger.async_git import AsyncGitRepo


def get_branch_name(ref_str: str) -> str:
    """Extracts branch name from ref string"""
    return ref_str.split('refs/heads/')[-1]


def get_repo_name(url: str) -> str:
    """Extracts repository name from repo URL (SSH)"""
    repo = url.strip().split("/")[-1]
    return repo.removesuffix(".git")


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
        all_branches: BranchConfig = next((branch for branch in repo.branches if branch.name == 'all'), None)

        if all_branches:
            list_branches_result = await self.mono_repo.list_branches(repo.url)
            print(list_branches_result.split())
            branch_list = [
                BranchConfig(name=get_branch_name(result), domain=all_branches.domain)
                for result in list_branches_result.split()
                if 'refs/heads/' in result
            ]
        else:
            branch_list = repo.branches

        total_branches = len(branch_list)
        logger.info("Processing repository: %s (%s branches)", repo.url, total_branches)

        branch_idx = 0
        while branch_idx < len(branch_list):
            batch_end = min(branch_idx + 5, total_branches)
            branches = branch_list[branch_idx:batch_end]

            logger.debug(
                "Processing branch batch for %s: %s-%s of %s", repo.url, branch_idx + 1, batch_end, total_branches
            )

            tasks = []
            for branch in branches:
                prefix = f"{branch.domain}/{get_repo_name(repo.url)}/{branch.name}"
                print(prefix)
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
