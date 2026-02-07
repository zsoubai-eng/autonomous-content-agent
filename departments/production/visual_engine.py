"""
THE VISUAL ENGINE - SUPER-CASCADE ARCHITECTURE
Module 3: Sources and processes background video clips.

SUPER-CASCADE ARCHITECTURE (Try-Catch Block Chain):
- Priority 1: Vidu API (Video AI)
- Priority 2: Luma API (Video AI)
- Priority 3: Runway API (Video AI)
- Priority 4: Pika API (Video AI)
- Priority 5: HeyGen API (Video AI)
- Priority 6: Pollinations.ai (Free/Unlimited, Abstract Dark Visuals)
- Priority 7: YouTube Gameplay (Retention Fallback, unstoppable)
- Priority 8: Dark Abstract Backgrounds (Local assets)
"""

import os
import random
import tempfile
import shutil
import requests
import time
import yt_dlp
from moviepy import VideoFileClip, CompositeVideoClip
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def _get_vidu_video(prompt: str, duration: float, output_path: str) -> str:
    """
    Generate video using Vidu API (Priority 1).
    
    Args:
        prompt: Visual engineering prompt
        duration: Desired video duration
        output_path: Path to save video
        
    Returns:
        Path to generated video
        
    Raises:
        Exception: If Vidu API fails
    """
    api_key = os.getenv("VIDU_API_KEY")
    
    if not api_key:
        raise Exception("VIDU_API_KEY not found in .env")
    
    print("   🎬 Checking Vidu API (Priority 1)...")
    print("   ⚠️ Vidu API integration not yet implemented (API documentation required)")
    raise Exception("Vidu API not implemented")


def _get_luma_video(prompt: str, duration: float, output_path: str) -> str:
    """
    Generate video using Luma API (Priority 2).
    
    Args:
        prompt: Visual engineering prompt
        duration: Desired video duration
        output_path: Path to save video
        
    Returns:
        Path to generated video
        
    Raises:
        Exception: If Luma API fails
    """
    api_key = os.getenv("LUMA_API_KEY")
    
    if not api_key:
        raise Exception("LUMA_API_KEY not found in .env")
    
    print("   🎬 Checking Luma API (Priority 2)...")
    print("   ⚠️ Luma API integration not yet implemented (API documentation required)")
    raise Exception("Luma API not implemented")


def _get_runway_video(prompt: str, duration: float, output_path: str) -> str:
    """
    Generate video using Runway API (Priority 3).
    
    Args:
        prompt: Visual engineering prompt
        duration: Desired video duration
        output_path: Path to save video
        
    Returns:
        Path to generated video
        
    Raises:
        Exception: If Runway API fails
    """
    api_key = os.getenv("RUNWAY_API_KEY")
    
    if not api_key:
        raise Exception("RUNWAY_API_KEY not found in .env")
    
    print("   🎬 Checking Runway API (Priority 3)...")
    
    try:
        # Runway API endpoint (example - adjust based on actual API)
        api_url = "https://api.runwayml.com/v1/image-to-video"
        
        # For now, we'll use a placeholder implementation
        # Runway typically requires image input, so this is a simplified version
        print("   ⚠️ Runway API requires image input - using fallback")
        raise Exception("Runway API requires image input (not yet implemented)")
        
    except Exception as e:
        raise Exception(f"Runway API failed: {e}")


def _get_pika_video(prompt: str, duration: float, output_path: str) -> str:
    """
    Generate video using Pika API (Priority 4).
    
    Args:
        prompt: Visual engineering prompt
        duration: Desired video duration
        output_path: Path to save video
        
    Returns:
        Path to generated video
        
    Raises:
        Exception: If Pika API fails
    """
    api_key = os.getenv("PIKA_API_KEY")
    
    if not api_key:
        raise Exception("PIKA_API_KEY not found in .env")
    
    print("   🎬 Checking Pika API (Priority 4)...")
    print("   ⚠️ Pika API integration not yet implemented (API documentation required)")
    raise Exception("Pika API not implemented")


def _get_heygen_video(prompt: str, duration: float, output_path: str) -> str:
    """
    Generate video using HeyGen API (Priority 5).
    
    Args:
        prompt: Visual engineering prompt
        duration: Desired video duration
        output_path: Path to save video
        
    Returns:
        Path to generated video
        
    Raises:
        Exception: If HeyGen API fails
    """
    api_key = os.getenv("HEYGEN_API_KEY")
    
    if not api_key:
        raise Exception("HEYGEN_API_KEY not found in .env")
    
    print("   🎬 Checking HeyGen API (Priority 5)...")
    print("   ⚠️ HeyGen API integration not yet implemented (API documentation required)")
    raise Exception("HeyGen API not implemented")


def _get_pollinations_video(prompt: str, duration: float, output_path: str) -> str:
    """
    Generate video using Pollinations.ai (Priority 6 - Free/Unlimited).
    
    Args:
        prompt: Visual engineering prompt
        duration: Desired video duration
        output_path: Path to save video
        
    Returns:
        Path to generated video
        
    Raises:
        Exception: If Pollinations fails
    """
    print("   🎬 Checking Pollinations.ai (Priority 6 - Free/Unlimited)...")
    
    try:
        # Pollinations.ai generates images, not videos
        # We'll generate a sequence of images and convert to video
        # For now, use a simple approach: generate one image and loop it
        
        # Clean prompt for URL
        clean_prompt = prompt.replace(" ", "%20").replace(",", "%2C")
        
        # Pollinations image API
        image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1080&height=1920&seed={random.randint(1000, 9999)}"
        
        print(f"   Generating abstract dark visuals: {prompt[:50]}...")
        
        # Download image
        response = requests.get(image_url, timeout=30)
        if response.status_code != 200:
            raise Exception(f"Pollinations API returned status {response.status_code}")
        
        # Save image
        temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_image.write(response.content)
        temp_image.close()
        
        # Convert image to video by looping it
        from moviepy import ImageClip, concatenate_videoclips
        
        image_clip = ImageClip(temp_image.name, duration=duration)
        image_clip = image_clip.resize((1080, 1920))
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Write video
        image_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            bitrate='3000k',
            logger=None
        )
        
        # Cleanup
        image_clip.close()
        os.remove(temp_image.name)
        
        print(f"   ✓ Pollinations video generated: {output_path}")
        return output_path
        
    except Exception as e:
        raise Exception(f"Pollinations failed: {e}")


def _load_used_timestamps() -> dict:
    """
    Load used timestamps from JSON file to avoid duplicates.
    
    Returns:
        Dict mapping video_id -> list of used (start, end) tuples
    """
    timestamp_file = "visual_engine_timestamps.json"
    if not os.path.exists(timestamp_file):
        return {}
    
    try:
        import json
        with open(timestamp_file, 'r') as f:
            return json.load(f)
    except:
        return {}


def _save_used_timestamps(timestamps: dict):
    """
    Save used timestamps to JSON file.
    
    Args:
        timestamps: Dict mapping video_id -> list of used (start, end) tuples
    """
    timestamp_file = "visual_engine_timestamps.json"
    try:
        import json
        with open(timestamp_file, 'w') as f:
            json.dump(timestamps, f, indent=2)
    except Exception as e:
        print(f"   ⚠️ Could not save timestamps: {e}")


def _is_timestamp_used(video_id: str, start: float, end: float, used_timestamps: dict, tolerance: float = 2.0) -> bool:
    """
    Check if a timestamp range has been used before.
    
    Args:
        video_id: YouTube video ID
        start: Start time in seconds
        end: End time in seconds
        used_timestamps: Dict of used timestamps
        tolerance: Time tolerance in seconds (default: 2.0s)
        
    Returns:
        True if timestamp is too close to a used one, False otherwise
    """
    if video_id not in used_timestamps:
        return False
    
    for used_start, used_end in used_timestamps[video_id]:
        # Check if ranges overlap or are too close
        if (start < used_end + tolerance and end > used_start - tolerance):
            return True
    
    return False


def _download_and_process_single_clip(search_query: str, segment_duration: float, temp_dir: str) -> str:
    """
    Download and process a single video clip segment from YouTube.
    
    Tracks used timestamps to avoid duplicate segments.
    
    Args:
        search_query: YouTube search query
        segment_duration: Duration of segment in seconds
        temp_dir: Temporary directory for downloads
        
    Returns:
        Path to processed clip file
    """
    download_path = os.path.join(temp_dir, f"segment_{random.randint(1000, 9999)}.mp4")
    
    # Load used timestamps
    used_timestamps = _load_used_timestamps()
    
    # Configure yt-dlp for 1080p HD with duration filter
    def match_filter(info_dict):
        """Filter out videos longer than 10 minutes"""
        duration = info_dict.get('duration')
        if duration and duration > 600:
            return "Video is longer than 10 minutes, skipping"
        return None
    
    # ENSURE 1080p: Strict format selection for high quality
    ydl_opts = {
        'format': 'bestvideo[height=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=1080][ext=mp4]/best[height>=1080][ext=mp4]',
        'outtmpl': download_path,
        'quiet': False,
        'no_warnings': False,
        'match_filter': match_filter,
    }
    
    # Search and download
    max_attempts = 5
    downloaded = False
    selected_video_id = None  # Store video ID for timestamp tracking
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for attempt in range(1, max_attempts + 1):
            search_url = f"ytsearch{attempt}:{search_query}"
            
            try:
                info = ydl.extract_info(search_url, download=False)
                
                if not info or 'entries' not in info or not info['entries']:
                    if attempt < max_attempts:
                        continue
                    raise Exception("No videos found for search query")
                
                # Check each entry until we find one that passes the filter
                for entry in info['entries']:
                    if not entry:
                        continue
                    
                    video_duration = entry.get('duration')
                    if video_duration and video_duration > 900:
                        continue
                    
                    video_id = entry.get('id')
                    if not video_id:
                        continue
                    
                    # Check if we've used too much of this video already
                    used_timestamps = _load_used_timestamps()
                    if video_id in used_timestamps:
                        used_ranges = used_timestamps[video_id]
                        total_used = sum(end - start for start, end in used_ranges)
                        # If we've used more than 50% of the video, skip it
                        if video_duration and total_used > video_duration * 0.5:
                            print(f"      Skipping {video_id}: already used {total_used:.1f}s of {video_duration:.1f}s")
                            continue
                    
                    selected_video_id = video_id
                    video_title = entry.get('title', 'Unknown')
                    print(f"   Downloading segment: {video_title} (ID: {video_id})")
                    
                    ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
                    downloaded = True
                    break
                
                if downloaded:
                    break
                    
            except Exception as e:
                if attempt < max_attempts:
                    continue
                raise
    
    if not downloaded:
        raise Exception("No suitable videos found")
    
    # Find the downloaded file
    downloaded_file = None
    for file in os.listdir(temp_dir):
        if file.startswith("segment_") and file.endswith(('.mp4', '.webm', '.mkv')):
            downloaded_file = os.path.join(temp_dir, file)
            break
    
    if not downloaded_file or not os.path.exists(downloaded_file):
        raise Exception(f"Downloaded file not found")
    
    # Load and process video (CRITICAL: strip ALL original audio)
    video_clip = VideoFileClip(downloaded_file)
    video_duration = video_clip.duration
    
    # Get video ID for timestamp tracking
    video_id = selected_video_id
    if not video_id:
        # Fallback: use filename hash as identifier
        import hashlib
        video_id = hashlib.md5(os.path.basename(downloaded_file).encode()).hexdigest()[:12]
        print(f"   ⚠️ Could not get video ID, using hash: {video_id}")
    
    # Cut segment - avoid used timestamps
    if video_duration <= segment_duration:
        segment_start = 0
        segment_end = video_duration
    else:
        max_start = video_duration - segment_duration
        max_attempts = 20  # Try up to 20 times to find unused timestamp
        segment_start = None
        segment_end = None
        
        for attempt in range(max_attempts):
            candidate_start = random.uniform(0, max_start)
            candidate_end = candidate_start + segment_duration
            
            # Check if this timestamp has been used
            if not _is_timestamp_used(video_id, candidate_start, candidate_end, used_timestamps):
                segment_start = candidate_start
                segment_end = candidate_end
                break
        
        # If all attempts failed, use random anyway (but log it)
        if segment_start is None:
            print(f"   ⚠️ Could not find unused timestamp for {video_id}, using random segment")
            segment_start = random.uniform(0, max_start)
            segment_end = segment_start + segment_duration
    
    # Record this timestamp as used
    if video_id not in used_timestamps:
        used_timestamps[video_id] = []
    used_timestamps[video_id].append([round(segment_start, 2), round(segment_end, 2)])
    _save_used_timestamps(used_timestamps)
    
    try:
        segment = video_clip.subclipped(segment_start, segment_end)
    except AttributeError:
        segment = video_clip.subclip(segment_start, segment_end)
    
    # HARD MUTE: remove all original audio so actors never bleed through
    segment = segment.without_audio()
    
    # Resize to 1080x1920
    target_width = 1080
    target_height = 1920
    current_width, current_height = segment.size
    
    # Save processed segment
    segment_path = os.path.join(temp_dir, f"processed_segment_{random.randint(1000, 9999)}.mp4")
    os.makedirs(os.path.dirname(segment_path) if os.path.dirname(segment_path) else ".", exist_ok=True)
    
    # IMPORTANT: ensure ffmpeg is called with audio disabled (-an)
    if segment.size != (target_width, target_height):
        segment.write_videofile(
            segment_path,
            codec='libx264',
            audio=False,  # remove audio track completely
            fps=30,
            preset='medium',
            bitrate='3000k',
            ffmpeg_params=[
                '-an',
                '-vf',
                f'scale={target_width}:{target_height}:flags=lanczos:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2',
            ],
            logger=None,
        )
    else:
        segment.write_videofile(
            segment_path,
            codec='libx264',
            audio=False,  # remove audio track completely
            fps=30,
            preset='medium',
            bitrate='3000k',
            ffmpeg_params=['-an'],
            logger=None,
        )
    
    video_clip.close()
    segment.close()
    
    if os.path.exists(downloaded_file):
        os.remove(downloaded_file)
    
    return segment_path


def get_gameplay_clip(duration: float, output_path: str, search_query: str = None) -> str:
    """
    Download and process high-retention gameplay video clips for background (Priority 7 - YouTube Fallback).
    
    Uses specific high-retention visual niches with timestamp tracking to avoid duplicates.
    
    Args:
        duration: Desired clip duration in seconds
        output_path: Path to save processed video (.mp4)
        search_query: YouTube search query (optional, will use high-retention niches if None)
        
    Returns:
        Path to the processed video file
        
    Raises:
        Exception: If download or processing fails
    """
    print("   🎮 Using High-Retention Visual Niches (Priority 7 - Retention Fallback)...")
    
    # Create temporary directory for downloads
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Visual Overstimulation: Clip Cycling
        segment_duration = 20.0
        num_segments = max(1, int(duration / segment_duration) + (1 if duration % segment_duration > 5 else 0))
        actual_segment_duration = duration / num_segments
        
        if num_segments > 1:
            print(f"   Creating {num_segments} video segments for visual variety...")
        
        # HIGH-RETENTION VISUAL NICHES: Specific niches proven to drive retention
        # Rotate through these to maximize engagement
        high_retention_niches = [
            "Satisfying hydraulic press vertical",
            "GTA 5 ramp jump gameplay vertical",
            "Minecraft parkour no copyright vertical",
            "Oddly satisfying slime cutting asm",
        ]
        
        # Use provided query or rotate through niches
        if search_query:
            search_queries = [search_query]
        else:
            # Rotate through niches, ensuring variety across segments
            search_queries = []
            for i in range(num_segments):
                niche = high_retention_niches[i % len(high_retention_niches)]
                search_queries.append(niche)
        
        segment_clips = []
        
        for i in range(num_segments):
            # Use query from rotation or fallback to first niche
            if search_query:
                query = search_query
            else:
                query = search_queries[i] if i < len(search_queries) else high_retention_niches[0]
            
            if num_segments > 1:
                print(f"   Segment {i+1}/{num_segments}: {query}")
            else:
                print(f"   Using niche: {query}")
            
            try:
                segment_path = _download_and_process_single_clip(query, actual_segment_duration, temp_dir)
                segment_clip = VideoFileClip(segment_path)
                
                # Verify 1080p quality
                if segment_clip.h < 1080:
                    print(f"      ⚠️ Warning: Segment is {segment_clip.h}p, not 1080p. Quality may be lower.")
                
                segment_clips.append(segment_clip)
            except Exception as e:
                print(f"   ⚠️ Segment {i+1} failed: {e}, trying next niche...")
                # Try next niche instead of reusing previous
                if i < len(high_retention_niches) - 1:
                    try:
                        fallback_query = high_retention_niches[(i + 1) % len(high_retention_niches)]
                        print(f"      Retrying with: {fallback_query}")
                        segment_path = _download_and_process_single_clip(fallback_query, actual_segment_duration, temp_dir)
                        segment_clip = VideoFileClip(segment_path)
                        segment_clips.append(segment_clip)
                    except:
                        # Last resort: reuse previous if available
                        if segment_clips:
                            print(f"      Using previous segment as fallback")
                            segment_clips.append(segment_clips[-1])
                elif segment_clips:
                    # Last resort: reuse previous
                    segment_clips.append(segment_clips[-1])
        
        if not segment_clips:
            raise Exception("No segments were successfully downloaded")
        
        # Concatenate all segments
        from moviepy import concatenate_videoclips
        if num_segments > 1:
            print(f"   Stitching {len(segment_clips)} segments together...")
        final_clip = concatenate_videoclips(segment_clips)
        
        # Trim to exact duration if needed
        if final_clip.duration > duration:
            final_clip = final_clip[0:duration]
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Save final video
        print(f"   Rendering final background: {output_path}")
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            bitrate='3000k',
            logger=None
        )
        
        # Cleanup
        final_clip.close()
        for clip in segment_clips:
            clip.close()
        
        # Remove temp files
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Verify output
        if not os.path.exists(output_path):
            raise Exception(f"Processed video was not created at {output_path}")
        
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            raise Exception(f"Processed video is empty at {output_path}")
        
        print(f"✓ Background video ready: {output_path} ({file_size} bytes)")
        return output_path
        
    except Exception as e:
        # Cleanup on error
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise Exception(f"Failed to get gameplay clip: {e}")


def get_best_video(prompt: str, duration: float, output_path: str) -> str:
    """
    Get best video using SUPER-CASCADE architecture (Try-Catch Block Chain).
    
    Tries each video AI API in order until one succeeds.
    
    Args:
        prompt: Visual engineering prompt from script
        duration: Desired video duration
        output_path: Path to save video
        
    Returns:
        Path to generated/downloaded video
    """
    print(f"📹 SUPER-CASCADE: Sourcing video (duration: {duration:.2f}s)...")
    print(f"   Visual Prompt: {prompt[:80]}...")
    
    # SUPER-CASCADE: Try each API in order
    cascade_chain = [
        ("Vidu", _get_vidu_video),
        ("Luma", _get_luma_video),
        ("Runway", _get_runway_video),
        ("Pika", _get_pika_video),
        ("HeyGen", _get_heygen_video),
        ("Pollinations", _get_pollinations_video),
    ]
    
    for api_name, api_func in cascade_chain:
        try:
            print(f"   → Trying {api_name}...")
            video_path = api_func(prompt, duration, output_path)
            print(f"   ✓ {api_name} succeeded!")
            return video_path
        except Exception as e:
            error_msg = str(e)
            if "not found in .env" in error_msg or "Key Missing" in error_msg:
                print(f"   ⚠️ {api_name}: Key Missing. Continuing...")
            elif "not yet implemented" in error_msg:
                print(f"   ⚠️ {api_name}: Not yet implemented. Continuing...")
            else:
                print(f"   ⚠️ {api_name} failed: {error_msg[:60]}...")
            continue
    
    # Priority 7: YouTube Gameplay (unstoppable fallback)
    print("   → Trying YouTube Gameplay (Priority 7 - Unstoppable Fallback)...")
    try:
        video_path = get_gameplay_clip(duration, output_path)
        print("   ✓ YouTube Gameplay succeeded!")
        return video_path
    except Exception as e:
        print(f"   ⚠️ YouTube Gameplay failed: {e}")
        raise Exception("All video sources failed (Vidu, Luma, Runway, Pika, HeyGen, Pollinations, YouTube)")


def generate_scene_visuals(scenes: list, output_dir: str = ".") -> list:
    """
    Generate individual visual assets for each scene (Visual Agent).
    
    Iterates through scenes and generates a unique video for each scene using Pollinations.ai
    or the SUPER-CASCADE architecture.
    
    Args:
        scenes: List of scene dicts with 'id', 'text', 'visual_prompt', 'duration'
        output_dir: Directory to save scene videos (default: current directory)
        
    Returns:
        List of paths to generated scene video files (scene_1.mp4, scene_2.mp4, etc.)
    """
    print(f"🎬 Visual Agent: Generating visuals for {len(scenes)} scenes...")
    
    scene_video_paths = []
    
    for scene in scenes:
        scene_id = scene.get('id', len(scene_video_paths) + 1)
        visual_prompt = scene.get('visual_prompt', 'Cinematic dark noir, moody lighting, psychological thriller vibe')
        duration = float(scene.get('duration', 3.0))
        
        output_path = os.path.join(output_dir, f"scene_{scene_id}.mp4")
        
        print(f"   Scene {scene_id}: Generating visual ({duration:.1f}s)...")
        print(f"      Prompt: {visual_prompt[:60]}...")
        
        try:
            # Use SUPER-CASCADE to generate video for this specific scene
            video_path = get_best_video(visual_prompt, duration, output_path)
            scene_video_paths.append(video_path)
            print(f"   ✓ Scene {scene_id} visual generated: {video_path}")
        except Exception as e:
            print(f"   ⚠️ Scene {scene_id} visual generation failed: {e}")
            # Continue with other scenes even if one fails
            # Could add fallback logic here if needed
            raise
    
    print(f"✓ Visual Agent: Generated {len(scene_video_paths)} scene visuals")
    return scene_video_paths


def get_visual_content(duration: float, output_path: str, script_data: dict = None, pacing: str = "Normal") -> str:
    """
    Get visual content using SUPER-CASCADE architecture.
    
    DEPRECATED: Use generate_scene_visuals() for scene-based workflow.
    This function is kept for backward compatibility.
    
    Args:
        duration: Desired video duration in seconds
        output_path: Path to save processed video
        script_data: Script data dict (contains 'visual_prompt' if available)
        pacing: Pacing tag from script ("Fast" or "Slow")
        
    Returns:
        Path to processed video file
    """
    # Extract visual prompt from script data
    visual_prompt = "Cinematic dark noir, moody lighting, psychological thriller vibe, hyper-realistic, 4k"
    if script_data and isinstance(script_data, dict):
        # Check if scene-based format
        if 'scenes' in script_data:
            # Use first scene's visual prompt
            scenes = script_data.get('scenes', [])
            if scenes:
                visual_prompt = scenes[0].get('visual_prompt', visual_prompt)
        else:
            visual_prompt = script_data.get('visual_prompt', visual_prompt)
    elif isinstance(script_data, str):
        # Fallback: if script_data is a string (script text), use default prompt
        visual_prompt = "Cinematic dark noir, moody lighting, psychological thriller vibe, hyper-realistic, 4k"
    
    # Use SUPER-CASCADE to get best video
    video_path = get_best_video(visual_prompt, duration, output_path)
    
    # Apply pacing-based speedup if "Fast" (handled at audio level in QC)
    if pacing == "Fast":
        print(f"   ⚡ Fast pacing detected (video speedup skipped - audio speedup in QC handles pacing)")
    
    return video_path


if __name__ == "__main__":
    # Test the visual engine
    print("=" * 60)
    print("🧪 TESTING VISUAL ENGINE (SUPER-CASCADE)")
    print("=" * 60)
    
    try:
        test_prompt = "Cinematic dark noir, moody lighting, psychological thriller vibe, hyper-realistic, 4k"
        video_path = get_best_video(test_prompt, 15.0, "test_background.mp4")
        print(f"\n✓ Video created at: {video_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
