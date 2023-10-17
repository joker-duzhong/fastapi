#! /usr/bin/env bash
# this script executed by start.sh/start-reload.sh, code in repo:uvicorn-gunicorn-docker

#
# Infinite loop to keep container live doing nothing
#
# tail /dev/null -f

# Create initial data in DB
python /app/app/initial_data.py
