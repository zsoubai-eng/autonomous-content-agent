#!/usr/bin/env python3
"""
Re-upload videos that were generated but failed to upload.
"""
import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from departments.logistics.upload_engine import upload_video
from departments.logistics.history_engine import _load_history, _save_history

def reupload_missing():
    print("🔍 Searching for missing uploads...")
    history = _load_history()
    count = 0
    
    for entry in history:
        video_id = entry.get('video_id')
        filename = entry.get('filename')
        
        if (not video_id or video_id == 'NOT UPLOADED') and filename and os.path.exists(filename):
            print(f"🚀 Re-uploading: {entry.get('title')}")
            try:
                new_id = upload_video(
                    file_path=filename,
                    title=entry.get('title'),
                    description=entry.get('description', 'AI Generated Horror Story'),
                    tags=entry.get('tags', []),
                    category_id="24"
                )
                if new_id:
                    entry['video_id'] = new_id
                    print(f"✅ Success! New ID: {new_id}")
                    count += 1
            except Exception as e:
                print(f"❌ Failed to re-upload {filename}: {e}")
    
    if count > 0:
        _save_history(history)
        print(f"✅ Re-uploaded {count} videos.")
    else:
        print("✓ No missing uploads found with local files available.")

if __name__ == "__main__":
    reupload_missing()
