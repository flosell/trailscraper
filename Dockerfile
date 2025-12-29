FROM python:3.11-alpine as base
FROM base as builder

RUN apk add build-base
RUN pip install uv

COPY . /src
WORKDIR /src

RUN mkdir /install
RUN uv pip install --prefix=/install .
RUN uv build
RUN uv pip install --prefix=/install dist/trailscraper*.whl


FROM base

COPY --from=builder /install /usr/local

ENTRYPOINT ["/usr/local/bin/trailscraper"]
