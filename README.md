# Nuclei Scan Runner

This project handles the orchestration of scanner nuclei, storing results in the database, and reporting to GitLab.

## Setup (Ansible)

See [SOCCER-Project-DEP/vulnman-ansible](https://github.com/SOCCER-Project-DEP/vulnman-ansible) for Ansible that deploys this tool alongside [vulnman-nuclei-orchestrator](https://github.com/SOCCER-Project-DEP/vulnman-nuclei-orchestrator).

## Getting started (manual installation)

```bash
# Install dependencies
poetry install

# Setup credentials
cp .env.template .env

# Setup credentials for testing
cp .env.template .env.testing
```

### How to use Poetry

```bash
# run the tool via poetry
poetry run nuclei-scan-runner

# enter development environment and run it directly or as a module
poetry shell
nuclei-scan-runner
python3 -m nuclei_scan_runner
```

### How to use Makefile

Makefile is a useful wrapper for linting and fixing issues:

```bash
# only check
make lint

# try to fix
make fix
```

## Usage

```
Usage: nuclei-scan-runner [OPTIONS]

  Running nuclei with postprocessing and updates

  All options can be set in a configuration file or environment variable.
  Environment variables are upper-case and have prefix NUCLEI_SCAN_RUNNER.
  Both environment variables and configuration file options are set without
  leading dashes.

  Targets are queried from the database, unless --dont-query-database is set.

Options:
  --config FILE
  --nuclei-conf FILE
  --logfile FILE                  [default: /var/log/nuclei_scanner.ndjson]
  --results FILE
  --results-dir DIR               [default: /var/log/nuclei/results/]
  --no-update-templates
  --no-update-nuclei
  --dont-query-database           Don't query database for targets, but
                                  specify them in the nuclei config instead.
                                  Implies --dont-mark-targets
  --number-of-targets INTEGER     Number of targets to pull from the database
                                  [default: 50]
  --all                           Scan all targets in the database
  --dont-mark-targets             Do not mark targets as scanned in the
                                  database
  --dont-process-results
  --gitlab-project-id TEXT
  --templates-directory TEXT      Templates are part of the package, but you
                                  can specify a custom path too  [default:
                                  /home/me/code/csirt/OrchS-
                                  nuclei/nuclei_scan_runner/vulnerability-
                                  templates]
  --skip-scan                     Process results only
  --dev                           Use .env.testing instead of .env.
  --assignee TEXT                 GitLab user IDs assigned for the issue.
                                  Defaults to Petr Marinec  [default: 1985]
  --env-file TEXT                 Custom path to the .env file with secrets
  --dont-create-issues            Do not save issues to DB or GitLab, just
                                  print them to the console
  --exceptions template-id[,template-id,...]
                                  Template IDs that should be always be
                                  processed even if they are of low severity
  -h, --help                      Show this message and exit.
```

## Examples of usage

### Process previously scanned results

```
poetry run nuclei-scan-runner --skip-scan --logfile /var/log/orchs_nuclei/logs/scheduled.ndjson.1 --results /var/log/orchs_nuclei/results/scheduled/2024-09-12T03\:49\:33.433654.json --gitlab-project-id 6355
```

## Additional information

- This repository is being developed as a part of the [SOCCER](https://soccer.agh.edu.pl/en/) project.
- Developed by cybersecurity team of [Masaryk University](https://www.muni.cz/en).
- This project is a "mirror" of the original repository hosted on university Gitlab. New features and fixes here are being added upon new releases of the original repository.

## Help

Are you missing something? Do you have any suggestions or problems? Please create an issue.
Or ask us at `info@csirt.muni.cz`, we are happy to help you, answer your questions or discuss your ideas.
