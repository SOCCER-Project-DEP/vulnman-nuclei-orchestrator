# Vulnerability Management (VulnMan) Nuclei Orchestrator

This project handles the orchestration of scanner nuclei, storing results in the database, and reporting to GitLab.

## Setup (Ansible)

See [SOCCER-Project-DEP/vulnman-ansible](https://github.com/SOCCER-Project-DEP/vulnman-ansible) for Ansible that deploys this tool alongside [vulnman-nuclei-orchestrator](https://github.com/SOCCER-Project-DEP/vulnman-nuclei-orchestrator).

This tool is meant to be used via systemd services, so refer first to the Ansible repository for the most straightforward setup. 
If you know what you are doing, you can also use the manual usage instructions below.

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
sudo poetry run nuclei-scan-runner
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

```bash
# To see all available options
sudo poetry run nuclei-scan-runner --help 

# Most general run
sudo poetry run nuclei-scan-runner --config configs/scheduled-config.toml --nuclei-config configs/scheduled-nuclei.yml --dont-create-issues
```

## Ignored finding severity

By defaul, severity `info` and `low` are ignored. You can change this behavior by variable in `nuclei_scan_runner/afterscan/script_constants.py`

## Examples of usage

### Process previously scanned results

```
poetry run nuclei-scan-runner --skip-scan --logfile /var/log/vulnman_nuclei/logs/scheduled.ndjson.1 --results /var/log/vulnman_nuclei/results/scheduled/2024-09-12T03\:49\:33.433654.json --gitlab-project-id 6355
```

## Additional information

- This repository is being developed as a part of the [SOCCER](https://soccer.agh.edu.pl/en/) project.
- Developed by the cybersecurity team of [Masaryk University](https://www.muni.cz/en).
- This project is a "mirror" of the original repository hosted on university Gitlab. New features and fixes here are being added upon new releases of the original repository.

## Help

Are you missing something? Do you have any suggestions or problems? Please create an issue.
Or ask us at `csirt-info@muni.cz`; we are happy to help you, answer your questions, or discuss your ideas.
