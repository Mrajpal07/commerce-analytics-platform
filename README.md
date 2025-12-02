# Commerce Analytics Platform

Multi-tenant SaaS analytics platform for e-commerce data ingestion and analytics.

## Architecture

- **Framework**: FastAPI
- **Database**: PostgreSQL 15+ with Row-Level Security
- **Task Queue**: Celery + Redis
- **Pattern**: Event-driven, CQRS, Multi-tenant

## Project Structure
```
app/
├── api/          # FastAPI routers (controllers)
├── services/     # Business logic
├── repositories/ # Data access layer
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic schemas
├── tasks/        # Celery tasks
├── db/           # Database utilities
├── middleware/   # Request/response middleware
├── core/         # Security, logging, exceptions
└── observability/# Metrics and tracing
```

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Local Development

1. **Clone and setup virtual environment:**
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
```

2. **Configure environment:**
```bash
   cp .env.example .env
   # Edit .env with your credentials
```

3. **Start services with Docker:**
```bash
   docker-compose up postgres redis -d
```

4. **Run database migrations:**
```bash
   alembic upgrade head
```

5. **Start the API server:**
```bash
   uvicorn app.main:app --reload
```

6. **Start Celery worker (separate terminal):**
```bash
   celery -A app.tasks.celery_app worker --loglevel=info
```

7. **Start Celery beat (separate terminal):**
```bash
   celery -A app.tasks.celery_app beat --loglevel=info
```

## Testing
```bash
pytest tests/
pytest tests/unit/
pytest tests/integration/
pytest --cov=app tests/
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

See `render.yaml` for Render.com deployment configuration.

## License

Proprietary