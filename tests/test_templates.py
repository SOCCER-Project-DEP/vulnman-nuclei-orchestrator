import json

from nuclei_scan_runner.afterscan.models import FindingData
from nuclei_scan_runner.afterscan.templates.templates import load_template

FIRST_N_CHAR = 60


def test_load_finding() -> None:
    with open("tests/test_data/finding-xss.json") as f:
        d = json.loads(f.read())
        finding = FindingData(**d)
    templ_dir = "nuclei_scan_runner/vulnerability-templates/"
    with open(f"{templ_dir}xss.jinja") as jinja_template:
        assert load_template(finding, templ_dir)[:FIRST_N_CHAR] == jinja_template.read()[:FIRST_N_CHAR]
