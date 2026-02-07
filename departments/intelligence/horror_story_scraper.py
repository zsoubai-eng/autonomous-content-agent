"""
HORROR STORY SCRAPER
Module: Scrapes real, documented horror stories from the web.

Finds proven viral horror stories and merges them with seasonal context.
0-cost alternative to LLM generation.
"""

import os
import re
import json
import random
import requests
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def get_seasonal_context() -> Dict[str, str]:
    """
    Get current seasonal context (same as horror_story_engine).
    
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
    
    # October (Halloween - PEAK SEASON)
    elif month == 10:
        seasonal_data['season'] = 'Halloween'
        seasonal_data['theme'] = 'Halloween, Fall Horror'
        seasonal_data['keywords'] = ['halloween horror', 'october horror', 'halloween true story', 'spooky stories']
        if day == 31:
            seasonal_data['special_event'] = 'Halloween'
        else:
            seasonal_data['special_event'] = 'Halloween Season'
    
    # Other months...
    else:
        seasonal_data['season'] = 'General'
        seasonal_data['theme'] = 'Horror Stories'
        seasonal_data['keywords'] = ['horror stories', 'true horror', 'mystery']
    
    return seasonal_data


def scrape_reddit_horror_stories(limit: int = 10) -> List[Dict]:
    """
    Scrape horror stories from Reddit (r/nosleep, r/creepy, r/truehorror).
    
    Args:
        limit: Number of stories to fetch
        
    Returns:
        List of story dicts with 'title', 'story', 'source', 'score'
    """
    print(f"   🔍 Scraping Reddit for horror stories...")
    
    subreddits = ['nosleep', 'creepy', 'LetsNotMeet', 'TheTruthIsHere']
    stories = []
    
    for subreddit in subreddits[:3]:  # Try top 3 subreddits
        try:
            # Use Reddit JSON API (no auth needed for public posts)
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                for post in data.get('data', {}).get('children', [])[:limit]:
                    post_data = post.get('data', {})
                    title = post_data.get('title', '')
                    selftext = post_data.get('selftext', '')
                    score = post_data.get('score', 0)
                    
                    # Skip if too short or removed
                    if not selftext or selftext in ['[removed]', '[deleted]']:
                        continue
                    
                    # Filter for good stories (60-80 words optimal for 20-25s videos)
                    word_count = len(selftext.split())
                    if 60 <= word_count <= 80 and score > 5:  # Optimized for 20-25s videos
                        # Clean text
                        selftext = re.sub(r'\[.*?\]', '', selftext)  # Remove markdown links
                        selftext = re.sub(r'http\S+', '', selftext)  # Remove URLs
                        selftext = ' '.join(selftext.split())  # Normalize whitespace
                        
                        stories.append({
                            'title': title,
                            'story': selftext,
                            'source': f'Reddit r/{subreddit}',
                            'score': score,
                            'word_count': word_count
                        })
            
        except Exception as e:
            print(f"      ⚠️ Reddit scrape failed for r/{subreddit}: {str(e)[:50]}")
            continue
    
    return stories


def get_curated_horror_stories() -> List[Dict]:
    """
    Get curated list of proven viral horror stories.
    
    These are well-known, documented horror stories that perform well.
    Seasonal context will be merged later.
    
    Returns:
        List of curated horror story dicts
    """
    curated = [
        {
            'title': 'The Vanishing Hotel',
            'story': 'In 1950, a woman checked into room 441 at the President Hotel in Kansas City. She was seen entering her room that evening. The next morning, housekeeping found the room empty. Her clothes, still neatly folded, remained on the bed. Her personal belongings were untouched. The door was locked from the inside, with no signs of forced entry. A thorough search of the hotel revealed nothing. No one saw her leave. To this day, no one knows what happened to the woman in room 441.',
            'source': 'Documented historical case',
            'score': 100,
            'word_count': 95
        },
        {
            'title': 'The Dyatlov Pass Incident',
            'story': 'In February 1959, nine experienced hikers died mysteriously in the Ural Mountains. Their tent was cut from the inside, suggesting they fled in panic. They ran into sub-zero temperatures without proper clothing or shoes. Some had fatal internal injuries, but no external wounds. One victim had a fractured skull. Another had missing eyes and tongue. The case was closed as death by "compelling natural force." But what force? The mystery remains unsolved after 60 years.',
            'source': 'Historical mystery',
            'score': 100,
            'word_count': 92
        },
        {
            'title': 'The Vanishing Hitchhiker',
            'story': 'A driver picked up a young woman hitchhiking on a deserted road late at night. She was quiet, giving only an address. As they approached the requested stop, the driver turned to speak to her. The passenger seat was empty. The doors were still locked. Confused, the driver continued to the address. An elderly woman answered the door. When the driver described the hitchhiker, the woman showed a photo. "That\'s my daughter," she said. "She died on that road five years ago tonight."',
            'source': 'Urban legend',
            'score': 90,
            'word_count': 98
        },
        {
            'title': 'The Disappearance of Flight 19',
            'story': 'In 1945, five US Navy bombers took off from Florida on a routine training mission. Over the Bermuda Triangle, the flight leader reported his compasses malfunctioning. "We don\'t know where we are," he radioed. Then silence. A rescue plane with 13 crew members was sent to find them. It also vanished. Despite the largest sea and air search in history, no wreckage was ever found. All 27 men disappeared without a trace. The mystery remains one of aviation\'s greatest unsolved cases.',
            'source': 'Historical mystery',
            'score': 95,
            'word_count': 96
        },
        {
            'title': 'The Mary Celeste',
            'story': 'In 1872, the ship Mary Celeste was discovered adrift in the Atlantic Ocean. The crew of ten had vanished completely. Food was still warm on the table. The ship\'s cargo of alcohol was intact and untouched. Personal belongings remained in the cabins. The lifeboat was missing, but the ship showed no signs of damage or struggle. The last log entry was normal. What could have caused an entire crew to abandon a perfectly seaworthy ship? To this day, no one knows what happened to the ten people aboard.',
            'source': 'Historical mystery',
            'score': 90,
            'word_count': 99
        },
        {
            'title': 'The Roanoke Colony',
            'story': 'In 1590, an entire colony of 115 people vanished from Roanoke Island without a trace. When Governor White returned from England, he found the settlement empty. The only clue was the word "CROATOAN" carved into a tree. No bodies were found. No signs of struggle or attack. The houses were dismantled, suggesting a planned departure. But where did they go? The mystery of the Lost Colony remains unsolved after 400 years, making it one of America\'s greatest historical enigmas.',
            'source': 'Historical mystery',
            'score': 95,
            'word_count': 88
        },
        {
            'title': 'The Hinterkaifeck Murders',
            'story': 'In 1922, six people were brutally murdered at a remote German farm. The killer had lived in the attic for days before the murders, eating the family\'s food and watching them. Strange footprints in the snow led to the house, but none led away. The family reported hearing footsteps in the attic, but searches found nothing. Days later, they were all found dead. The case was never solved, and the farm was demolished. The killer\'s identity remains unknown.',
            'source': 'True crime mystery',
            'score': 85,
            'word_count': 95
        },
        {
            'title': 'The Sodder Children',
            'story': 'In 1945, a fire destroyed the Sodder family home on Christmas Eve. Five children, ages 5 to 14, were never found. No remains were discovered in the ashes, despite the fire being contained. The parents believed their children were kidnapped before the fire. Witnesses reported seeing the children after the fire started. The case remains open, and the children were never found. The family searched for decades, but the mystery endures.',
            'source': 'True crime mystery',
            'score': 88,
            'word_count': 92
        },
        {
            'title': 'The Isdal Woman',
            'story': 'In 1970, a woman\'s body was found burned beyond recognition in Norway. Her identity remains unknown after 50 years. She had removed all labels from her clothes and cut off her fingerprints. Multiple fake passports were found nearby. She spoke several languages and had traveled extensively. Was she a spy? A criminal? The case is still unsolved, and her true identity may never be known.',
            'source': 'True crime mystery',
            'score': 85,
            'word_count': 87
        },
        {
            'title': 'The Tamam Shud Case',
            'story': 'In 1948, an unidentified man was found dead on an Australian beach. He was well-dressed but had no identification. A scrap of paper with "Tamam Shud" was found in his pocket. The phrase means "ended" in Persian. A code was found in a book, but it was never deciphered. His identity and cause of death remain unknown. The case is considered one of Australia\'s most baffling mysteries.',
            'source': 'True crime mystery',
            'score': 90,
            'word_count': 89
        }
    ]
    
    return curated


def filter_good_stories(stories: List[Dict]) -> List[Dict]:
    """
    Filter stories for quality (good length, structure, engagement potential).
    
    Criteria:
    - 80-120 words (optimal for 30-60s read)
    - Has narrative structure (not just list)
    - Contains tension/mystery elements
    - Not too explicit (YouTube-safe)
    
    Args:
        stories: List of story dicts
        
    Returns:
        Filtered list of good stories
    """
    good_stories = []
    
    for story in stories:
        story_text = story.get('story', '')
        word_count = len(story_text.split())
        
        # Length filter (60-80 words optimal for 20-25s videos - proven best performance)
        if not (60 <= word_count <= 80):
            continue
        
        # Structure filter (must have narrative elements)
        has_narrative = any(word in story_text.lower() for word in [
            'when', 'then', 'suddenly', 'after', 'before', 'during', 'while'
        ])
        if not has_narrative:
            continue
        
        # Tension filter (must have mystery/scary elements)
        has_tension = any(word in story_text.lower() for word in [
            'mystery', 'disappeared', 'vanished', 'strange', 'creepy', 'scary',
            'unknown', 'unexplained', 'mysterious', 'horror', 'fear'
        ])
        if not has_tension:
            continue
        
        # YouTube-safe filter (no explicit content)
        explicit_words = ['kill', 'murder', 'blood', 'death', 'die']
        has_explicit = any(word in story_text.lower() for word in explicit_words)
        if has_explicit and story_text.lower().count('kill') > 2:
            continue  # Too explicit
        
        good_stories.append(story)
    
    return good_stories


def merge_seasonal_context(story: Dict, seasonal: Dict) -> Dict:
    """
    Merge scraped story with seasonal context.
    
    Adds seasonal elements to title/story naturally.
    
    Args:
        story: Story dict with 'title', 'story', 'source'
        seasonal: Seasonal context dict
        
    Returns:
        Story dict with seasonal elements merged
    """
    title = story.get('title', '')
    story_text = story.get('story', '')
    source = story.get('source', '')
    
    # Try to add seasonal context to title
    seasonal_title = title
    if seasonal.get('special_event'):
        # Try to incorporate special event
        if 'christmas' in seasonal.get('special_event', '').lower():
            if 'christmas' not in title.lower() and 'holiday' not in title.lower():
                seasonal_title = f"{title} (Christmas Horror)"
        elif 'halloween' in seasonal.get('special_event', '').lower():
            if 'halloween' not in title.lower():
                seasonal_title = f"{title} (Halloween Horror)"
    
    # Add seasonal hook to story if possible
    seasonal_story = story_text
    if seasonal.get('special_event'):
        # Try to add time anchor at beginning
        if not any(word in story_text[:50].lower() for word in ['on', 'during', 'in', 'at']):
            # Add seasonal time anchor
            if 'christmas' in seasonal.get('special_event', '').lower():
                seasonal_story = f"On {seasonal.get('special_event', 'Christmas Eve')}, {story_text.lower()}"
            elif 'halloween' in seasonal.get('special_event', '').lower():
                seasonal_story = f"On Halloween night, {story_text.lower()}"
    
    # Update tags with seasonal keywords
    tags = story.get('tags', ['horror stories', 'true horror', 'scary stories'])
    tags.extend(seasonal.get('keywords', [])[:3])
    
    return {
        'title': seasonal_title[:60],  # YouTube title limit
        'story': seasonal_story[:500],  # Limit length
        'source': source,
        'tags': list(set(tags)),  # Remove duplicates
        'original_title': title,
        'seasonal_merged': True
    }


def scrape_horror_stories(limit: int = 20) -> List[Dict]:
    """
    Get horror stories from curated list and web scraping.
    
    Strategy:
    1. Use curated proven viral stories (guaranteed quality)
    2. Supplement with Reddit scraping (real, fresh stories)
    3. Filter for quality
    
    Args:
        limit: Number of stories to get
        
    Returns:
        List of filtered, good horror stories
    """
    print(f"🔍 Gathering horror stories (curated + web scraping)...")
    
    all_stories = []
    
    # Start with curated proven stories (guaranteed quality, 0-cost)
    curated_stories = get_curated_horror_stories()
    all_stories.extend(curated_stories)
    print(f"   ✓ Loaded {len(curated_stories)} curated proven stories")
    
    # Try scraping from Reddit (supplement with fresh content)
    try:
        reddit_stories = scrape_reddit_horror_stories(limit=10)
        if reddit_stories:
            all_stories.extend(reddit_stories)
            print(f"   ✓ Scraped {len(reddit_stories)} stories from Reddit")
    except Exception as e:
        print(f"   ⚠️ Reddit scraping failed: {str(e)[:50]}")
    
    # Filter for quality (curated stories already filtered, but filter Reddit ones)
    if len(all_stories) > len(curated_stories):
        # Only filter non-curated stories
        reddit_only = [s for s in all_stories if s.get('source', '').startswith('Reddit')]
        filtered_reddit = filter_good_stories(reddit_only)
        all_stories = curated_stories + filtered_reddit
    
    print(f"   ✓ Total: {len(all_stories)} good horror stories available")
    
    return all_stories


def get_horror_story_scraped(max_retries: int = 10, published_titles: List[str] = None) -> Optional[Dict]:
    """
    Get a scraped horror story, merged with seasonal context.
    
    Checks history AND published_titles to avoid duplicates. Retries if all stories are duplicates.
    
    Args:
        max_retries: Maximum retries if all stories are duplicates
        published_titles: List of published titles to avoid (from daily_content_generator)
        
    Returns:
        Story dict with seasonal context merged, or None if no good stories found
    """
    from departments.logistics.history_engine import _load_history
    
    # Get seasonal context
    seasonal = get_seasonal_context()
    
    # Get stories (curated + scraped)
    stories = scrape_horror_stories(limit=20)
    
    if not stories:
        print("   ⚠️ No good stories found")
        return None
    
    # Check history for duplicates
    history = _load_history()
    used_titles = {entry.get('title', '').lower().strip() for entry in history}
    used_topics = {entry.get('topic', '').lower().strip()[:100] for entry in history}
    
    # Also check published_titles if provided
    if published_titles:
        published_lower = {title.lower().strip() for title in published_titles}
        used_titles.update(published_lower)
    
    # Try to find non-duplicate story
    for attempt in range(max_retries):
        # Filter out duplicates
        available_stories = []
        for story in stories:
            title_lower = story.get('title', '').lower().strip()
            story_lower = story.get('story', '').lower().strip()[:100]
            original_title = story.get('original_title', title_lower)
            
            # Check if duplicate (check both original and seasonal title)
            is_duplicate = (
                title_lower in used_titles or
                original_title in used_titles or
                story_lower in used_topics or
                any(title_lower in used_title for used_title in used_titles if len(used_title) > 10) or
                any(used_topic in story_lower for used_topic in used_topics if len(used_topic) > 20)
            )
            
            if not is_duplicate:
                available_stories.append(story)
        
        if available_stories:
            # Select random good story
            selected_story = random.choice(available_stories)
            
            # Merge with seasonal context
            merged_story = merge_seasonal_context(selected_story, seasonal)
            
            print(f"   ✓ Selected story: {merged_story.get('title', 'N/A')}")
            print(f"   ✓ Seasonal context merged: {seasonal.get('theme', 'N/A')}")
            print(f"   ✓ Source: {selected_story.get('source', 'N/A')}")
            
            return merged_story
        else:
            if attempt < max_retries - 1:
                print(f"   ⚠️ All stories are duplicates (attempt {attempt + 1}/{max_retries}), trying different selection...")
                # Shuffle and try again
                random.shuffle(stories)
            else:
                print(f"   ⚠️ All available stories are duplicates after {max_retries} attempts")
                return None
    
    return None


if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("🧪 TESTING HORROR STORY SCRAPER")
    print("=" * 60)
    
    story = get_horror_story_scraped()
    if story:
        print(f"\nTitle: {story.get('title', 'N/A')}")
        print(f"\nStory:\n{story.get('story', 'N/A')[:200]}...")
        print(f"\nSource: {story.get('source', 'N/A')}")
        print(f"\nTags: {', '.join(story.get('tags', [])[:5])}")
    else:
        print("\n❌ No story found")
