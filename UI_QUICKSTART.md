# MeshClean UI - Quick Start Guide

## Status: ✓ RUNNING

Your MeshClean web interface is now active and accessible!

---

## 🌐 How to Access

**URL:** `http://localhost:7860`

Open this link in your web browser to access the MeshClean interface.

---

## 🚀 How to Start the UI

### Option 1: Quick Start (Recommended)
```bash
python start_ui.py
```

### Option 2: Direct Start
```bash
python ui.py
```

### Option 3: Using Gradio CLI
```bash
gradio ui.py
```

---

## 🔧 Using the Interface

1. **Select Task**
   - Choose from Easy, Medium, or Hard difficulty
   - Easy: Simple 3-node pipeline
   - Medium: Multi-stage 7-node ETL
   - Hard: Complex DAG with decoy errors

2. **Run Session**
   - Click "Run Debugging Session" button
   - Wait for automated agent to complete

3. **View Results**
   - **Execution Log**: See step-by-step actions and rewards
   - **Summary**: Final prediction, grade, and accuracy

---

## 📊 What You'll See

### Execution Log Example
```
[STEP 1] action=inspect_node(A_source) reward=+0.20 total_reward=+0.20
[STEP 2] action=check_schema(A_source) reward=+0.10 total_reward=+0.30
[STEP 3] action=move_to_parent(B_processor) reward=+0.20 total_reward=+0.50
[STEP 4] action=submit_root_cause(A_source) reward=+1.00 total_reward=+1.50
```

### Summary Example
```
╔════════════════════════════════════════╗
║    DEBUGGING SESSION SUMMARY           ║
╠════════════════════════════════════════╣
║ Task:           task_1                 ║
║ Steps Taken:    4                      ║
║ Total Reward:   1.50                   ║
║ Predicted Root: A_source               ║
║ Correct Root:   A_source               ║
║ Result:         CORRECT                ║
║ Grade:          1.00 / 1.00            ║
╚════════════════════════════════════════╝
```

---

## 🛑 How to Stop the Server

Press **Ctrl+C** in the terminal where you started the UI.

You'll see:
```
Server stopped.
```

---

## 🐛 Troubleshooting

### Port Already in Use
If you get "Address already in use" error:
1. Find and kill the existing process:
   ```bash
   netstat -ano | findstr :7860
   taskkill /PID <PID> /F
   ```
2. Restart the UI

### Permission Denied
Make sure you're in the correct directory:
```bash
cd C:\Users\madhu\OneDrive\Documents\MeshCleanDebuggerEnv
```

### Module Not Found
Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📝 Testing the System

To verify everything works without the UI:
```bash
python test_system.py
```

---

## 🎓 How It Works

1. **Task Creation**: Dynamic error injection at random node
2. **Agent Exploration**: Automated reasoning over DAG
3. **Error Propagation**: Errors flow downstream from root cause
4. **Grading**: Distance-based scoring on predictions
5. **Feedback**: Logs show each step and reward

---

## 📚 Documentation

- System Design: See `SYSTEM_DESIGN.md` (if created)
- API Reference: In `pipeline_debug_env/__init__.py`
- OpenEnv Spec: See `openenv.yaml`

---

**Last Updated:** April 5, 2026
**Status:** Production Ready ✓
