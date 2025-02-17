import logging
from sys import exit

from sqlalchemy.orm import Session

from nuclei_scan_runner.afterscan.database.models import Finding
from nuclei_scan_runner.afterscan.lib import (
    add_id_to_finding,
    parse_finding,
    parse_line,
    read_file,
    save_issue_to_db,
)
from nuclei_scan_runner.afterscan.models import PreFinding
from nuclei_scan_runner.afterscan.script_constants import ScriptConstants


class FindingProcessor:
    def __init__(
        self,
        file_path: str,
        session: Session,
        project: object,
        scan_id: str,
        assignees: list[str],
        dont_create_issues: bool,
        templates_directory: str,
    ) -> None:
        self.file_path = file_path
        self.session = session
        self.project = project
        self.scan_id = scan_id
        self.assignees = assignees
        self.dont_create_issues = dont_create_issues
        self.templates_directory = templates_directory

    def process_finding_record(self, line: dict) -> None:
        try:
            finding_id = f"{line.get('matched-at', 'unknown')} {line.get('template', 'unknown')}"
            name = f"[{line['info'].get('name', 'unknown')}] [{line.get('matched-at', 'unknown')}]"
            finding_time = line.get("timestamp", "unknown")

            finding = PreFinding(
                id=finding_id,
                name=name,
                line=line,
                scan_id=self.scan_id,
                timestamp=finding_time,
            )

            if save_issue_to_db(self.session, self.scan_id, finding):
                issue_id, severity = self.handle_gitlab_issue(finding)
                if not add_id_to_finding(finding_id, issue_id, self.session):
                    logging.error(f"Failed to associate issue ID with finding {finding_id}")

            db_finding = self.session.query(Finding).filter_by(finding_identifier=finding_id).first()
            if db_finding:
                db_finding.last_seen = finding_time
                db_finding.severity = db_finding.severity or severity
            else:
                logging.error(f"Cannot update last seen for {finding_id}")

            self.session.commit()
            logging.info(f"Updated last seen for {name}")
        except Exception as e:
            logging.exception(f"Error processing finding: {e}")
            exit(1)

    def handle_gitlab_issue(self, finding: PreFinding) -> tuple[str, str]:
        severity, description = parse_finding(finding.line, self.templates_directory, self.file_path)
        issue_data = {
            "title": finding.name[: ScriptConstants.MAX_SIZE_GL_TITLE],
            "description": description[: ScriptConstants.MAX_SIZE_GL_DESCRIPTION],
            "assignee_ids": self.assignees,
            "labels": [f"severity::{severity}", "state::new"],
        }

        if self.dont_create_issues or severity in ScriptConstants.IGNORED_SEVERITY:
            logging.info(f"Skipping issue creation for {finding.name} with severity {severity}")
            return "", severity

        issue = self.project.issues.create(issue_data)
        if not issue:
            logging.error(f"Failed to create issue for {finding.id}")
            exit(1)

        return issue.web_url, severity

    def main(self) -> None:
        lines = read_file(self.file_path)
        for line in map(parse_line, lines):
            self.process_finding_record(line)
        logging.info("Processing complete")
