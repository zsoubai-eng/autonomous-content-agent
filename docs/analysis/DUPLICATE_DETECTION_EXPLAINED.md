# 🔍 Duplicate Detection Issue - Complete Explanation

**Date:** January 10, 2026

---

## 🎯 **THE PROBLEM**

7 out of 8 videos failed to generate because the duplicate detection system marks everything as duplicates, even when stories are actually different.

---

## 🔍 **HOW IT WORKS (Two-Stage Process)**

### **Stage 1: Scraping Stories**

1. System scrapes Reddit for 10-20 horror stories
2. Checks each story title against:
   - `PUBLISHED_TITLES` list (hardcoded list)
   - `history.json` (all previously published titles)
3. If **ALL** scraped stories match published ones → "All stories are duplicates"
4. Falls back to LLM generation

### **Stage 2: LLM Generation**

1. If scraping fails, uses LLM (Cerebras/Gemini/Groq) to generate new story
2. LLM generates a title (e.g., "Winter's Chill")
3. Title is checked with `is_duplicate_title()` function
4. If duplicate → Retry (up to 10 times)
5. After 10 failures → Video generation fails ❌

---

## ❌ **THE THREE CHECKS (In Order)**

The `is_duplicate_title()` function in `daily_content_generator.py` (lines 135-176) does three checks:

### **Check 1: Substring Matching (TOO STRICT - THE MAIN PROBLEM)**

```python
if title_lower in published.lower() or published.lower() in title_lower:
    return True  # EXITS IMMEDIATELY
```

**Problem:** This uses simple substring matching, which is way too broad.

**Examples:**

1. **"Winter's Chill" vs "Winter's Chill (TRUE STORY)"**
   - Check: `"winter's chill" in "winter's chill (true story)"` → **TRUE** ❌
   - Result: Marked as duplicate (even though it's the same story, just with suffix)

2. **"Winter's Chill" vs "Winter's Cold Case"**
   - Check: `"winter's" in "winter's cold case"` → **TRUE** ❌
   - Result: Marked as duplicate (but these are DIFFERENT stories!)

3. **"Winter Disappearance" vs "Winter's Chilling Disappearance"**
   - Check: `"winter" in "winter's chilling disappearance"` → **TRUE** ❌
   - Result: Marked as duplicate (different stories, just share "winter")

**Why it's bad:**
- Any title containing "Winter" matches ANY other title containing "Winter"
- It catches completely different stories that just share a word
- This check happens FIRST and exits immediately, so word overlap check never runs

---

### **Check 2: Exact Match (GOOD)**

```python
if title_lower == published_title:
    return True
```

**This is correct** - exact duplicates should be blocked.

---

### **Check 3: Word Overlap (TOO STRICT)**

```python
# If 2+ significant words overlap, likely duplicate
if len(overlap) >= 2:
    return True
```

**Problem:** Even if this check runs (which it often doesn't because substring check exits first), 2-word overlap is too low.

**Examples:**
- "Winter Disappearance" vs "Winter's Chilling Disappearance"
- Overlap: `{"winter", "disappearance"}` = 2 words → **DUPLICATE** ❌
- But these could be completely different stories!

**Note:** This check rarely runs because substring check exits first.

---

## 📊 **REAL EXAMPLE FROM YOUR LOGS**

From the generation logs, we see:

```
⚠️ All stories are duplicates (attempt 1/10), trying different selection...
...
⚠️ All available stories are duplicates after 10 attempts
⚠️ Scraping found only duplicates, falling back to LLM generation...
🧠 Generating horror story with Cerebras...
✓ Horror story generated with Cerebras
⚠️ Duplicate title detected: Winter's Chill, retrying...
```

**What happened:**

1. **Scraping stage:** All scraped stories matched published ones (substring matching too strict)
2. **LLM stage:** LLM generated "Winter's Chill"
3. **Duplicate check:** "Winter's Chill" matched "Winter's Chill (TRUE STORY)" in history.json
   - Substring check: `"winter's chill" in "winter's chill (true story)"` → **TRUE** ❌
   - Marked as duplicate
4. **Retry:** LLM generates another winter-themed title
5. **Repeat:** 10 times, all marked as duplicates
6. **Result:** Video generation fails ❌

---

## ✅ **WHY ONE VIDEO SUCCEEDED**

"Winter's Vanishing (UNSOLVED)" succeeded because:

1. **No exact match** in history.json
2. **Substring check passed:**
   - "winter's vanishing" is NOT a substring of any published title
   - It's a unique title that doesn't match existing ones
3. **Word overlap check:**
   - Only "winter's" overlaps (1 word)
   - Needs 2+ words to be duplicate → Passes ✅

**Result:** Made it through all checks and was uploaded successfully.

---

## 🔧 **THE ROOT CAUSE**

**The substring matching is the main culprit:**

1. ✅ It runs FIRST and exits immediately
2. ✅ It's too broad - catches different stories that share words
3. ✅ It prevents word overlap check from running
4. ✅ It marks everything as duplicates

**Secondary issues:**

1. Word overlap threshold (2 words) is too low
2. Common words list doesn't include genre-specific words
3. Small story pool gets exhausted quickly

---

## 💡 **SOLUTIONS**

### **Option 1: Fix Substring Matching (RECOMMENDED)**

Change substring matching to only match exact titles (with suffix variations):

```python
# Remove suffix patterns before comparing
def normalize_title(title):
    # Remove patterns like "(TRUE STORY)", "(UNSOLVED)", etc.
    title = re.sub(r'\s*\([^)]+\)\s*$', '', title.lower().strip())
    return title

# Then compare normalized titles
if normalize_title(title) == normalize_title(published_title):
    return True  # Exact match (ignoring suffixes)
```

### **Option 2: Remove Substring Matching Entirely**

Only use exact matches and word overlap:

```python
# Remove substring check
# Only use exact match and word overlap
```

### **Option 3: Increase Word Overlap Threshold**

Change from 2 words to 3+ words:

```python
# If 3+ significant words overlap, likely duplicate
if len(overlap) >= 3:
    return True
```

### **Option 4: Add More Common Words**

Add genre-specific words to common words list:

```python
common_words = {
    ..., 'winter', 'disappearance', 'vanishing', 'chill', 
    'dark', 'mystery', 'case', 'eve', 'night', 'frozen', ...
}
```

---

## 📋 **SUMMARY**

**The duplicate detection fails because:**

1. ✅ **Substring matching is too broad** - catches different stories
2. ✅ **Substring check runs first** - exits before other checks
3. ✅ **Word overlap threshold too low** - 2 words catch different stories
4. ✅ **Small story pool** - gets exhausted quickly

**Result:** System can't find any "unique" stories and marks everything as duplicates.

**Solution:** Fix substring matching (use normalized titles) or remove it entirely, and increase word overlap threshold.

---

## 🎯 **QUICK FIX**

The fastest fix is to **remove or fix the substring matching**:

1. Remove substring check entirely, OR
2. Normalize titles before substring check (remove suffixes), OR
3. Only use substring for very short strings (3-4 chars)

This would allow different stories with shared themes (like "Winter's Chill" vs "Winter's Dark Secret") to pass through.
