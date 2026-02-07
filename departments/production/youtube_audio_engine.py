"""
YOUTUBE AUDIO ENGINE
Module: Downloads audio from YouTube videos for background music.

Simplified: Just download the audio, no complex processing.
"""

import os
import yt_dlp
import tempfile
from typing import Optional


HORROR_BACKGROUND_MUSIC_URL = "https://youtu.be/NfduxcR_ccQ?si=yAz5nnOG2xc_i7EE"


def download_youtube_audio(url: str, output_path: str, duration_limit: float = None) -> str:
    """
    Download audio from a YouTube video.
    
    Args:
        url: YouTube video URL
        output_path: Path to save the audio file (.mp3)
        duration_limit: Optional max duration to download (in seconds). If None, downloads full video.
        
    Returns:
        Path to the downloaded audio file
        
    Raises:
        Exception: If download fails
    """
    print(f"   🎵 Downloading audio from YouTube: {url[:50]}...")
    
    # Configure yt-dlp for audio only
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path.replace('.mp3', '.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'no_warnings': False,
    }
    
    # Add duration filter if specified
    if duration_limit:
        def match_filter(info_dict):
            duration = info_dict.get('duration')
            if duration and duration > duration_limit:
                return f"Video is longer than {duration_limit}s, skipping"
            return None
        ydl_opts['match_filter'] = match_filter
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Find the downloaded file (yt-dlp may change extension)
        base_path = output_path.replace('.mp3', '')
        for ext in ['.mp3', '.m4a', '.webm', '.opus']:
            if os.path.exists(base_path + ext):
                downloaded_file = base_path + ext
                # If not mp3, convert it
                if ext != '.mp3':
                    import subprocess
                    subprocess.run([
                        'ffmpeg', '-i', downloaded_file, '-acodec', 'libmp3lame', output_path, '-y'
                    ], check=True, capture_output=True)
                    os.remove(downloaded_file)
                    return output_path
                else:
                    # Rename to ensure .mp3 extension
                    if downloaded_file != output_path:
                        os.rename(downloaded_file, output_path)
                    return output_path
        
        raise Exception(f"Downloaded file not found. Expected: {output_path}")
        
    except Exception as e:
        raise Exception(f"YouTube audio download failed: {e}")


def get_horror_background_music(output_path: str, duration: float) -> str:
    """
    Get horror background music from the specified YouTube URL.
    
    Args:
        output_path: Path to save the audio file
        duration: Desired duration in seconds (will loop if needed)
        
    Returns:
        Path to the audio file
    """
    try:
        # Download the audio (or use cached version)
        cache_dir = "cache"
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, "horror_bg_music.mp3")
        
        # Download if not cached
        if not os.path.exists(cache_path):
            print(f"   Downloading horror background music...")
            download_youtube_audio(HORROR_BACKGROUND_MUSIC_URL, cache_path)
            print(f"   ✓ Background music cached: {cache_path}")
        else:
            print(f"   ✓ Using cached background music")
        
        # Copy to output path
        import shutil
        shutil.copy2(cache_path, output_path)
        
        # If we need a specific duration, we'll handle looping in the audio engine
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to get horror background music: {e}")


if __name__ == "__main__":
    # Test
    print("=" * 60)
    print("🧪 TESTING YOUTUBE AUDIO ENGINE")
    print("=" * 60)
    
    try:
        test_output = "test_horror_bg.mp3"
        audio_path = get_horror_background_music(test_output, 60.0)
        print(f"\n✓ Audio downloaded: {audio_path}")
        print(f"   Size: {os.path.getsize(audio_path)} bytes")
    except Exception as e:
        print(f"\n❌ Error: {e}")
