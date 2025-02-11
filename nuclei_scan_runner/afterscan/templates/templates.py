from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from nuclei_scan_runner.afterscan.templates import get_compiled_regexes, get_jinja_env

if TYPE_CHECKING:
    from jinja2 import Environment, Template

    from nuclei_scan_runner.afterscan.models import FindingData


def get_tool_output(f: FindingData, path: str) -> str:
    return (
        "<details>\n"
        "<summary>Info</summary>\n\n"
        f"Scan ID: `{path}`\n\n"
        "| Finding Template | Finding Template URL | Finding Template ID | Type | Host |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"| {f.template} | {f.template_url} | {f.template_id} | {f.type_a} | {f.host} |\n\n"
        "| Matched At | IP | Timestamp | Severity |\n"
        "| --- | --- | --- | --- |\n"
        f"| ``` {f.matched_at} ``` | {f.ip} | {f.timestamp} | {f.severity} |\n\n"
        "</details>\n\n"
        "<details>\n"
        "<summary>Nuclei log</summary>\n\n"
        "```json\n"
        f"{json.dumps(f.json, indent=4)}`\n"
        "```\n"
        "</details>\n"
    )


def load_template(
    finding: FindingData, templates_directory: str, path: str = Path.cwd(),
) -> str:
    jinja = get_jinja_env(templates_directory)
    if (name := finding.info.get("name")) is None:
        msg = "Finding name is None"
        raise ValueError(msg)
    return (
        get_jinja_env(templates_directory)
        .get_template(look_for_template(name, jinja, templates_directory))
        .render(
            tool="nuclei",
            tool_output=get_tool_output(finding, path),
        )
    )


def look_for_template(
    issue: str, jinja: Environment, templates_directory: str,
) -> Template | str:
    for template in jinja.list_templates():
        for reg in get_compiled_regexes(templates_directory):
            if reg.search(str(template)) and reg.search(issue):
                return template
    return jinja.get_template("default.jinja")
