import asyncio
from pathlib import Path

FATAL_ERR_EXIT_CODE = 128


class AsyncGitRepo:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()

    async def init(self) -> str:
        """Initialize a git repository"""
        return await self._run_git_command("init")

    async def add(self, *files) -> str:
        """Add files to staging area"""
        return await self._run_git_command("add", *files)

    async def commit(self, message: str) -> str:
        """Create a commit with message"""
        return await self._run_git_command("commit", "-m", message)

    async def subtree_add(
        self,
        prefix: str,
        repository: str,
        ref: str = "main",
        squash: bool = False,
    ) -> str:
        """Add a subtree"""
        args = ["subtree", "add", "--prefix", prefix, repository, ref]

        if squash:
            args.insert(len(args) - 1, "--squash")
        
        return await self._run_git_command(*args, timeout=600)

    async def _run_git_command(self, *args, timeout: int = 300) -> str:
        """Run a git command asynchronously"""
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
            print(stdout)
            print(stderr)

            if process.returncode == FATAL_ERR_EXIT_CODE:
                raise Exception(
                    f"Git command failed: git {' '.join(args)}\nError: {stderr.decode()}"
                )

            return stdout.decode().strip()

        except asyncio.TimeoutError:
            if process.returncode is None:
                process.kill()
                await process.wait()
            raise Exception(f"Git command timed out: git {' '.join(args)}")
