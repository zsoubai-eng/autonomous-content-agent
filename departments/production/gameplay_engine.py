"""
GAMEPLAY DOWNLOADER
Module: Downloads "satisfying" gameplay footage (Minecraft, GTA, etc.) for split-screen shorts.
Uses yt-dlp to fetch no-copyright gameplay from YouTube.
"""

import os
import random
import yt_dlp
from typing import Optional

# Curated "No Copyright/Free Use" gameplay sources for split-screen
GAMEPLAY_SOURCES = [
    "https://www.youtube.com/watch?v=S2S6jYpE9uM", # Minecraft Parkour 2025
    "https://www.youtube.com/watch?v=NQreZ_x0O0Y", # Minecraft Parkour (retry)
    "https://www.youtube.com/watch?v=iYvSIdS1uUo", # Minecraft No Copyright Vertical
    "https://www.youtube.com/watch?v=Fj-cWj_H5pY", # GTA 5 Stunts No Copyright
    "https://www.youtube.com/watch?v=V9X9Y_8_r60"  # Satisfying Slime/Sand
]

def download_gameplay_video(output_dir: str = "assets/gameplay") -> Optional[str]:
    """
    Downloads a random satisfying gameplay video to use as background.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if we already have files to save bandwidth
    existing_files = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
    if existing_files:
        print(f"   ✓ Using existing gameplay asset: {existing_files[0]}")
        return os.path.join(output_dir, random.choice(existing_files))

    output_path = os.path.join(output_dir, "gameplay_bg.mp4")

    # Try downloading from curated sources first
    random.shuffle(GAMEPLAY_SOURCES)
    for url in GAMEPLAY_SOURCES:
        print(f"   🎥 Attempting satisfying gameplay download: {url}")
        if _download_with_opts(url, output_path):
            return output_path
            
    # Fallback to YouTube Search if curated links are dead
    search_query = "ytsearch1:Satisfying Minecraft Parkour No Copyright 9:16"
    print(f"   🔍 Searching YouTube for fresh gameplay: {search_query}")
    if _download_with_opts(search_query, output_path):
        return output_path
        
    # Final Procedural Fallback: Generate a satisfying moving gradient (0 cost, 100% uptime)
    print("   � All downloads failed. Generating procedural satisfying background...")
    try:
        import subprocess
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 'cellauto=s=1080x960:rate=15', 
            '-t', '60', '-pix_fmt', 'yuv420p', output_path, '-y'
        ], check=True, capture_output=True)
        return output_path
    except Exception as fe:
        print(f"   ⚠️ Procedural fallback failed: {fe}")
        return None

def _download_with_opts(url: str, output_path: str) -> bool:
    ydl_opts = {
        'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return os.path.exists(output_path)
    except:
        return False

if __name__ == "__main__":
    path = download_gameplay_video()
    if path:
        print(f"✓ Downloaded to: {path}")
