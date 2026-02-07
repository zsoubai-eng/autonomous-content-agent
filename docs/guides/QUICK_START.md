# ⚡ Quick Start Guide

**For new team members who want to get started immediately.**

---

## 🚀 5-Minute Setup

### 1. Install Dependencies
```bash
cd AI-Youtube-Shorts-Generator
pip install -r requirements.txt
```

### 2. Configure API Keys
Create `.env` file:
```env
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
ELEVENLABS_API_KEY=your_key  # Optional
PEXELS_API_KEY=your_key      # Optional
```

### 3. Setup YouTube API
- Download `client_secrets.json` from Google Cloud Console
- Place in project root

### 4. Run Factory
```bash
python main.py
```

**That's it!** The factory will:
- ✅ Generate script
- ✅ Create audio + visuals
- ✅ Assemble video
- ✅ Upload to YouTube
- ✅ Log to history

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `main.py` | Main controller (orchestrates everything) |
| `modules/script_engine.py` | Generates scripts |
| `modules/audio_engine.py` | Creates voiceovers |
| `modules/visual_engine.py` | Sources background videos |
| `modules/render_engine.py` | Assembles final video |
| `modules/upload_engine.py` | Uploads to YouTube |
| `modules/history_engine.py` | Prevents duplicates |
| `modules/qc_engine.py` | Quality control |
| `config/monetization.json` | Comment templates |
| `history.json` | Video tracking (auto-generated) |

---

## 🎯 Common Commands

```bash
# Generate and upload one video
python main.py

# Check history
cat history.json

# View recent videos
python -c "from modules.history_engine import get_recent_topics; print(get_recent_topics(5))"

# Test individual module
python -c "from modules.script_engine import generate_script; print(generate_script())"
```

---

## ⚙️ Configuration Quick Reference

### `.env` File
```env
# Required
GEMINI_API_KEY=...
GROQ_API_KEY=...

# Optional (for premium features)
ELEVENLABS_API_KEY=...
PEXELS_API_KEY=...
```

### `config/monetization.json`
```json
{
  "safe_link": "https://your-link.com",
  "comments": ["Template with {link}"]
}
```

---

## 🔍 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "API key not found" | Check `.env` file exists |
| "client_secrets.json not found" | Download from Google Cloud Console |
| "Piper voice model not found" | Auto-downloads on first run |
| "Upload failed" | Delete `token.json` → Re-run (re-authenticate) |
| "Script generation failed" | Check `GEMINI_API_KEY` and `GROQ_API_KEY` |

---

## 📊 System Status Check

```bash
# Check if everything is configured
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('Gemini:', '✓' if os.getenv('GEMINI_API_KEY') else '✗')
print('Groq:', '✓' if os.getenv('GROQ_API_KEY') else '✗')
print('ElevenLabs:', '✓' if os.getenv('ELEVENLABS_API_KEY') else '✗ (optional)')
print('Pexels:', '✓' if os.getenv('PEXELS_API_KEY') else '✗ (optional)')
print('client_secrets.json:', '✓' if os.path.exists('client_secrets.json') else '✗')
"
```

---

## 🎬 Production Workflow

1. **Run**: `python main.py`
2. **Wait**: Factory generates and uploads video
3. **Copy**: Monetization comment (auto-copied to clipboard)
4. **Paste**: Comment on YouTube video
5. **Pin**: Pin the comment for maximum engagement

---

## 📚 Full Documentation

For complete details, see: **`ONBOARDING_GUIDE.md`**

---

*Last Updated: Phase 19*

