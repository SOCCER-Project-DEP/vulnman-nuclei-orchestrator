from typing import Any

from sqlalchemy.orm import declarative_base

Base = declarative_base()


def get_base() -> Any:
    return Base
