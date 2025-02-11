# Nuclei Scan Runner

Nuclei scan orchestration tool. Handles nuclei updates, storing results in the database and reporting to GitLab.
 
[[_TOC_]]

## Getting started

Database connection strings and GitLab tokens are stored in Passbolt.

```bash
# Install dependencies
poetry install

# Setup credentials
cp .env.template .env

# Setup credentials for testing
cp .env.template .env.testing
```

### Make your tool available system-wide

[pipx](https://pipx.pypa.io/stable/installation/) is very useful for installing Python tools in virtual environments.

```bash
# install from local directory
# great for development
pipx install . --editable
pipx uninstall nuclei_scan_runner 

# install from GitLab
# great for production
pipx install git+ssh://git@gitlab.ics.muni.cz/dkb-zh/vulnerability-management/orchestration-services/OrchS-nuclei.git@master
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

