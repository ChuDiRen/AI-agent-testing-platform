import argparse
import asyncio
import json
import logging.config
import pathlib

from langgraph_api.queue_entrypoint import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--grpc-port", type=int, default=50051)
    args = parser.parse_args()
    with open(pathlib.Path(__file__).parent.parent / "logging.json") as file:
        loaded_config = json.load(file)
        logging.config.dictConfig(loaded_config)
    try:
        import uvloop  # type: ignore[unresolved-import]

        uvloop.install()
    except ImportError:
        pass
    from langgraph_api import config

    config.IS_EXECUTOR_ENTRYPOINT = True
    asyncio.run(main(grpc_port=args.grpc_port, entrypoint_name="python-executor"))
