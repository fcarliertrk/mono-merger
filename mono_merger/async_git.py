import asyncio
import time
from pathlib import Path
from mono_merger.config import logger

FATAL_ERR_EXIT_CODE = 128


class AsyncGitRepo:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        logger.debug(f"AsyncGitRepo initialized with path: {self.repo_path}")

    async def init(self) -> str:
        """Initialize a git repository"""
        logger.info(f"Initializing git repository at {self.repo_path}")
        result = await self._run_git_command("init")
        logger.info("Git repository initialized successfully")
        return result

    async def add(self, *files) -> str:
        """Add files to staging area"""
        logger.debug(f"Adding files to staging area: {', '.join(files)}")
        return await self._run_git_command("add", *files)

    async def commit(self, message: str) -> str:
        """Create a commit with message"""
        logger.debug(f"Creating commit with message: {message}")
        result = await self._run_git_command("commit", "-m", message)
        logger.info(f"Commit created successfully: {message}")
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
            f"Adding subtree - Repository: {repository}, Branch: {ref}, Prefix: {prefix}"
        )

        args = ["subtree", "add", "--prefix", prefix, repository, ref]

        if squash:
            args.append("--squash")
            logger.debug("Using squash option for subtree add")

        result = await self._run_git_command(*args, timeout=600)
        logger.info(f"Subtree add completed successfully for {repository}:{ref}")
        return result

    async def _run_git_command(self, *args, timeout: int = 300) -> str:
        """Run a git command asynchronously"""
        command_str = f"git {' '.join(args)}"
        start_time = time.time()

        logger.debug(f"Executing git command: {command_str}")
        logger.debug(f"Working directory: {self.repo_path}")

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
                logger.debug(f"Git command stdout: {stdout.decode().strip()}")
            if stderr:
                logger.debug(f"Git command stderr: {stderr.decode().strip()}")

            if process.returncode == FATAL_ERR_EXIT_CODE:
                error_msg = (
                    f"Git command failed: {command_str}\nError: {stderr.decode()}"
                )
                logger.error(error_msg)
                raise Exception(error_msg)
            elif process.returncode != 0:
                warning_msg = f"Git command returned non-zero exit code {process.returncode}: {command_str}"
                logger.warning(warning_msg)

            logger.debug(
                f"Git command completed in {execution_time:.2f}s: {command_str}"
            )
            return stdout.decode().strip()

        except asyncio.TimeoutError:
            if process.returncode is None:
                process.kill()
                await process.wait()
            error_msg = f"Git command timed out after {timeout}s: {command_str}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Git command failed: {command_str} - {e}")
            raise
