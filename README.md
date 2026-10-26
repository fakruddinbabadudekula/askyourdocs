# Notebook RAG Backend

⚠️ **Learning project — not production ready**

This project is a Python backend for user accounts, notebooks, PDF ingestion, and document-grounded chat. It is a learning project for exploring backend design, RAG workflows, and the trade-offs involved in building a reliable service.

## Architecture and design patterns

The project uses a **layered architecture with pragmatic, selective hexagonal (ports and adapters) boundaries**. Ports are defined for dependencies with meaningful replacement seams, such as persistence, file storage, vector storage, document loading and splitting, and LLM calls. Other libraries, including LangChain and LangGraph, are used directly where their abstraction is not currently a project goal.

The main patterns are:

- **Ports and adapters:** application-facing contracts are implemented by infrastructure adapters.
- **Dependency injection / composition root:** `app/root.py` constructs and wires application services and adapters.
- **Repository and Unit of Work:** repositories encapsulate persistence operations, while the unit of work groups them around a SQLAlchemy session and transaction.
- **Service layer:** application services coordinate authentication, ingestion, and chat use cases.
- **Domain model:** dataclasses and domain methods represent core concepts such as users, notebooks, messages, and refresh tokens.
- **Workflow orchestration:** `DocumentProcessor` coordinates loading and splitting, while `LangGraphWorkflow` coordinates retrieval and answer generation.

The architecture aims to keep HTTP handling at the interface edge and put use-case coordination in the application layer, without introducing an interface for every dependency.

## Features

- User registration and login with Argon2 password hashing.
- Short-lived JWT access tokens and rotating refresh tokens stored as an HTTP-only cookie.
- PDF upload, parsing with PyMuPDF, and chunking with a recursive text splitter.
- Google Generative AI embeddings and a FAISS vector store, with retrieval filtered by user and notebook metadata.
- RAG chat orchestrated by a two-step LangGraph workflow: retrieve relevant chunks, then generate an answer with numbered citations.
- Notebook and message persistence in PostgreSQL through SQLAlchemy's async ORM.
- Structured request logging with a request ID and centralized application exception handling.
- A FastAPI HTTP interface and Docker Compose setup for local development.

## Architecture

The code is organized around application use cases, domain objects, and infrastructure adapters. Ports are used where an external implementation is a likely point of change, including persistence, file storage, document loading and splitting, vector storage, and LLM calls. `app/root.py` wires the concrete implementations together.

```text
Client
  │
  ▼
FastAPI routes and dependencies        app/interface/api
  │
  ▼
Application services and workflow     app/application
  ├── Domain objects                   app/domain
  └── Ports                            app/application/ports
          ▲
          │ implemented by
          └── Infrastructure adapters  app/infrastructure
              ├── SQLAlchemy repositories and unit of work
              ├── Local file storage
              ├── PDF loader and text splitter
              ├── FAISS vector store
              └── OpenRouter LLM client
```

This is a pragmatic, selective use of ports. LangChain types are used in several RAG interfaces and services, and `LangGraphWorkflow` directly uses LangGraph. Those libraries are part of the current application design; the code does not aim to hide them behind a framework-independent RAG model.

## Technology

| Area | Technology |
|---|---|
| HTTP API | FastAPI, Uvicorn |
| Runtime | Python 3.11+, managed with `uv` |
| Relational database | PostgreSQL, SQLAlchemy 2 async, asyncpg |
| Authentication | JWT with `python-jose`, Argon2 with Passlib |
| RAG orchestration | LangGraph and LangChain |
| Embeddings | Google Generative AI (`gemini-embedding-001`) |
| Chat model | OpenRouter-compatible API through `ChatOpenAI` |
| Vector storage | FAISS on local disk |
| PDF parsing | PyMuPDF through LangChain's PDF loader |
| Chunking | LangChain recursive text splitter |
| Retry handling | Tenacity |
| Local environment | Docker and Docker Compose |

## Project layout

```text
app/
├── main.py                         # FastAPI app, lifespan, router registration
├── root.py                         # Dependency composition and application container
├── core/                           # Configuration, exceptions, request context, logging
├── domain/                         # User, notebook, message, file and token objects
├── application/
│   ├── ports/                      # Repository, unit-of-work, storage and RAG contracts
│   ├── schemas/                    # Application service input/output schemas
│   ├── auth_service.py             # Registration, login and refresh-token use cases
│   ├── chat_service.py             # Notebook validation, chat and message persistence
│   ├── file_ingestion_service.py   # Upload and ingestion use case
│   ├── doc_processor.py            # Loader and splitter orchestration
│   ├── vector_store_service.py     # Vector document operations
│   └── workflow.py                 # LangGraph retrieval and answer generation
├── infrastructure/
│   ├── rag/                        # PDF, splitter, LLM and FAISS adapters
│   ├── sqlalchemy_repositories/    # ORM models, mappers and repository adapters
│   ├── db.py                       # Async engine and session factory
│   ├── unit_of_work.py             # SQLAlchemy unit of work
│   └── file_storage_repository.py  # Local filesystem storage adapter
└── interface/api/
    ├── routes/                     # Auth, registration, chat, upload and test routes
    ├── schemas/                    # HTTP request and response models
    ├── dependencies.py             # FastAPI dependency wiring
    ├── middleware.py               # Request logging middleware
    └── exception_handlers.py       # Application exceptions to HTTP responses
```

## Getting started

### Requirements

- Python 3.11 or later
- [`uv`](https://docs.astral.sh/uv/)
- Docker and Docker Compose, or a local PostgreSQL instance
- An OpenRouter API key and a Google API key

### Configure environment

Copy `.env.example` to `.env`, then set your API keys and a unique `SECRET_KEY`. The example file contains development credentials; replace them before using the application outside a local development environment.

```bash
cp .env.example .env
```

The required settings are:

| Variable | Purpose |
|---|---|
| `OPENROUTER_BASE_URL` | OpenRouter-compatible chat API base URL |
| `OPENROUTER_API_KEY` | Chat model API key |
| `GOOGLE_API_KEY` | Embedding API key |
| `DATABASE_URL` | SQLAlchemy async PostgreSQL connection URL |
| `SECRET_KEY` | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh-token lifetime |
| `ALGORITHM` | JWT signing algorithm, for example `HS256` |

Other settings, including model name, chunk size, retrieval count, and timeouts, have defaults in `app/core/config.py` and can be overridden with environment variables.

### Run with Docker Compose

The Compose configuration expects the database URL in `.env` to use the `postgres_db` service hostname. The example file is configured for this local setup.

```bash
docker compose up --build
```

The API is available at `http://localhost:8000`. The interactive API documentation is at `http://localhost:8000/docs`, and the health endpoint is at `http://localhost:8000/health`.

### Run locally

Start PostgreSQL and set `DATABASE_URL` in `.env` to point to it. Then install dependencies and start the API:

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On startup, the application creates database tables through SQLAlchemy metadata. This project does not currently include a database migration tool or migration scripts.

## API overview

All application endpoints use the `/api/v1` prefix.

| Method | Path | Authentication | Description |
|---|---|---|---|
| `POST` | `/api/v1/register` | None | Create a user account |
| `POST` | `/api/v1/auth/login` | None | Log in; returns an access token and sets a refresh cookie |
| `POST` | `/api/v1/auth/refresh` | Refresh cookie | Rotate the refresh token and return a new access token |
| `POST` | `/api/v1/auth/logout` | Refresh cookie | Revoke the refresh token and clear the cookie |
| `POST` | `/api/v1/upload` | Bearer access token | Upload and ingest a PDF; optionally provide a notebook ID |
| `POST` | `/api/v1/chat` | Bearer access token | Ask a question about a notebook's documents |
| `GET` | `/api/v1/test/current_user` | Bearer access token | Return the authenticated user's ID (development endpoint) |
| `GET` | `/` | None | Basic service response |
| `GET` | `/health` | None | Basic health response |

Protected endpoints use `Authorization: Bearer <access_token>`. The refresh and logout endpoints use the `refresh_token` HTTP-only cookie.

## Request flows

### PDF ingestion

1. The client uploads a PDF and may include a `notebook_id` form field.
2. The service creates a notebook if no ID was supplied, then saves the file under the configured upload directory.
3. The document processor loads the PDF and splits its pages into chunks.
4. The chunks are added to the FAISS store with user, notebook, and file metadata; file metadata and document references are written to PostgreSQL.

### Chat

1. The client submits a `notebook_id` and question.
2. The service checks notebook ownership and loads the notebook's message history.
3. The retriever finds relevant chunks using the user and notebook metadata filters.
4. LangGraph passes retrieved context and conversation history to the LLM workflow.
5. The answer and citation references are persisted, then returned with citation data.

## Data model

The current SQLAlchemy models represent:

| Entity | Purpose |
|---|---|
| `user` | Account name, email, password hash and creation time |
| `notebook` | User-owned chat notebook and its creation time |
| `message` | Notebook conversation messages and citation references |
| `file_metadata` | Uploaded PDF metadata associated with a notebook |
| `document_ref` | Link between a vector-store document ID and a file |
| `refresh_token` | Hashed refresh token, family, status and expiry data |

## Known limitations

This is an evolving learning project. Current limitations include:

- **Ingestion cleanup:** file and vector-store writes are external side effects and are not currently compensated if a later ingestion step fails. Database rollback alone cannot undo those writes. Cleanup behavior remains to be implemented.
- **Local FAISS storage:** the vector index is stored on the local filesystem. This setup is suited to development and a single instance; multiple replicas need shared storage or a different vector-store deployment.
- **PDF-only ingestion:** the loader and file type currently support PDF only.
- **In-process document processing:** parsing, chunking, embedding, and storage run in the request flow rather than a background worker.
- **Limited automated coverage:** automated tests are not included in this project snapshot.
- **Development route:** `/api/v1/test/current_user` is registered for development use.
- **Schema evolution:** tables are created from SQLAlchemy metadata at startup; versioned migrations are not configured.

## Contributing

1. Create a branch for your change.
2. Install dependencies with `uv sync`.
3. Keep HTTP-specific concerns in `app/interface/api`; use application services for use cases and infrastructure adapters for external systems.
4. Add or update documentation when an endpoint or behavior changes.
5. Include tests for new behavior as the test suite is established, and describe the change and its motivation in your pull request.




