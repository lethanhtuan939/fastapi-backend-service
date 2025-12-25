# FastAPI Backend Service

## Overview

This is a FastAPI-based backend service designed to provide robust API endpoints. It utilizes PostgreSQL as the database and includes Docker support for easy deployment.

## Prerequisites

Before running the project, ensure you have the following installed:

*   **Python 3.11+**
*   **Docker & Docker Compose**
*   **Git**

## Environment Configuration

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    cd fastapi-backend-service
    ```

2.  Create a `.env` file in the root directory. You can use the provided `.env.example` as a template:
    ```bash
    cp .env.example .env
    ```

3.  Update the `.env` file with your specific configuration values:
    ```env
    DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/dbname"
    POSTGRES_USER="user"
    POSTGRES_PASSWORD="password"
    POSTGRES_DB="dbname"
    SECRET_KEY="your_super_secret_key"
    ```
    *Note: The project uses `psycopg` (v3). Use `postgresql+psycopg://` scheme. For Docker, use `db` or `postgres` as host: `postgresql+psycopg://user:password@postgres:5432/dbname`.*

## Running Locally

### 1. Setup Virtual Environment

It is recommended to use a virtual environment to manage dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Ensure you have a PostgreSQL instance running. You can start one using Docker if you don't have it installed locally:

```bash
docker run --name local-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -e POSTGRES_DB=dbname -p 5432:5432 -d postgres:15-alpine
```

Initialize the database schema using the `init.sql` script (requires `psql` or a database client):

```bash
psql -h localhost -U user -d dbname -f init.sql
```

### 4. Run the Application

Start the development server using `uvicorn`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Or use the convenience script:
```bash
./run.sh
```

The API will be available at `http://localhost:8000`. You can access the interactive API docs at `http://localhost:8000/docs`.

## Running with Docker

To run the entire application stack (API + Database) using Docker Compose:

1.  Ensure your `.env` file is configured correctly.
2.  Run the following command:

```bash
docker-compose up --build
```

The service will start, and the database will be automatically initialized with `init.sql`.

*   API: `http://localhost:8000`
*   Docs: `http://localhost:8000/docs`

## Running Tests

To run the test suite, ensure your virtual environment is active and dependencies are installed, then run:

```bash
pytest
```
This will run all tests defined in the `tests/` directory and generate a coverage report.
