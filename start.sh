#!/bin/bash
export PYTHONPATH=$(pwd)
gunicorn backend.auth_server:app --bind 0.0.0.0:$PORT
