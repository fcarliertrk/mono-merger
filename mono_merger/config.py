from dataclasses import dataclass
from typing import List, Dict
import argparse
import asyncio
import logging
import yaml
import aiofiles
from pybiztools.logger import setup_logger

logger = setup_logger("mono-merger", logging.INFO)


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
        logger.debug("Creating AppConfig from dictionary")

        try:
            repos = []
            for repo_data in data["repos"]:
                branches = [
                    BranchConfig(name=branch["name"], domain=branch["domain"])
                    for branch in repo_data["branches"]
                ]
                repos.append(RepoConfig(url=repo_data["url"], branches=branches))
                logger.debug(
                    "Processed repo: %s with %s branches", repo_data['url'], len(branches)
                )

            config = cls(
                repos=repos,
                domain_mapping=data["domain_mapping"],
                output_dir=data["output_dir"],
            )

            logger.info(
                "AppConfig created successfully with %s repositories", len(repos)
            )
            return config

        except KeyError as e:
            logger.error("Missing required configuration field: %s", e)
            raise
        except Exception as e:
            logger.error("Failed to create AppConfig: %s", e)
            raise


async def load_config_async(path: str) -> AppConfig:
    """Load and parse configuration from a YAML file"""
    logger.info("Loading configuration from: %s", path)

    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as file:
            content = await file.read()
        logger.debug("Successfully read %s characters from config file", len(content))

        raw = await asyncio.to_thread(yaml.safe_load, content)
        logger.debug("YAML parsing completed successfully")

        config = AppConfig.from_dict(raw)
        logger.info("Configuration loaded and validated successfully")
        return config

    except FileNotFoundError:
        logger.error("Configuration file not found: %s", path)
        raise
    except yaml.YAMLError as e:
        logger.error("YAML parsing error in %s: %s", path, e)
        raise
    except Exception as e:
        logger.error("Failed to load configuration from %s: %s", path, e)
        raise


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
