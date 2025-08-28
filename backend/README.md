# CIRI service

AI agent service.

## Features

- FastAPI framework for high-performance API development
- PostgreSQL database integration with SQLAlchemy ORM
- JWT authentication
- Alembic for database migrations
- Docker support for easy deployment
- Clean architecture with proper separation of concerns

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Docker (optional)

### Environment Setup

1. Clone the repository
2. Create a virtual environment:
   \`\`\`
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`
3. Install dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`
4. Copy `.env.example` to `.env` and update the values:
   \`\`\`
   cp .env.example .env
   \`\`\`

### Database Setup

1. Run database migrations:
   \`\`\`
   python scripts/run_migrations.py
   \`\`\`

2. Seed the database with sample data (optional):
   \`\`\`
   # Using SQL script
   psql -U your_user -d your_database -f seed_data.sql
   \`\`\`

### Running the Application

#### Without Docker

\`\`\`
uvicorn main:app --reload
\`\`\`

#### With Docker

\`\`\`
docker-compose up -d
\`\`\`

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migrations

### Create a New Migration

\`\`\`
python scripts/create_migration.py "your migration message"
\`\`\`

### Run Migrations

\`\`\`
python scripts/run_migrations.py
\`\`\`

## Project Structure

\`\`\`
.
├── alembic/                  # Database migration files
├── app/                      # Application code
│   ├── api/                  # API endpoints
│   │   ├── deps.py           # Dependencies
│   │   └── routes/           # API routes
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Configuration
│   │   └── security.py       # Security utilities
│   ├── crud/                 # CRUD operations
│   ├── db/                   # Database setup
│   ├── models/               # SQLAlchemy models
│   └── schemas/              # Pydantic schemas
├── scripts/                  # Utility scripts
├── .env.example              # Example environment variables
├── alembic.ini               # Alembic configuration
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker configuration
├── main.py                   # Application entry point
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
