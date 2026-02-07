"""
DAILY CONTENT GENERATOR
Scrapes web for trending content, generates videos, and schedules them for optimal publishing windows.
"""

import os
import sys
import json
import re
import requests
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from departments.intelligence.horror_story_engine import generate_horror_story
from departments.intelligence.time_based_horror import get_4x_daily_schedule, get_time_based_horror_type
from departments.intelligence.title_optimizer import optimize_title
from departments.production.audio_engine import generate_audio
from departments.production.youtube_audio_engine import get_horror_background_music
from departments.production.image_search_engine import download_multiple_horror_images, download_horror_image
from departments.production.thumbnail_engine import generate_thumbnail
from departments.production.simple_render_engine import render_horror_video
from departments.logistics.upload_engine import upload_video
from departments.logistics.history_engine import log_video, has_topic_been_used, get_recent_topics
from moviepy import AudioFileClip
import tempfile

EST = pytz.timezone('US/Eastern')

from config.published_titles import PUBLISHED_TITLES
from config.paths import TEMP_DIR, SHORTS_OUTPUT_DIR, TEMP_THUMBNAILS_DIR


def scrape_trending_horror_content() -> List[Dict]:
    """
    Scrape web for trending horror/mystery content.
    
    Returns:
        List of story ideas with title, description, source
    """
    print("🔍 Scraping web for trending horror content...")
    stories = []
    
    # 1. Scrape Reddit for trending horror
    subreddits = ['nosleep', 'creepy', 'LetsNotMeet', 'TheTruthIsHere', 'UnresolvedMysteries', 'TrueCrime']
    for subreddit in subreddits[:4]:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for post in data.get('data', {}).get('children', [])[:5]:
                    post_data = post.get('data', {})
                    title = post_data.get('title', '')
                    # Filter out titles that match published ones
                    if not any(published.lower() in title.lower() for published in PUBLISHED_TITLES):
                        stories.append({
                            'title': title,
                            'source': f'Reddit r/{subreddit}',
                            'score': post_data.get('score', 0),
                            'url': post_data.get('url', '')
                        })
        except Exception as e:
            print(f"   ⚠️ Failed to scrape r/{subreddit}: {e}")
            continue
    
    print(f"   ✓ Found {len(stories)} trending stories from Reddit")
    return stories


def is_duplicate_title(title: str) -> bool:
    """
    Check if title matches any published title (including history).
    Also checks for similar titles (same core topic).
    """
    from departments.logistics.history_engine import _load_history
    
    title_lower = title.lower().strip()
    
    # Check PUBLISHED_TITLES list
    for published in PUBLISHED_TITLES:
        if title_lower in published.lower() or published.lower() in title_lower:
            return True
    
    # Check history.json for all published titles
    history = _load_history()
    for entry in history:
        published_title = entry.get('title', '').lower().strip()
        if not published_title:
            continue
        
        # Exact match
        if title_lower == published_title:
            return True
        
        # Substring match (avoid "Christmas Eve X" matching "Christmas Eve Y")
        # Only flag if core topic is the same
        title_words = set(title_lower.split())
        published_words = set(published_title.split())
        
        # If titles share 3+ significant words (ignore common words)
        common_words = {'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'and', 'or', 'but', 'story', 'stories', 'horror', 'mystery', 'mysteries', 'true', 'real', 'unsolved', 'shocking', 'case', 'incident'}
        significant_title = title_words - common_words
        significant_published = published_words - common_words
        
        if len(significant_title) > 0 and len(significant_published) > 0:
            overlap = significant_title.intersection(significant_published)
            # If 2+ significant words overlap, likely duplicate
            if len(overlap) >= 2:
                return True
    
    return False


def get_daily_publishing_schedule(start_date: datetime, num_days: int = 7) -> List[tuple]:
    """
    Get 4x daily publishing schedule with time-based horror types.
    
    Returns:
        List of (datetime, label, horror_type_dict) tuples
    """
    return get_4x_daily_schedule(start_date, num_days)


def generate_video_with_duplicate_check(video_number: int, publish_time: datetime, horror_type: Dict = None) -> Optional[Dict]:
    """Generate a video, ensuring no duplicates, with time-based horror type."""
    max_retries = 10
    
    # Get time-based horror guidance
    time_window = horror_type.get('time_window', 'evening') if horror_type else 'evening'
    horror_guidance = horror_type.get('prompt_guidance', '') if horror_type else ''
    
    for attempt in range(max_retries):
        try:
            # Generate horror story with time-based guidance
            print(f"\n[📖 HORROR STORY] Generating {time_window} horror story (attempt {attempt + 1}/{max_retries})...")
            if horror_guidance:
                print(f"   🎯 Time-based type: {horror_type.get('horror_type', 'N/A')} ({horror_type.get('intensity', 'moderate')} intensity)")
            story_data = generate_horror_story(max_retries=5, use_scraper=True, time_window=time_window, horror_type_guidance=horror_guidance)
            title = story_data.get('title', 'Horror Story')
            story_text = story_data.get('story') or story_data.get('script', '')
            
            # Check for duplicates
            if is_duplicate_title(title):
                print(f"   ⚠️ Duplicate title detected: {title}, retrying...")
                continue
            
            # Check history
            if has_topic_been_used(story_text[:200]):
                print(f"   ⚠️ Story already used, retrying...")
                continue
            
            print(f"✓ Unique story generated: {title}")
            print(f"   Length: {len(story_text.split())} words")
            
            # Optimize title
            original_title = title
            title = optimize_title(title, story_type="horror")
            if title != original_title:
                print(f"   Optimized: {title}")
            
            # Generate audio
            print("\n[🎙️ NARRATION] Generating TTS audio...")
            audio_output = os.path.join(TEMP_DIR, f"temp_audio_{video_number}.mp3")
            audio_path, subtitles = generate_audio(story_text, audio_output, script_text=story_text)
            
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            audio_clip.close()
            
            print(f"✓ Audio generated: {audio_duration:.2f}s")
            
            # Background music
            print("\n[🎵 BACKGROUND MUSIC]...")
            bg_music_path = get_horror_background_music(os.path.join(TEMP_DIR, f"temp_bg_{video_number}.mp3"), audio_duration)
            
            # Multiple images
            print("\n[🖼️ IMAGES] Downloading 6 images...")
            temp_image_dir = tempfile.mkdtemp(prefix=f"images_{video_number}_")
            image_paths = download_multiple_horror_images(
                story_text=story_text,
                story_title=title,
                output_dir=temp_image_dir,
                num_images=6,
                width=1080,
                height=1920
            )
            
            if not image_paths or len(image_paths) < 3:
                image_output = f"temp_image_{video_number}.jpg"
                fallback_image = download_horror_image(story_text, title, image_output, 1080, 1920)
                if fallback_image:
                    image_paths = [fallback_image]
            
            print(f"✓ Downloaded {len(image_paths)} images")
            
            # Thumbnail
            thumbnail_path = os.path.join(TEMP_THUMBNAILS_DIR, f"thumbnail_{video_number}.png")
            generate_thumbnail(title=title, output_path=thumbnail_path)
            
            # Render video
            print("\n[🎬 RENDERING] Creating video...")
            output_dir = "output/shorts"
            os.makedirs(output_dir, exist_ok=True)
            
            safe_title = re.sub(r'[^\w\s-]', '', title).strip()
            safe_title = re.sub(r'[-\s]+', '-', safe_title)[:50]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(SHORTS_OUTPUT_DIR, f"{safe_title}_{timestamp}.mp4")
            
            render_horror_video(
                narration_audio_path=audio_path,
                background_music_path=bg_music_path,
                image_paths=image_paths,
                output_path=output_path,
                video_duration=None,
                subtitles=subtitles,
                story_title=title
            )
            
            print(f"✓ Video rendered: {output_path}")
            
            # Description
            description = f"""👻 {title}

{story_text}

💀 This is a TRUE horror story that will give you chills.

🔔 Subscribe for more scary horror stories every day!

💬 What did you think of this story? Let me know in the comments below!

⚠️ WARNING: This story may be disturbing for some viewers. Viewer discretion is advised.

#HorrorStories #ScaryStories #TrueHorror #HorrorShorts #CreepyStories #UrbanLegends"""
            
            return {
                'video_path': output_path,
                'title': title,
                'description': description,
                'tags': story_data.get('tags', []),
                'thumbnail_path': thumbnail_path,
                'story_text': story_text[:200]
            }
            
        except Exception as e:
            print(f"   ⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                return None
            continue
    
    return None


def generate_daily_content(num_days: int = 7, start_date: Optional[datetime] = None):
    """Generate and schedule videos for next N days."""
    print("=" * 70)
    print("🎬 DAILY CONTENT GENERATOR")
    print("=" * 70)
    
    # Use provided start_date or default to today
    if start_date is None:
        start_date = datetime.now(EST)
    
    print(f"Generating videos starting from: {start_date.strftime('%A, %B %d, %Y')}")
    print(f"Number of days: {num_days}")
    print(f"Using multi-image system (6 images per video)")
    print(f"Avoiding {len(PUBLISHED_TITLES)} published titles")
    print()
    
    # Get publishing schedule
    schedule = get_daily_publishing_schedule(start_date, num_days)
    
    print(f"📅 PUBLISHING SCHEDULE ({len(schedule)} videos - 4 per day):")
    current_date = None
    for i, schedule_item in enumerate(schedule, 1):
        if len(schedule_item) == 3:
            publish_time, label, horror_type = schedule_item
        else:
            publish_time, label = schedule_item
            horror_type = get_time_based_horror_type(publish_time)
        
        if current_date != publish_time.date():
            if current_date is not None:
                print()
            print(f"   {publish_time.strftime('%A, %B %d')}:")
            current_date = publish_time.date()
        
        print(f"      {i:2d}. {publish_time.strftime('%I:%M %p %Z')} - {label} ({horror_type['intensity']} intensity)")
    print()
    
    # Scrape trending content for inspiration
    trending_stories = scrape_trending_horror_content()
    
    successful = 0
    failed = 0
    scheduled_videos = []
    
    # Generate each video
    for i, schedule_item in enumerate(schedule, 1):
        if len(schedule_item) == 3:
            publish_time, label, horror_type = schedule_item
        else:
            publish_time, label = schedule_item
            horror_type = get_time_based_horror_type(publish_time)
        
        print(f"\n{'='*70}")
        print(f"📹 GENERATING VIDEO {i}/{len(schedule)}")
        print(f"{'='*70}")
        print(f"Scheduled for: {publish_time.strftime('%A, %B %d at %I:%M %p %Z')}")
        print(f"Time Window: {horror_type['time_window']} | Type: {horror_type['horror_type']} | Intensity: {horror_type['intensity']}")
        
        video_data = generate_video_with_duplicate_check(i, publish_time, horror_type)
        
        if not video_data:
            print(f"❌ Video {i} generation failed")
            failed += 1
            continue
        
        # Try to schedule (but don't fail if upload fails)
        try:
            schedule_iso = publish_time.isoformat()
            print(f"\n📅 Scheduling video {i}...")
            
            video_id = None
            try:
                video_id = upload_video(
                    file_path=video_data['video_path'],
                    title=video_data['title'],
                    description=video_data['description'],
                    tags=video_data['tags'],
                    category_id="24",
                    horror_mode=True,
                    schedule_time=schedule_iso,
                    thumbnail_path=video_data['thumbnail_path']
                )
            except Exception as upload_error:
                print(f"   ⚠️ Upload failed: {upload_error}")
                print(f"   ✅ Video saved: {video_data['video_path']}")
                print(f"   📋 Ready for manual upload")
            
            if video_id:
                log_video(
                    topic=video_data['story_text'],
                    title=video_data['title'],
                    video_id=video_id,
                    filename=video_data['video_path']
                )
                scheduled_videos.append({
                    'video_id': video_id,
                    'title': video_data['title'],
                    'publish_time': publish_time,
                    'status': 'scheduled'
                })
                print(f"✅ Video {i} scheduled: {video_id}")
            else:
                scheduled_videos.append({
                    'video_id': None,
                    'title': video_data['title'],
                    'publish_time': publish_time,
                    'file_path': video_data['video_path'],
                    'status': 'ready_for_upload'
                })
                print(f"✅ Video {i} generated (ready for upload)")
            
            successful += 1
            
        except Exception as e:
            print(f"❌ Error with video {i}: {e}")
            failed += 1
            continue
    
    # Summary
    print(f"\n{'='*70}")
    print("✅ GENERATION COMPLETE!")
    print(f"{'='*70}")
    print(f"📊 SUMMARY:")
    print(f"   Total: {len(schedule)} videos")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    
    if scheduled_videos:
        print(f"\n📅 GENERATED VIDEOS:")
        for i, vid in enumerate(scheduled_videos, 1):
            status_icon = "📺" if vid.get('video_id') else "📁"
            print(f"   {i:2d}. {status_icon} {vid['title']}")
            print(f"       {vid['publish_time'].strftime('%A, %B %d at %I:%M %p %Z')}")
            if vid.get('video_id'):
                print(f"       🆔 {vid['video_id']}")
            print()
    
    return successful, failed


if __name__ == "__main__":
    generate_daily_content(num_days=7)
