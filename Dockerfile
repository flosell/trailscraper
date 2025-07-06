FROM python:3.11-alpine as base
FROM base as builder

RUN apk add build-base

COPY . /src
WORKDIR /src

RUN mkdir /install
RUN pip install --prefix=/install .


FROM base

COPY --from=builder /install /usr/local

ENTRYPOINT ["/usr/local/bin/trailscraper"]
