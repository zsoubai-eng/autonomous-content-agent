# 🔍 Internal Audit Report - Video Generation Issues

**Date:** December 28, 2025  
**Issues Identified:** 4 Critical Problems

---

## ❌ Issue 1: Images Not Displaying

**Root Cause:**
- Unsplash API/Source is failing → falling back to dark placeholder
- Placeholder is just a dark gradient (no actual image content)
- The `make_animated_frame` function is working, but it's animating a placeholder instead of a real image

**Evidence:**
- Log shows: "⚠️ Using dark placeholder image (no text)..."
- Image file exists but is just a dark gradient background
- No actual horror-related image content

**Fix Required:**
1. Improve image download reliability
2. Add better fallback image sources
3. Ensure actual images are downloaded, not just placeholders

---

## ❌ Issue 2: Subtitles Too Huge

**Root Cause:**
- Font size set to 120px (expert recommendation was 110-140px range)
- This is too large for 1080x1920 vertical format
- Should be 70-85px for optimal readability

**Current Code:**
```python
'font_size': 120,  # Too large!
```

**Fix Required:**
- Reduce to 75-80px for better balance

---

## ❌ Issue 3: No Video Organization

**Root Cause:**
- Videos are saved directly to project root
- No folder structure for organization
- Files get cluttered

**Fix Required:**
- Create `output/shorts/` folder
- Organize by date or batch
- Clean filename with story title

---

## ❌ Issue 4: Title Not Displayed in Video

**Root Cause:**
- Story title is not rendered as text overlay in video
- Only hook, subtitles, and badge are shown
- Title should appear at the beginning or as overlay

**Fix Required:**
- Add title text overlay (first 3-5 seconds)
- Or display title in a corner throughout video

---

## 🔧 Fixes to Implement

1. **Reduce subtitle font size** from 120px → 75px
2. **Create output folder structure** (`output/shorts/YYYY-MM-DD/`)
3. **Add title overlay** to video
4. **Improve image download** with better fallbacks
5. **Simplify image processing** (remove unnecessary complexity)

---

**Status:** Fixes being implemented now...
