import pytest
from unittest.mock import AsyncMock

from mono_merger.merge_repos import RepoMerger


@pytest.mark.asyncio
async def test_prepare_mono_repo(mock_async_git, sample_config, mock_aiofiles):
    mono_merger = RepoMerger(sample_config, mock_async_git)
    await mono_merger.prepare_mono_repo()

    mock_aiofiles["makedirs"].assert_called_once_with(
        sample_config.output_dir, exist_ok=True
    )

    expected_readme_path = sample_config.output_dir / "README.md"
    mock_aiofiles["open"].assert_called_once_with(expected_readme_path, mode="w")

    mock_aiofiles["file"].write.assert_any_call("# Monolith\n")
    mock_aiofiles["file"].write.assert_any_call(
        "This file was created automatically by mono_merger\n"
    )

    mock_async_git.init.assert_called()
    mock_async_git.add.assert_called_with("README.md")
    mock_async_git.commit.assert_called_with("first commit")


@pytest.mark.asyncio
async def test_clone_repo_branches(mock_async_git, sample_config, mocker):
    # Mock the call to subtree_add
    mock_subtree_add = mocker.patch.object(
        RepoMerger, "_subtree_add_branches", new_callable=AsyncMock
    )
    mono_merger = RepoMerger(sample_config, mock_async_git)
    await mono_merger.clone_repo_branches()

    assert mock_subtree_add.call_count == len(sample_config.repos)

    for repo in sample_config.repos:
        mock_subtree_add.assert_any_call(repo)


@pytest.mark.asyncio
async def test_subtree_add_branches(mock_async_git, sample_config, mocker):
    mono_merger = RepoMerger(sample_config, mock_async_git)

    for repo in sample_config.repos:
        await mono_merger._subtree_add_branches(repo)

    total_branches = sum(len(repo.branches) for repo in sample_config.repos)
    assert mock_async_git.subtree_add.call_count == total_branches

    for repo in sample_config.repos:
        for branch in repo.branches:
            mock_async_git.subtree_add.assert_any_call(
                "%s/%s" % (branch.domain, branch.name), repo.url, branch.name, True
            )
