# Portfolio Backend API

The backend service for Abdul Mannan Saipi's personal portfolio website, built with FastAPI. It handles data for projects, experiences, blog posts, terminal logs, and integrates with the Google Gemini API to power an interactive AI terminal assistant.

## Features

- **Domain-Driven Architecture**: Structured into `api`, `core`, `models`, and `schemas` for modularity and scalability.
- **RESTful Endpoints**: CRUD operations for Projects, Experiences, Writings, Comments, and Certificates.
- **Interactive AI Endpoint**: Uses Google Gemini to act as a personal assistant representing Abdul Mannan Saipi, answering questions based on provided context.
- **Terminal Logs**: Tracks, filters, and paginates terminal interactions (including AI mode vs. Standard mode) and logs user metadata (IP, Country, Execution Time) for analytics.
- **Security & Rate Limiting**: Employs JWT-based authentication for admin routes and SlowAPI for rate limiting to prevent abuse.
- **Relational Database**: Uses SQLAlchemy ORM to manage interactions with the database (SQLite for local/tests, PostgreSQL in production).

## Technologies Used

- **Framework:** FastAPI
- **Database ORM:** SQLAlchemy
- **Authentication:** JWT (JSON Web Tokens), Passlib (Bcrypt)
- **AI Integration:** Google GenAI SDK (Gemini Models)
- **Rate Limiting:** SlowAPI
- **Testing:** Pytest, HTTPX

## Installation

### Prerequisites

- Python 3.10+
- pip

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/manansaipi/portfolio-backend-api.git
   cd portfolio-backend-api
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add the following keys:
   ```env
   # Database
   DATABASE_URL=sqlite:///./portfolio.db  # Use PostgreSQL URL in production

   # Security
   SECRET_KEY=your_super_secret_jwt_key
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD_HASH=$2b$12$YourHashedPasswordHere

   # AI Integration
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_API_KEY_2=optional_backup_gemini_api_key_here
   ```

## Running the Application

Start the FastAPI development server:
```bash
fastapi run app/main.py
```
*Or using Uvicorn directly:*
```bash
uvicorn app.main:app --reload
```

The API will be accessible at `http://localhost:8000`. 
Interactive API documentation (Swagger UI) is automatically available at `http://localhost:8000/docs`.

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── endpoints/    # FastAPI routers (projects, comments, ai, etc.)
│   ├── core/             # Infrastructure logic (auth, database, rate limiter)
│   ├── models/           # SQLAlchemy database models (domain-driven)
│   ├── schemas/          # Pydantic validation schemas (domain-driven)
│   └── main.py           # FastAPI application factory and entry point
├── tests/                # Pytest unit tests (test_api.py, etc.)
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (not tracked in Git)
```

## Running Tests

To run the automated test suite and verify all endpoints:
```bash
pytest tests/
```

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Abdul Mannan Saipi - [AbdulMannan.Saipi@gmail.com](mailto:AbdulMannan.Saipi@gmail.com)

GitHub Link: [https://github.com/manansaipi](https://github.com/manansaipi)
