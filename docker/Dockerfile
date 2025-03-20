FROM python:3.13.2-alpine3.20 AS builder

ENV POETRY_VIRTUALENVS_IN_PROJECT=false
ENV PYSETUP_PATH="/app"
ENV PATH="$PYSETUP_PATH/.local/bin:/usr/bin:$PATH"
ENV HISTFILE=$PYSETUP_PATH/.local/.ash_history
ENV PYTHONPATH="/app"

WORKDIR ${PYSETUP_PATH}

RUN pip install --no-cache-dir --ignore-installed poetry==2.1.1

COPY poetry.lock pyproject.toml ./

FROM builder AS install

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root \
    && ln -s $PYSETUP_PATH/.local/bin/gunicorn /usr/bin/gunicorn \
    && ln -s $PYSETUP_PATH/.local/bin/uvicorn /usr/bin/uvicorn

RUN adduser -D -u 1000 -h $PYSETUP_PATH appuser

COPY . .

USER appuser
