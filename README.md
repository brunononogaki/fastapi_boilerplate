# FastAPI Boilerplate

A starter template for building FastAPI backends with PostgreSQL. This project includes basic CRUD routes for user management and OAuth2 authentication. You will need a running PostgreSQL server, ideally with two separate databases: one for development and one for testing.

## Requirements
- Python 3.13 or higher
- Poetry 2.1.4 or higher
- PostgreSQL

## Setup

Install dependencies:
```bash
poetry install
```

Configure your environment variables by editing the `.env-example` file with your database details, then rename it to `.env`:
```env
# Database Configuration
DATABASE_HOST=mydatabase.local
DATABASE_PORT=5432
DATABASE_USER=dbusername
DATABASE_PASSWORD=dbpassword
DATABASE_NAME=dbname
DATABASE_NAME_TEST=dbname_test
ADMIN_PASSWORD=xxxxxxx

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
```

## Running the Application

Start the server:
```bash
poetry run task run
```
Note: This will automatically create a `Users` table and an `admin` user with the password specified in your `.env` file.

## Running Tests

Execute the test suite:
```bash
poetry run task test
```

## Code Formatting

Run the linter and formatter:
```bash
poetry run task format
```
