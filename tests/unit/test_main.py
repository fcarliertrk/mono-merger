from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import pytest
from mono_merger.main import bootstrap, main


@pytest.mark.asyncio
@patch("mono_merger.main.RepoMerger")
async def test_main(mock_repo_merger_class, mock_async_git, sample_config):
    mock_instance = AsyncMock()
    mock_repo_merger_class.return_value = mock_instance

    await main(sample_config, mock_async_git)

    mock_repo_merger_class.assert_called_once_with(sample_config, mock_async_git)
    mock_instance.prepare_mono_repo.assert_called_once()
    mock_instance.clone_repo_branches.assert_called_once()


@pytest.mark.asyncio
@patch("mono_merger.main.main")
@patch("mono_merger.main.parse_args")
@patch("mono_merger.main.load_config_async")
@patch("mono_merger.main.AsyncGitRepo")
async def test_bootstrap(
    mock_async_git_repo_class,
    mock_load_config_async,
    mock_parse_args,
    mock_main,
    sample_config,
):
    mock_parse_args.return_value = SimpleNamespace(config="mock_dir")
    mock_load_config_async.return_value = sample_config

    mock_async_git_instance = AsyncMock()
    mock_async_git_repo_class.return_value = mock_async_git_instance

    await bootstrap()
    mock_async_git_repo_class.assert_called_once_with(sample_config.output_dir)
    mock_main.assert_called_once_with(sample_config, mock_async_git_instance)
