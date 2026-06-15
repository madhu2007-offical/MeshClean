# 🚀 MeshClean Debugger - Deployment Guide

Complete production deployment guide for **MeshClean Debugger Environment**.

---

## 📋 Table of Contents

1. [Local Setup](#1-local-setup)
2. [Docker Deployment](#2-docker-deployment)
3. [GitHub Setup](#3-github-setup)
4. [Hugging Face Spaces](#4-hugging-face-spaces-deployment)
5. [Auto-Update Flow](#5-auto-update-flow)
6. [Verification & Testing](#6-verification--testing)

---

## 1️⃣ Local Setup

### Requirements
- Python 3.11+
- Git
- ~500MB disk space

### Installation

```bash
# Clone or download the repository
git clone https://github.com/YOUR_USERNAME/meshclean-debugger.git
cd meshclean-debugger

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python start_ui.py
```

**Access:** http://localhost:7860

**Expected Output:**
```
============================================================
[*] MeshClean Pipeline Debugging Environment
============================================================

Starting Flask UI...
Listening on: http://localhost:7860

Press Ctrl+C to stop the server

 * Running on http://127.0.0.1:7860
```

---

## 2️⃣ Docker Deployment

### Prerequisites
- Docker installed ([Download](https://www.docker.com/products/docker-desktop))

### Build Docker Image

```bash
# Navigate to project directory
cd meshclean-debugger

# Build image
docker build -t meshclean-debugger:latest .

# Verify build
docker images | grep meshclean
```

### Run Docker Container

```bash
# Run container
docker run -p 7860:7860 meshclean-debugger:latest

# Or run in background
docker run -d -p 7860:7860 --name meshclean meshclean-debugger:latest

# View logs
docker logs -f meshclean

# Stop container
docker stop meshclean

# Remove container
docker rm meshclean
```

**Access:** http://localhost:7860

### Docker Compose (Optional - for scalability)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  meshclean:
    build: .
    ports:
      - "7860:7860"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with Docker Compose:
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

## 3️⃣ GitHub Setup

### Initialize Repository

```bash
# Navigate to project
cd meshclean-debugger

# Initialize git
git init

# Add all files
git add .

# Add .gitignore (create if not exists)
cat > .gitignore << EOF
venv/
__pycache__/
*.pyc
.env
.DS_Store
*.egg-info/
dist/
build/
EOF

# Initial commit
git commit -m "Initial commit: MeshClean Debugger"
```

### Connect to Remote Repository

```bash
# Create repo on GitHub first at https://github.com/new

# Add remote origin
git remote add origin https://github.com/YOUR_USERNAME/meshclean-debugger.git

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

### GitHub Files

Create these files in your repo root:

**`.github/workflows/docker-publish.yml`** (CI/CD Pipeline):

```yaml
name: Publish Docker

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t meshclean-debugger:latest .
      
      - name: Test image
        run: docker run --rm meshclean-debugger:latest python -c "from pipeline_debug_env import PipelineDebugEnv; print('✓ Image OK')"
```

**`CONTRIBUTING.md`**:

```markdown
# Contributing to MeshClean Debugger

## Development Setup

1. Clone repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes
4. Test locally: `python start_ui.py`
5. Commit: `git commit -m "Add feature"`
6. Push: `git push origin feature/your-feature`
7. Create Pull Request

## Testing

Before commit, ensure:
- No errors: `python start_ui.py` works
- Docker builds: `docker build -t meshclean:test .`
```

---

## 4️⃣ Hugging Face Spaces Deployment

### Step-by-Step

#### 1. Create Space on Hugging Face

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **Create new Space**
3. Fill in:
   - **Space name:** meshclean-debugger
   - **License:** Apache 2.0 (or your choice)
   - **Space SDK:** Docker
   - **Space hardware:** CPU (2-core, 8GB default)
4. Click **Create Space**

#### 2. Connect GitHub Repository

**Option A: Direct Git Connection (Recommended)**

```bash
# Clone the Space
git clone https://huggingface.co/spaces/YOUR_HF_USERNAME/meshclean-debugger
cd meshclean-debugger

# Copy your files here, then push
# Or set up automatic sync:
```

**Option B: GitHub Integration**

1. In Space settings, connect GitHub repository
2. Set branch to `main`
3. Check "Auto-sync from GitHub"
4. Space redeploys automatically on each push

#### 3. Docker Configuration

Hugging Face automatically:
- Reads your `Dockerfile`
- Builds the image
- Exposes port 7860
- Handles SSL/HTTPS

**Only ensure:**
- `EXPOSE 7860` in Dockerfile ✓
- ` CMD ["python", "start_ui.py"]` in Dockerfile ✓

#### 4. Add Files to Space

```bash
# If not synced from GitHub
git add -A
git commit -m "Add MeshClean Debugger"
git push

# Hugging Face rebuilds automatically
```

#### 5. Access Your Space

After deployment (~5 min):
- URL: `https://huggingface.co/spaces/YOUR_HF_USERNAME/meshclean-debugger`
- Direct app link: Click "App" button on Space page

---

## 5️⃣ Auto-Update Flow

### How It Works

```
Local Development
       ↓
   git push to GitHub
       ↓
(Optional) GitHub Actions CI checks
       ↓
   Push triggers webhook
       ↓
Hugging Face rebuilds & redeploys
       ↓
Live at HF Spaces URL
```

### Workflow

**1. Make changes locally:**
```bash
# Edit files
nano pipeline_debug_env/tasks.py

# Test
python start_ui.py
```

**2. Commit and push:**
```bash
git add .
git commit -m "Fix: improved error handling"
git push origin main
```

**3. Hugging Face auto-redeploys:**
- Detects push
- Rebuilds Docker image
- Redeploys in ~2-5 minutes
- Your live app updates automatically

**4. View deployment logs (HF Spaces):**
- Go to your Space
- Click "Logs" to see build output

### Preventing Bad Deployments

```bash
# Before pushing, always test locally
docker build -t meshclean:test .
docker run -p 7860:7860 meshclean:test

# Only if above works:
git push origin main
```

---

## 6️⃣ Verification & Testing

### Local Verification

```bash
# 1. Test Python imports
python -c "from pipeline_debug_env import PipelineDebugEnv; print('✓ Core imports OK')"

# 2. Test inference
python -c "from inference import DebugAgent; a = DebugAgent('task_1'); print('✓ Agent loads OK')"

# 3. Test UI locally
python start_ui.py
# Access: http://localhost:7860

# 4. Run all tasks
python -c "
from inference import DebugAgent
for task in ['task_1', 'task_2', 'task_3']:
    agent = DebugAgent(task)
    result = agent.run()
    print(f'✓ {task}: Grade={result[\"grade\"]:.1%}')
"
```

### Docker Verification

```bash
# Build and run
docker build -t meshclean:test .
docker run -p 7860:7860 --rm meshclean:test

# In another terminal, test
curl http://localhost:7860/task/task_1

# Expected: JSON response with task info
```

### Hugging Face Verification

1. Go to your Space URL
2. Change task selector → Should load task info
3. Click "Run Debugger" → Should see results
4. Check "Logs" for any errors

---

## 📊 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Local startup | < 2s | ✓ |
| Docker build | < 60s | ✓ |
| First request | < 3s | ✓ |
| Task execution | < 10s | ✓ |
| HF Spaces deploy | < 5 min | ✓ |

---

## 🆘 Troubleshooting

### Issue: Port already in use

```bash
# Find what's using port 7860
lsof -i :7860

# Kill the process (macOS/Linux)
kill -9 <PID>

# Or use different port
python -c "from ui_minimal import app; app.run(host='0.0.0.0', port=8000)"
```

### Issue: Docker build fails

```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker build --no-cache -t meshclean:latest .
```

### Issue: HF Spaces won't deploy

1. Check Dockerfile syntax: `docker build . --dry-run`
2. Check file paths in Dockerfile match your repo
3. Check Space logs for error messages
4. Ensure requirements.txt has all dependencies

### Issue: App runs but no output

```bash
# Check Flask environment
export FLASK_ENV=development
python start_ui.py
# More verbose output
```

---

## 📚 Additional Resources

- [Docker Docs](https://docs.docker.com/)
- [GitHub Docs](https://docs.github.com/)
- [Hugging Face Spaces Guide](https://huggingface.co/docs/hub/spaces)
- [Flask Deployment](https://flask.palletsprojects.com/deployment/)

---

## ✅ Deployment Checklist

- [ ] Local setup works (`python start_ui.py`)
- [ ] All imports pass (`python -c "from ...import..."`)
- [ ] Docker builds successfully (`docker build .`)
- [ ] Docker runs successfully (`docker run -p 7860:7860 ...`)
- [ ] GitHub repo created and pushed
- [ ] Hugging Face Space created
- [ ] Space synced with GitHub
- [ ] HF Spaces app loads at URL
- [ ] All 3 tasks work in UI
- [ ] Logs are clean (no errors)

---

**Status:** ✅ Production-Ready  
**Last Updated:** April 5, 2026
