# Quick Start Guide

## 🚀 Get the Server Running in 3 Steps

### Step 1: Install Dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install requests  # For testing
```

### Step 2: Configure Remote LLM Servers
```bash
# From the project root directory:
python configure_servers.py
```
This will help you set up the IP addresses of your remote Ollama and LM Studio servers.

### Step 3: Start the Server
```bash
# From the project root directory:
python start_server.py
```

### Step 4: Test the API
Open your browser and go to:
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## 🧪 What We've Built

✅ **Phase 1 Complete**: Basic LLM Testing Interface
- FastAPI backend with SQLite database
- Conversation management (create, read, update, delete)
- LLM service integration (Ollama, LM Studio)
- Health monitoring and metrics
- RESTful API with automatic documentation

## 📋 Available Endpoints

- `GET /health` - System health check
- `GET /api/v1/conversations` - List conversations
- `POST /api/v1/conversations` - Create new conversation
- `GET /api/v1/llm/services` - List LLM services
- `POST /api/v1/llm/generate` - Generate LLM response
- `GET /api/v1/monitoring/health` - Detailed health info

## 🔧 Configuration

The server uses default settings for development. To customize:
1. Copy `backend/env.example` to `backend/.env`
2. Edit the `.env` file with your settings
3. **Important**: Update the LLM server URLs to point to your remote servers:
   - `OLLAMA_BASE_URL=http://YOUR_SERVER_IP:11434`
   - `LM_STUDIO_BASE_URL=http://YOUR_SERVER_IP:1234/v1`

## 🎯 Next Steps

This is Phase 1 - a working foundation! Next phases will add:
- Frontend UI
- LLM-Bench integration
- Advanced benchmarking
- PostgreSQL migration

## 🐛 Troubleshooting

If the server won't start:
1. Make sure you're in the `backend` directory
2. Ensure virtual environment is activated
3. Check that all dependencies are installed
4. Try running: `python -c "from app.main import app; print('App loads successfully')"`

---

**🎉 You now have a working LLM Testing Interface!**
