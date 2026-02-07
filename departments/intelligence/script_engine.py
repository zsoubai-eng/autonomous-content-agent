"""
THE INTELLIGENT SCRIPT ENGINE
Module 1: Generates clean, production-ready YouTube Short scripts.

Solves the "weird words" problem with strict JSON enforcement and sanitization.
"""

import os
import json
import re
from typing import Dict, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys - Hydra Brain (Multi-Key Failover)
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")  # Primary Brain (The Strategist)
GEMINI_API_KEY_1 = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_1")  # Backup Brain
GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2")  # Backup Brain
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Tertiary Brain


def clean_script(text: str) -> Dict:
    """
    THE SANITIZER: Removes markdown, parses JSON, and extracts clean script data.
    
    CRITICAL: This function ensures we NEVER get conversational text or metadata.
    
    Args:
        text: Raw response from AI (may contain markdown, metadata, etc.)
        
    Returns:
        Dict: Clean script data with 'title', 'script', 'tags', etc.
        
    Raises:
        ValueError: If JSON cannot be extracted or parsed
    """
    # Step 1: Remove markdown code blocks (```json ... ```)
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = re.sub(r'```', '', text)
    
    # Step 2: Remove common conversational prefixes
    prefixes_to_remove = [
        r'^Here is your script:?\s*',
        r'^Here\'s your script:?\s*',
        r'^Here is the script:?\s*',
        r'^Here\'s the script:?\s*',
        r'^Script:?\s*',
        r'^JSON:?\s*',
        r'^Output:?\s*',
    ]
    for prefix in prefixes_to_remove:
        text = re.sub(prefix, '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Step 3: Find JSON object boundaries
    # Look for first { and last }
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    
    if first_brace == -1 or last_brace == -1 or first_brace >= last_brace:
        raise ValueError("No JSON object found in response")
    
    # Extract JSON substring
    json_str = text[first_brace:last_brace + 1]
    
    # Step 4: Clean up common JSON issues
    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    # Step 5: Parse JSON
    try:
        script_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        # Try to fix common issues
        # Remove comments (not valid in JSON but sometimes added)
        json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        try:
            script_data = json.loads(json_str)
        except json.JSONDecodeError:
            # Try using json_repair if available
            try:
                import json_repair
                json_str = json_repair.repair_json(json_str)
                script_data = json.loads(json_str)
            except (ImportError, Exception):
                # If json_repair fails, try to fix incomplete JSON manually
                # Check if JSON is incomplete (missing closing braces)
                open_braces = json_str.count('{')
                close_braces = json_str.count('}')
                if open_braces > close_braces:
                    # Add missing closing braces
                    json_str += '}' * (open_braces - close_braces)
                    try:
                        script_data = json.loads(json_str)
                    except:
                        raise ValueError(f"Failed to parse JSON: {e}. Extracted text: {json_str[:200]}")
                else:
                    raise ValueError(f"Failed to parse JSON: {e}. Extracted text: {json_str[:200]}")
    
    # Step 6: Validate and clean storyboard content
    # Check for new scene-based format first
    if 'scenes' in script_data:
        # New scene-based format
        if not isinstance(script_data['scenes'], list):
            raise ValueError("JSON 'scenes' field must be a list")
        
        # Clean each scene
        for scene in script_data['scenes']:
            if 'text' not in scene:
                raise ValueError("Scene missing required 'text' field")
            if 'visual_prompt' not in scene:
                raise ValueError("Scene missing required 'visual_prompt' field")
            if 'duration' not in scene:
                raise ValueError("Scene missing required 'duration' field")
            
            # Clean scene text
            scene_text = scene['text']
            scene_text = re.sub(r'\([^)]*\)', '', scene_text)  # Remove (stage directions)
            scene_text = re.sub(r'\[[^\]]*\]', '', scene_text)  # Remove [metadata]
            scene_text = re.sub(r'<[^>]*>', '', scene_text)  # Remove <tags>
            scene_text = re.sub(r'\*\*', '', scene_text)  # Remove **bold**
            scene_text = re.sub(r'__', '', scene_text)  # Remove __underline__
            scene_text = re.sub(r'\s+', ' ', scene_text).strip()
            
            # Remove common AI artifacts
            artifacts = ['Narrator:', 'Voiceover:', 'Speaker:', 'Text:', 'Script:', 'Title:']
            for artifact in artifacts:
                scene_text = re.sub(rf'^{re.escape(artifact)}\s*', '', scene_text, flags=re.IGNORECASE)
            
            scene['text'] = scene_text
            
            # Ensure duration is a float
            try:
                scene['duration'] = float(scene['duration'])
            except (ValueError, TypeError):
                scene['duration'] = 3.0  # Default duration
            
            # Ensure id is an integer
            if 'id' not in scene:
                scene['id'] = script_data['scenes'].index(scene) + 1
            else:
                try:
                    scene['id'] = int(scene['id'])
                except (ValueError, TypeError):
                    scene['id'] = script_data['scenes'].index(scene) + 1
        
        # Generate combined script text for backward compatibility
        script_text = ' '.join([scene['text'] for scene in script_data['scenes']])
        script_data['script'] = script_text
    elif 'script' in script_data:
        # Old format - clean the script text itself
        script_text = script_data['script']
        
        # Remove stage directions, metadata, and formatting artifacts
        script_text = re.sub(r'\([^)]*\)', '', script_text)  # Remove (stage directions)
        script_text = re.sub(r'\[[^\]]*\]', '', script_text)  # Remove [metadata]
        script_text = re.sub(r'<[^>]*>', '', script_text)  # Remove <tags>
        script_text = re.sub(r'\*\*', '', script_text)  # Remove **bold**
        script_text = re.sub(r'__', '', script_text)  # Remove __underline__
        
        # Remove excessive whitespace
        script_text = re.sub(r'\s+', ' ', script_text)
        script_text = script_text.strip()
        
        # Remove common AI artifacts
        artifacts = [
            'Narrator:',
            'Voiceover:',
            'Speaker:',
            'Text:',
            'Script:',
            'Title:',
        ]
        for artifact in artifacts:
            script_text = re.sub(rf'^{re.escape(artifact)}\s*', '', script_text, flags=re.IGNORECASE)
        
        # Update cleaned script
        script_data['script'] = script_text
    else:
        raise ValueError("JSON missing required 'script' or 'scenes' field")
    
    # Ensure title exists
    if 'title' not in script_data:
        # Extract first line or first 50 chars as title
        first_line = script_text.split('\n')[0].strip()
        script_data['title'] = first_line[:50] if first_line else "AI Generated Short"
    
    # Ensure tags exist
    if 'tags' not in script_data:
        script_data['tags'] = ['YouTube Shorts', 'Viral', 'AI Generated']
    
    return script_data


def generate_script_cerebras(topic: str, niche: str, viral_titles: List[str] = None) -> Optional[Dict]:
    """
    Generate script using Cerebras API (The Strategist - Primary Brain).
    
    Uses Cerebras API with llama3.1-70b model for high-quality storyboard generation.
    
    Args:
        topic: Specific topic for the script
        niche: Niche category (Dark Psychology)
        viral_titles: List of viral titles for market intelligence
        
    Returns:
        Dict: Clean script data with scene-based storyboard or None if failed
    """
    if not CEREBRAS_API_KEY:
        return None
    
    try:
        import requests
        
        # Build viral analysis section if titles provided
        viral_analysis = ""
        if viral_titles and len(viral_titles) > 0:
            viral_analysis = f"""

**MARKET INTELLIGENCE - VIRAL TOPICS ANALYSIS:**
Analyze these {len(viral_titles)} viral titles (all >100k views):
{chr(10).join(f"- {title}" for title in viral_titles[:5])}

**YOUR TASK:** Identify the psychological hook structure these viral videos used. What pattern makes them successful? Then write a NEW script that uses a similar hook structure but for a FRESH fact. Do NOT copy them directly - use the pattern, not the content.
"""
        
        prompt = f"""You are a Survival Historian and Dark Psychology Expert. Your mission is to frame psychological manipulation as a THREAT-LED SURVIVAL STORY, not a Wikipedia entry.
{viral_analysis}
YOUR MISSION - THREAT-LED STORYTELLING (Hominid History Aesthetic):

1. **CONCEPT:** Pick a specific, named psychological law or theory (e.g., 'The Ben Franklin Effect', 'Cognitive Dissonance', 'Reciprocity', 'The Anchoring Bias', 'The Door-in-the-Face Technique'). Frame it as a SURVIVAL STORY, not an informational list.

2. **THE HOOK (0-5 seconds - Scene 1):**
   - MUST use a **Time Anchor** (e.g., "In 1920, a psychologist discovered...", "In ancient Rome, they used...", "During World War II, they found...") OR
   - MUST use a **Specific Survival Hook** (e.g., "If you feel watched right now...", "When someone asks you a favor...", "The moment you see a price tag...")
   - MUST open an **Open Loop** - create a question or incomplete thought that demands resolution.
   - NO generic statements. NO "Did you know" openings. NO listicle structures.

3. **THE BODY (Scenes 2-7):**
   - **FORBIDDEN:** Do NOT use listicles (Reason 1, Reason 2, Reason 3). NO numbered lists. NO bullet points in narration.
   - **REQUIRED:** Use continuous narrative flow. Tell a story. Connect each scene to the next with cause-and-effect.
   - Frame Dark Psychology as a **survival mechanism** - how predators use it, how prey can detect it, how to protect yourself.
   - Each scene should build tension and reveal the psychological mechanism through STORY, not explanation.

4. **VISUAL PROMPTS - GOLDEN HOUR AESTHETIC:**
   - ALL visual_prompts MUST include: "Cinematic, 8k, mysterious, golden hour lighting"
   - Focus on **golden-hour aesthetic** descriptions (warm amber tones, long shadows, dramatic sky, sunset/sunrise atmosphere).
   - Match the "Hominid History" aesthetic - ancient, primal, survival-focused visuals.
   - Examples: "Cinematic, 8k, mysterious, golden hour lighting, ancient stone ruins, long shadows, warm amber tones, survival aesthetic"
   - NO dark noir. NO abstract neural networks. Use golden hour, cinematic landscapes, historical/primordial imagery.

5. **TONE:** Deep, authoritative, slightly paranoid but helpful. Speak like a survival expert warning about psychological predators. Be urgent but measured. Use short, punchy sentences. Create a sense of imminent threat that can be avoided.

6. **CONSTRAINT:** NEVER repeat a topic found in history.json. Always teach a fresh psychological concept framed as survival.

CRITICAL REQUIREMENTS:
1. You MUST return ONLY a valid JSON object. No conversational text, no markdown, no explanations.
2. The total script must be LESS THAN 130 WORDS total across all scenes.
3. The script should be 30-60 seconds when read aloud (sum of all scene durations).
4. **HOOK:** First scene (3-5 seconds) MUST use Time Anchor OR Survival Hook + Open Loop. NO listicles.
5. **INFINITE LOOP HACK:** The last scene should end with an incomplete thought that grammatically flows perfectly into the first scene. Do NOT say "In conclusion" or any closing phrases. The script should seamlessly loop back to the beginning.
6. **NARRATIVE FLOW:** NO numbered lists. NO "Reason 1, Reason 2". Use continuous story flow connecting scenes.

Return JSON in this EXACT format (SCENE-BASED STORYBOARD):
{{
    "title": "Survival-focused, threat-led title that triggers primal curiosity",
    "scenes": [
        {{
            "id": 1,
            "text": "Time Anchor or Survival Hook that opens an Open Loop. Example: 'In 1920, a psychologist discovered something that changes everything...' OR 'If you feel watched right now, your brain is already...'",
            "visual_prompt": "Cinematic, 8k, mysterious, golden hour lighting, [specific survival/historical visual], warm amber tones, long shadows, dramatic sky",
            "duration": 3.0
        }},
        {{
            "id": 2,
            "text": "Continue the narrative flow. Reveal the psychological mechanism through story, not list. Build tension.",
            "visual_prompt": "Cinematic, 8k, mysterious, golden hour lighting, [matching visual that continues the story], golden hour aesthetic, survival atmosphere",
            "duration": 4.0
        }},
        {{
            "id": 3,
            "text": "Further narrative development. Show HOW it's used as a threat or survival tool. NO numbered lists.",
            "visual_prompt": "Cinematic, 8k, mysterious, golden hour lighting, [visual that matches narrative progression], warm amber tones, cinematic landscape",
            "duration": 3.5
        }}
    ],
    "tags": ["dark psychology", "human behavior", "psychology", "mind tricks", "body language", "manipulation", "influence"],
    "pacing": "Fast"
}}

CRITICAL SCENE REQUIREMENTS:
1. Generate 5-8 scenes total. Each scene should be 1-2 sentences in continuous narrative flow.
2. Each scene MUST have: id (1, 2, 3...), text (the narration), visual_prompt (MUST include "Cinematic, 8k, mysterious, golden hour lighting"), duration (2.0-5.0 seconds).
3. Total duration should be 30-60 seconds when all scenes are combined.
4. First scene MUST use Time Anchor OR Survival Hook + Open Loop (NO generic hooks).
5. Last scene should end with an incomplete thought that loops back to the first scene.
6. NO listicles. NO "Reason 1, Reason 2". Use continuous narrative flow.
7. ALL visual_prompts MUST include "Cinematic, 8k, mysterious, golden hour lighting" for Hominid History aesthetic.

REMEMBER: Return ONLY the JSON object. Frame Dark Psychology as a survival story, not a Wikipedia entry. Think threat-led storytelling, not informational lists."""

        # Cerebras API endpoint
        api_url = "https://api.cerebras.ai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {CEREBRAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b",  # Updated to correct model name
            "messages": [
                {
                    "role": "system",
                    "content": "You are a Survival Historian and Dark Psychology Expert. Your mission is threat-led storytelling with Hominid History aesthetic. Frame psychological manipulation as survival stories, not Wikipedia entries. Always return ONLY valid JSON. Never add conversational text. Use Time Anchors or Survival Hooks. NO listicles."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.9,
            "max_tokens": 2000
        }
        
        print("   🧠 The Strategist (Cerebras): Generating storyboard...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=60)
        
        if response.status_code != 200:
            raise Exception(f"Cerebras API returned status {response.status_code}: {response.text}")
        
        result = response.json()
        raw_text = result['choices'][0]['message']['content'].strip()
        
        # Clean and parse
        script_data = clean_script(raw_text)
        return script_data
        
    except Exception as e:
        print(f"⚠️ Cerebras failed: {e}")
        return None


def generate_script_gemini(topic: str, niche: str, viral_titles: List[str] = None, api_key: str = None) -> Optional[Dict]:
    """
    Generate script using Google Gemini (Hydra Brain - Multi-Key Failover).
    
    Args:
        topic: Specific topic for the script
        niche: Niche category (Dark Psychology)
        viral_titles: List of viral titles for market intelligence
        api_key: Specific API key to use (for failover)
        
    Returns:
        Dict: Clean script data or None if failed
    """
    if not api_key:
        return None
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        # Try gemini-1.5-flash first (most reliable), fallback to gemini-pro
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
        except:
            try:
                model = genai.GenerativeModel('gemini-pro')
            except:
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Build viral analysis section if titles provided
        viral_analysis = ""
        if viral_titles and len(viral_titles) > 0:
            viral_analysis = f"""

**MARKET INTELLIGENCE - VIRAL TOPICS ANALYSIS:**
Analyze these {len(viral_titles)} viral titles (all >100k views):
{chr(10).join(f"- {title}" for title in viral_titles[:5])}

**YOUR TASK:** Identify the psychological hook structure these viral videos used. What pattern makes them successful? Then write a NEW script that uses a similar hook structure but for a FRESH fact. Do NOT copy them directly - use the pattern, not the content.
"""
        
        prompt = f"""You are a Survival Historian and Dark Psychology Expert. Your mission is to frame psychological manipulation as a THREAT-LED SURVIVAL STORY, not a Wikipedia entry.
{viral_analysis}
YOUR MISSION - THREAT-LED STORYTELLING (Hominid History Aesthetic):

1. **CONCEPT:** Pick a specific, named psychological law or theory (e.g., 'The Ben Franklin Effect', 'Cognitive Dissonance', 'Reciprocity', 'The Anchoring Bias', 'The Door-in-the-Face Technique'). Frame it as a SURVIVAL STORY, not an informational list.

2. **THE HOOK (0-5 seconds):**
   - MUST use a **Time Anchor** (e.g., "In 1920, a psychologist discovered...", "In ancient Rome, they used...", "During World War II, they found...") OR
   - MUST use a **Specific Survival Hook** (e.g., "If you feel watched right now...", "When someone asks you a favor...", "The moment you see a price tag...")
   - MUST open an **Open Loop** - create a question or incomplete thought that demands resolution.
   - NO generic statements. NO "Did you know" openings. NO listicle structures.

3. **THE BODY:**
   - **FORBIDDEN:** Do NOT use listicles (Reason 1, Reason 2, Reason 3). NO numbered lists. NO bullet points in narration.
   - **REQUIRED:** Use continuous narrative flow. Tell a story. Connect each scene to the next with cause-and-effect.
   - Frame Dark Psychology as a **survival mechanism** - how predators use it, how prey can detect it, how to protect yourself.
   - Build tension and reveal the psychological mechanism through STORY, not explanation.

4. **VISUAL PROMPTS - GOLDEN HOUR AESTHETIC:**
   - ALL visual_prompts MUST include: "Cinematic, 8k, mysterious, golden hour lighting"
   - Focus on **golden-hour aesthetic** descriptions (warm amber tones, long shadows, dramatic sky, sunset/sunrise atmosphere).
   - Match the "Hominid History" aesthetic - ancient, primal, survival-focused visuals.
   - NO dark noir. NO abstract neural networks. Use golden hour, cinematic landscapes, historical/primordial imagery.

5. **TONE:** Deep, authoritative, slightly paranoid but helpful. Speak like a survival expert warning about psychological predators. Be urgent but measured. Use short, punchy sentences. Create a sense of imminent threat that can be avoided.

6. **CONSTRAINT:** NEVER repeat a topic found in history.json. Always teach a fresh psychological concept framed as survival.

CRITICAL REQUIREMENTS:
1. You MUST return ONLY a valid JSON object. No conversational text, no markdown, no explanations.
2. The script must be LESS THAN 130 WORDS total.
3. The script should be 30-60 seconds when read aloud.
4. **HOOK:** First 3-5 seconds MUST use Time Anchor OR Survival Hook + Open Loop. NO listicles.
5. **INFINITE LOOP HACK:** The script must be written as a LOOP. The last sentence must be an incomplete thought that grammatically flows perfectly into the first sentence. Do NOT say "In conclusion" or any closing phrases. The script should seamlessly loop back to the beginning.
6. **NARRATIVE FLOW:** NO numbered lists. NO "Reason 1, Reason 2". Use continuous story flow.

Return JSON in this EXACT format (SCENE-BASED STORYBOARD):
{{
    "title": "Survival-focused, threat-led title that triggers primal curiosity",
    "scenes": [
        {{
            "id": 1,
            "text": "Time Anchor or Survival Hook that opens an Open Loop. Example: 'In 1920, a psychologist discovered something that changes everything...' OR 'If you feel watched right now, your brain is already...'",
            "visual_prompt": "Cinematic, 8k, mysterious, golden hour lighting, [specific survival/historical visual], warm amber tones, long shadows, dramatic sky",
            "duration": 3.0
        }},
        {{
            "id": 2,
            "text": "Continue the narrative flow. Reveal the psychological mechanism through story, not list. Build tension.",
            "visual_prompt": "Cinematic, 8k, mysterious, golden hour lighting, [matching visual that continues the story], golden hour aesthetic, survival atmosphere",
            "duration": 4.0
        }}
    ],
    "tags": ["dark psychology", "human behavior", "psychology", "mind tricks", "body language", "manipulation", "influence"],
    "pacing": "Fast"
}}

CRITICAL SCENE REQUIREMENTS:
1. Generate 5-8 scenes total. Each scene should be 1-2 sentences in continuous narrative flow.
2. Each scene MUST have: id (1, 2, 3...), text (the narration), visual_prompt (MUST include "Cinematic, 8k, mysterious, golden hour lighting"), duration (2.0-5.0 seconds).
3. Total duration should be 30-60 seconds when all scenes are combined.
4. First scene MUST use Time Anchor OR Survival Hook + Open Loop (NO generic hooks).
5. Last scene should end with an incomplete thought that loops back to the first scene.
6. NO listicles. NO "Reason 1, Reason 2". Use continuous narrative flow.
7. ALL visual_prompts MUST include "Cinematic, 8k, mysterious, golden hour lighting" for Hominid History aesthetic.

REMEMBER: Return ONLY the JSON object. Frame Dark Psychology as a survival story, not a Wikipedia entry. Think threat-led storytelling, not informational lists."""

        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Clean and parse
        script_data = clean_script(raw_text)
        return script_data
        
    except Exception as e:
        print(f"⚠️ Gemini failed: {e}")
        return None


def generate_script_groq(topic: str, niche: str, viral_titles: List[str] = None) -> Optional[Dict]:
    """
    Generate script using Groq/Llama 3 (Fallback Brain).
    
    Args:
        topic: Specific topic for the script
        niche: Niche category (Space, History, Tech, Minecraft)
        
    Returns:
        Dict: Clean script data or None if failed
    """
    if not GROQ_API_KEY:
        return None
    
    try:
        from groq import Groq
        
        client = Groq(api_key=GROQ_API_KEY)
        
        # Build viral analysis section if titles provided
        viral_analysis = ""
        if viral_titles and len(viral_titles) > 0:
            viral_analysis = f"""

**MARKET INTELLIGENCE - VIRAL TOPICS ANALYSIS:**
Analyze these {len(viral_titles)} viral titles (all >100k views):
{chr(10).join(f"- {title}" for title in viral_titles[:5])}

**YOUR TASK:** Identify the psychological hook structure these viral videos used. What pattern makes them successful? Then write a NEW script that uses a similar hook structure but for a FRESH fact. Do NOT copy them directly - use the pattern, not the content.
"""
        
        prompt = f"""You are a Survival Historian and Dark Psychology Expert. Your mission is to frame psychological manipulation as a THREAT-LED SURVIVAL STORY, not a Wikipedia entry.
{viral_analysis}
YOUR MISSION - THREAT-LED STORYTELLING (Hominid History Aesthetic):

1. **CONCEPT:** Pick a specific, named psychological law or theory (e.g., 'The Ben Franklin Effect', 'Cognitive Dissonance', 'Reciprocity', 'The Anchoring Bias', 'The Door-in-the-Face Technique'). Frame it as a SURVIVAL STORY, not an informational list.

2. **THE HOOK (0-5 seconds - Scene 1):**
   - MUST use a **Time Anchor** (e.g., "In 1920, a psychologist discovered...", "In ancient Rome, they used...", "During World War II, they found...") OR
   - MUST use a **Specific Survival Hook** (e.g., "If you feel watched right now...", "When someone asks you a favor...", "The moment you see a price tag...")
   - MUST open an **Open Loop** - create a question or incomplete thought that demands resolution.
   - NO generic statements. NO "Did you know" openings. NO listicle structures.

3. **THE BODY (Scenes 2-7):**
   - **FORBIDDEN:** Do NOT use listicles (Reason 1, Reason 2, Reason 3). NO numbered lists. NO bullet points in narration.
   - **REQUIRED:** Use continuous narrative flow. Tell a story. Connect each scene to the next with cause-and-effect.
   - Frame Dark Psychology as a **survival mechanism** - how predators use it, how prey can detect it, how to protect yourself.
   - Each scene should build tension and reveal the psychological mechanism through STORY, not explanation.

4. **VISUAL PROMPTS - GOLDEN HOUR AESTHETIC:**
   - ALL visual_prompts MUST include: "Cinematic, 8k, mysterious, golden hour lighting"
   - Focus on **golden-hour aesthetic** descriptions (warm amber tones, long shadows, dramatic sky, sunset/sunrise atmosphere).
   - Match the "Hominid History" aesthetic - ancient, primal, survival-focused visuals.
   - Examples: "Cinematic, 8k, mysterious, golden hour lighting, ancient stone ruins, long shadows, warm amber tones, survival aesthetic"
   - NO dark noir. NO abstract neural networks. Use golden hour, cinematic landscapes, historical/primordial imagery.

5. **TONE:** Deep, authoritative, slightly paranoid but helpful. Speak like a survival expert warning about psychological predators. Be urgent but measured. Use short, punchy sentences. Create a sense of imminent threat that can be avoided.

6. **CONSTRAINT:** NEVER repeat a topic found in history.json. Always teach a fresh psychological concept framed as survival.

CRITICAL REQUIREMENTS:
1. You MUST return ONLY a valid JSON object. No conversational text, no markdown, no explanations.
2. The total script must be LESS THAN 130 WORDS total across all scenes.
3. The script should be 30-60 seconds when read aloud (sum of all scene durations).
4. **HOOK:** First scene (3-5 seconds) MUST use Time Anchor OR Survival Hook + Open Loop. NO listicles.
5. **INFINITE LOOP HACK:** The last scene should end with an incomplete thought that grammatically flows perfectly into the first scene. Do NOT say "In conclusion" or any closing phrases. The script should seamlessly loop back to the beginning.
6. **NARRATIVE FLOW:** NO numbered lists. NO "Reason 1, Reason 2". Use continuous story flow connecting scenes.

Return JSON in this EXACT format (SCENE-BASED STORYBOARD):
{{
    "title": "Survival-focused, threat-led title that triggers primal curiosity",
    "scenes": [
        {{
            "id": 1,
            "text": "Time Anchor or Survival Hook that opens an Open Loop. Example: 'In 1920, a psychologist discovered something that changes everything...' OR 'If you feel watched right now, your brain is already...'",
            "visual_prompt": "Cinematic, 8k, mysterious, golden hour lighting, [specific survival/historical visual], warm amber tones, long shadows, dramatic sky",
            "duration": 3.0
        }},
        {{
            "id": 2,
            "text": "Continue the narrative flow. Reveal the psychological mechanism through story, not list. Build tension.",
            "visual_prompt": "Cinematic, 8k, mysterious, golden hour lighting, [matching visual that continues the story], golden hour aesthetic, survival atmosphere",
            "duration": 4.0
        }},
        {{
            "id": 3,
            "text": "Further narrative development. Show HOW it's used as a threat or survival tool. NO numbered lists.",
            "visual_prompt": "Cinematic, 8k, mysterious, golden hour lighting, [visual that matches narrative progression], warm amber tones, cinematic landscape",
            "duration": 3.5
        }}
    ],
    "tags": ["dark psychology", "human behavior", "psychology", "mind tricks", "body language", "manipulation", "influence"],
    "pacing": "Fast"
}}

CRITICAL SCENE REQUIREMENTS:
1. Generate 5-8 scenes total. Each scene should be 1-2 sentences in continuous narrative flow.
2. Each scene MUST have: id (1, 2, 3...), text (the narration), visual_prompt (MUST include "Cinematic, 8k, mysterious, golden hour lighting"), duration (2.0-5.0 seconds).
3. Total duration should be 30-60 seconds when all scenes are combined.
4. First scene MUST use Time Anchor OR Survival Hook + Open Loop (NO generic hooks).
5. Last scene should end with an incomplete thought that loops back to the first scene.
6. NO listicles. NO "Reason 1, Reason 2". Use continuous narrative flow.
7. ALL visual_prompts MUST include "Cinematic, 8k, mysterious, golden hour lighting" for Hominid History aesthetic.

REMEMBER: Return ONLY the JSON object. Frame Dark Psychology as a survival story, not a Wikipedia entry. Think threat-led storytelling, not informational lists."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a Survival Historian and Dark Psychology Expert. Your mission is threat-led storytelling with Hominid History aesthetic. Frame psychological manipulation as survival stories, not Wikipedia entries. Always return ONLY valid JSON. Never add conversational text. Use Time Anchors or Survival Hooks. NO listicles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=500
        )
        
        raw_text = response.choices[0].message.content.strip()
        
        # Clean and parse
        script_data = clean_script(raw_text)
        return script_data
        
    except Exception as e:
        print(f"⚠️ Groq failed: {e}")
        return None


def generate_draft_script(topic: str = None, niche: str = None, viral_titles: List[str] = None) -> Dict:
    """
    Main entry point: Generate script using dual-brain approach with market intelligence.
    
    Args:
        topic: Specific topic (if None, will be generated - HARDCODED to Dark Psychology)
        niche: Niche category (if None, will be HARDCODED to "Dark Psychology")
        viral_titles: List of viral titles from market research (optional)
        
    Returns:
        Dict: Clean script data with 'title', 'script', 'tags'
        
    Raises:
        Exception: If both Gemini and Groq fail
    """
    # HARDCODED: Always use Dark Psychology niche for monetization alignment
    niche = "Dark Psychology"
    
    # HARDCODED: Always use dark psychology/human behavior topic
    if not topic:
        topic = "A viral 'Dark Psychology' fact or a 'Human Behavior Hack' that is mind-blowing. The hook must be about reading people, lying, or influence."
    
    print(f"🌐 Generating script about {niche} - {topic}...")
    if viral_titles:
        print(f"   📊 Using {len(viral_titles)} viral topics for market intelligence")
    
    # THE STRATEGIST: Cerebras as Primary Brain (Infinite Free Stack)
    script_data = None
    
    # Try Cerebras (The Strategist - Primary Brain)
    if CEREBRAS_API_KEY:
        print("   🧠 The Strategist (Cerebras): Generating storyboard...")
        script_data = generate_script_cerebras(topic, niche, viral_titles)
        if script_data:
            print("✓ Storyboard generated successfully with Cerebras (The Strategist)")
            return script_data
        else:
            print("   ⚠️ Cerebras failed, falling back...")
    
    # HYDRA BRAIN: Multi-Key Failover (Gemini Key 1 -> Gemini Key 2 -> Groq)
    # Try Gemini Key 1 (Backup Brain)
    if GEMINI_API_KEY_1:
        print("   🧠 Attempting Gemini Key 1 (Backup Brain)...")
        script_data = generate_script_gemini(topic, niche, viral_titles, GEMINI_API_KEY_1)
        if script_data:
            print("✓ Script generated successfully with Gemini Key 1")
            return script_data
        else:
            print("   ⚠️ Gemini Key 1 failed")
    
    # Try Gemini Key 2 (Backup Brain)
    if GEMINI_API_KEY_2:
        print("   🧠 Attempting Gemini Key 2 (Backup Brain)...")
        script_data = generate_script_gemini(topic, niche, viral_titles, GEMINI_API_KEY_2)
        if script_data:
            print("✓ Script generated successfully with Gemini Key 2")
            return script_data
        else:
            print("   ⚠️ Gemini Key 2 failed")
    
    # Fallback to Groq (Tertiary Brain)
    print("🔄 Falling back to Groq (Tertiary Brain)...")
    script_data = generate_script_groq(topic, niche, viral_titles)
    if script_data:
        print("✓ Script generated successfully with Groq")
        return script_data
    
    # All failed
    raise Exception("All API keys failed (Cerebras, Gemini Key 1, Gemini Key 2, Groq). Check API keys and network connection.")


def polish_script_gemini(draft_data: Dict, tone: str) -> Optional[Dict]:
    """
    Polish script using Google Gemini (Adversarial Editor).
    
    Args:
        draft_data: Draft script data with 'title', 'script' or 'scenes', 'tags'
        tone: Tone to inject (Aggressive, Conspiratorial, Scientific, Urgent)
        
    Returns:
        Polished script data or None if failed
    """
    # Use GEMINI_API_KEY_1 as fallback for polish function
    api_key = GEMINI_API_KEY_1 or GEMINI_API_KEY_2
    if not api_key:
        return None
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        # Try gemini-1.5-flash first (most reliable), fallback to gemini-pro
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
        except:
            try:
                model = genai.GenerativeModel('gemini-pro')
            except:
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Check if draft is scene-based or old format
        if 'scenes' in draft_data:
            scenes_text = "\n".join([f"Scene {s.get('id', i+1)}: {s.get('text', '')}" for i, s in enumerate(draft_data.get('scenes', []))])
            script_preview = scenes_text
        else:
            script_preview = draft_data.get('script', '')
        
        prompt = f"""Act as a Survival Historian and Viral Script Editor. Review the following YouTube Short script and refactor it into THREAT-LED STORYTELLING with Hominid History aesthetic.

**DRAFT SCRIPT:**
Title: {draft_data.get('title', 'N/A')}
Script: {script_preview}

**CRITIQUE CHECKLIST:**
1. Does the Hook use a Time Anchor (e.g., "In 1920...") OR a Survival Hook (e.g., "If you feel watched...") with an Open Loop?
2. Is it framed as a survival story, NOT a Wikipedia entry or listicle?
3. Does the Loop work perfectly (last scene flows into first scene)?
4. Are visual prompts using golden hour aesthetic?

**ACTION:** REWRITE the script as a scene-based storyboard using THREAT-LED STORYTELLING. Make it survival-focused, urgent, and strictly under 130 words total.

**TONE INJECTION:** Rewrite in a {tone} tone. Make it feel {tone.lower()}, urgent, and survival-focused. Deep, authoritative, slightly paranoid but helpful.

**REQUIREMENTS:**
- Hook (first scene, 3-5 seconds) MUST use Time Anchor OR Survival Hook + Open Loop. NO generic hooks.
- NO listicles. NO "Reason 1, Reason 2". Use continuous narrative flow.
- Language must be simple and direct (Grade 5 level)
- Loop must be perfect (last scene flows into first scene)
- Maximum 130 words total across all scenes
- Tone: {tone} (survival-focused, threat-led)
- Generate 5-8 scenes
- ALL visual_prompts MUST include "Cinematic, 8k, mysterious, golden hour lighting" for Hominid History aesthetic

Return JSON in this EXACT format (SCENE-BASED STORYBOARD):
{{
    "title": "Survival-focused, threat-led title",
    "scenes": [
        {{
            "id": 1,
            "text": "Time Anchor or Survival Hook with Open Loop. Example: 'In 1920, a psychologist discovered...' OR 'If you feel watched right now...'",
            "visual_prompt": "Cinematic, 8k, mysterious, golden hour lighting, [specific survival/historical visual], warm amber tones, long shadows",
            "duration": 3.0
        }},
        {{
            "id": 2,
            "text": "Continue narrative flow. NO listicles. Build tension through story.",
            "visual_prompt": "Cinematic, 8k, mysterious, golden hour lighting, [matching visual], golden hour aesthetic, survival atmosphere",
            "duration": 4.0
        }}
    ],
    "tags": {draft_data.get('tags', [])},
    "pacing": "Fast"
}}

IMPORTANT: Include a "pacing" field with value "Fast" or "Slow" based on the script's energy level.

REMEMBER: Return ONLY the JSON object. Frame as survival story, not Wikipedia entry. NO listicles."""

        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Clean and parse
        script_data = clean_script(raw_text)
        return script_data
        
    except Exception as e:
        print(f"⚠️ Gemini polish failed: {e}")
        return None


def polish_script_groq(draft_data: Dict, tone: str) -> Optional[Dict]:
    """
    Polish script using Groq/Llama 3 (Adversarial Editor).
    
    Args:
        draft_data: Draft script data with 'title', 'script', 'tags'
        tone: Tone to inject (Aggressive, Conspiratorial, Scientific, Urgent)
        
    Returns:
        Polished script data or None if failed
    """
    if not GROQ_API_KEY:
        return None
    
    try:
        from groq import Groq
        
        client = Groq(api_key=GROQ_API_KEY)
        
        # Check if draft is scene-based or old format
        if 'scenes' in draft_data:
            scenes_text = "\n".join([f"Scene {s.get('id', i+1)}: {s.get('text', '')}" for i, s in enumerate(draft_data.get('scenes', []))])
            script_preview = scenes_text
        else:
            script_preview = draft_data.get('script', '')
        
        prompt = f"""Act as a Survival Historian and Viral Script Editor. Review the following YouTube Short script and refactor it into THREAT-LED STORYTELLING with Hominid History aesthetic.

**DRAFT SCRIPT:**
Title: {draft_data.get('title', 'N/A')}
Script: {script_preview}

**CRITIQUE CHECKLIST:**
1. Does the Hook use a Time Anchor (e.g., "In 1920...") OR a Survival Hook (e.g., "If you feel watched...") with an Open Loop?
2. Is it framed as a survival story, NOT a Wikipedia entry or listicle?
3. Does the Loop work perfectly (last scene flows into first scene)?
4. Are visual prompts using golden hour aesthetic?

**ACTION:** REWRITE the script as a scene-based storyboard using THREAT-LED STORYTELLING. Make it survival-focused, urgent, and strictly under 130 words total.

**TONE INJECTION:** Rewrite in a {tone} tone. Make it feel {tone.lower()}, urgent, and survival-focused. Deep, authoritative, slightly paranoid but helpful.

**REQUIREMENTS:**
- Hook (first scene, 3-5 seconds) MUST use Time Anchor OR Survival Hook + Open Loop. NO generic hooks.
- NO listicles. NO "Reason 1, Reason 2". Use continuous narrative flow.
- Language must be simple and direct (Grade 5 level)
- Loop must be perfect (last scene flows into first scene)
- Maximum 130 words total across all scenes
- Tone: {tone} (survival-focused, threat-led)
- Generate 5-8 scenes
- ALL visual_prompts MUST include "Cinematic, 8k, mysterious, golden hour lighting" for Hominid History aesthetic

Return JSON in this EXACT format (SCENE-BASED STORYBOARD):
{{
    "title": "Survival-focused, threat-led title",
    "scenes": [
        {{
            "id": 1,
            "text": "Time Anchor or Survival Hook with Open Loop. Example: 'In 1920, a psychologist discovered...' OR 'If you feel watched right now...'",
            "visual_prompt": "Cinematic, 8k, mysterious, golden hour lighting, [specific survival/historical visual], warm amber tones, long shadows",
            "duration": 3.0
        }},
        {{
            "id": 2,
            "text": "Continue narrative flow. NO listicles. Build tension through story.",
            "visual_prompt": "Cinematic, 8k, mysterious, golden hour lighting, [matching visual], golden hour aesthetic, survival atmosphere",
            "duration": 4.0
        }}
    ],
    "tags": {draft_data.get('tags', [])},
    "pacing": "Fast"
}}

IMPORTANT: Include a "pacing" field with value "Fast" or "Slow" based on the script's energy level.

REMEMBER: Return ONLY the JSON object. Frame as survival story, not Wikipedia entry. NO listicles."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a Survival Historian and Dark Psychology Expert. Your mission is threat-led storytelling with Hominid History aesthetic. Frame psychological manipulation as survival stories. Always return ONLY valid JSON. Never add conversational text. Use Time Anchors or Survival Hooks. NO listicles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=500
        )
        
        raw_text = response.choices[0].message.content.strip()
        
        # Clean and parse
        script_data = clean_script(raw_text)
        return script_data
        
    except Exception as e:
        print(f"⚠️ Groq polish failed: {e}")
        return None


def polish_script(draft_data: Dict) -> Dict:
    """
    Polish draft script using adversarial editing (QA Protocol).
    
    Args:
        draft_data: Draft script data with 'title', 'script', 'tags'
        
    Returns:
        Polished script data (or original if polishing fails)
    """
    import random
    
    # Random tone injection (prevents Bot Fatigue)
    tones = ["Aggressive", "Conspiratorial", "Scientific", "Urgent"]
    selected_tone = random.choice(tones)
    
    print(f"   🔍 Polishing Script (Tone: {selected_tone})...")
    
    # Try Gemini first
    polished = polish_script_gemini(draft_data, selected_tone)
    if polished:
        print(f"   ✓ Script polished with {selected_tone} tone")
        return polished
    
    # Fallback to Groq
    print(f"   🔄 Falling back to Groq for polishing...")
    polished = polish_script_groq(draft_data, selected_tone)
    if polished:
        print(f"   ✓ Script polished with {selected_tone} tone")
        return polished
    
    # If both fail, return original draft
    print(f"   ⚠️ Polishing failed, using original draft")
    return draft_data


def generate_script(topic: str = None, niche: str = None, viral_titles: List[str] = None) -> Dict:
    """
    Main entry point: Generate script using draft -> polish pipeline (QA Protocol).
    
    Includes history checking to prevent duplicate topics.
    
    Args:
        topic: Specific topic (if None, will be generated - HARDCODED to Dark Psychology)
        niche: Niche category (if None, will be HARDCODED to "Dark Psychology")
        
    Returns:
        Dict: Polished script data with 'title', 'script', 'tags'
        
    Raises:
        Exception: If draft generation fails after 3 attempts
    """
    from departments.logistics.history_engine import has_topic_been_used, get_recent_topics
    
    # HARDCODED: Always use Dark Psychology niche for monetization alignment
    niche = "Dark Psychology"
    
    # HARDCODED: Always use dark psychology/human behavior topic
    base_topic = "A viral 'Dark Psychology' fact or a 'Human Behavior Hack' that is mind-blowing. The hook must be about reading people, lying, or influence."
    
    # Check history and avoid duplicates
    print("🔍 Checking history for duplicate topics...")
    recent_topics = get_recent_topics(10)
    
    max_attempts = 3
    draft_data = None
    
    for attempt in range(1, max_attempts + 1):
        # Generate draft with topic variation if needed
        if attempt > 1:
            print(f"   🔄 Attempt {attempt}/{max_attempts}: Generating different topic...")
            # Add variation to topic to ensure uniqueness
            topic = f"{base_topic} (Variation {attempt}: Focus on a different psychological technique or angle)"
        else:
            topic = base_topic
        
        print(f"🌐 Generating draft script about {niche} - {topic[:80]}...")
        
        # Step 1: Generate Draft
        print("   📝 Generating Draft...")
        draft_data = generate_draft_script(topic, niche, viral_titles)
        
        if not draft_data:
            if attempt < max_attempts:
                continue
            raise Exception("Draft generation failed. Check API keys and network connection.")
        
        # Check if the generated script topic has been used
        script_text = draft_data.get('script', '')
        title = draft_data.get('title', '')
        
        # Use title as topic identifier (more reliable than script text)
        if has_topic_been_used(title):
            print(f"   ⚠️ Topic already used: {title}")
            if attempt < max_attempts:
                print(f"   🔄 Trying different topic...")
                continue
            else:
                print(f"   ⚠️ All attempts used similar topics, proceeding anyway...")
                break
        else:
            print(f"   ✓ Topic is unique: {title}")
            break
    
    if not draft_data:
        raise Exception("Failed to generate unique script after 3 attempts.")
    
    print(f"   ✓ Draft generated: {len(draft_data.get('script', '').split())} words")
    
    # Step 2: Polish Script (QA Protocol)
    polished_data = polish_script(draft_data)
    
    print(f"   ✓ Final Script Ready: {len(polished_data.get('script', '').split())} words")
    
    return polished_data


if __name__ == "__main__":
    # Test the script engine
    print("=" * 60)
    print("🧪 TESTING SCRIPT ENGINE")
    print("=" * 60)
    
    try:
        script_data = generate_script()
        
        print("\n📝 Generated Script:")
        print(f"Title: {script_data.get('title', 'N/A')}")
        print(f"\nScript ({len(script_data['script'].split())} words):")
        print(script_data['script'])
        print(f"\nTags: {', '.join(script_data.get('tags', []))}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

