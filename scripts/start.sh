#! /usr/bin/env bash

set -euo pipefail


PYTHONPATH=. alembic upgrade head
#PYTHONPATH=. python ./scripts/create_superadmin.py
#PYTHONPATH=. python ./scripts/create_random_data.py
exec uvicorn saas.web.app:web_app --port 8080 --host 0.0.0.0
