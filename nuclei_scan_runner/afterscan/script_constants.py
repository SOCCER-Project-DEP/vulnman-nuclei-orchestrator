

from typing import ClassVar


class ScriptConstants:
    MAX_SIZE_GL_DESCRIPTION: ClassVar[int] = 10000
    MAX_SIZE_GL_TITLE: ClassVar[int] = 255
    TABLE_DOMAINS: ClassVar[str] = "domains"
    ATTRIBUTE_LAST_SCAN_TOOL: ClassVar[str] = "last_scan_nuclei"
    IGNORED_SEVERITY: ClassVar[list[str]] = ["info", "low"]
    REQUIRED_FINDING_ATTRIBUTES: ClassVar[list[str]] = [
        "template",
        "template-url",
        "template-id",
        "template-path",
        "info",
        "type",
        "host",
        "matched-at",
        "extracted-results",
        "ip",
        "timestamp",
        "matcher-status",
        "matched-line",
    ]

    SEVERITY_MAPPING: ClassVar[dict[str, str]] = {
        "info": "info",
        "low": "low",
        "medium": "moderate",
        "high": "important",
        "critical": "critical",
    }
