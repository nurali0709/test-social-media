FROM python:3.11.3-alpine

RUN mkdir /social

WORKDIR /social

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without test

COPY . .

CMD gunicorn social_media.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
