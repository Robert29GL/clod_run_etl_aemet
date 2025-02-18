#-------------#
# BUILD STAGE #
#-------------#
FROM python:3.11-buster as builder
WORKDIR /build

#copy config files

COPY pyproject.toml uv.lock* /build/

#install UV

RUN pip install --no-cache-dir uv

#install dependency from pyproject.toml
RUN uv pip install --system .

#-------------#
# FINAL STAGE #
#-------------#
FROM python:3.11-slim AS runner
WORKDIR /app

ENV PYTHONUNBUFFERED=true

#create a non-privileged user
RUN groupadd -r appgroup \
    && useradd -r -m -g appgroup appuser

# Copy the executable 'uv' from build step
COPY --from=builder --chown=appuser:appgroup /usr/local/bin/uv /usr/local/bin/uv
COPY --from=builder --chown=appuser:appgroup /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --chown=appuser:appgroup src/ /app/src/

USER appuser

EXPOSE 8080

CMD ["uv", "run", "src/main.py"]
