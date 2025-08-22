# 🚀 Quick Commands Guide

## **One Command to Start Everything**

When you're in the `m@RKBBC llm-testing-interface %` terminal, just run:

```bash
./start
```

That's it! This will:
- ✅ Check your environment
- ✅ Start the backend server
- ✅ Start the frontend server  
- ✅ Show you all the URLs
- ✅ Monitor everything and keep it running

## **Quick Status Check**

To see what's running:

```bash
./status
```

This shows you:
- ✅ Virtual environment status
- ✅ Database status
- ✅ Backend server status
- ✅ Frontend server status
- ✅ Log files status

## **Testing Everything**

To test the entire system:

```bash
./test
```

Or for specific tests:
```bash
./test quick    # Just environment and database
./test backend  # Backend tests only
./test full     # Complete system tests (default)
```

## **Stop Everything**

To stop all servers:

```bash
./stop
```

Or just press `Ctrl+C` when running `./start`

## **What Each Command Does**

| Command | What It Does |
|---------|-------------|
| `./start` | Starts everything with full error checking and logging |
| `./status` | Shows current system status |
| `./test` | Runs comprehensive tests with detailed reports |
| `./stop` | Stops all servers cleanly |

## **Logs and Debugging**

All logs are saved in the `logs/` directory:
- `logs/backend.log` - Backend server logs
- `logs/frontend.log` - Frontend server logs  
- `logs/test_system.log` - Test framework logs
- `logs/test_report_*.json` - Detailed test reports

## **URLs When Running**

Once you run `./start`, you can access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## **Troubleshooting**

If something doesn't work:

1. **Check status**: `./status`
2. **Run tests**: `./test`
3. **Check logs**: `tail -f logs/backend.log` or `tail -f logs/frontend.log`
4. **Restart everything**: `./stop` then `./start`

## **Behind the Scenes**

These commands use:
- **Comprehensive error checking** - Every step is verified
- **Detailed logging** - Everything is logged for debugging
- **Process monitoring** - Automatically detects if servers die
- **Clean shutdown** - Proper cleanup when stopping
- **Test framework** - Full system testing with reports

No more guessing what's wrong - everything is testable and checkable! 🎯
