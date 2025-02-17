from dataclasses import dataclass


class FindingData:
    template: str
    template_url: str
    template_id: str
    type_a: str
    host: str
    matched_at: str
    ip: str
    timestamp: str
    severity: str
    info: dict

    def __init__(self, **kwargs) -> None:
        self.json = kwargs
        self.template = kwargs.get("template", "")
        self.template_url = kwargs.get("template-url", "")
        self.template_id = kwargs.get("template-id", "")
        self.type_a = kwargs.get("type", "")
        self.host = kwargs.get("host", "")
        self.matched_at = kwargs.get("matched-at", "")
        self.ip = kwargs.get("ip", "")
        self.timestamp = kwargs.get("timestamp", "")
        self.info = kwargs.get("info", {})
        self.severity = self.info.get("severity", "unknown")


@dataclass
class PreFinding:
    id: str
    name: str
    line: dict
    scan_id: str
    timestamp: str
