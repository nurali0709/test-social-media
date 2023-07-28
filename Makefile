.PHONY: lint
lint:
	poetry run pylint ./social_media

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: pre-commit
pre-commit:
	poetry run pre-commit run --all-files

.PHONY: migrate
migrate:
	alembic upgrade head

.PHONY: serve
serve:
	poetry run uvicorn social_media.main:app --reload

.PHONY: host
host:
	poetry run uvicorn social_media.main:app --host 0.0.0.0 --port 8000 --reload
