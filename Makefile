.PHONY: lint
lint:
	poetry run pylint ./social_media

.PHONY: migrate
migrate:
	alembic upgrade head

.PHONY: serve
serve:
	poetry run uvicorn social_media.main:app --reload

.PHONY: host
host: 
	poetry run uvicorn social_media.main:app --host 0.0.0.0 --port 8000 --reload