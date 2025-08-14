import asyncio
from pathlib import Path


class AsyncGitRepo:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()

    async def run_git_command(self, *args, timeout: int = 300) -> str:
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

            if process.returncode != 0:
                raise Exception(
                    f"Git command failed: git {' '.join(args)}\nError: {stderr.decode()}"
                )

            return stdout.decode().strip()

        except asyncio.TimeoutError:
            if process.returncode is None:
                process.kill()
                await process.wait()
            raise Exception(f"Git command timed out: git {' '.join(args)}")
