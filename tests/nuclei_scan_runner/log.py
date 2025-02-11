import json
import logging
import sys
from time import sleep


class JSONLogginFormat(logging.Formatter):
    def __init__(self, scan_id: str, dev: bool, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.scan_id = scan_id
        self.dev = dev

    def format(self, record: logging.LogRecord) -> str:
        record_dict = {
            "level": record.levelname,
            "timestamp": self.formatTime(record),
            "scan_id": self.scan_id,
            "subprocess": " ".join(record.subprocess) if hasattr(record, "subprocess") else None,
            "message": record.msg,
            "trace": record.exc_text,
        }

        if self.dev and not hasattr(record, "subprocess"):
            sleep(0)

        return json.dumps(record_dict)


def setup_logger(path: str, start: str, dev: bool) -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # add stderr logging stream
    stdout_handler = logging.StreamHandler(stream=sys.stderr)
    stdout_handler.setFormatter(logging.Formatter("%(levelname)5s: %(message)s"))

    logger.addHandler(stdout_handler)

    # add json logging stream
    try:
        json_handler = logging.FileHandler(path, mode="a")
    except Exception:
        logging.exception(msg="Couldn't open log file.")
        sys.exit(1)

    json_handler.setFormatter(JSONLogginFormat(start, dev))
    logger.addHandler(json_handler)
