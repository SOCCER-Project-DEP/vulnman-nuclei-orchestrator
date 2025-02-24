FROM golang:1.24.1-alpine3.21

WORKDIR /vulnman-nuclei-orchestrator    
COPY . .

# Install Nuclei
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
RUN nuclei -update-templates

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
