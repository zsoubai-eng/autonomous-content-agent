"""
THE RESEARCH ENGINE
Module: Market Intelligence - Scrapes viral topics from YouTube.

Identifies winning content patterns to inform script generation.
"""

from typing import List, Dict
# Removed youtube-search-python, using googlesearch-python fallback
try:
    from youtubesearchpython import VideosSearch
    YOUTUBE_SEARCH_AVAILABLE = True
except ImportError:
    YOUTUBE_SEARCH_AVAILABLE = False


def get_viral_topics(niche: str = "Dark Psychology", min_views: int = 100000) -> List[str]:
    """
    Get viral topics by analyzing top-performing YouTube Shorts.
    
    Searches YouTube for the niche, filters by view count, and returns top viral titles.
    
    Args:
        niche: Niche to search for (default: "Dark Psychology")
        min_views: Minimum view count threshold (default: 100k)
        
    Returns:
        List of top 5 viral titles (strings)
    """
    print(f"🔍 Researching viral topics in '{niche}' niche...")
    
    try:
        # Search for YouTube Shorts in the niche
        # Use search query that targets Shorts
        search_query = f"{niche} shorts"
        
        print(f"   Searching: {search_query}")
        
        # Search YouTube (limit to 20 results to get good sample)
        try:
            videos_search = VideosSearch(search_query, limit=20)
            results = videos_search.result()
        except Exception as search_error:
            # Handle compatibility issues
            print(f"   ⚠️ Search error: {search_error}")
            # Try alternative method
            try:
                from youtubesearchpython import Search
                search = Search(search_query, limit=20)
                results = search.result()
            except:
                raise search_error
        
        if not results:
            print("   ⚠️ No search results found")
            return []
        
        # Handle different result formats
        if isinstance(results, dict):
            videos = results.get('result', [])
        elif isinstance(results, list):
            videos = results
        else:
            videos = []
        
        if not videos:
            print("   ⚠️ No videos in results")
            return []
        
        print(f"   Found {len(videos)} videos")
        
        # Extract titles and view counts
        viral_candidates = []
        
        for video in videos:
            title = video.get('title', '')
            view_count_text = video.get('viewCount', {}).get('text', '0')
            
            # Parse view count (e.g., "1.2M views" -> 1200000)
            view_count = _parse_view_count(view_count_text)
            
            if view_count >= min_views:
                viral_candidates.append({
                    'title': title,
                    'views': view_count
                })
        
        # Sort by view count (descending)
        viral_candidates.sort(key=lambda x: x['views'], reverse=True)
        
        # Get top 5 titles
        top_titles = [candidate['title'] for candidate in viral_candidates[:5]]
        
        if top_titles:
            print(f"   ✓ Found {len(top_titles)} viral topics (>100k views)")
            for i, title in enumerate(top_titles, 1):
                views = viral_candidates[i-1]['views']
                print(f"      {i}. {title[:60]}... ({views:,} views)")
        else:
            print(f"   ⚠️ No videos found with >{min_views:,} views")
            # Fallback: return top 5 titles regardless of views
            top_titles = [video.get('title', '') for video in videos[:5] if video.get('title')]
            if top_titles:
                print(f"   → Using top 5 results regardless of view count")
            else:
                # LLM Fallback: Ask LLM to simulate market research
                print(f"   → No results from scraper, using LLM fallback...")
                top_titles = _get_viral_topics_llm_fallback(niche)
        
        return top_titles
        
    except Exception as e:
        print(f"   ⚠️ Research failed: {e}")
        print("   → Continuing without viral topic data")
        return []


def _get_viral_topics_llm_fallback(niche: str) -> List[str]:
    """
    LLM Fallback: Ask LLM to simulate market research when scraper fails.
    
    Args:
        niche: Niche category
        
    Returns:
        List of 3-5 simulated viral topics
    """
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        
        prompt = f"""List 3-5 viral psychology topics that are trending right now in the '{niche}' niche. 
        
Return ONLY a simple list, one topic per line, no numbering, no explanations.
Each topic should be a short title (5-10 words) that would work as a YouTube Short title.
Focus on psychological theories, laws, or concepts that are currently popular.

Example format:
The Ben Franklin Effect Explained
Cognitive Dissonance in Relationships
How Reciprocity Controls Your Decisions"""
        
        # Try Gemini first
        if GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                try:
                    model = genai.GenerativeModel('gemini-1.5-pro')
                except:
                    try:
                        model = genai.GenerativeModel('gemini-pro')
                    except:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                
                response = model.generate_content(prompt)
                raw_text = response.text.strip()
                
                # Parse lines
                topics = [line.strip() for line in raw_text.split('\n') if line.strip() and not line.strip().startswith('#')]
                topics = topics[:5]  # Limit to 5
                
                if topics:
                    print(f"   ✓ LLM generated {len(topics)} viral topics")
                    return topics
            except:
                pass
        
        # Fallback to Groq
        if GROQ_API_KEY:
            try:
                from groq import Groq
                client = Groq(api_key=GROQ_API_KEY)
                
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a market research assistant. Return only a simple list, one topic per line."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.9,
                    max_tokens=200
                )
                
                raw_text = response.choices[0].message.content.strip()
                topics = [line.strip() for line in raw_text.split('\n') if line.strip() and not line.strip().startswith('#')]
                topics = topics[:5]
                
                if topics:
                    print(f"   ✓ LLM generated {len(topics)} viral topics")
                    return topics
            except:
                pass
        
        # Ultimate fallback: return hardcoded topics
        print("   ⚠️ LLM fallback failed, using hardcoded topics")
        return [
            "The Ben Franklin Effect Explained",
            "Cognitive Dissonance in Relationships",
            "How Reciprocity Controls Decisions",
            "The Anchoring Bias Trap",
            "Door-in-the-Face Technique"
        ]
        
    except Exception as e:
        print(f"   ⚠️ LLM fallback error: {e}")
        return []


def _parse_view_count(view_count_text: str) -> int:
    """
    Parse view count string to integer.
    
    Examples:
        "1.2M views" -> 1200000
        "500K views" -> 500000
        "50,000 views" -> 50000
        "1.5B views" -> 1500000000
    
    Args:
        view_count_text: View count string from YouTube
        
    Returns:
        Integer view count
    """
    if not view_count_text:
        return 0
    
    # Remove "views" and whitespace
    text = view_count_text.lower().replace('views', '').strip()
    
    # Remove commas
    text = text.replace(',', '')
    
    # Handle different formats
    if 'b' in text:
        # Billions
        number = float(text.replace('b', '').strip())
        return int(number * 1_000_000_000)
    elif 'm' in text:
        # Millions
        number = float(text.replace('m', '').strip())
        return int(number * 1_000_000)
    elif 'k' in text:
        # Thousands
        number = float(text.replace('k', '').strip())
        return int(number * 1_000)
    else:
        # Try to parse as integer
        try:
            return int(float(text))
        except:
            return 0


if __name__ == "__main__":
    # Test the research engine
    print("=" * 60)
    print("🧪 TESTING RESEARCH ENGINE")
    print("=" * 60)
    
    viral_topics = get_viral_topics("Dark Psychology", min_views=100000)
    
    print(f"\n📊 Top Viral Topics:")
    for i, topic in enumerate(viral_topics, 1):
        print(f"   {i}. {topic}")

