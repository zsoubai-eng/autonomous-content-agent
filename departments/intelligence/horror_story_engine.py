"""
THE HORROR STORY ENGINE
Module: Generates or finds real horror stories for YouTube Shorts.

Simplified workflow: Story → TTS Narration → Background Music → Subtitles → Publish
"""

import os
import json
import random
from typing import Dict, Optional, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
GEMINI_API_KEY_1 = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_1")
GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def get_seasonal_context() -> Dict[str, str]:
    """
    Get current seasonal context for content generation.
    
    Returns:
        Dict with 'season', 'month', 'date', 'theme', 'keywords'
    """
    now = datetime.now()
    month = now.month
    day = now.day
    
    seasonal_data = {
        'month': now.strftime('%B'),
        'date': now.strftime('%B %d, %Y'),
        'day_name': now.strftime('%A'),
    }
    
    # December (Christmas/Winter)
    if month == 12:
        seasonal_data['season'] = 'Christmas/Winter'
        seasonal_data['theme'] = 'Christmas, Winter Holidays'
        seasonal_data['keywords'] = ['christmas horror', 'winter mystery', 'holiday horror', 'christmas eve', 'december horror']
        if day == 24:
            seasonal_data['special_event'] = 'Christmas Eve'
        elif day == 25:
            seasonal_data['special_event'] = 'Christmas Day'
        elif day >= 20 and day <= 31:
            seasonal_data['special_event'] = 'Holiday Season'
    
    # January (New Year/Winter)
    elif month == 1:
        seasonal_data['season'] = 'New Year/Winter'
        seasonal_data['theme'] = 'New Year, Winter'
        seasonal_data['keywords'] = ['new year horror', 'winter mystery', 'january horror', 'winter true story']
        if day == 1:
            seasonal_data['special_event'] = 'New Year\'s Day'
        elif day == 31:
            seasonal_data['special_event'] = 'New Year\'s Eve'
    
    # February (Valentine's Day/Winter)
    elif month == 2:
        seasonal_data['season'] = 'Valentine\'s Day/Winter'
        seasonal_data['theme'] = 'Valentine\'s Day, Winter'
        seasonal_data['keywords'] = ['valentine horror', 'winter mystery', 'february horror', 'love gone wrong']
        if day == 14:
            seasonal_data['special_event'] = 'Valentine\'s Day'
    
    # October (Halloween - PEAK SEASON)
    elif month == 10:
        seasonal_data['season'] = 'Halloween'
        seasonal_data['theme'] = 'Halloween, Fall Horror'
        seasonal_data['keywords'] = ['halloween horror', 'october horror', 'halloween true story', 'spooky stories']
        if day == 31:
            seasonal_data['special_event'] = 'Halloween'
        else:
            seasonal_data['special_event'] = 'Halloween Season'
    
    # November (Thanksgiving/Fall)
    elif month == 11:
        seasonal_data['season'] = 'Thanksgiving/Fall'
        seasonal_data['theme'] = 'Thanksgiving, Fall'
        seasonal_data['keywords'] = ['thanksgiving horror', 'fall mystery', 'november horror']
        if day >= 20 and day <= 30:
            seasonal_data['special_event'] = 'Thanksgiving Week'
    
    # Spring (March-May)
    elif month in [3, 4, 5]:
        seasonal_data['season'] = 'Spring'
        seasonal_data['theme'] = 'Spring'
        seasonal_data['keywords'] = ['spring horror', 'spring mystery', f'{now.strftime("%B").lower()} horror']
    
    # Summer (June-August)
    elif month in [6, 7, 8]:
        seasonal_data['season'] = 'Summer'
        seasonal_data['theme'] = 'Summer'
        seasonal_data['keywords'] = ['summer horror', 'summer mystery', f'{now.strftime("%B").lower()} horror']
    
    # Fall (September)
    elif month == 9:
        seasonal_data['season'] = 'Fall'
        seasonal_data['theme'] = 'Fall'
        seasonal_data['keywords'] = ['fall horror', 'fall mystery', 'september horror']
    
    else:
        seasonal_data['season'] = 'General'
        seasonal_data['theme'] = 'Horror Stories'
        seasonal_data['keywords'] = ['horror stories', 'true horror', 'mystery']
    
def get_niche_rotation() -> Dict:
    """
    Returns a random trending niche for business attractivity.
    Rotates through Horror, Politics, Business, and Sports.
    """
    niches = [
        {
            "category": "Classic Mystery",
            "focus": "Identity mimcs, glitches, or urban legends",
            "keywords": ["POV", "Mimic", "Secret", "Scary"]
        },
        {
            "category": "Political Dark Secrets",
            "focus": "Vanished whistleblowers, secret summits, or historical conspiracies",
            "keywords": ["Classified", "Government", "Evidence", "Cover-up"]
        },
        {
            "category": "Corporate Horror",
            "focus": "Cursed bankruptcies, billionaire hideouts, or corporate espionage gone wrong",
            "keywords": ["Business", "Billionaire", "Bankruptcy", "Corporate"]
        },
        {
            "category": "Sports Enigmas",
            "focus": "Athletes who vanished mid-game, cursed stadiums, or rigged occult games",
            "keywords": ["Stadium", "Athlete", "Mystery", "Unexplained"]
        }
    ]
    return random.choice(niches)

def get_seasonal_context() -> Dict[str, str]:
    """
    Get current seasonal context for content generation.
    """
    now = datetime.now()
    month = now.month
    day = now.day
    
    seasonal_data = {
        'month': now.strftime('%B'),
        'date': now.strftime('%B %d, %Y'),
        'day_name': now.strftime('%A'),
        'theme': 'General Trivia',
        'season': 'General',
        'keywords': ['mystery', 'true story', 'unexplained']
    }
    
    # December (Christmas/Winter)
    if month == 12:
        seasonal_data['season'] = 'Christmas/Winter'
        seasonal_data['theme'] = 'Christmas, Winter Holidays'
    elif month == 1:
        seasonal_data['season'] = 'New Year/Winter'
        seasonal_data['theme'] = 'New Year, Winter'
    
    return seasonal_data


def generate_horror_story_cerebras(time_window: str = None, horror_type_guidance: str = None, used_topics: str = None, trend_guidance: str = None, niche: Dict = None) -> Optional[Dict]:
    """
    Generate a real horror story using Cerebras API.
    
    Args:
        time_window: Time window (morning/afternoon/evening/night)
        horror_type_guidance: Specific guidance for horror type
        used_topics: String list of recently used topics to avoid repetition
        trend_guidance: Social media trend guidance (e.g. 'The Mimic Trend', 'Reality Glitches')
    """
    if not CEREBRAS_API_KEY:
        return None
    
    try:
        import requests
        
        # Get seasonal context
        seasonal = get_seasonal_context()
        
        seasonal_context = f"""
SEASONAL CONTEXT (IMPORTANT - MERGE THIS WITH THE STORY):
- Current Date: {seasonal['date']}
- Season/Theme: {seasonal['theme']}
- Special Event: {seasonal.get('special_event', 'None')}

INSTRUCTIONS:
- If possible, set the story during {seasonal['season']} or on {seasonal.get('special_event', seasonal['month'])}
- Naturally incorporate {seasonal['theme']} elements into the story
- Use seasonal context to make the story more relevant and engaging
"""
        
        # Add time-based horror guidance if provided
        time_guidance = ""
        if horror_type_guidance:
            time_guidance = f"""
TIME-BASED CONTENT GUIDANCE (CRITICAL):
{horror_type_guidance}

IMPORTANT: Match the story intensity and type to the time window. This is essential for viewer engagement.
"""
        
        # Add social media trend guidance if provided
        trend_context = ""
        if trend_guidance:
            trend_context = f"""
SOCIAL MEDIA TRENDING FOCUS (CRITICAL):
Current Trend focus: {trend_guidance}

INSTRUCTION: Align the story elements, hook, or atmosphere with this trend to maximize viral potential.
"""
        
        # niche context
        niche_context = ""
        if niche:
            niche_context = f"""
TARGET CATEGORY: {niche['category']}
FOCUS AREA: {niche['focus']}
SMART KEYWORDS TO INCLUDE: {', '.join(niche['keywords'])}
"""

        # Banned phrases to prevent repetition
        # Only ban winter phrases if we are NOT doing a Frozen Money niche
        banned_phrases = ["Dyatlov", "Ural Mountains", "Hiking"]
        if niche and "Winter" not in niche.get('category', ''):
             banned_phrases.extend(["Winter", "Chill", "Frozen", "Snow"])
        
        prompt = f"""You are a professional scriptwriter and researcher. Generate a SCARY, TRUE-CRIME or MYSTERY story optimized for YouTube Shorts (13 to 14 seconds read).

{seasonal_context}{time_guidance}{trend_context}{niche_context}

BANNED WORDS (DO NOT USE THESE): {', '.join(banned_phrases)}

ALREADY USED TOPICS (DO NOT REPEAT):
{used_topics if used_topics else 'None.'}

REQUIREMENTS:
1. Strictly 40-50 words. Exactly 14 seconds at 160 WPM.
2. Use the "Smart Keywords" provided above to ensure business-attractive SEO.
3. Hook structure: Pattern interrupt → Context → Climax → Infinite Loop.
4. MUST be a NEW topic unrelated to the banned words.
5. If category is BUSINESS/POLITICS/SPORTS, tell a DARK, MYSTERIOUS fact or scandal.

Return ONLY valid JSON in this format:
{{
    "title": "Intriguing mystery title reflecting the TARGET CATEGORY (max 60 chars)",
    "story": "The full horror story text, 40-50 words (Exactly 14 seconds). Include seasonal context naturally. MUST have looping ending.",
    "source": "Brief mention of where this story comes from",
    "tags": ["horror", "horror stories", "scary stories", "true horror", "urban legends", "creepy", "youtube shorts"] + {seasonal['keywords']}
}}

Remember: Return ONLY the JSON object. No explanations."""
        
        api_url = "https://api.cerebras.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {CEREBRAS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a horror story writer specializing in real, documented horror stories. Always return ONLY valid JSON. Never add conversational text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.9,
            "max_tokens": 1000
        }
        
        print("   🧠 Generating horror story with Cerebras...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=60)
        
        if response.status_code != 200:
            raise Exception(f"Cerebras API returned status {response.status_code}: {response.text}")
        
        result = response.json()
        raw_text = result['choices'][0]['message']['content'].strip()
        
        # Clean and parse JSON
        import json
        import re
        
        # Remove markdown
        raw_text = re.sub(r'```json\s*', '', raw_text)
        raw_text = re.sub(r'```\s*', '', raw_text)
        raw_text = re.sub(r'```', '', raw_text)
        
        # Find JSON object
        first_brace = raw_text.find('{')
        last_brace = raw_text.rfind('}')
        if first_brace != -1 and last_brace != -1:
            json_str = raw_text[first_brace:last_brace + 1]
            story_data = json.loads(json_str)
            
            # Ensure 'script' field exists (map 'story' to 'script' if needed)
            if 'story' in story_data and 'script' not in story_data:
                story_data['script'] = story_data['story']
            
            return story_data
        else:
            raise Exception("No JSON object found in response")
        
    except Exception as e:
        print(f"⚠️ Cerebras failed: {e}")
        return None


def generate_horror_story_gemini(api_key: str = None, time_window: str = None, horror_type_guidance: str = None, used_topics: str = None, trend_guidance: str = None, niche: Dict = None) -> Optional[Dict]:
    """
    Generate a horror story using Gemini API.
    
    Args:
        api_key: Google Gemini API Key
        time_window: Time window (morning/afternoon/evening/night)
        horror_type_guidance: Specific guidance for horror type
        used_topics: String list of recently used topics to avoid repetition
        trend_guidance: Social media trend guidance
        niche: The specific business/news niche to target
    """
    """Generate horror story using Gemini."""
    if not api_key:
        api_key = GEMINI_API_KEY_1
    if not api_key:
        return None
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
        except:
            model = genai.GenerativeModel('gemini-pro')
        
        # Get seasonal context
        seasonal = get_seasonal_context()
        
        seasonal_context = f"""
SEASONAL CONTEXT (IMPORTANT - MERGE THIS WITH THE STORY):
- Current Date: {seasonal['date']}
- Season/Theme: {seasonal['theme']}
- Special Event: {seasonal.get('special_event', 'None')}

INSTRUCTIONS:
- If possible, set the story during {seasonal['season']} or on {seasonal.get('special_event', seasonal['month'])}
- Naturally incorporate {seasonal['theme']} elements into the story
- Use seasonal context to make the story more relevant and engaging
"""
        
        # Add time-based horror guidance if provided
        time_guidance = ""
        if horror_type_guidance:
            time_guidance = f"""
TIME-BASED CONTENT GUIDANCE (CRITICAL):
{horror_type_guidance}

IMPORTANT: Match the story intensity and type to the time window. This is essential for viewer engagement.
"""
        
        # Add social media trend guidance if provided
        trend_context = ""
        if trend_guidance:
            trend_context = f"""
SOCIAL MEDIA TRENDING FOCUS (CRITICAL):
Current Trend focus: {trend_guidance}

INSTRUCTION: Align the story elements, hook, or atmosphere with this trend to maximize viral potential.
"""
        
        # niche context
        niche_context = ""
        if niche:
            niche_context = f"""
TARGET CATEGORY: {niche['category']}
FOCUS AREA: {niche['focus']}
SMART KEYWORDS TO INCLUDE: {', '.join(niche['keywords'])}
"""

        # Banned phrases to prevent repetition
        # Only ban winter phrases if we are NOT doing a Frozen Money niche
        banned_phrases = ["Dyatlov", "Ural Mountains", "Hiking"]
        if niche and "Winter" not in niche.get('category', ''):
             banned_phrases.extend(["Winter", "Chill", "Frozen", "Snow"])
        
        prompt = f"""You are a professional scriptwriter and researcher. Generate a SCARY, TRUE-CRIME or MYSTERY story optimized for YouTube Shorts (thirteen to fourteen seconds read).

{seasonal_context}{time_guidance}{trend_context}{niche_context}

BANNED WORDS (DO NOT USE THESE): {', '.join(banned_phrases)}

ALREADY USED TOPICS (DO NOT REPEAT):
{used_topics if used_topics else 'None.'}

REQUIREMENTS:
1. Strictly 40-50 words. Exactly 14 seconds at 160 WPM.
2. Use the "Smart Keywords" provided above to ensure business-attractive SEO.
3. Hook structure: Pattern interrupt → Context → Climax → Infinite Loop.
4. MUST be a NEW topic unrelated to the banned words.
5. If category is BUSINESS/POLITICS/SPORTS, tell a DARK, MYSTERIOUS fact or scandal.
6. **HOOK STRUCTURE (CRITICAL - First 3 seconds)**:
   - 0 to 2 seconds: Pattern interrupt ("They still haven't found...", "This hotel erased people...")
   - 2 to 3 seconds: Context ("Christmas Eve, 1992.", "In 1950...")
   - 3 seconds plus: Build tension → Reveal → Twist
7. **LOOPING ENDING**: Last sentence should flow into the first sentence when looped.
8. Naturally incorporate the seasonal context ({seasonal['theme']}) into the story if possible.

Return ONLY valid JSON in this format:
{{
    "title": "Intriguing mystery title reflecting the TARGET CATEGORY (max 60 chars)",
    "story": "The full horror story text, 40-50 words (Exactly 14 seconds). Include seasonal context naturally. MUST have looping ending.",
    "source": "Brief mention of where this story comes from",
    "tags": ["horror", "mystery", "true crime", "documentary"]
}}

Remember: Return ONLY the JSON object. No explanations."""
        
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Clean and parse JSON
        import json
        import re
        
        # Remove markdown
        raw_text = re.sub(r'```json\s*', '', raw_text)
        raw_text = re.sub(r'```\s*', '', raw_text)
        raw_text = re.sub(r'```', '', raw_text)
        
        # Find JSON object
        first_brace = raw_text.find('{')
        last_brace = raw_text.rfind('}')
        if first_brace != -1 and last_brace != -1:
            json_str = raw_text[first_brace:last_brace + 1]
            story_data = json.loads(json_str)
            
            # Ensure 'script' field exists (map 'story' to 'script' if needed)
            if 'story' in story_data and 'script' not in story_data:
                story_data['script'] = story_data['story']
            
            return story_data
        else:
            raise Exception("No JSON object found in response")
        
    except Exception as e:
        print(f"⚠️ Gemini failed: {e}")
        return None


def generate_horror_story_groq(time_window: str = None, horror_type_guidance: str = None, used_topics: str = None, trend_guidance: str = None, niche: Dict = None) -> Optional[Dict]:
    """
    Generate a real horror story using Groq API.
    
    Args:
        time_window: Time window (morning/afternoon/evening/night)
        horror_type_guidance: Specific guidance for horror type
        used_topics: String list of recently used topics to avoid repetition
        trend_guidance: Social media trend guidance
        niche: The specific business/news niche to target
    """
    """Generate horror story using Groq."""
    if not GROQ_API_KEY:
        return None
    
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        # Get seasonal context
        seasonal = get_seasonal_context()
        
        seasonal_context = f"""
SEASONAL CONTEXT (IMPORTANT - MERGE THIS WITH THE STORY):
- Current Date: {seasonal['date']}
- Season/Theme: {seasonal['theme']}
- Special Event: {seasonal.get('special_event', 'None')}

INSTRUCTIONS:
- If possible, set the story during {seasonal['season']} or on {seasonal.get('special_event', seasonal['month'])}
- Naturally incorporate {seasonal['theme']} elements into the story
- Use seasonal context to make the story more relevant and engaging
"""
        
        # Add time-based horror guidance if provided
        time_guidance = ""
        if horror_type_guidance:
            time_guidance = f"""
TIME-BASED CONTENT GUIDANCE (CRITICAL):
{horror_type_guidance}

IMPORTANT: Match the story intensity and type to the time window. This is essential for viewer engagement.
"""
        
        # Add social media trend guidance if provided
        trend_context = ""
        if trend_guidance:
            trend_context = f"""
SOCIAL MEDIA TRENDING FOCUS (CRITICAL):
Current Trend focus: {trend_guidance}

INSTRUCTION: Align the story elements, hook, or atmosphere with this trend to maximize viral potential.
"""
        
        # niche context
        niche_context = ""
        if niche:
            niche_context = f"""
TARGET CATEGORY: {niche['category']}
FOCUS AREA: {niche['focus']}
SMART KEYWORDS TO INCLUDE: {', '.join(niche['keywords'])}
"""

        # Banned phrases to prevent repetition
        # Only ban winter phrases if we are NOT doing a Frozen Money niche
        banned_phrases = ["Dyatlov", "Ural Mountains", "Hiking"]
        if niche and "Winter" not in niche.get('category', ''):
             banned_phrases.extend(["Winter", "Chill", "Frozen", "Snow"])
        
        prompt = f"""You are a professional scriptwriter and researcher. Generate a SCARY, TRUE-CRIME or MYSTERY story optimized for YouTube Shorts (thirteen to fourteen seconds read).

{seasonal_context}{time_guidance}{trend_context}{niche_context}

BANNED WORDS (DO NOT USE THESE): {', '.join(banned_phrases)}

ALREADY USED TOPICS (DO NOT REPEAT):
{used_topics if used_topics else 'None.'}

REQUIREMENTS:
1. Strictly 40-50 words. Exactly 14 seconds at 160 WPM.
2. Use the "Smart Keywords" provided above to ensure business-attractive SEO.
3. Hook structure: Pattern interrupt → Context → Climax → Infinite Loop.
4. MUST be a NEW topic unrelated to the banned words.
5. If category is BUSINESS/POLITICS/SPORTS, tell a DARK, MYSTERIOUS fact or scandal.
6. **HOOK STRUCTURE (CRITICAL - First 3 seconds)**:
   - 0 to 2 seconds: Pattern interrupt ("They still haven't found...", "This hotel erased people...")
   - 2 to 3 seconds: Context ("Christmas Eve, 1992.", "In 1950...")
   - 3 seconds plus: Build tension → Reveal → Twist
7. **LOOPING ENDING**: Last sentence should flow into the first sentence when looped.
8. Naturally incorporate the seasonal context ({seasonal['theme']}) into the story if possible.

Return ONLY valid JSON in this format:
{{
    "title": "Intriguing mystery title reflecting the TARGET CATEGORY (max 60 chars)",
    "story": "The full horror story text, 40-50 words (Exactly 14 seconds). Include seasonal context naturally. MUST have looping ending.",
    "source": "Brief mention of where this story comes from",
    "tags": ["horror", "mystery", "true crime", "documentary"]
}}

Remember: Return ONLY the JSON object. No explanations."""
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a horror story writer. Always return ONLY valid JSON. Never add conversational text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=500
        )
        
        raw_text = response.choices[0].message.content.strip()
        
        # Clean and parse JSON
        import json
        import re
        
        # Remove markdown
        raw_text = re.sub(r'```json\s*', '', raw_text)
        raw_text = re.sub(r'```\s*', '', raw_text)
        raw_text = re.sub(r'```', '', raw_text)
        
        # Find JSON object
        first_brace = raw_text.find('{')
        last_brace = raw_text.rfind('}')
        if first_brace != -1 and last_brace != -1:
            json_str = raw_text[first_brace:last_brace + 1]
            story_data = json.loads(json_str)
            
            # Ensure 'script' field exists (map 'story' to 'script' if needed)
            if 'story' in story_data and 'script' not in story_data:
                story_data['script'] = story_data['story']
            
            return story_data
        else:
            raise Exception("No JSON object found in response")
        
    except Exception as e:
        print(f"⚠️ Groq failed: {e}")
        return None


def has_story_been_used(story_title: str, story_text: str) -> bool:
    """
    Check if a horror story has already been generated (prevent duplicates).
    
    Args:
        story_title: Title of the story
        story_text: Full text of the story
        
    Returns:
        True if story already exists, False otherwise
    """
    from departments.logistics.history_engine import _load_history
    
    history = _load_history()
    
    # Normalize for comparison
    normalized_title = story_title.lower().strip()
    # Use first 100 chars of story for comparison (to catch similar stories)
    normalized_story = story_text.lower().strip()[:100]
    
    for entry in history:
        entry_title = entry.get('title', '').lower().strip()
        entry_topic = entry.get('topic', '').lower().strip()[:100]
        
        # Check if title or story matches
        if entry_title == normalized_title:
            return True
        if entry_topic == normalized_story:
            return True
    
    return False


def generate_horror_story(time_window: str = None, horror_type_guidance: str = None, use_scraper: bool = True, max_retries: int = 5, force: bool = False, **kwargs) -> Optional[Dict]:
    """
    Orchestrates horror story generation with fallbacks and duplicate prevention.
    
    Args:
        time_window: Time window (morning/afternoon/evening/night)
        horror_type_guidance: Specific guidance for horror type
        use_scraper: Whether to try scraping first
        max_retries: Max retries for LLM generation
        force: If True, bypass duplicate check (Experimental for developers)
        
    Returns:
        Dict with 'title', 'story', 'source', 'tags'
    """
    # Try scraping first (0-cost, real stories)
    if use_scraper:
        try:
            from departments.intelligence.horror_story_scraper import get_horror_story_scraped
            # Import PUBLISHED_TITLES if available (from daily_content_generator)
            published_titles = []
            try:
                from config.published_titles import PUBLISHED_TITLES
                published_titles = PUBLISHED_TITLES
            except ImportError:
                pass
            
            scraped_story = get_horror_story_scraped(published_titles=published_titles)
            if scraped_story:
                print("✓ Horror story scraped from web (0-cost, real story)")
                return scraped_story
            else:
                print("   ⚠️ Scraping found only duplicates, falling back to LLM generation...")
        except Exception as e:
            print(f"   ⚠️ Scraping failed: {e}, falling back to LLM generation...")
    
    # Fetch recent topics to avoid repetition
    from departments.logistics.history_engine import get_recent_topics
    recent_topics = get_recent_topics(limit=10)
    used_topics_str = "\n".join([f"- {t}" for t in recent_topics])

    # Niche Selection (Business Attractivity)
    # Niche Selection (Business Attractivity)
    selected_niche = kwargs.get('niche_override')
    if not selected_niche:
        selected_niche = get_niche_rotation()
    print(f"   🎯 Target Niche: {selected_niche['category']} - {selected_niche['focus']}")

    # Fallback to LLM generation
    for attempt in range(max_retries):
        # Try Cerebras first
        story_data = generate_horror_story_cerebras(
            time_window=time_window, 
            horror_type_guidance=horror_type_guidance,
            used_topics=used_topics_str,
            trend_guidance=kwargs.get('trend_guidance'),
            niche=selected_niche
        )
        if story_data:
            title = story_data.get('title', '')
            story_text = story_data.get('story') or story_data.get('script', '')
            
            # Check if duplicate (unless forced)
            if force or not has_story_been_used(title, story_text):
                print(f"✓ Horror story generated with Cerebras{' (Forced)' if force else ''}")
                return story_data
            else:
                print(f"   ⚠️ Duplicate story detected (attempt {attempt + 1}/{max_retries}), retrying...")
                continue
        
        if GEMINI_API_KEY_1:
            story_data = generate_horror_story_gemini(
                GEMINI_API_KEY_1, 
                time_window=time_window, 
                horror_type_guidance=horror_type_guidance,
                used_topics=used_topics_str,
                trend_guidance=kwargs.get('trend_guidance'),
                niche=selected_niche
            )
            if story_data:
                title = story_data.get('title', '')
                story_text = story_data.get('story') or story_data.get('script', '')
                if force or not has_story_been_used(title, story_text):
                    print(f"✓ Horror story generated with Gemini{' (Forced)' if force else ''}")
                    return story_data
                else:
                    print(f"   ⚠️ Duplicate story detected (attempt {attempt + 1}/{max_retries}), retrying...")
                    continue
        
        if GEMINI_API_KEY_2:
            story_data = generate_horror_story_gemini(
                GEMINI_API_KEY_2, 
                time_window=time_window, 
                horror_type_guidance=horror_type_guidance,
                used_topics=used_topics_str,
                trend_guidance=kwargs.get('trend_guidance'),
                niche=selected_niche
            )
            if story_data:
                title = story_data.get('title', '')
                story_text = story_data.get('story') or story_data.get('script', '')
                if force or not has_story_been_used(title, story_text):
                    print(f"✓ Horror story generated with Gemini Key 2{' (Forced)' if force else ''}")
                    return story_data
                else:
                    print(f"   ⚠️ Duplicate story detected (attempt {attempt + 1}/{max_retries}), retrying...")
                    continue
        
        # Fallback to Groq
        story_data = generate_horror_story_groq(
            time_window=time_window, 
            horror_type_guidance=horror_type_guidance,
            used_topics=used_topics_str,
            trend_guidance=kwargs.get('trend_guidance'),
            niche=selected_niche
        )
        if story_data:
            title = story_data.get('title', '')
            story_text = story_data.get('story') or story_data.get('script', '')
            if force or not has_story_been_used(title, story_text):
                print(f"✓ Horror story generated with Groq{' (Forced)' if force else ''}")
                return story_data
            else:
                print(f"   ⚠️ Duplicate story detected (attempt {attempt + 1}/{max_retries}), retrying...")
                continue
    
    raise Exception(f"All API keys failed or all generated stories were duplicates after {max_retries} attempts.")


if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("🧪 TESTING HORROR STORY ENGINE")
    print("=" * 60)
    
    try:
        story = generate_horror_story()
        print(f"\nTitle: {story.get('title', 'N/A')}")
        print(f"\nStory:\n{story.get('story', 'N/A')}")
        print(f"\nSource: {story.get('source', 'N/A')}")
        print(f"\nTags: {', '.join(story.get('tags', []))}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
