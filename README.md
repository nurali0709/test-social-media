# Social Media FastAPI Test Project

This is a FastAPI project.

## Getting started

### Prerequisites

- Python 3.11
- Poetry

## Installation


   ```
   git clone https://github.com/nurali0709/test-social-media.git

   ```
   As a package and dependency manager I used poetry, so firstly you need to install poetry on your machine. You can do it [here](https://python-poetry.org/docs/).
   
   ```
   python3.11 -m venv .venv
   source /.venv/bin/activate
   pip install poetry
   poetry install

   ```
## Usage
After poetry has been installed, you can start using application. Just write VIN you looking for in a field, and it'll respond with appropriate ones.
```
poetry run uvicorn vin.main:app --reload
```
