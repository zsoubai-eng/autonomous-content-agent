"""
THE AUTONOMOUS SCHEDULER
Orchestrates the entire viral factory: Scrape → Generate → Schedule → Publish

Your role: Just say "schedule the publish"
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from departments.intelligence.horror_scraper import scrape_viral_horror_titles
from departments.intelligence.horror_story_engine import generate_horror_story


def autonomous_weekly_batch(num_videos: int = 7, publish_times: List[str] = None):
    """
    Autonomous weekly batch: Scrape viral titles → Generate videos → Schedule publish.
    
    This is the "one-command" pipeline that runs the entire factory.
    
    Args:
        num_videos: Number of videos to generate (default: 7 for daily posting)
        publish_times: List of publish times in "HH:MM" format (default: channel schedule)
        
    Returns:
        Dict with schedule and file paths
    """
    print("=" * 60)
    print("🤖 AUTONOMOUS VIRAL FACTORY - STARTING")
    print("=" * 60)
    
    # Default publish schedule (based on @TrueHorrorStories-w9s channel)
    if not publish_times:
        publish_times = ["07:30", "14:00", "20:00", "22:30"]
    
    # Step 1: Scrape viral horror titles
    print("\n[STEP 1/4] 🔍 Scraping viral horror titles...")
    viral_titles = scrape_viral_horror_titles(min_views=50000, limit=num_videos * 2)
    
    if not viral_titles:
        print("❌ ERROR: No viral titles found. Aborting.")
        return None
    
    print(f"✅ Scraped {len(viral_titles)} viral titles")
    
    # Step 2: Generate horror stories (using existing engine)
    print("\n[STEP 2/4] 📖 Generating horror stories...")
    generated_stories = []
    
    for i in range(1, min(num_videos, len(viral_titles)) + 1):
        viral_item = viral_titles[i-1]
        print(f"\n   Story {i}/{num_videos}: Inspired by '{viral_item['title'][:50]}...'")
        
        try:
            # Generate story using existing engine (no viral_inspiration param)
            story_data = generate_horror_story()
            
            # Add metadata
            story_data['viral_source'] = viral_item
            story_data['video_number'] = i
            
            generated_stories.append(story_data)
            print(f"   ✅ Generated: {story_data.get('title', 'Untitled')}")
            
        except Exception as e:
            print(f"   ❌ Failed to generate story {i}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if not generated_stories:
        print("❌ ERROR: No stories generated. Aborting.")
        return None
    
    print(f"\n✅ Generated {len(generated_stories)} horror stories")
    
    # Step 3: Render videos using main.py's horror factory
    print("\n[STEP 3/4] 🎬 Rendering videos (this will take 2-3 hours)...")
    
    # Import after path setup
    import main
    
    rendered_videos = []
    
    for i, story in enumerate(generated_stories, 1):
        try:
            print(f"\n   Rendering video {i}/{len(generated_stories)}...")
            
            # Run horror factory for this story
            # The factory will handle everything: TTS, music, rendering, etc.
            result = main.run_horror_factory(
                video_number=i,
                total_videos=len(generated_stories)
            )
            
            if result == 0:
                # Find the rendered video file
                from config.paths import SHORTS_OUTPUT_DIR
                import glob
                
                # Get most recent video
                videos = glob.glob(os.path.join(SHORTS_OUTPUT_DIR, "*.mp4"))
                if videos:
                    latest_video = max(videos, key=os.path.getctime)
                    rendered_videos.append({
                        'file_path': latest_video,
                        'story': story,
                        'video_number': i
                    })
                    print(f"   ✅ Rendered: {os.path.basename(latest_video)}")
            else:
                print(f"   ❌ Rendering failed for video {i}")
                
        except Exception as e:
            print(f"   ❌ Failed to render video {i}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if not rendered_videos:
        print("❌ ERROR: No videos rendered. Aborting.")
        return None
    
    print(f"\n✅ Rendered {len(rendered_videos)} videos")
    
    # Step 4: Schedule publish times
    print("\n[STEP 4/4] 📅 Scheduling publish times...")
    
    schedule = []
    current_date = datetime.now()
    
    # Start tomorrow
    publish_date = current_date + timedelta(days=1)
    
    time_slot_index = 0
    
    for video_item in rendered_videos:
        # Get next publish time
        publish_time = publish_times[time_slot_index % len(publish_times)]
        
        # Create datetime
        hour, minute = map(int, publish_time.split(':'))
        publish_datetime = publish_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        schedule_entry = {
            'video_number': video_item['video_number'],
            'file_path': video_item['file_path'],
            'title': video_item['story'].get('title', 'Untitled'),
            'publish_datetime': publish_datetime.isoformat(),
            'publish_time_str': publish_datetime.strftime('%Y-%m-%d %H:%M'),
            'story_data': video_item['story']
        }
        
        schedule.append(schedule_entry)
        
        print(f"   📅 Video {video_item['video_number']}: {publish_datetime.strftime('%a %b %d, %H:%M')}")
        
        # Move to next time slot
        time_slot_index += 1
        
        # If we've used all time slots for today, move to next day
        if time_slot_index % len(publish_times) == 0:
            publish_date += timedelta(days=1)
    
    # Save schedule to file
    schedule_file = "autonomous_schedule.json"
    with open(schedule_file, 'w') as f:
        json.dump(schedule, f, indent=2)
    
    print(f"\n✅ Schedule saved to: {schedule_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ AUTONOMOUS FACTORY COMPLETE")
    print("=" * 60)
    print(f"   Videos Generated: {len(rendered_videos)}")
    print(f"   Schedule File: {schedule_file}")
    print(f"   First Publish: {schedule[0]['publish_time_str']}")
    print(f"   Last Publish: {schedule[-1]['publish_time_str']}")
    print("\n📋 NEXT STEP: Review schedule and say 'schedule the publish'")
    print("=" * 60)
    
    return {
        'schedule': schedule,
        'schedule_file': schedule_file,
        'num_videos': len(rendered_videos)
    }


def execute_scheduled_publish(schedule_file: str = "autonomous_schedule.json"):
    """
    Execute the scheduled publish: Upload videos to YouTube at scheduled times.
    
    This is what runs when you say "schedule the publish"
    
    Args:
        schedule_file: Path to the schedule JSON file
        
    Returns:
        Dict with upload results
    """
    print("=" * 60)
    print("🚀 EXECUTING SCHEDULED PUBLISH")
    print("=" * 60)
    
    if not os.path.exists(schedule_file):
        print(f"❌ ERROR: Schedule file not found: {schedule_file}")
        return None
    
    # Load schedule
    with open(schedule_file, 'r') as f:
        schedule = json.load(f)
    
    print(f"📋 Loaded schedule with {len(schedule)} videos")
    
    # Upload to YouTube with scheduled publish times
    from departments.logistics.upload_engine import upload_video
    
    upload_results = []
    
    for entry in schedule:
        print(f"\n📤 Uploading: {entry['title']}")
        print(f"   Scheduled for: {entry['publish_time_str']}")
        
        try:
            # Prepare description
            story_data = entry['story_data']
            description = f"""👻 {entry['title']}

{story_data.get('story', '')}

{story_data.get('source', 'Based on a real horror story.')}

💀 This is a TRUE horror story that will give you chills.

🔔 Subscribe for more scary horror stories every day!

💬 What did you think of this story? Let me know in the comments below!

⚠️ WARNING: This story may be disturbing for some viewers. Viewer discretion is advised.

#HorrorStories #ScaryStories #TrueHorror #HorrorShorts #CreepyStories #UrbanLegends"""
            
            # Upload with scheduled publish time
            video_id = upload_video(
                file_path=entry['file_path'],
                title=entry['title'],
                description=description,
                tags=story_data.get('tags', ['horror', 'horror stories', 'scary stories']),
                category_id="24",  # Entertainment
                horror_mode=True,
                scheduled_publish_time=entry['publish_datetime']  # This sets the scheduled time
            )
            
            if video_id:
                print(f"   ✅ Uploaded: https://www.youtube.com/watch?v={video_id}")
                upload_results.append({
                    'video_id': video_id,
                    'title': entry['title'],
                    'scheduled_time': entry['publish_time_str'],
                    'status': 'scheduled'
                })
            else:
                print(f"   ❌ Upload failed")
                upload_results.append({
                    'title': entry['title'],
                    'status': 'failed'
                })
                
        except Exception as e:
            print(f"   ❌ Upload error: {e}")
            upload_results.append({
                'title': entry['title'],
                'status': 'error',
                'error': str(e)
            })
    
    # Save results
    results_file = "upload_results.json"
    with open(results_file, 'w') as f:
        json.dump(upload_results, f, indent=2)
    
    # Summary
    successful = len([r for r in upload_results if r.get('status') == 'scheduled'])
    failed = len([r for r in upload_results if r.get('status') in ['failed', 'error']])
    
    print("\n" + "=" * 60)
    print("✅ PUBLISH EXECUTION COMPLETE")
    print("=" * 60)
    print(f"   Total Videos: {len(upload_results)}")
    print(f"   ✅ Scheduled: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   Results saved to: {results_file}")
    print("=" * 60)
    
    return {
        'results': upload_results,
        'results_file': results_file,
        'successful': successful,
        'failed': failed
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Autonomous Horror Factory")
    parser.add_argument('--generate', action='store_true', help='Generate weekly batch')
    parser.add_argument('--publish', action='store_true', help='Execute scheduled publish')
    parser.add_argument('--num-videos', type=int, default=7, help='Number of videos to generate')
    
    args = parser.parse_args()
    
    if args.generate:
        autonomous_weekly_batch(num_videos=args.num_videos)
    elif args.publish:
        execute_scheduled_publish()
    else:
        print("Usage:")
        print("  python autonomous_scheduler.py --generate [--num-videos 7]")
        print("  python autonomous_scheduler.py --publish")
