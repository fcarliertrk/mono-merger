import pytest

# from unittest.mock import AsyncMock

from mono_merger.async_git import AsyncGitRepo


@pytest.mark.asyncio
async def test_init(mocker, sample_config):
    mock_run_git_command = mocker.patch.object(AsyncGitRepo, "_run_git_command")
    mock_async_git = AsyncGitRepo(sample_config.output_dir)
    await mock_async_git.init()
    mock_run_git_command.assert_called_once_with("init")


@pytest.mark.asyncio
async def test_add(mocker, sample_config):
    mock_run_git_command = mocker.patch.object(AsyncGitRepo, "_run_git_command")
    mock_async_git = AsyncGitRepo(sample_config.output_dir)
    await mock_async_git.add("someFile1", "someFile2", "someFile3")
    mock_run_git_command.assert_called_once_with(
        "add", "someFile1", "someFile2", "someFile3"
    )


@pytest.mark.asyncio
async def test_commit(mocker, sample_config):
    mock_run_git_command = mocker.patch.object(AsyncGitRepo, "_run_git_command")
    mock_async_git = AsyncGitRepo(sample_config.output_dir)
    await mock_async_git.commit("myCommitMsg")
    mock_run_git_command.assert_called_once_with("commit", "-m", "myCommitMsg")


@pytest.mark.asyncio
async def test_subtree_add(mocker, sample_config):
    mock_run_git_command = mocker.patch.object(AsyncGitRepo, "_run_git_command")

    mock_async_git = AsyncGitRepo(sample_config.output_dir)

    repo = sample_config.repos[0]
    branch = repo.branches[0]
    prefix = f"{branch.domain}/{branch.name}"

    await mock_async_git.subtree_add(prefix, repo.url, branch.name, True)

    mock_run_git_command.assert_called_once_with(
        "subtree",
        "add",
        "--prefix",
        prefix,
        repo.url,
        branch.name,
        "--squash",
        timeout=600,
    )
