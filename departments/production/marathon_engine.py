"""
THE MARATHON ENGINE
Module: Creates compilation videos from existing Shorts for Long-Form RPM monetization.

Scans existing videos, selects random ones, and concatenates them with transitions.
"""

import os
import random
import json
from datetime import datetime
from typing import List, Optional
from moviepy import VideoFileClip, concatenate_videoclips, CompositeVideoClip, ColorClip


def _get_compiled_videos() -> set:
    """
    Get set of video filenames that have already been compiled.
    
    Returns:
        Set of video filenames (basenames) that have been used in compilations
    """
    compiled_file = "marathon_compiled.json"
    if not os.path.exists(compiled_file):
        return set()
    
    try:
        with open(compiled_file, 'r') as f:
            data = json.load(f)
            return set(data.get('compiled_videos', []))
    except:
        return set()


def _mark_videos_as_compiled(video_paths: List[str]):
    """
    Mark videos as compiled so they won't be selected again.
    
    Args:
        video_paths: List of video file paths that were compiled
    """
    compiled_file = "marathon_compiled.json"
    compiled = _get_compiled_videos()
    
    # Add basenames of compiled videos
    for path in video_paths:
        compiled.add(os.path.basename(path))
    
    data = {'compiled_videos': list(compiled)}
    with open(compiled_file, 'w') as f:
        json.dump(data, f, indent=2)


def create_marathon_compilation(
    source_folder: str = ".",
    output_folder: str = "output/marathon_videos",
    num_videos: int = 7,
    fade_duration: float = 0.5,
    horizontal: bool = False
) -> str:
    """
    Create a compilation video from existing Shorts.
    
    Args:
        source_folder: Folder to scan for video files (default: current directory)
        output_folder: Folder to save compilation (default: "output/marathon_videos")
        num_videos: Number of videos to include (5-10, default: 7)
        fade_duration: Duration of fade transition between clips (default: 0.5s)
        horizontal: If True, create horizontal format (1920x1080) with blurred background padding.
                    If False, create vertical format (1080x1920). Default: False.
        
    Returns:
        Path to the created compilation video
        
    Raises:
        Exception: If not enough videos found or compilation fails
    """
    print("🎬 Marathon Engine: Creating compilation video...")
    
    # Ensure num_videos is in valid range
    num_videos = max(5, min(10, num_videos))
    
    # Scan for video files
    print(f"   Scanning {source_folder} for video files...")
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    all_videos = []
    
    # Check common locations
    search_paths = [
        source_folder,
        ".",
        "output",
        "final_shorts"
    ]
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
        
        for root, dirs, files in os.walk(search_path):
            # Skip marathon output folder
            if 'marathon' in root.lower():
                continue
            
            for file in files:
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    # Skip temp files and very small files
                    if 'temp' in file.lower() or 'TEMP' in file:
                        continue
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    if file_size > 1000000:  # At least 1MB
                        all_videos.append(file_path)
    
    if not all_videos:
        raise Exception(f"No video files found in {source_folder} or common locations")
    
    print(f"   Found {len(all_videos)} video files")
    
    # Get already compiled videos
    compiled = _get_compiled_videos()
    
    # Filter out already compiled videos
    available_videos = [
        v for v in all_videos 
        if os.path.basename(v) not in compiled
    ]
    
    if len(available_videos) < num_videos:
        print(f"   ⚠️ Only {len(available_videos)} unused videos available, using all of them")
        selected_videos = available_videos
    else:
        # Randomly select videos
        selected_videos = random.sample(available_videos, num_videos)
    
    print(f"   Selected {len(selected_videos)} videos for compilation:")
    for i, v in enumerate(selected_videos, 1):
        print(f"      {i}. {os.path.basename(v)}")
    
    # Determine target format
    if horizontal:
        target_size = (1080, 1920)  # Keep vertical source, will pad to horizontal
        output_size = (1920, 1080)  # Final horizontal output
        print("   Format: Horizontal (1920x1080) with blurred background padding")
    else:
        target_size = (1080, 1920)  # Vertical Shorts format
        output_size = (1080, 1920)
        print("   Format: Vertical (1080x1920) Shorts format")
    
    # Load and prepare video clips
    print("   Loading video clips...")
    clips = []
    for i, video_path in enumerate(selected_videos):
        try:
            clip = VideoFileClip(video_path)
            # Resize to target format (vertical source)
            if clip.size != target_size:
                print(f"      Resizing {os.path.basename(video_path)} to {target_size[0]}x{target_size[1]}...")
                clip = clip.resized(target_size)
            clips.append(clip)
            print(f"      ✓ Loaded: {os.path.basename(video_path)} ({clip.duration:.2f}s)")
        except Exception as e:
            print(f"      ⚠️ Failed to load {video_path}: {e}")
            continue
    
    if len(clips) < 2:
        raise Exception(f"Not enough valid video clips loaded ({len(clips)}). Need at least 2.")
    
    # Apply fade transitions
    print(f"   Applying {fade_duration}s fade transitions...")
    faded_clips = []
    
    for i, clip in enumerate(clips):
        if i == 0:
            # First clip: fade in
            faded_clip = clip.fadein(fade_duration)
        elif i == len(clips) - 1:
            # Last clip: fade out
            faded_clip = clip.fadeout(fade_duration)
        else:
            # Middle clips: fade in and out
            faded_clip = clip.fadein(fade_duration).fadeout(fade_duration)
        
        faded_clips.append(faded_clip)
    
    # Concatenate all clips
    print("   Concatenating clips...")
    final_video = concatenate_videoclips(faded_clips, method="compose")
    total_duration = final_video.duration
    
    print(f"   ✓ Compilation duration: {total_duration:.2f}s ({total_duration/60:.2f} minutes)")
    
    # Warn if duration is below 8 minutes for horizontal (mid-roll ads require 8+ min)
    if horizontal and total_duration < 480:
        print(f"   ⚠️ Warning: Duration ({total_duration/60:.2f} min) is below 8 minutes.")
        print(f"      Mid-roll ads require 8+ minutes. Consider adding more videos.")
    
    # Convert to horizontal format if requested (with side padding)
    if horizontal and output_size != target_size:
        print("   Converting to horizontal format (1920x1080) with side padding...")
        
        # For horizontal: scale vertical video to fit height (1080), then pad sides with black
        # This creates a "pillarbox" effect (black bars on sides)
        # Scale video to match horizontal height (1080)
        scaled_video = final_video.resized(height=output_size[1])  # Height = 1080
        
        # Calculate padding needed for width
        current_width = scaled_video.w
        if current_width < output_size[0]:  # If width < 1920, pad it
            # Center the video horizontally
            x_center = (output_size[0] - current_width) // 2
            # Create black background
            bg = ColorClip(size=output_size, color=(0, 0, 0), duration=total_duration)
            # Composite video on background, centered
            final_video = CompositeVideoClip([bg, scaled_video.set_position((x_center, 0))])
        else:
            # Video is wider than 1920, crop to center
            crop_x = (current_width - output_size[0]) // 2
            try:
                final_video = scaled_video.cropped(x1=crop_x, x2=crop_x + output_size[0])
            except:
                final_video = scaled_video.resized(output_size)
    
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Generate output filename with date and format indicator
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    format_suffix = "horizontal" if horizontal else "vertical"
    output_path = os.path.join(output_folder, f"compilation_{format_suffix}_{date_str}.mp4")
    
    # Render final video
    print(f"   Rendering compilation to: {output_path}...")
    final_video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=30,
        bitrate='6000k',
        audio_bitrate='192k',
        logger=None
    )
    
    # Cleanup
    for clip in clips:
        clip.close()
    final_video.close()
    
    # Mark videos as compiled
    _mark_videos_as_compiled(selected_videos)
    print(f"   ✓ Marked {len(selected_videos)} videos as compiled")
    
    # Verify output
    if not os.path.exists(output_path):
        raise Exception(f"Compilation video was not created at {output_path}")
    
    file_size = os.path.getsize(output_path)
    if file_size == 0:
        raise Exception(f"Compilation video is empty at {output_path}")
    
    print(f"✓ Marathon compilation created: {output_path} ({file_size} bytes)")
    return output_path


if __name__ == "__main__":
    # Test the marathon engine
    print("=" * 60)
    print("🧪 TESTING MARATHON ENGINE")
    print("=" * 60)
    
    try:
        output_path = create_marathon_compilation(num_videos=5)
        print(f"\n✓ Compilation created at: {output_path}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
