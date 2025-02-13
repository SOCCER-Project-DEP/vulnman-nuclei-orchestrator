import logging
import os
import sys
import tempfile

from sqlalchemy.orm import Session

from nuclei_scan_runner.afterscan.database.models import Domains, Scanned
from nuclei_scan_runner.afterscan.finding_processor import FindingProcessor
from nuclei_scan_runner.afterscan.lib import get_project, prepare_db
from nuclei_scan_runner.lib import get_database, safely_run


def get_targets(number_of_targets: int, all_targets: bool) -> tuple[str, list[str]]:
    connection_string = os.getenv("DB_CONNECTION_STRING")
    if not connection_string:
        logging.error("DB_CONNECTION_STRING is not set")
        sys.exit(1)

    engine = get_database(connection_string)

    with Session(engine) as conn:
        if conn.query(Scanned).first() is None or all_targets:
            q = conn.query(Domains.name, Domains.port).filter(
                Domains.blacklisted == False, # noqa: E712
            )

        else:
            q = (
                conn.query(Scanned.name, Scanned.port)
                .filter(Scanned.scan_id.like("nuclei%"))
                .order_by(Scanned.timestamp)
                .limit(number_of_targets)
            )

        domains = [(f"{name}:{port}") for name, port in q.all()]

    if not domains:
        logging.info("No targets found")
        sys.exit(0)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.writelines(f"{domain}\n".encode() for domain in domains)
        return temp_file.name, domains


def run(
    nuclei_conf: str,
    no_update_templates: bool,
    no_update_nuclei: bool,
    results: str,
    number_of_targets: int,
    all_targets: bool,
    dont_mark_targets: bool,
    dont_query_database: bool,
    dont_process_results: bool,
    gitlab_project_id: str,
    templates_directory: str,
    skip_scan: bool,
    scan_id: str,
    assignees: list[str],
    dont_create_issues: bool,
) -> None:
    if (skip_scan or not dont_query_database) and not os.getenv("DB_CONNECTION_STRING"):
        logging.error("DB_CONNECTION_STRING is not set")
        sys.exit(1)

    if not no_update_templates:
        safely_run(["nuclei", "-update-templates", "-no-color"])

    if not no_update_nuclei:
        safely_run(["nuclei", "-update", "-no-color"])

    if not skip_scan:
        if not dont_query_database:
            domains_file, domains = get_targets(number_of_targets, all_targets)
            safely_run(
                ["nuclei", "-o", results, "-config", nuclei_conf, "-l", domains_file],
            )
        else:
            safely_run(["nuclei", "-o", results, "-config", nuclei_conf])

    if not skip_scan and not dont_mark_targets:
        connection_string = os.getenv("DB_CONNECTION_STRING")
        engine = get_database(connection_string)
        with Session(engine) as conn:
            for domain in domains:
                name, port = domain.split(":")
                conn.add(Scanned(name=name, port=port, scan_id=scan_id))
            conn.commit()

    if dont_process_results:
        return

    gl_token = os.getenv("GL-TOKEN")
    if not gl_token:
        logging.error("GL-TOKEN is not set")
        sys.exit(1)

    project = (
        get_project(gl_token, gitlab_project_id) if not dont_create_issues else None
    )
    _, session = prepare_db()

    FindingProcessor(
        file_path=results,
        session=session,
        project=project,
        scan_id=scan_id,
        assignees=assignees,
        dont_create_issues=dont_create_issues,
        templates_directory=templates_directory,
    ).main()
