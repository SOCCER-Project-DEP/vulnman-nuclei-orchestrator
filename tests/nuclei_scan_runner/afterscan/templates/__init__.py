import logging
import re
import sys
from functools import cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


@cache
def get_jinja_env(path: str) -> Environment:
    if not Path(path).is_dir():
        logging.error("Could not find vulnerability-templates directory, exiting...")
        sys.exit(1)

    return Environment(
        loader=FileSystemLoader(path),
        autoescape=select_autoescape(),
    )


@cache
def get_compiled_regexes(directory: str) -> list[re.Pattern[str]]:
    try:
        pure_regexes = None
        with open(directory + "/regex.txt") as f:
            pure_regexes = f.readlines()
        logging.info("Following regexes were loaded: ")
        logging.info(pure_regexes)
    except Exception as e:
        logging.exception(e)
        logging.exception("Could not load regexes.txt with templates module, exiting...")
        sys.exit(1)

    return [re.compile(reg.rstrip(), re.IGNORECASE) for reg in pure_regexes]
