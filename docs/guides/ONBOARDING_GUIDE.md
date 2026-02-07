# 🚀 Zero-Cost Content Factory - Complete Onboarding Guide

**Welcome to the AI YouTube Shorts Generator!** This document will help you understand the entire project from conception to current state.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Module Breakdown](#module-breakdown)
4. [Evolution Timeline (Phases 1-19)](#evolution-timeline)
5. [Setup Instructions](#setup-instructions)
6. [How to Use](#how-to-use)
7. [Configuration](#configuration)
8. [Key Features](#key-features)
9. [Troubleshooting](#troubleshooting)
10. [Production Workflow](#production-workflow)

---

## 🎯 Project Overview

### What Is This?

An **autonomous YouTube Shorts factory** that generates viral content from scratch:
- **Scripts**: AI-generated Dark Psychology content
- **Audio**: High-quality voiceovers with word-level sync
- **Visuals**: Stock videos + AI-generated image hooks
- **Assembly**: Professional video editing with captions, progress bars, effects
- **Upload**: Automatic YouTube publishing
- **Memory**: Prevents duplicate content

### The Goal

Create a **zero-cost content factory** that produces YouTube Shorts automatically, with:
- ✅ No manual editing required
- ✅ Viral-optimized content (hooks, loops, retention hacks)
- ✅ Quality control built-in
- ✅ Monetization-ready (comment generation)
- ✅ History tracking (no duplicates)

---

## 🏗️ System Architecture

### The Pipeline

```
┌─────────────┐
│   SCRIPT    │ → AI generates viral script (Dark Psychology niche)
│   ENGINE    │   - Creative Director prompts
│             │   - Adversarial editing (QA Protocol)
└─────────────┘
       ↓
┌─────────────┐
│   AUDIO     │ → Voice generation (Lean Cascade)
│   ENGINE    │   Priority 1: ElevenLabs (Premium)
│             │   Priority 2: Edge-TTS (Free)
│             │   Priority 3: Piper TTS (Local)
└─────────────┘
       ↓
┌─────────────┐
│   VISUAL    │ → Background video sourcing
│   ENGINE    │   Priority 1: Pexels API (Stock)
│             │   Priority 2: YouTube (Gameplay)
└─────────────┘
       ↓
┌─────────────┐
│   IMAGE     │ → AI image hook (Pollinations.ai)
│   ENGINE    │   - 3-second hook at start
└─────────────┘
       ↓
┌─────────────┐
│   QC        │ → Quality Control Inspector
│   ENGINE    │   - Silence removal
│             │   - Audio normalization (15dB balance)
│             │   - Speedup for pacing
└─────────────┘
       ↓
┌─────────────┐
│   RENDER    │ → Final video assembly
│   ENGINE    │   - Ken Burns effect (zoom)
│             │   - Word-level captions
│             │   - Progress bar
│             │   - Background music + SFX
└─────────────┘
       ↓
┌─────────────┐
│   UPLOAD    │ → YouTube publishing
│   ENGINE    │   - Automatic upload
│             │   - Public status
└─────────────┘
       ↓
┌─────────────┐
│   HISTORY   │ → Memory system
│   ENGINE    │   - Prevents duplicates
│             │   - Tracks all videos
└─────────────┘
```

### Lean Cascade Architecture

The system uses a **"Lean Cascade"** approach - it tries premium services first, then falls back to free/unstoppable alternatives:

- **Audio**: ElevenLabs → Edge-TTS → Piper TTS
- **Visuals**: Pexels API → YouTube downloads
- **Images**: Pollinations.ai (no API key needed)

**Why?** Ensures the factory **never stops** - even if APIs fail or keys expire.

---

## 📦 Module Breakdown

### 1. `modules/script_engine.py` - The Creative Director

**Purpose**: Generates viral YouTube Short scripts

**Key Functions**:
- `generate_draft_script()`: Creates initial script (Creative Director prompts)
- `polish_script()`: Adversarial editing (QA Protocol)
- `generate_script()`: Main entry point (draft → polish → return)

**Features**:
- **Creative Director Mode**: AI acts as elite YouTube strategist
- **Adversarial Editing**: Script Editor critiques and rewrites
- **Tone Injection**: Random tones (Aggressive, Conspiratorial, Scientific, Urgent)
- **Infinite Loop**: Scripts loop seamlessly (last sentence → first sentence)
- **History Check**: Prevents duplicate topics

**Output**: JSON with `title`, `script`, `tags`, `pacing`

---

### 2. `modules/audio_engine.py` - The Voice Factory

**Purpose**: Generates high-quality voiceovers with perfect word sync

**Key Functions**:
- `generate_audio()`: Main entry point (Lean Cascade)
- `_generate_audio_elevenlabs()`: Premium TTS (Priority 1)
- `_generate_audio_edge_tts_async()`: Free TTS with word timestamps (Priority 2)
- `_generate_audio_piper()`: Local TTS (Priority 3)
- `mix_background_music()`: Adds music and sound effects

**Features**:
- **Word-Level Timestamps**: Perfect subtitle synchronization
- **Background Music**: Automatic mixing (15dB ducking)
- **Sound Effects**: Whoosh (start) + Pop (every 5th word)
- **Smart Subtitles**: Calculated timing if timestamps unavailable

**Output**: MP3 file + JSON subtitles with word timings

---

### 3. `modules/visual_engine.py` - The Visual Sourcer

**Purpose**: Sources and processes background video clips

**Key Functions**:
- `get_visual_content()`: Main entry point (Lean Cascade)
- `_get_pexels_video()`: Stock video from Pexels API (Priority 1)
- `get_gameplay_clip()`: YouTube gameplay videos (Priority 2)

**Features**:
- **1080p HD**: Strict quality requirements
- **Vertical Format**: 1080x1920 (9:16) for Shorts
- **Clip Cycling**: Multiple segments for visual variety (>20s videos)
- **Pacing Integration**: Speedup for "Fast" pacing scripts
- **Duration Filter**: Skips videos >10 minutes

**Output**: Processed MP4 video (1080x1920, muted, looped)

---

### 4. `modules/image_engine.py` - The Hook Generator

**Purpose**: Creates AI-generated image hooks

**Key Functions**:
- `generate_image_hook()`: Creates hook image from topic

**Features**:
- **Pollinations.ai**: No API key required
- **Cinematic Prompts**: Hyper-realistic, 8k, dramatic lighting
- **Vertical Format**: 1080x1920 for Shorts

**Output**: JPG image (displayed for first 3 seconds)

---

### 5. `modules/qc_engine.py` - The Quality Inspector

**Purpose**: Detects and fixes audio/visual defects

**Key Functions**:
- `remove_silence()`: Removes silence >300ms (Piper TTS)
- `normalize_audio_mix()`: Balances voice/music (15dB difference)
- `apply_speedup()`: Applies 1.1x speedup for pacing

**Features**:
- **Silence Killer**: Creates "tight" audio
- **Perfect Balance**: Music always 15dB quieter than voice
- **Pacing Control**: Speedup for "Fast" scripts

**Output**: Processed audio file

---

### 6. `modules/render_engine.py` - The Video Assembler

**Purpose**: Assembles final video from all components

**Key Functions**:
- `assemble_video()`: Main assembly function

**Features**:
- **Image Hook**: 3-second AI image at start
- **Ken Burns Effect**: Subtle zoom (1.0x → 1.05x)
- **Word-Level Captions**: Karaoke-style, word-by-word
- **Progress Bar**: Red animated bar (retention hack)
- **M1 Hardware Acceleration**: `h264_videotoolbox` for speed

**Output**: Final MP4 video (1080x1920, 30fps, high bitrate)

---

### 7. `modules/upload_engine.py` - The Publisher

**Purpose**: Uploads videos to YouTube

**Key Functions**:
- `upload_video()`: Main upload function

**Features**:
- **OAuth2 Authentication**: Google Cloud credentials
- **Public Status**: Required for Shorts
- **Progress Tracking**: Shows upload percentage
- **Metadata**: Title, description, tags, category

**Output**: YouTube video ID and URL

---

### 8. `modules/history_engine.py` - The Memory System

**Purpose**: Tracks videos to prevent duplicates

**Key Functions**:
- `has_topic_been_used()`: Checks if topic exists
- `log_video()`: Logs video to history
- `get_recent_topics()`: Retrieves recent topics

**Features**:
- **Duplicate Prevention**: Checks before generation
- **Persistent Storage**: `history.json` file
- **Topic Tracking**: Uses title as identifier

**Output**: History file (`history.json`)

---

## 📅 Evolution Timeline (Phases 1-19)

### Phase 1-3: Foundation
- Built core modules (script, audio, visual engines)
- Basic video assembly

### Phase 4: Final Assembly
- Render engine with captions
- Upload engine with OAuth
- Main controller orchestration

### Phase 7: Perfect Sync
- Word-level timestamping (Edge-TTS WordBoundary events)
- Perfect subtitle synchronization

### Phase 8: Viral Upgrade
- Visual overstimulation (clip cycling)
- Karaoke-style captions
- Sound effects (ear candy)
- Draft mode (manual review)

### Phase 9-10: Audio Reliability
- Switched to Piper TTS (local, unstoppable)
- Smart subtitle calculation
- SSL certificate fixes

### Phase 11: Retention & Money
- Red progress bar (retention hack)
- Infinite loop scripting
- Monetization comment generation

### Phase 13: Assistant Mode
- Clipboard automation
- Voice alerts (Mac)
- Config-based comments

### Phase 14: Lean Cascade
- ElevenLabs integration (Priority 1)
- Edge-TTS fallback (Priority 2)
- Pexels API integration
- Image hook generation

### Phase 15: Creative Director
- Strategic script prompts
- Machiavellian tone
- Non-obvious angles

### Phase 16: Production Mode
- Auto-upload enabled
- Post-upload assistant mode

### Phase 17: Adversarial Script Engine
- Draft → Polish pipeline
- QA Protocol
- Tone injection (variation)

### Phase 18: QC Inspector
- Silence removal
- Audio normalization
- Ken Burns effect
- Pacing-based speedup

### Phase 19: History Tracker
- Duplicate prevention
- Video logging
- Production mode re-enabled

---

## 🛠️ Setup Instructions

### Prerequisites

- **Python 3.11+**
- **FFmpeg** (for video processing)
- **Google Cloud Project** (for YouTube API)
- **API Keys** (optional but recommended):
  - ElevenLabs (for premium audio)
  - Pexels (for stock videos)
  - Gemini/Groq (for script generation)

### Installation

1. **Clone/Navigate to Project**:
   ```bash
   cd AI-Youtube-Shorts-Generator
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download Piper Voice Model** (if using local TTS):
   ```bash
   # Model will auto-download on first run, or manually:
   mkdir -p ~/.local/share/piper/voices/en_US-lessac-medium
   curl -L -o ~/.local/share/piper/voices/en_US-lessac-medium/en_US-lessac-medium.onnx \
     https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
   ```

4. **Configure Environment**:
   Create `.env` file:
   ```env
   # LLM APIs (Required)
   GEMINI_API_KEY=your_gemini_key
   GROQ_API_KEY=your_groq_key
   
   # Premium Services (Optional)
   ELEVENLABS_API_KEY=your_elevenlabs_key
   PEXELS_API_KEY=your_pexels_key
   ```

5. **YouTube API Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create project → Enable YouTube Data API v3
   - Create OAuth 2.0 credentials
   - Download `client_secrets.json` → Place in project root

6. **Create Asset Directories** (Optional):
   ```bash
   mkdir -p assets/music assets/sfx fonts config
   ```

7. **Configure Monetization**:
   Edit `config/monetization.json`:
   ```json
   {
     "safe_link": "https://your-monetization-link.com",
     "comments": [
       "Your comment template 1 with {link} placeholder",
       "Your comment template 2 with {link} placeholder"
     ]
   }
   ```

---

## 🎬 How to Use

### Basic Usage

```bash
python main.py
```

**What Happens**:
1. ✅ Checks history for duplicates
2. ✅ Generates script (draft → polish)
3. ✅ Generates AI image hook
4. ✅ Creates audio (Lean Cascade)
5. ✅ Sources background video
6. ✅ QC processing (silence removal, normalization)
7. ✅ Assembles final video
8. ✅ Uploads to YouTube
9. ✅ Logs to history
10. ✅ Copies monetization comment to clipboard

### Output

- **Video**: `final_short.mp4` (1080x1920, ~30 seconds)
- **History**: `history.json` (tracks all videos)
- **YouTube**: Video published and public
- **Clipboard**: Monetization comment ready to paste

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Required | Purpose |
|----------|----------|---------|
| `GEMINI_API_KEY` | Yes | Script generation (Primary) |
| `GROQ_API_KEY` | Yes | Script generation (Fallback) |
| `ELEVENLABS_API_KEY` | No | Premium audio (Priority 1) |
| `PEXELS_API_KEY` | No | Stock videos (Priority 1) |

### Config Files

**`config/monetization.json`**:
```json
{
  "safe_link": "https://your-link.com",
  "comments": [
    "Template 1 with {link}",
    "Template 2 with {link}"
  ]
}
```

**`history.json`** (Auto-generated):
```json
[
  {
    "topic": "Script content...",
    "title": "Video Title",
    "video_id": "youtube_id",
    "filename": "final_short.mp4",
    "date": "2025-12-11T..."
  }
]
```

### Asset Directories

- **`assets/music/`**: Background music MP3 files
- **`assets/sfx/`**: Sound effects (`whoosh.mp3`, `pop.mp3`)
- **`fonts/`**: Auto-downloaded fonts (Impact, Roboto-Bold)

---

## ✨ Key Features

### 1. Lean Cascade Architecture
- **Never Stops**: Falls back through priorities
- **Premium When Available**: Uses best services first
- **Free Fallbacks**: Always works without API keys

### 2. Quality Control (QC Inspector)
- **Silence Removal**: Tight audio (no dead air)
- **Audio Normalization**: Perfect voice/music balance
- **Pacing Control**: Speedup for fast scripts

### 3. Viral Optimization
- **Hooks**: 3-second AI image + shocking first line
- **Loops**: Scripts loop seamlessly
- **Progress Bar**: Red animated bar (retention hack)
- **Captions**: Word-level karaoke style

### 4. Memory System
- **Duplicate Prevention**: Checks history before generation
- **Retry Logic**: Up to 3 attempts for unique topics
- **Full Tracking**: All videos logged with metadata

### 5. Adversarial Script Engine
- **Draft → Polish**: Two-stage quality assurance
- **Tone Variation**: Random tones prevent monotony
- **Strategic Prompts**: Creative Director + Editor

### 6. Assistant Mode
- **Clipboard Automation**: Comment copied automatically
- **Voice Alerts**: Mac notifications
- **Monetization Ready**: Pre-formatted comments

---

## 🔧 Troubleshooting

### Common Issues

**1. "Piper voice model not found"**
- **Fix**: Model auto-downloads on first run, or download manually (see Setup)

**2. "Edge-TTS failed: No audio received"**
- **Fix**: System automatically falls back to Piper TTS (local)

**3. "client_secrets.json not found"**
- **Fix**: Download from Google Cloud Console → Place in project root

**4. "Script generation failed"**
- **Fix**: Check `GEMINI_API_KEY` and `GROQ_API_KEY` in `.env`

**5. "Upload failed: Authentication error"**
- **Fix**: Delete `token.json` → Re-run (will open browser for OAuth)

**6. "Video is blurry"**
- **Fix**: Visual engine uses 1080p filter, but some sources may be lower quality

**7. "Captions not visible"**
- **Fix**: Fonts auto-download, but if missing, check `fonts/` directory

---

## 🎯 Production Workflow

### Daily Production

1. **Run Factory**:
   ```bash
   python main.py
   ```

2. **Monitor Output**:
   - Check terminal for errors
   - Verify video uploaded successfully
   - Check YouTube URL

3. **Post-Upload Tasks**:
   - Paste monetization comment (from clipboard)
   - Pin comment on video
   - Monitor performance in YouTube Studio

### Batch Production

For multiple videos, run in a loop:
```bash
for i in {1..5}; do
  echo "Generating video $i..."
  python main.py
  sleep 60  # Wait 1 minute between videos
done
```

### Quality Control

- **Review History**: Check `history.json` for duplicates
- **Check Videos**: Review `final_short.mp4` before publishing
- **Monitor Performance**: Track views, engagement in YouTube Studio

---

## 📊 Current System Status

### ✅ Working Features

- ✅ Script generation (Creative Director + QA Protocol)
- ✅ Audio generation (Lean Cascade: ElevenLabs → Edge-TTS → Piper)
- ✅ Visual sourcing (Pexels → YouTube)
- ✅ Image hooks (Pollinations.ai)
- ✅ QC processing (silence removal, normalization)
- ✅ Video assembly (Ken Burns, captions, progress bar)
- ✅ Auto-upload (YouTube)
- ✅ History tracking (duplicate prevention)
- ✅ Assistant mode (clipboard + voice alerts)

### 🎯 Production Ready

- **Niche**: Dark Psychology (hardcoded for monetization)
- **Format**: YouTube Shorts (1080x1920, vertical)
- **Duration**: 30-60 seconds
- **Quality**: 1080p HD, high bitrate
- **Privacy**: Public (required for Shorts)

---

## 🚀 Next Steps for New Recruits

1. **Read This Guide**: Understand the architecture
2. **Set Up Environment**: Follow Setup Instructions
3. **Run Test Video**: `python main.py` (verify everything works)
4. **Review History**: Check `history.json` to see past videos
5. **Monitor Production**: Watch YouTube channel for new uploads
6. **Optimize**: Adjust prompts, pacing, or QC settings as needed

---

## 📝 Important Notes

### API Rate Limits

- **Gemini**: Free tier has limits
- **Groq**: Fast but may have rate limits
- **ElevenLabs**: Pay-per-use (check quota)
- **Pexels**: Free tier available

### Best Practices

1. **Monitor History**: Check for duplicates before long runs
2. **Review Videos**: Quality check before publishing
3. **Update Comments**: Keep monetization comments fresh
4. **Track Performance**: Monitor YouTube Analytics
5. **Backup History**: Keep `history.json` backed up

### Safety Features

- **Draft Mode**: Can disable uploads for testing
- **History Check**: Prevents duplicate content
- **Error Handling**: Graceful fallbacks at every step
- **QC Inspector**: Automatic quality checks

---

## 🎓 Learning Resources

### Key Technologies

- **MoviePy**: Video editing library
- **yt-dlp**: YouTube video downloading
- **pydub**: Audio processing
- **edge-tts**: Free TTS with timestamps
- **piper-tts**: Local TTS (unstoppable)
- **Google APIs**: YouTube Data API v3, Gemini

### Code Structure

- **Modular Design**: Each engine is independent
- **Lean Cascade**: Priority-based fallbacks
- **Error Handling**: Try/except at every level
- **Logging**: Clear status messages

---

## 📞 Support

### If Something Breaks

1. **Check Logs**: Terminal output shows errors
2. **Verify API Keys**: Ensure `.env` is configured
3. **Check Dependencies**: Run `pip install -r requirements.txt`
4. **Review History**: Check `history.json` for issues
5. **Test Components**: Run individual modules to isolate issues

### Common Fixes

- **Re-authenticate YouTube**: Delete `token.json` → Re-run
- **Update Dependencies**: `pip install --upgrade -r requirements.txt`
- **Clear Temp Files**: Delete `temp_*.mp3`, `temp_*.mp4`
- **Reset History**: Delete `history.json` (if needed)

---

## 🎉 Welcome to the Team!

You're now ready to operate the **Zero-Cost Content Factory**. This system has been built through 19 phases of iteration, each adding new capabilities and reliability.

**Remember**: The factory is designed to be **unstoppable** - it will always find a way to produce content, even if premium services fail.

**Good luck, and happy content creation!** 🚀

---

*Last Updated: Phase 19 - History Tracker & Production Launch*
*Version: 1.0 (Production Ready)*

