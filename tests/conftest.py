"""
Shared pytest fixtures for mono-merger tests.
"""

import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, AsyncMock
import pytest


from mono_merger.async_git import AsyncGitRepo
from mono_merger.config import AppConfig, RepoConfig, BranchConfig


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_directory:
        yield Path(temp_directory)


@pytest.fixture
def mock_async_git(sample_config) -> AsyncGitRepo:
    mock_async_git_svc = Mock(spec=AsyncGitRepo)
    mock_async_git_svc.repo_path = sample_config.output_dir
    mock_async_git_svc.init = AsyncMock(
        return_value="Initialized empty Git repository in .git/"
    )
    return mock_async_git_svc


@pytest.fixture
def mock_aiofiles(mocker):
    mocks = {}

    mocks["makedirs"] = mocker.patch("mono_merger.merge_repos.aiofiles.os.makedirs")

    mock_file = AsyncMock()
    mock_open = mocker.patch("mono_merger.merge_repos.aiofiles.open")
    mock_open.return_value.__aenter__.return_value = mock_file
    mock_open.return_value.__aexit__.return_value = None

    mocks["open"] = mock_open
    mocks["file"] = mock_file

    return mocks


@pytest.fixture
def sample_config(temp_dir) -> AppConfig:
    """Provide a sample configuration for testing."""
    return AppConfig(
        repos=[
            RepoConfig(
                url="https://github.com/test/repo1.git",
                branches=[
                    BranchConfig(name="main", domain="domain1"),
                    BranchConfig(name="feature", domain="domain2"),
                ],
            ),
            RepoConfig(
                url="https://github.com/test/repo2.git",
                branches=[
                    BranchConfig(name="develop", domain="domain1"),
                ],
            ),
        ],
        domain_mapping={
            "domain1": "services/domain1",
            "domain2": "services/domain2",
        },
        output_dir=temp_dir / "test-mono-repo",
    )


@pytest.fixture
def sample_config_dict() -> dict:
    """Provide a sample configuration dictionary for testing."""
    return {
        "repos": [
            {
                "url": "https://github.com/test/repo1.git",
                "branches": [
                    {"name": "main", "domain": "domain1"},
                    {"name": "feature", "domain": "domain2"},
                ],
            },
            {
                "url": "https://github.com/test/repo2.git",
                "branches": [
                    {"name": "develop", "domain": "domain1"},
                ],
            },
        ],
        "domain_mapping": {
            "domain1": "services/domain1",
            "domain2": "services/domain2",
        },
        "output_dir": "/tmp/test-mono-repo",
    }
