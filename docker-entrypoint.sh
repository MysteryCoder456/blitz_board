#!/bin/bash
${VENV_PATH}/bin/poetry run alembic upgrade head
${VENV_PATH}/bin/poetry run gunicorn -k eventlet "blitz_board:app" -b web:5000 --threads $(nproc) --certfile /etc/ssl/cert.pem --keyfile /etc/ssl/cert.key
