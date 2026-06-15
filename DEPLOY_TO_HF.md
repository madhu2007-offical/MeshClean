# Deploy to Hugging Face Spaces

## Quick Deployment (3 steps)

### Step 1: Clone your HF Spaces repo
```bash
git clone https://huggingface.co/spaces/Madhu007official/MeshClean-Debugger meshclean-hf
cd meshclean-hf
```

### Step 2: Copy project files
```bash
# Copy all files from your local project to the HF Spaces repo
cp -r ../MeshCleanDebuggerEnv/* .
# Or on Windows PowerShell:
# Copy-Item -Recurse -Path ..\MeshCleanDebuggerEnv\* -Destination .
```

### Step 3: Push to HF Spaces
```bash
git add .
git commit -m "Deploy MeshClean Debugger"
git push
```

**Done!** Your Space will auto-build and deploy in 2-5 minutes.

---

## Verification

After pushing, check your Space at:
```
https://huggingface.co/spaces/Madhu007official/MeshClean-Debugger
```

You should see:
- Build log showing Dockerfile execution
- UI loading at the Space's public URL
- All 3 debug tasks operational

---

## Auto-Updates

From now on:
```bash
# In your local folder:
git push
# → HF Spaces auto-detects changes
# → Auto-rebuilds in 2-5 minutes
# → Updates live automatically
```

No need to manually trigger anything!

---

## Troubleshooting

**Issue:** Build fails with "Module not found"
- **Fix:** Ensure `requirements.txt` is in the root with all dependencies

**Issue:** Space won't load after build
- **Fix:** Check Space logs for Python errors, ensure `ui.py` has no syntax errors

**Issue:** Can't push to HF Spaces
- **Fix:** 
  ```bash
  # Auth with HF token
  huggingface-cli login
  # Then push again
  git push
  ```

**Issue:** Port issues
- **Fix:** HF Spaces automatically handles port management (uses 7860 or fallback)

---

## Space Settings (Optional)

In your HF Space Settings:
- **Runtime:** Docker (already detected from Dockerfile)
- **Public/Private:** Choose based on preference
- **Persistent Storage:** Not needed unless you save model outputs

---

## Monitoring Deployment

```bash
# Live log tail (if SSH access enabled)
# Or just watch the Build log in the Space UI
```

Your HF Space will show:
- ✅ Build Status (In Progress → Success)
- 📋 Build Logs (Real-time)
- 🌐 Public URL (Available after build completes)

---

**Status:** Ready to deploy whenever you run the 3 commands above!
