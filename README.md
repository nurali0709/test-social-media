# Social Media FastAPI Test Project

This is a Social media FastAPI project, where you can create, read, update and delete posts and give your reactions (likes and dislikes) to another user's posts. As an authentication tool used JWT

## Getting started

### Prerequisites

- Python 3.11
- Poetry
- PostgreSQL

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

## Notes
Make sure to create your Database in PostgreSQL, and define your database name, user, port, host and password in .env file
Additionaly, you need to generate your own JWT_SECRET in order to use JWT authentication.
JWT algorithm is HS256
Make sure to paste all this data in .env file
```
poetry run uvicorn vin.main:app --reload
```
## You can use Makefile to simplify commands
```
make serve
```
