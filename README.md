# FastAPI Boilerplate

Template for FastAPI backend using FastAPI and Postgres. It implements basic routes for User management (CRUD) and oAuth2 authentication.

## Requirements
- Python 3.13+
- Poetry
- Postgres

## Setup
```bash
poetry install
```

Edit the `.env-example` file with your Database information and rename it to .env
```env
# Database Configuration
DATABASE_HOST=mydatabase.local
DATABASE_PORT=5432
DATABASE_USER=dbusername
DATABASE_PASSWORD=dbpassword
DATABASE_NAME=dbname

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
```

## Execute
```bash
poetry run task run
```

## Run tests
```bash
poetry run task test
```

## Linter
```bash
poetry run task format
```

