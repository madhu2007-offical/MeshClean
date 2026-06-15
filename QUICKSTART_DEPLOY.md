# 🚀 QUICK START - Deployment Commands

## Local Deployment

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/meshclean-debugger.git
cd meshclean-debugger

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run locally
python start_ui.py

# Access: http://localhost:7860
```

## Docker Deployment

```bash
# 1. Build image
docker build -t meshclean-debugger:latest .

# 2. Run container
docker run -p 7860:7860 meshclean-debugger:latest

# Access: http://localhost:7860
```

## GitHub Setup

```bash
# 1. Initialize repo
git init
git add .
git commit -m "Initial commit"

# 2. Add remote (create repo on GitHub first)
git remote add origin https://github.com/YOUR_USERNAME/meshclean-debugger.git
git branch -M main
git push -u origin main
```

## Hugging Face Spaces (Auto-Deploy)

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Select "Docker" SDK
4. Connect your GitHub repo (or upload files)
5. Space deploys automatically
6. Access at: `https://huggingface.co/spaces/YOUR_USERNAME/meshclean-debugger`

---

## Files Included

- **requirements.txt** - All dependencies (production-ready versions)
- **Dockerfile** - Production Docker image (Python 3.11-slim)
- **.dockerignore** - Optimizes Docker build size
- **.gitignore** - Git ignore patterns
- **DEPLOYMENT.md** - Complete deployment guide
- **deploy.sh** - Interactive deployment script

---

## Production Checklist

- [ ] `requirements.txt` has all dependencies
- [ ] `Dockerfile` builds without errors
- [ ] Local run works: `python start_ui.py`
- [ ] Docker run works: `docker run -p 7860:7860 meshclean:latest`
- [ ] GitHub repo created and synced
- [ ] Hugging Face Space created
- [ ] Auto-updates working (git push triggers deploy)

---

## Support

See **DEPLOYMENT.md** for:
- Detailed setup instructions
- Troubleshooting guide
- Performance metrics
- Auto-update workflow

---

**Status:** ✅ Production-Ready
