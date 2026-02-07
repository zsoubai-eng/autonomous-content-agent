"""
THE HORROR SCRAPER
Autonomous Intelligence Module: Scrapes viral horror story titles from YouTube.

Designed specifically for @TrueHorrorStories-w9s channel DNA.
"""

import os
import re
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

try:
    from youtubesearchpython import VideosSearch
    YOUTUBE_SEARCH_AVAILABLE = True
except ImportError:
    YOUTUBE_SEARCH_AVAILABLE = False


def scrape_viral_horror_titles(min_views: int = 50000, limit: int = 10) -> List[Dict]:
    """
    Scrape viral horror story titles from YouTube that match your channel's DNA.
    
    Based on analysis of @TrueHorrorStories-w9s:
    - True crime horror
    - Historical/dated stories (e.g., "1945", "1888")
    - Unsolved mysteries
    - Seasonal themes (winter, holidays)
    - Real-life tragedies
    
    Args:
        min_views: Minimum view count to consider viral (default: 50k)
        limit: Number of titles to scrape (default: 10)
        
    Returns:
        List of dicts with 'title', 'views', 'hook_type'
    """
    print("🔍 HORROR SCRAPER: Hunting for viral horror stories...")
    
    # Search queries that match your channel's DNA
    search_queries = [
        "true horror stories shorts",
        "real horror stories unsolved",
        "scary true stories real",
        "horror stories true crime",
        "creepy true stories",
        "disturbing true stories",
        "unsolved mysteries horror",
        "real life horror stories",
    ]
    
    all_candidates = []
    
    for query in search_queries:
        print(f"   Searching: {query}")
        
        try:
            if not YOUTUBE_SEARCH_AVAILABLE:
                print("   ⚠️ YouTube search library not available, using LLM fallback")
                break
                
            videos_search = VideosSearch(query, limit=20)
            results = videos_search.result()
            
            if isinstance(results, dict):
                videos = results.get('result', [])
            elif isinstance(results, list):
                videos = results
            else:
                videos = []
            
            for video in videos:
                title = video.get('title', '')
                view_count_text = video.get('viewCount', {}).get('text', '0')
                view_count = _parse_view_count(view_count_text)
                
                # Filter by view count
                if view_count >= min_views:
                    # Analyze hook type
                    hook_type = _identify_hook_type(title)
                    
                    all_candidates.append({
                        'title': title,
                        'views': view_count,
                        'hook_type': hook_type,
                        'query': query
                    })
        
        except Exception as e:
            print(f"   ⚠️ Search failed for '{query}': {e}")
            continue
    
    # Remove duplicates and sort by views
    seen_titles = set()
    unique_candidates = []
    for candidate in all_candidates:
        title_lower = candidate['title'].lower()
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_candidates.append(candidate)
    
    # Sort by views (descending)
    unique_candidates.sort(key=lambda x: x['views'], reverse=True)
    
    # Take top N
    top_candidates = unique_candidates[:limit]
    
    if top_candidates:
        print(f"   ✅ Found {len(top_candidates)} viral horror titles")
        for i, candidate in enumerate(top_candidates[:5], 1):
            print(f"      {i}. {candidate['title'][:60]}... ({candidate['views']:,} views | {candidate['hook_type']})")
    else:
        print("   ⚠️ No viral titles found, using LLM fallback")
        top_candidates = _get_horror_titles_llm_fallback(limit)
    
    return top_candidates


def _identify_hook_type(title: str) -> str:
    """
    Identify the psychological hook type used in the title.
    
    Hook types based on @TrueHorrorStories-w9s analysis:
    - DATE_LEAD: Starts with a year/date (e.g., "1945", "1888")
    - LOCATION: Mentions a specific place
    - UNSOLVED: Contains "unsolved", "mystery", "never found"
    - SHOCKING: Contains "shocking", "terrifying", "disturbing"
    - REAL_TAG: Contains "(REAL)", "(TRUE)", "(SHOCKING)"
    
    Args:
        title: Video title
        
    Returns:
        Hook type string
    """
    title_lower = title.lower()
    
    # Check for date lead (most powerful hook)
    if re.search(r'\b(19|20)\d{2}\b', title):
        return "DATE_LEAD"
    
    # Check for real/true tags
    if re.search(r'\(real\)|\(true\)|\(shocking\)', title_lower):
        return "REAL_TAG"
    
    # Check for unsolved mystery
    if any(word in title_lower for word in ['unsolved', 'mystery', 'never found', 'disappeared', 'missing']):
        return "UNSOLVED"
    
    # Check for shocking/disturbing
    if any(word in title_lower for word in ['shocking', 'terrifying', 'disturbing', 'horrifying']):
        return "SHOCKING"
    
    # Check for location
    if re.search(r'\b(in|at|from)\s+[A-Z][a-z]+', title):
        return "LOCATION"
    
    return "GENERIC"


def _get_horror_titles_llm_fallback(limit: int = 10) -> List[Dict]:
    """
    LLM Fallback: Generate horror story titles when scraper fails.
    
    Uses the channel DNA to generate titles that match the style.
    
    Args:
        limit: Number of titles to generate
        
    Returns:
        List of dicts with 'title', 'views', 'hook_type'
    """
    try:
        import google.generativeai as genai
        
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            print("   ⚠️ No Gemini API key, using hardcoded fallback")
            return _get_hardcoded_horror_titles()
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Generate {limit} viral horror story titles for YouTube Shorts.

CHANNEL DNA (based on @TrueHorrorStories-w9s):
- True crime horror and unsolved mysteries
- Historical/dated stories (e.g., "1945. A fire destroyed...", "1888. The Frozen Inn...")
- Real-life tragedies and disappearances
- Seasonal themes (winter, holidays, cold)
- Grave, intense tone (not cheap jump scares)

TITLE FORMULA:
[Year/Date] + [Event] + [Scary Element] + (OPTIONAL TAG)

Examples from the channel:
- "1945. A fire destroyed their home (REAL STORY)"
- "The Frozen Inn of 1888 (UNSOLVED MYSTERY)"
- "Christmas Eve Terror: 1992 (TRUE STORY)"
- "New Year's Nightmare: The Vanishing (SHOCKING)"

REQUIREMENTS:
1. Start with a specific year (1800s-1990s preferred)
2. Include a real-sounding location or event
3. Use tags like (REAL STORY), (UNSOLVED), (TRUE STORY), (SHOCKING)
4. Keep it under 60 characters
5. Make it feel like a documentary, not fiction

Return ONLY the titles, one per line, no numbering."""

        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Parse titles
        titles = [line.strip() for line in raw_text.split('\n') if line.strip() and not line.startswith('#')]
        titles = titles[:limit]
        
        # Convert to dict format
        candidates = []
        for title in titles:
            hook_type = _identify_hook_type(title)
            candidates.append({
                'title': title,
                'views': 100000,  # Simulated view count
                'hook_type': hook_type,
                'query': 'LLM_GENERATED'
            })
        
        print(f"   ✅ LLM generated {len(candidates)} horror titles")
        return candidates
        
    except Exception as e:
        print(f"   ⚠️ LLM fallback failed: {e}")
        return _get_hardcoded_horror_titles()


def _get_hardcoded_horror_titles() -> List[Dict]:
    """
    Ultimate fallback: Hardcoded horror titles matching channel DNA.
    
    Returns:
        List of dicts with 'title', 'views', 'hook_type'
    """
    hardcoded_titles = [
        "1987. The Cabin Disappearance (UNSOLVED)",
        "1945. The Fire That Took Them All (REAL STORY)",
        "The Frozen Lake of 1902 (TRUE HORROR)",
        "1978. They Never Came Back (SHOCKING)",
        "Christmas Eve 1991: The Vanishing (REAL)",
        "1888. The Inn That Froze Over (UNSOLVED MYSTERY)",
        "New Year's Terror: 1985 (TRUE STORY)",
        "1956. The Basement Discovery (DISTURBING)",
        "The Winter of 1899 (REAL HORROR)",
        "1973. The Hitchhiker's Last Ride (SHOCKING)",
    ]
    
    return [
        {
            'title': title,
            'views': 100000,
            'hook_type': _identify_hook_type(title),
            'query': 'HARDCODED'
        }
        for title in hardcoded_titles
    ]


def _parse_view_count(view_count_text: str) -> int:
    """Parse view count string to integer."""
    if not view_count_text:
        return 0
    
    text = view_count_text.lower().replace('views', '').replace(',', '').strip()
    
    if 'b' in text:
        return int(float(text.replace('b', '').strip()) * 1_000_000_000)
    elif 'm' in text:
        return int(float(text.replace('m', '').strip()) * 1_000_000)
    elif 'k' in text:
        return int(float(text.replace('k', '').strip()) * 1_000)
    else:
        try:
            return int(float(text))
        except:
            return 0


if __name__ == "__main__":
    # Test the scraper
    print("=" * 60)
    print("🧪 TESTING HORROR SCRAPER")
    print("=" * 60)
    
    viral_titles = scrape_viral_horror_titles(min_views=50000, limit=10)
    
    print(f"\n📊 Top Viral Horror Titles:")
    for i, item in enumerate(viral_titles, 1):
        print(f"   {i}. {item['title']}")
        print(f"      Views: {item['views']:,} | Hook: {item['hook_type']}")
