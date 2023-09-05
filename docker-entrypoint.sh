#!/bin/bash
${VENV_PATH}/bin/poetry run alembic upgrade head
${VENV_PATH}/bin/poetry run gunicorn -w 16 -k eventlet "blitz_board:app" -b 0.0.0.0:5000
