import asyncio
from mono_merger.config import AppConfig, parse_args, load_config_async


async def main(config: AppConfig) -> None:
    print(config)


async def bootstrap() -> None:
    args = parse_args()
    config = await load_config_async(args.config)
    await main(config)


if __name__ == "__main__":
    asyncio.run(bootstrap())
