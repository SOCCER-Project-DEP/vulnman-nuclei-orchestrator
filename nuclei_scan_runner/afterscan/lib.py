from __future__ import annotations

import json
import logging
import os
from sys import exit
from typing import TYPE_CHECKING

import gitlab
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from nuclei_scan_runner.afterscan.database.models import Finding, get_base
from nuclei_scan_runner.afterscan.models import FindingData, PreFinding
from nuclei_scan_runner.afterscan.script_constants import ScriptConstants
from nuclei_scan_runner.afterscan.templates.templates import load_template
from nuclei_scan_runner.lib import get_database

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


def getenv_throws(key: str) -> str:
    if (res := os.getenv(key)) is None:
        msg = f"Could not load environment variable {key}"
        raise RuntimeError(msg)
    return res


def read_file(file_path: str) -> list[str]:
    with open(file_path) as f:
        return f.readlines()


def prepare_db() -> tuple[Engine, Session]:
    connection_string = os.getenv("DB_CONNECTION_STRING")
    assert connection_string  # checked before
    engine = get_database(connection_string)

    s = sessionmaker(bind=engine)
    session = s()

    try:
        get_base().metadata.create_all(engine)
        logging.info("Tables in afterscan database created")
        return engine, session
    except SQLAlchemyError:
        logging.exception("Error when creating tables in afterscan database.")
        exit(1)


def get_project(token: str, project_id: str | int, gitlab_host: str) -> object:
    logging.info(f"Connecting to GitLab project {project_id}")
    logging.info(f"GitLab host: {gitlab_host}")
    logging.info(f"GitLab token: {token}")
    gl = gitlab.Gitlab(gitlab_host, token)
    gl.auth()
    return gl.projects.get(project_id)


def save_issue_to_db(session, scan_id: str, f: PreFinding) -> bool:
    json_finding = json.dumps(f.line)
    try:
        if not check_if_issue_exists(f.id, session):
            new_finding = Finding(
                finding_identifier=f.id,
                name=f.name,
                finding=json_finding,
                scan_id=scan_id,
            )
            session.add(new_finding)
            session.commit()
            return True
        logging.info(f"Issue {f.name} already exists in the database")
        return False

    except SQLAlchemyError as e:
        logging.exception(f"Error: {e}")
        exit(1)


def parse_finding(
    finding_dict: dict, templates_directory: str, path: str,
) -> tuple[str, str]:
    finding = FindingData(**finding_dict)
    severity = ScriptConstants.SEVERITY_MAPPING.get(finding.severity, "unknown")

    description = load_template(finding, templates_directory, path)
    return severity, description


def check_if_issue_exists(uid: str, session) -> bool:
    url_combinations = [
        uid,
        uid.replace("http://", "https://"),
        uid.replace("https://", "http://"),
        uid.replace("https://", "http://www."),
        uid.replace("http://www.", "https://"),
        uid.replace("https://", "https://www."),
        uid.replace("http://", "http://www."),
    ]
    for url in url_combinations:
        try:
            exists = (
                session.query(Finding).filter_by(finding_identifier=url).scalar()
                is not None
            )
            if exists:
                return True
        except SQLAlchemyError as e:
            logging.exception(f"Error: {e}")
            continue
    return False


def parse_line(line: str) -> dict[str, str]:
    try:
        json_data = json.loads(line)
        return {
            key: value
            for key, value in json_data.items()
            if key in ScriptConstants.REQUIRED_FINDING_ATTRIBUTES
        }
    except json.JSONDecodeError as e:
        logging.exception(f"Error decoding JSON string: {e}\n")
        exit(1)


def add_id_to_finding(finding_identifier: str, id_gl: str, session) -> bool:
    try:
        existing_finding = (
            session.query(Finding)
            .filter_by(finding_identifier=finding_identifier)
            .first()
        )
        if existing_finding:
            existing_finding.issue_id = id_gl
            session.commit()
            return True
        logging.error(
            f"Error adding id_gl to finding with finding_identifier  {finding_identifier }",
        )
        return False

    except SQLAlchemyError as e:
        logging.exception(
            f"Error adding id_gl to finding with finding_identifier  {finding_identifier }, error: {e}",
        )
        exit(1)

