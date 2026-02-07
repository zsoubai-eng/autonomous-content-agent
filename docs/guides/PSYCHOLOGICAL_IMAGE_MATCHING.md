# Psychological Image Matching Enhancement

## Overview
Enhanced the image search engine to create **better psychological connection** between the story narrative and visual imagery. Images now match what the viewer should visualize while listening to the story.

## Key Improvements

### 1. **Narrative-Aware Keyword Extraction
   - **Before**: Simple keyword matching (location, object, atmosphere)
   - **After**: Extracts the MAIN VISUAL SCENE based on story narrative
   
   - **Priority System**:
     1. **Main Subject** (what the story is about - mental anchor)
     2. **Primary Location** (where it happens - spatial visualization)
     3. **Key Action/Event** (what's happening - narrative visualization)
     4. **Important Object** (visual detail that enhances scene)
     5. **Atmosphere** (mood/feeling - emotional connection)

### 2. **Action Pattern Recognition
   - Identifies story type: disappearance, murder, mystery, encounter, haunting, isolation, danger
   - Matches images to the **core action** happening in the story
   - Creates psychological connection: viewer visualizes the event, not just a generic location

### 3. **Historical Event Detection
   - Recognizes historical horror terms: colony, murder, disappearance, mystery, case, incident
   - Prioritizes these in keyword extraction for better matching to real historical events

### 4. **Enhanced Location Extraction
   - More comprehensive location keywords (colony, settlement, village, town, city)
   - Prioritizes the most specific location mentioned in the story

### 5. **Scene Composition Logic
   - Keywords are ordered to create a narrative flow in search queries
   - Format: "subject location action atmosphere"
   - Example: "colony disappearance abandoned dark" (vs. old: "abandoned dark horror")

## Psychological Benefits

1. **Visual Anchoring**: Main subject provides mental anchor for viewer
2. **Spatial Visualization**: Location helps viewer "place" themselves in the scene
3. **Narrative Visualization**: Action keywords help viewer visualize what's happening
4. **Emotional Connection**: Atmosphere keywords create mood alignment
5. **Story Immersion**: Images match the story moment, not just generic horror

## Example Transformations

### Example 1: "The Roanoke Colony"
- **Old Keywords**: "colony, abandoned, dark, horror"
- **New Keywords**: "colony, settlement, disappearance, abandoned, dark"
- **Result**: Image matches the historical disappearance event, not just any abandoned place

### Example 2: "The Hinterkaifeck Murders"
- **Old Keywords**: "house, abandoned, dark, horror"
- **New Keywords**: "murder, house, farm, isolated, dark"
- **Result**: Image matches the murder event at an isolated farmhouse

### Example 3: "The Isdal Woman"
- **Old Keywords**: "woman, mystery, dark, horror"
- **New Keywords**: "mystery, mountain, disappearance, isolated, dark"
- **Result**: Image matches the mysterious disappearance in a mountain setting

## Technical Implementation

- **File**: `departments/production/image_search_engine.py`
- **Function**: `_extract_keywords_from_story()`
- **Changes**: Complete rewrite with narrative-aware extraction logic
- **Backward Compatible**: Yes, maintains same function signature

## Testing

To test the improvements:
```bash
python main.py
```

The system will now extract more narrative-focused keywords and find images that better match the story's visual narrative.
