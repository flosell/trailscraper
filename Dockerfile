ARG PYTHON_VERSION="TBD"

FROM python:${PYTHON_VERSION}-alpine

# Copy the pre-built wheel (assumes ./go build has been run)
COPY dist/trailscraper*.whl /tmp/

# Install the wheel
RUN pip install --no-cache-dir /tmp/trailscraper*.whl && \
    rm -rf /tmp/trailscraper*.whl

ENTRYPOINT ["/usr/local/bin/trailscraper"]
