import asyncio
import time
from pathlib import Path
from mono_merger.config import logger

FATAL_ERR_EXIT_CODE = 128


class AsyncGitRepo:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        logger.debug("AsyncGitRepo initialized with path: %s", self.repo_path)

    async def init(self) -> str:
        """Initialize a git repository"""
        logger.info("Initializing git repository at %s", self.repo_path)
        result = await self._run_git_command("init")
        logger.info("Git repository initialized successfully")
        return result

    async def add(self, *files) -> str:
        """Add files to staging area"""
        logger.debug("Adding files to staging area: %s", ', '.join(files))
        return await self._run_git_command("add", *files)

    async def commit(self, message: str) -> str:
        """Create a commit with message"""
        logger.debug("Creating commit with message: %s", message)
        result = await self._run_git_command("commit", "-m", message)
        logger.info("Commit created successfully: %s", message)
        return result

    async def subtree_add(
        self,
        prefix: str,
        repository: str,
        ref: str = "main",
        squash: bool = False,
    ) -> str:
        """Add a subtree"""
        logger.info(
            "Adding subtree - Repository: %s, Branch: %s, Prefix: %s", repository, ref, prefix
        )

        args = ["subtree", "add", "--prefix", prefix, repository, ref]

        if squash:
            args.append("--squash")
            logger.debug("Using squash option for subtree add")

        result = await self._run_git_command(*args, timeout=600)
        logger.info("Subtree add completed successfully for %s:%s", repository, ref)
        return result

    async def _run_git_command(self, *args, timeout: int = 300) -> str:
        """Run a git command asynchronously"""
        command_str = "git %s" % ' '.join(args)
        start_time = time.time()

        logger.debug("Executing git command: %s", command_str)
        logger.debug("Working directory: %s", self.repo_path)

        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                *args,
                cwd=self.repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            execution_time = time.time() - start_time

            # Log command output for debugging
            if stdout:
                logger.debug("Git command stdout: %s", stdout.decode().strip())
            if stderr:
                logger.debug("Git command stderr: %s", stderr.decode().strip())

            if process.returncode == FATAL_ERR_EXIT_CODE:
                error_msg = (
                    "Git command failed: %s\nError: %s" % (command_str, stderr.decode())
                )
                logger.error(error_msg)
                raise Exception(error_msg)
            elif process.returncode != 0:
                warning_msg = "Git command returned non-zero exit code %s: %s" % (process.returncode, command_str)
                logger.warning(warning_msg)

            logger.debug(
                "Git command completed in %.2fs: %s", execution_time, command_str
            )
            return stdout.decode().strip()

        except asyncio.TimeoutError:
            if process.returncode is None:
                process.kill()
                await process.wait()
            error_msg = "Git command timed out after %ss: %s" % (timeout, command_str)
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error("Git command failed: %s - %s", command_str, e)
            raise
