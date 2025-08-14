from dataclasses import dataclass
from typing import List, Dict
import argparse
import asyncio
import yaml
import aiofiles


@dataclass
class BranchConfig:
    """Represents a git branch with its associated domain"""

    name: str
    domain: str


@dataclass
class RepoConfig:
    """Represents a GitHub repository with its URL and branches"""

    url: str
    branches: List[BranchConfig]


@dataclass
class AppConfig:
    """Configuration class for the YAML config file"""

    repos: List[RepoConfig]
    domain_mapping: Dict[str, str]
    output_dir: str

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        """Creates an AppConfig instance from a dictionary"""
        repos = []
        for repo_data in data["repos"]:
            branches = [
                BranchConfig(name=branch["name"], domain=branch["domain"])
                for branch in repo_data["branches"]
            ]
            repos.append(RepoConfig(url=repo_data["url"], branches=branches))

        return cls(
            repos=repos,
            domain_mapping=data["domain_mapping"],
            output_dir=data["output_dir"],
        )


async def load_config_async(path: str) -> AppConfig:
    async with aiofiles.open(path, "r", encoding="utf-8") as file:
        content = await file.read()
    raw = await asyncio.to_thread(yaml.safe_load, content)
    return AppConfig.from_dict(raw)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Consolidate multiple GitHub repos into a single mono-repo"
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help=(
            "The full path of the configuration YAML file, please see the sample config in the README for an example."
        ),
    )
    return parser.parse_args()
