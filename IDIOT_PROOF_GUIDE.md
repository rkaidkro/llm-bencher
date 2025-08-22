# 🎯 IDIOT-PROOF GUIDE
## (For Product Managers Learning to Code)

### 🚨 BEFORE YOU START
**You need to activate the virtual environment EVERY TIME you open a new terminal!**

---

## 📋 STEP-BY-STEP (Copy & Paste Each Command)

### Step 1: Open Terminal & Navigate to Project
```bash
cd /Users/m/llm-bench2/llm-testing-interface
```

### Step 2: Activate Virtual Environment (DO THIS FIRST!)
```bash
cd backend
source venv/bin/activate
cd ..
```
**✅ SUCCESS**: You should see `(venv)` at the start of your terminal prompt

### Step 3: Start the Backend Server
```bash
python start_server.py
```
**✅ SUCCESS**: You should see "Server started successfully" and "API running on http://127.0.0.1:8000"

### Step 4: Open New Terminal Tab (Keep Backend Running!)
- Press `Cmd + T` for new terminal tab
- Navigate to project: `cd /Users/m/llm-bench2/llm-testing-interface`
- Activate venv again: `cd backend && source venv/bin/activate && cd ..`

### Step 5: Start the Frontend
```bash
python test_frontend.py
```
**✅ SUCCESS**: You should see "Frontend server started successfully"

### Step 6: Open Your Browser
- Go to: http://localhost:3000
- You should see the LLM Testing Interface!

---

## 🚨 TROUBLESHOOTING

### "source: no such file or directory: venv/bin/activate"
**SOLUTION**: You're in the wrong directory!
```bash
cd /Users/m/llm-bench2/llm-testing-interface/backend
source venv/bin/activate
cd ..
```

### "cd: no such file or directory: backend"
**SOLUTION**: You're in the wrong place!
```bash
cd /Users/m/llm-bench2/llm-testing-interface
```

### "Connection refused" or "Cannot connect to API"
**SOLUTION**: Backend server isn't running!
1. Go back to Step 3
2. Make sure you see "Server started successfully"

### "npm: command not found"
**SOLUTION**: Frontend dependencies not installed!
```bash
cd frontend
npm install
cd ..
```

---

## 🎯 QUICK COMMANDS (Copy & Paste)

**Start Everything:**
```bash
cd /Users/m/llm-bench2/llm-testing-interface
cd backend && source venv/bin/activate && cd ..
python start_server.py
```

**In New Terminal Tab:**
```bash
cd /Users/m/llm-bench2/llm-testing-interface
cd backend && source venv/bin/activate && cd ..
python test_frontend.py
```

---

## 🎉 SUCCESS INDICATORS

✅ **Backend Running**: "Server started successfully"  
✅ **Frontend Running**: "Frontend server started successfully"  
✅ **Virtual Environment**: `(venv)` in terminal prompt  
✅ **Website Working**: http://localhost:3000 loads  

---

## 🆘 STILL STUCK?

1. **Check your terminal prompt** - should show `(venv)`
2. **Check your directory** - should be in `llm-testing-interface`
3. **Check both servers** - backend on port 8000, frontend on port 3000
4. **Restart everything** - close terminals, start fresh

**You got this! 🚀**
