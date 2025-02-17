import logging
import subprocess
import sys
from functools import wraps
from typing import Any, Callable

import click
import psycopg2
import toml
from click.core import ParameterSource
from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import SQLAlchemyError


def check_config_file(arg: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = click.get_current_context()

            # do not do anything if configuration file is not set
            if not ctx.params[arg]:
                return func(*args, **kwargs)

            # read and parse the configuration file
            try:
                config = toml.load(ctx.params[arg])
            except toml.TomlDecodeError as e:
                logging.exception("Could not parse configuration file")
                logging.exception(e)
                sys.exit(1)

            # update context to reflect the configuration file changes
            for k, v in config.items():
                # click replaces dashes with underscores
                k = k.replace("-", "_")

                match ctx.get_parameter_source(k):
                    # only change the parameter if it's default or set in env
                    case ParameterSource.DEFAULT | ParameterSource.ENVIRONMENT:
                        ctx.params[k] = v
                    case _:
                        pass

            # call the function with arguments and updated parameters
            return func(*args, **ctx.params)

        return wrapper

    return decorator


def check_args_defined(required_arguments: list[str]) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = click.get_current_context()

            for a in required_arguments:
                a = a.replace("-", "_")
                if a not in ctx.params or ctx.params[a] is None:
                    logging.error(f"{a} is required argument")
                    sys.exit(1)

            # call the function with arguments and updated parameters
            return func(*args, **kwargs)

        return wrapper

    return decorator


def safely_run(cmd: list[str]) -> None:
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0) as proc:
        assert proc.stdout  # make mypy happy

        for line in proc.stdout:
            # we code it ourselves to catch any decoding errors in the process output
            try:
                text_line = line.decode("utf-8", errors="replace")
            except Exception:
                logging.exception("Couldn't decode line")
                # better to continue than to stop the whole scan
                continue

            logging.info(text_line.rstrip(), extra={"subprocess": cmd})

    return_code = proc.wait()

    if return_code != 0:
        logging.error("Subprocess failed")
        sys.exit(1)

def get_database(connection_string: str) -> Engine:
    engine = create_engine(connection_string, connect_args={"connect_timeout": 10})

    logging.info("Testing database connection")

    try:
        with engine.connect():
            logging.info("Databse connection established")
    except (SQLAlchemyError, psycopg2.OperationalError):
        logging.exception("Failed to connect to the database")
        sys.exit(1)

    return engine

