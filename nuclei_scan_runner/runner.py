import logging
import os
import sys
import tempfile
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from nuclei_scan_runner.afterscan.database.models import Domains, Scanned
from nuclei_scan_runner.afterscan.finding_processor import FindingProcessor
from nuclei_scan_runner.afterscan.lib import get_project, prepare_db
from nuclei_scan_runner.lib import get_database, safely_run


def prepare_domains(session: Session) -> None:
    domains = (
        session.query(Domains).filter(Domains.blacklisted == False).all()  # noqa: E712
    )
    for domain in domains:
        if (
            not session.query(Scanned)
            .filter(Scanned.name == domain.name, Scanned.port == domain.port)
            .first()
        ):
            session.add(
                Scanned(
                    name=domain.name,
                    port=domain.port,
                    scan_id="nuclei:prepare",
                    timestamp="1970-01-01 00:00:00",
                    info="Prepared for nuclei scan",
                ),
            )
    session.commit()


def get_targets(number_of_targets: int, all_targets: bool) -> tuple[str, list[str]]:
    connection_string = os.getenv("DB_CONNECTION_STRING")
    if not connection_string:
        logging.error("DB_CONNECTION_STRING is not set")
        sys.exit(1)

    engine = get_database(connection_string)

    with Session(engine) as conn:
        prepare_domains(conn)

        if all_targets:
            q = conn.query(Domains.name, Domains.port).filter(
                Domains.blacklisted == False,  # noqa: E712
            )

        else:
            # Get maximal timestamp for each domain
            subq = (
                conn.query(
                    Scanned.name,
                    Scanned.port,
                    func.max(Scanned.timestamp).label("max_timestamp"),
                )
                .group_by(Scanned.name, Scanned.port)
                .subquery()
            )
            # find N of minimal timestamps of all domains
            q = (
                conn.query(subq.c.name, subq.c.port)
                .filter(Domains.name == subq.c.name, Domains.port == subq.c.port)
                .order_by(subq.c.max_timestamp)
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
    timestamp: datetime,
    gitlab_host: str,
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

    scan_info = f"""
    nuclei_conf: {nuclei_conf}
    no_update_templates: {no_update_templates}
    no_update_nuclei: {no_update_nuclei}
    results: {results}
    number_of_targets: {number_of_targets}
    all_targets: {all_targets}
    dont_mark_targets: {dont_mark_targets}
    dont_query_database: {dont_query_database}
    dont_process_results: {dont_process_results}
    gitlab_project_id: {gitlab_project_id}
    templates_directory: {templates_directory}
    skip_scan: {skip_scan}
    scan_id: {scan_id}
    assignees: {assignees}
    dont_create_issues: {dont_create_issues}
    """

    if not dont_mark_targets:
        connection_string = os.getenv("DB_CONNECTION_STRING")
        engine = get_database(connection_string)
        with Session(engine) as conn:
            for domain in domains:
                name, port = domain.split(":")
                conn.add(
                    Scanned(
                        name=name,
                        port=port,
                        scan_id=scan_id,
                        timestamp=timestamp,
                        info=scan_info,
                    ),
                )
            conn.commit()

    if dont_process_results:
        logging.info("Skipping processing of results")
        return

    gl_token = os.getenv("GL-TOKEN")
    if not gl_token:
        logging.error("GL-TOKEN is not set")
        sys.exit(1)

    project = (
        get_project(gl_token, gitlab_project_id, gitlab_host) if not dont_create_issues else None
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
