FROM python:3.9.1-slim

WORKDIR '/app'
COPY pyproject.toml poetry.lock* ./

RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .

#RUN PYTHONPATH=. alembic upgrade head
#CMD ls -al
#CMD exec uvicorn saas.web.app:web_app --port $PORT --host 0.0.0.0

CMD ["scripts/start.sh"]