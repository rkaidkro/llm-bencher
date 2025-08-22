# Quick Start Guide

## 🚀 Get Everything Running in 1 Command

**From the `m@RKBBC llm-testing-interface %` terminal, just run:**

```bash
./start
```

That's it! This will automatically:
- ✅ Check your environment
- ✅ Start the backend server
- ✅ Start the frontend server
- ✅ Show you all the URLs
- ✅ Monitor everything and keep it running

## 🔍 Check Status

To see what's running:

```bash
./status
```

## 🧪 Test Everything

To test the entire system:

```bash
./test
```

## 🛑 Stop Everything

To stop all servers:

```bash
./stop
```

## 📋 Available URLs

Once running, you can access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## 🛠️ Manual Setup (Advanced)

If you need to set up manually:

## 🧪 What We've Built

✅ **Phase 1 Complete**: Basic llm-bencher
- FastAPI backend with SQLite database
- Conversation management (create, read, update, delete)
- LLM service integration (Ollama, LM Studio)
- Health monitoring and metrics
- RESTful API with automatic documentation

✅ **Phase 2 Complete**: Intuitive Command System
- One-command startup (`./start`)
- Status checking (`./status`)
- Comprehensive testing (`./test`)
- Clean shutdown (`./stop`)
- Detailed logging and error reporting
- Process monitoring and automatic cleanup

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

### Quick Troubleshooting

If something doesn't work:

1. **Check status**: `./status`
2. **Run tests**: `./test`
3. **Check logs**: `tail -f logs/backend.log` or `tail -f logs/frontend.log`
4. **Restart everything**: `./stop` then `./start`

### Manual Troubleshooting

**If you see `source: no such file or directory: venv/bin/activate`:**
1. Make sure you're in the `backend` directory first
2. Check if the virtual environment exists: `ls -la venv/`
3. If it doesn't exist, create it: `python3 -m venv venv`
4. Then activate: `source venv/bin/activate`

**If you see `(venv)` in your prompt, you're good to go!**

### Server Won't Start
If the server won't start:
1. Make sure you're in the project root directory
2. Ensure virtual environment is activated (see `(venv)` in prompt)
3. Check that all dependencies are installed
4. Try running: `python -c "from app.main import app; print('App loads successfully')"`

### Common Commands
```bash
# Check if venv is activated (should see (venv) in prompt)
echo $VIRTUAL_ENV

# Activate venv from project root
cd backend && source venv/bin/activate && cd ..

# Check Python path (should point to venv)
which python
```

---

**🎉 You now have a working llm-bencher!**
