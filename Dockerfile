FROM python:3.10.4

WORKDIR /

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin: $PATH"

COPY poetry.lock pyproject.toml /

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . /