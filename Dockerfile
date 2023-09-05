FROM python:3.11-bookworm

ENV VENV_PATH="/opt/poetry"

RUN python3 -m venv ${VENV_PATH}
RUN ${VENV_PATH}/bin/pip install -U pip setuptools
RUN ${VENV_PATH}/bin/pip install poetry

WORKDIR /app
COPY ./pyproject.toml .

RUN ${VENV_PATH}/bin/poetry install

COPY . .
RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT [ "./docker-entrypoint.sh" ]
