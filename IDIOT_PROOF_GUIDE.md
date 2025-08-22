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

### Step 2: Run the Magic Startup Script (EASY!)
```bash
python START_EVERYTHING.py
```
**✅ SUCCESS**: You should see "SUCCESS! Everything is running!" and both URLs

### Step 3: Open Your Browser
- Go to: http://localhost:3000
- You should see the LLM Testing Interface!

---

## 🎯 ALTERNATIVE: Manual Steps (If Magic Script Doesn't Work)

### Step 1: Activate Virtual Environment
```bash
cd backend
source venv/bin/activate
cd ..
```

### Step 2: Start Backend
```bash
python start_server.py
```

### Step 3: New Terminal Tab - Start Frontend
```bash
cd backend && source venv/bin/activate && cd ..
python test_frontend.py
```

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
