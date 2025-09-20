FROM python:3.12-slim-bookworm

# Install dependencies
RUN apt update
RUN apt install -y build-essential libpq-dev

# Install poetry
ENV VENV_PATH="/opt/poetry"
RUN python3 -m venv ${VENV_PATH}
RUN ${VENV_PATH}/bin/pip install -U pip setuptools
RUN ${VENV_PATH}/bin/pip install poetry

WORKDIR /app
COPY ./pyproject.toml .

RUN ${VENV_PATH}/bin/poetry install --only main --no-root

# Setup app diretories & entrypoint
COPY . .
COPY ./nginx/ssl/ /etc/ssl/
RUN mkdir -p /app/blitz_board/media/avatars
RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT [ "./docker-entrypoint.sh" ]
