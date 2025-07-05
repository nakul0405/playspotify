#!/bin/bash
gunicorn auth_server:app --bind 0.0.0.0:$PORT
