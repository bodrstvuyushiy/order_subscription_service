FROM python:3.9-alpine3.16

WORKDIR /service

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && apk add --no-cache libffi-dev

RUN apk add --no-cache postgresql-client build-base

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

RUN adduser --disabled-password admin

COPY . /service

RUN chown -R admin /service

USER admin

EXPOSE 8000