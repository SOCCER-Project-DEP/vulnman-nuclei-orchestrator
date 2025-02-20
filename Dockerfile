FROM projectdiscovery/nuclei:latest

WORKDIR /vulnman-nuclei-orchestrator
    
COPY . .

# Install dependencies
RUN apk --no-cache add curl python3
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr/ python3 -
RUN /usr/bin/poetry install

# Create directories for logs and results
RUN mkdir -p /var/log/vulnman_nuclei/logs
RUN mkdir -p /var/log/vulnman_nuclei/results/scheduled
RUN mkdir -p /var/log/vulnman_nuclei/results/adhoc
RUN mkdir -p /var/log/vulnman_nuclei/results/latest
RUN mkdir -p /var/log/vulnman_nuclei/results/testing
