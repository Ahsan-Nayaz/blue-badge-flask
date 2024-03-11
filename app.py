import asyncio
import signal

import uvloop
from hypercorn.asyncio import serve
from hypercorn.config import Config

from app import app

shutdown_event = asyncio.Event()


def _signal_handler(*_) -> None:
    shutdown_event.set()


config = Config()
config.bind = ["0.0.0.0:5000"]  # As an example configuration setting

if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.new_event_loop()
    loop.add_signal_handler(signal.SIGTERM, _signal_handler)
    loop.add_signal_handler(signal.SIGINT, _signal_handler)
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        serve(
            app,
            config,
            shutdown_trigger=shutdown_event.wait  # type: ignore
        )
    )
