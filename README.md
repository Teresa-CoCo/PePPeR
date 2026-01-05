# PePPeR - Papers with Explanations, Processing, and Reader

An intelligent ArXiv research assistant that helps you discover, read, and understand research papers using AI-powered analysis and interactive chat.

![CI/CD](https://github.com/yourusername/PePPeR/actions/workflows/ci-cd.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Paper Discovery**: Fetch and browse papers from ArXiv by category
- **PDF Processing**: Automatic PDF download and text extraction using OCR
- **AI Analysis**: Generate summaries, key findings, and methodology analysis using LLMs
- **Interactive Chat**: Ask questions about papers and get contextual answers
- **Scheduled Fetching**: Automatically fetch new papers on a schedule
- **PDF Viewer**: Built-in PDF reading with synchronized chat

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Frontend | React 18, TypeScript, Vite |
| PDF Viewer | @react-pdf-viewer/core (pdf.js) |
| Data Source | ArXiv API via `arxiv` Python library |
| OCR | PaddleOCR API with PyMuPDF fallback |
| LLM | OpenRouter API (Claude 3.5 Sonnet, 200K context) |
| Scheduler | APScheduler |
| Styling | Tailwind CSS |
| Testing | pytest (backend), Vitest (frontend) |

## Project Structure

```
PePPeR/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── models/            # Pydantic models
│   │   ├── config.py          # Settings
│   │   └── utils/             # Utilities
│   ├── tests/                 # Backend tests
│   ├── papers/                # PDF storage
│   ├── data/                  # JSON database
│   ├── requirements.txt
│   ├── pytest.ini
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API client
│   │   ├── types/             # TypeScript types
│   │   └── test/              # Test setup
│   ├── package.json
│   ├── vitest.config.ts
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- OpenRouter API key (for AI features)
- PaddleOCR token (optional, for OCR features)

### Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/PePPeR.git
   cd PePPeR
   ```

2. Copy environment file and configure:
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys
   ```

3. Start the application:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Testing

### Backend Tests

```bash
cd backend
pip install pytest pytest-cov
pytest tests/ --cov=app --cov-report=term-missing
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

## CI/CD Pipeline

The project includes a comprehensive GitHub Actions workflow (`.github/workflows/ci-cd.yml`) that:

1. **Lint & Type Check**
   - Python linting with flake8 and ruff
   - TypeScript linting with ESLint
   - Frontend type checking with TypeScript

2. **Unit Tests**
   - Backend: pytest with coverage reporting
   - Frontend: Vitest with coverage reporting

3. **Docker Build**
   - Build and verify backend and frontend images
   - Multi-stage builds for production optimization

4. **Integration Tests**
   - API health checks
   - Endpoint validation

5. **Deployment**
   - Automated deployment on main branch push
   - Staging environment support

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/papers` | List papers with filters |
| POST | `/api/papers/fetch` | Fetch papers from ArXiv |
| GET | `/api/papers/{id}` | Get paper details |
| GET | `/api/papers/{id}/pdf` | Serve PDF file |
| POST | `/api/papers/{id}/process` | Process paper (OCR + AI) |
| POST | `/api/chat/{id}` | Stream chat response |
| GET | `/api/chat/{id}/history` | Get chat history |

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM | Required |
| `OPENROUTER_DEFAULT_MODEL` | Default LLM model | `anthropic/claude-3.5-sonnet` |
| `PADDLEOCR_TOKEN` | PaddleOCR access token | Optional |
| `ARXIV_DELAY_SECONDS` | Delay between ArXiv requests | `3.0` |
| `ARXIV_MAX_RESULTS` | Max papers per fetch | `50` |
| `SCHEDULER_ENABLED` | Enable daily fetching | `false` |
| `SCHEDULER_TIME` | Daily fetch time | `08:00` |
| `SCHEDULER_CATEGORIES` | Categories to fetch | `cs.AI,cs.LG,cs.CL` |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Acknowledgments

- [ArXiv](https://arxiv.org/) for providing open access to research papers
- [OpenRouter](https://openrouter.ai/) for LLM API access
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for OCR capabilities
