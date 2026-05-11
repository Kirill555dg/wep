"""
Run uvicorn with project logging configuration enabled early.

Why:
`uvicorn` configures logging before importing the app module, so startup logs can look
unformatted. This wrapper configures our structured/colored logs first, then runs uvicorn
without its default log config.

Usage:
  python -m app.scripts.run_server --host 0.0.0.0 --port 8023 --reload
"""

import argparse

import uvicorn

from app.core import logging_config as logging_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8023)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    # Ensure our formatter is installed before uvicorn prints anything.
    logging_config.setup_logging()

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_config=None,
        access_log=False,
    )


if __name__ == "__main__":
    main()

