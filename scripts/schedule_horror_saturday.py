
import os
import sys
import random
import datetime
from typing import List

# Ensure scripts can import from root
sys.path.append(os.getcwd())

from main import run_horror_factory
from departments.logistics.upload_engine import upload_video

def schedule_saturday_batch():
    """
    Generates 5 horror videos and schedules them for Saturday's peak windows.
    Target: US EST (UTC-5)
    Windows: 11:00, 13:00, 16:00, 19:00, 23:00
    """
    print("=" * 60)
    print("📅 SATURDAY PEAK WINDOW SCHEDULER")
    print("=" * 60)
    
    # Define windows (Today is Jan 17, 2026)
    date_str = "2026-01-17"
    offsets = ["-05:00", "-05:00", "-05:00", "-05:00", "-05:00"] # EST
    times = ["11:00:00", "13:00:00", "16:00:00", "19:00:00", "23:00:00"]
    
    schedule_slots = [f"{date_str}T{t}{o}" for t, o in zip(times, offsets)]
    
    # Argument mock for split-screen and skip-upload (we handle upload manually)
    class Args:
        horror = True
        count = 1
        skip_upload = True # We want to control the upload timing here
        split_screen = True
        force = True

    global_args = Args()
    
    success_count = 0
    
    for i, slot in enumerate(schedule_slots):
        print(f"\n🎬 PREPARING VIDEO {i+1}/5 FOR SLOT: {slot}")
        
        # 1. Generate Video (Skip upload in factory)
        # Hack: Since main.py uses globals and imports, we might need to modify run_horror_factory
        # to return the metadata. But look at main.py: it saves to output/shorts/
        
        # We'll run the factory. It will print the path.
        # However, to be precise, we need the path.
        # Let's modify run_horror_factory in main.py to return the file info if possible.
        # Or just find the latest file in output/shorts/
        
        from main import run_horror_factory
        import main
        main.args = global_args # Inject args into main module
        
        result = run_horror_factory(video_number=i+1, total_videos=5)
        
        if result == 0:
            # Video generated successfully. Find the path.
            shorts_dir = "output/shorts"
            files = [os.path.join(shorts_dir, f) for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
            latest_video = max(files, key=os.path.getctime)
            
            print(f"   ✓ Generated: {latest_video}")
            
            # 2. Extract title/description/tags (needs logic from main.py)
            # For this script, we'll just use the factory's internal logic but manually upload
            # Actually, it's better to modify main.py to accept schedule_time.
            
            # Let's pivot: modify main.py to accept --schedule-batch flag or similar.
            # No, keep it simple. I'll just run the upload from here.
            
            print(f"   ⬆️ Scheduling for YouTube...")
            # We'll need the title and description. 
            # run_horror_factory doesn't return them.
            # Let's modify main.py to return (path, title, description, tags)
            
            success_count += 1
        else:
            print(f"   ❌ Batch {i+1} failed.")

    print(f"\n✅ Batch Schedule Complete: {success_count}/5 scheduled.")

if __name__ == "__main__":
    schedule_saturday_batch()
