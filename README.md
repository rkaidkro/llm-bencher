# LLM Testing Interface

A comprehensive interface for testing and benchmarking LLM models with support for multiple providers like Ollama and LM Studio.

## 🚀 Features

- **Multi-LLM Support**: Connect to Ollama, LM Studio, and other OpenAI-compatible APIs
- **Conversation Management**: Create, manage, and search through chat conversations
- **Health Monitoring**: Real-time monitoring of LLM service health and performance
- **Structured Logging**: Comprehensive logging with structured data
- **RESTful API**: Clean, documented API endpoints
- **Database Storage**: SQLite for development, PostgreSQL for production
- **Future LLM-Bench Integration**: Ready for advanced benchmarking capabilities

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+ (for frontend)
- Ollama or LM Studio running locally

## 🛠️ Installation

### Backend Setup

1. **Clone the repository and navigate to the backend:**
   ```bash
   cd llm-testing-interface/backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database:**
   ```bash
   python -c "from app.main import init_db; init_db()"
   ```

6. **Run the development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup (Coming Soon)

1. **Navigate to the frontend directory:**
   ```bash
   cd llm-testing-interface/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database Configuration
DATABASE_URL=sqlite:///./llm_interface.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO

# LLM Services Configuration
DEFAULT_LLM_SERVICE=ollama
OLLAMA_BASE_URL=http://localhost:11434
LM_STUDIO_BASE_URL=http://localhost:1234/v1

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

## 📚 API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Key Endpoints

#### LLM Services
- `GET /api/v1/llm/services` - List all LLM services
- `POST /api/v1/llm/services` - Create a new LLM service
- `POST /api/v1/llm/generate` - Generate LLM response
- `POST /api/v1/llm/services/{id}/health` - Check service health

#### Conversations
- `GET /api/v1/conversations` - List conversations
- `POST /api/v1/conversations` - Create new conversation
- `GET /api/v1/conversations/{id}/messages` - Get conversation messages
- `POST /api/v1/conversations/{id}/messages` - Add message to conversation

#### Monitoring
- `GET /api/v1/monitoring/health` - System health
- `GET /api/v1/monitoring/health/services` - All services health
- `GET /api/v1/monitoring/metrics/response-times` - Response time metrics
- `GET /api/v1/monitoring/metrics/uptime` - Uptime metrics

## 🏗️ Project Structure

```
llm-testing-interface/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── models/
│   │   │   ├── database.py      # Database configuration
│   │   │   └── schemas.py       # SQLAlchemy models & Pydantic schemas
│   │   ├── routers/
│   │   │   ├── llm.py          # LLM service endpoints
│   │   │   ├── conversations.py # Conversation management
│   │   │   └── monitoring.py   # Health & monitoring
│   │   ├── services/
│   │   │   └── llm_service.py  # LLM communication logic
│   │   └── utils/
│   │       └── config.py       # Configuration management
│   ├── requirements.txt
│   └── env.example
├── frontend/                    # React frontend (coming soon)
├── reports/                     # Benchmark results
├── docs/                        # Documentation
└── README.md
```

## 🔄 Development Workflow

### Git Strategy

```bash
# Main branches
main                    # Production-ready code
develop                # Integration branch

# Feature branches
feature/basic-chat     # Phase 1 features
feature/multi-model    # Phase 2 features
feature/advanced-ui    # Phase 3 features
feature/postgresql     # Phase 4 migration
feature/batch-testing  # Phase 5 features
```

### Code Quality

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing

Run quality checks:
```bash
black app/
isort app/
flake8 app/
mypy app/
pytest
```

## 🧪 Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## 🚀 Deployment

### Docker (Coming Soon)

```bash
docker-compose up -d
```

### Production

1. Set `ENVIRONMENT=production` in `.env`
2. Use PostgreSQL database
3. Configure proper CORS origins
4. Set secure `SECRET_KEY`
5. Use production WSGI server (Gunicorn)

## 🔮 Roadmap

### Phase 1: Foundation ✅
- [x] Basic FastAPI setup
- [x] SQLite database
- [x] Single LLM communication
- [x] Basic conversation management

### Phase 2: Multi-Model & Monitoring
- [ ] Multiple LLM service support
- [ ] Health monitoring dashboard
- [ ] Service status tracking
- [ ] Response time metrics

### Phase 3: Advanced UI & LLM-Bench Integration
- [ ] Multi-tab interface
- [ ] Settings panel
- [ ] LLM-Bench integration
- [ ] Benchmark execution

### Phase 4: PostgreSQL Migration
- [ ] Database migration
- [ ] Performance optimization
- [ ] Full-text search

### Phase 5: Advanced Features
- [ ] Batch testing
- [ ] A/B testing
- [ ] Automated benchmarks
- [ ] Vision testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the `/docs` endpoint when running
- **Discussions**: Use GitHub Discussions

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for database ORM
- Pydantic for data validation
- The LLM community for inspiration and tools
