FROM python:3.7-alpine as base
FROM base as builder

RUN apk add build-base

COPY . /src
WORKDIR /src

RUN mkdir /install
RUN pip install --prefix=/install -r requirements.txt
RUN python3 setup.py sdist bdist_wheel
RUN pip install --prefix=/install dist/trailscraper*.tar.gz


FROM base

COPY --from=builder /install /usr/local

ENTRYPOINT ["/usr/local/bin/trailscraper"]
