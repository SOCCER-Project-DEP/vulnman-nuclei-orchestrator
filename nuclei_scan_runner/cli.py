import importlib.resources
import logging
import pathlib
import random
import sys
from datetime import datetime

import click
import pytz
from dotenv import find_dotenv, load_dotenv

import nuclei_scan_runner.log
from nuclei_scan_runner import lib, runner


@click.command(
    context_settings={
        "auto_envvar_prefix": "NUCLEI_SCAN_RUNNER",
        "help_option_names": ["-h", "--help"],
        "show_default": True,
    },
    help="""Run nuclei with postprocessing and updates.

    Options can be set via a configuration file or environment variables.
    Environment variables are upper-case with the prefix NUCLEI_SCAN_RUNNER.
    Configuration file and environment variables exclude leading dashes.

    Targets are queried from the database unless --dont-query-database is specified.
    """,
)
@click.option("--config", metavar="FILE", help="Path to the configuration file.")
@click.option("--nuclei-config", metavar="FILE", help="Nuclei configuration file.")
@click.option(
    "--logfile",
    default="/var/log/nuclei_scanner.ndjson",
    metavar="FILE",
    help="Log file path.",
)
@click.option("--results", metavar="FILE", help="Path to the results file.")
@click.option(
    "--results-dir",
    default="/var/log/nuclei/results/",
    metavar="DIR",
    help="Directory to save results.",
)
@click.option(
    "--no-update-templates",
    is_flag=True,
    default=False,
    help="Skip updating nuclei templates.",
)
@click.option(
    "--no-update-nuclei",
    is_flag=True,
    default=False,
    help="Skip updating nuclei.",
)
@click.option(
    "--dont-query-database",
    is_flag=True,
    default=False,
    help="Don't query the database for targets.",
)
@click.option(
    "--number-of-targets",
    default=50,
    type=click.INT,
    help="Number of targets to query from the database.",
)
@click.option(
    "--all-targets",
    is_flag=True,
    default=False,
    help="Scan all targets in the database.",
)
@click.option(
    "--dont-mark-targets",
    is_flag=True,
    default=False,
    help="Don't mark targets as scanned in the database.",
)
@click.option(
    "--dont-process-results",
    is_flag=True,
    default=False,
    help="Skip processing scan results.",
)
@click.option("--gitlab-project-id", help="GitLab project ID for issue creation.")
@click.option(
    "--templates-directory",
    default=importlib.resources.files("nuclei_scan_runner") / "vulnerability-templates",
    help="Path to the nuclei templates directory.",
)
@click.option(
    "--skip-scan",
    is_flag=True,
    default=False,
    help="Skip the scan and only process results.",
)
@click.option(
    "--dev",
    is_flag=True,
    default=False,
    help="Use development mode with .env.testing.",
)
@click.option(
    "--assignee",
    default="1985",
    help="GitLab user IDs for assigning issues, comma-separated.",
)
@click.option("--env-file", help="Path to a custom .env file.")
@click.option(
    "--dont-create-issues",
    is_flag=True,
    default=False,
    help="Don't create issues in GitLab.",
)
@click.option("--gitlab-host", default="https://gitlab.com", help="GitLab host URL.")
@lib.check_config_file(arg="config")
def cli(
    config: str,
    nuclei_config: str,
    logfile: str,
    results: str,
    results_dir: str,
    no_update_templates: bool,
    no_update_nuclei: bool,
    dont_query_database: bool,
    number_of_targets: int,
    all_targets: bool,
    dont_mark_targets: bool,
    dont_process_results: bool,
    gitlab_project_id: str,
    templates_directory: str,
    skip_scan: bool,
    dev: bool,
    assignee: str,
    env_file: str,
    dont_create_issues: bool,
    gitlab_host: str,
) -> None:
    scan_id = f"nuclei:{random.randint(100000, 999999)}"

    logging.info(f"Starting nuclei scan with ID: {scan_id}")
    logging.info(f"Configuration file: {config}")

    nuclei_scan_runner.log.setup_logger(logfile, scan_id, dev)

    env_path = (
        find_dotenv(".env.testing", usecwd=True)
        if dev
        else find_dotenv(env_file or ".env", usecwd=True)
    )
    load_dotenv(env_path)
    tz = pytz.timezone("Europe/Prague")
    results = (
        results
        or pathlib.Path(results_dir)
        .joinpath(f"{datetime.now(tz).isoformat()}.json")
        .as_posix()
    )

    if number_of_targets < 1:
        logging.error("Number of targets (--number-of-targets) must be at least 1.")
        sys.exit(1)

    if dont_query_database:
        dont_mark_targets = True

    try:
        assignees = [int(a.strip()) for a in assignee.split(",") if a.strip()]
    except ValueError:
        logging.exception("Failed to parse assignee IDs.")
        sys.exit(1)

    try:
        runner.run(
            nuclei_conf=nuclei_config,
            no_update_templates=no_update_templates,
            no_update_nuclei=no_update_nuclei,
            results=results,
            number_of_targets=number_of_targets,
            all_targets=all_targets,
            dont_mark_targets=dont_mark_targets,
            dont_query_database=dont_query_database,
            dont_process_results=dont_process_results,
            gitlab_project_id=gitlab_project_id,
            templates_directory=templates_directory,
            skip_scan=skip_scan,
            scan_id=scan_id,
            assignees=assignees,
            dont_create_issues=dont_create_issues,
            gitlab_host=gitlab_host,
        )
    except Exception as e:
        logging.exception(f"Error during execution: {e}")
        sys.exit(1)
