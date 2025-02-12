#-------------#
# BUILD STAGE #
#-------------#
FROM python:3.11-buster as builder
WORKDIR /build

ARG POETRY_VERSION=1.8.3
ENV PIP_ROOT_USER_ACTION=ignore

COPY pyproject.toml poetry.lock /build/

RUN pip install --no-cache-dir poetry==${POETRY_VERSION} \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-root

#-------------#
# FINAL STAGE #
#-------------#
FROM python:3.11-slim AS runner
WORKDIR /app

ENV PYTHONUNBUFFERED=true

RUN groupadd -r appgroup \
    && useradd appuser -r -g appgroup

COPY --from=builder --chown=appuser:appgroup /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder --chown=appuser:appgroup /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --chown=appuser:appgroup main.py /app/
COPY --chown=appuser:appgroup cloud_run_etl_template /app/cloud_run_etl_template

USER appuser

EXPOSE $PORT

CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 --timeout 0 main:app
