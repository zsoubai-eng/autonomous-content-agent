# 🔍 Duplicate Detection Issue - Explained

**Date:** January 10, 2026

---

## 🎯 **THE PROBLEM**

7 out of 8 videos failed to generate because the duplicate detection system is **too strict** and marks everything as duplicates, even when stories are different.

---

## 🔍 **HOW DUPLICATE DETECTION WORKS**

### **1. Two-Stage Process:**

#### **Stage 1: Scraping Stories (horror_story_scraper.py)**
- Scrapes Reddit for horror stories
- Checks each scraped story title against `PUBLISHED_TITLES` list
- Checks against `history.json` titles
- If ALL scraped stories match published ones → "All stories are duplicates"

#### **Stage 2: LLM Generation (horror_story_engine.py)**
- If scraping fails (all duplicates), falls back to LLM (Cerebras/Gemini/Groq)
- LLM generates a new story and title
- Title is checked with `is_duplicate_title()` function
- If duplicate → Retry (up to 10 times)

---

## ❌ **THE ISSUES**

### **Issue 1: Semantic Similarity Too Strict**

The `is_duplicate_title()` function (lines 135-176 in `daily_content_generator.py`) uses **word overlap detection**:

```python
# If 2+ significant words overlap, likely duplicate
if len(overlap) >= 2:
    return True
```

**Problem:** This catches stories that share common themes but are actually different:

**Examples:**
- "Winter's Chill" vs "Winter's Cold Case" → **2 words overlap** ("winter", "cold") → Marked as duplicate ❌
- "Winter's Dark" vs "Winter's Dark Secret" → **2 words overlap** ("winter", "dark") → Marked as duplicate ❌
- "New Year's Eve Disappearance" vs "Christmas Eve Disappearance" → **1 word overlap** ("eve", "disappearance") → Might be OK, but "disappearance" is significant → Could be duplicate ❌

**Real Problem:** Many horror stories share common words:
- "Winter", "Dark", "Chill", "Disappearance", "Mystery", "Vanishing"
- Stories about winter mysteries will naturally share words
- But they can be completely different stories!

---

### **Issue 2: Common Words List Incomplete**

The common words list excludes some words but might miss others:

```python
common_words = {'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'and', 'or', 'but', 'story', 'stories', 'horror', 'mystery', 'mysteries', 'true', 'real', 'unsolved', 'shocking', 'case', 'incident'}
```

**Problem:**
- "Disappearance", "vanishing", "chill", "dark" are NOT in common words
- These are significant words that many horror stories share
- Two different winter stories will share "winter" + "disappearance" → Marked as duplicate ❌

---

### **Issue 3: Scraper Filtering Too Aggressive**

The scraper (line 120 in `daily_content_generator.py`) filters stories:

```python
if not any(published.lower() in title.lower() for published in PUBLISHED_TITLES):
```

**Problem:**
- Uses substring matching: `"Winter" in "Winter's Chill"` → True
- If you published "Winter's Chill", any story with "Winter" gets filtered
- Even unrelated winter stories get rejected

---

### **Issue 4: Limited Story Pool**

From logs:
- Only 10 curated stories available
- Scraping finds 10 stories from Reddit
- Total: 10-20 stories to choose from
- If all match published ones → No stories available

**Problem:**
- Small pool of stories
- After filtering duplicates, pool shrinks to zero
- System can't find any unique stories

---

## 📊 **WHAT THE LOGS SHOW**

```
⚠️ All stories are duplicates (attempt 1/10), trying different selection...
⚠️ All stories are duplicates (attempt 2/10), trying different selection...
...
⚠️ All available stories are duplicates after 10 attempts
⚠️ Scraping found only duplicates, falling back to LLM generation...
🧠 Generating horror story with Cerebras...
✓ Horror story generated with Cerebras
⚠️ Duplicate title detected: Winter's Chill, retrying...
```

**Pattern:**
1. Scraping finds 10 stories
2. ALL marked as duplicates (too strict filtering)
3. Falls back to LLM generation
4. LLM generates "Winter's Chill"
5. `is_duplicate_title()` checks: "Winter's Chill" vs published titles
6. Finds overlap with "Winter's Chill" (already published) or "Winter's Cold Case" (2-word overlap)
7. Marks as duplicate ❌
8. Retries... but LLM keeps generating similar winter-themed titles
9. After 10 retries → FAILED

---

## ✅ **WHY ONE VIDEO SUCCEEDED**

"Winter's Vanishing (UNSOLVED)" succeeded because:
- It's semantically different enough from published titles
- Word overlap: "winter" (1 word) or "vanishing" (1 word, but not in other titles)
- Didn't trigger the 2-word overlap threshold
- Made it through the duplicate check

---

## 🔧 **THE ROOT CAUSE**

**The duplicate detection is designed to prevent:**
- Exact duplicates: "The Roanoke Colony" vs "The Roanoke Colony" ✅ Good
- Very similar titles: "Winter's Chill" vs "Winter's Chill (TRUE STORY)" ✅ Good

**But it's also catching:**
- Different stories with shared themes: "Winter's Chill" vs "Winter's Dark Secret" ❌ Bad
- Different stories with common words: "Winter Disappearance" vs "Christmas Eve Disappearance" ❌ Bad

**Result:** System can't find any "unique" stories because everything shares common horror/winter words.

---

## 💡 **SOLUTIONS**

### **Option 1: Relax Word Overlap Threshold**
Change from 2 words to 3+ words:
```python
# If 3+ significant words overlap, likely duplicate (instead of 2+)
if len(overlap) >= 3:
    return True
```

### **Option 2: Add More Common Words**
Add genre-specific words to common words list:
```python
common_words = {..., 'winter', 'disappearance', 'vanishing', 'chill', 'dark', 'mystery', 'case', 'eve', 'night', 'frozen', ...}
```

### **Option 3: Use Exact/High Similarity Only**
Only flag exact matches or very high similarity (4+ words):
```python
# Only flag if 4+ significant words overlap (very similar)
if len(overlap) >= 4:
    return True
```

### **Option 4: Allow Similar Themes, Different Stories**
Focus on unique story identifiers (names, locations, dates):
- "Winter's Chill" vs "Winter's Dark Secret" → Different stories, allow both
- "The Roanoke Colony" vs "The Roanoke Mystery" → Same story, block

---

## 📋 **SUMMARY**

**The duplicate detection is too strict because:**
1. ✅ 2-word overlap catches different stories with shared themes
2. ✅ Common words list doesn't include genre-specific words
3. ✅ Scraper filtering uses substring matching (too broad)
4. ✅ Small story pool gets exhausted quickly
5. ✅ LLM keeps generating similar titles (winter-themed)

**Result:** System marks everything as duplicates and can't generate unique content.

**Solution:** Relax the duplicate detection (3+ word overlap, more common words, or exact matches only).
