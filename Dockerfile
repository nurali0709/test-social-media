FROM python:3.11.3-alpine

EXPOSE 8000

RUN mkdir /social

WORKDIR /social

RUN apk add gcc musl-dev libffi-dev
RUN pip install poetry

COPY . /social

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without test

RUN chmod a+x docker/*.sh

CMD gunicorn social_media.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
