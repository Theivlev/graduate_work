#!/usr/bin/env bash

alembic upgrade head
exec uvicorn src.main:app --reload --host $UVICORN_HOST --port $UVICORN_PORT_WS
