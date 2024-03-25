#!/bin/bash

# Database migrations
${VENV_PATH}/bin/poetry run alembic upgrade head

# Launch worker processes
${VENV_PATH}/bin/poetry run gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker "blitz_board:app" \
    -b web:5000 --workers 1 --threads $(nproc) \
    --certfile /etc/ssl/cert.pem --keyfile /etc/ssl/cert.key &
${VENV_PATH}/bin/poetry run gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker "blitz_board:app" \
    -b web:5001 --workers 1 --threads $(nproc) \
    --certfile /etc/ssl/cert.pem --keyfile /etc/ssl/cert.key &
${VENV_PATH}/bin/poetry run gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker "blitz_board:app" \
    -b web:5002 --workers 1 --threads $(nproc) \
    --certfile /etc/ssl/cert.pem --keyfile /etc/ssl/cert.key &
${VENV_PATH}/bin/poetry run gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker "blitz_board:app" \
    -b web:5003 --workers 1 --threads $(nproc) \
    --certfile /etc/ssl/cert.pem --keyfile /etc/ssl/cert.key &
wait
