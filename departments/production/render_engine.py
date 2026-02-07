"""
THE RENDER ENGINE
Module 4: Assembles final video from background, audio, and subtitles.

Combines all media elements into a polished YouTube Short.
"""

import os
import urllib.request
import gc
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, ColorClip, ImageClip, ImageClip
import numpy as np


def _ensure_font_exists():
    """
    Ensure a bold font file exists. Downloads Impact (bold) if needed, falls back to Roboto-Bold.
    
    Returns:
        Path to font file, or None if not available
    """
    fonts_dir = "fonts"
    os.makedirs(fonts_dir, exist_ok=True)
    
    # Try Impact font first (bold, highly visible)
    font_path = os.path.join(fonts_dir, "Impact.ttf")
    
    if not os.path.exists(font_path):
        print(f"   Downloading Impact font (bold)...")
        try:
            # Try Impact font from a reliable source
            font_urls = [
                "https://github.com/google/fonts/raw/main/ofl/impact/Impact-Regular.ttf",
                "https://raw.githubusercontent.com/google/fonts/main/ofl/impact/Impact-Regular.ttf",
            ]
            downloaded = False
            for font_url in font_urls:
                try:
                    urllib.request.urlretrieve(font_url, font_path)
                    if os.path.exists(font_path) and os.path.getsize(font_path) > 1000:
                        print(f"   ✓ Impact font downloaded: {font_path}")
                        downloaded = True
                        break
                except:
                    continue
            
            if not downloaded:
                # Fallback to Roboto-Bold
                font_path = os.path.join(fonts_dir, "Roboto-Bold.ttf")
                if not os.path.exists(font_path):
                    print(f"   Downloading Roboto-Bold font (fallback)...")
                    font_urls = [
                        "https://raw.githubusercontent.com/google/fonts/main/apache/roboto/Roboto-Bold.ttf",
                        "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf",
                    ]
                    for font_url in font_urls:
                        try:
                            urllib.request.urlretrieve(font_url, font_path)
                            if os.path.exists(font_path) and os.path.getsize(font_path) > 1000:
                                print(f"   ✓ Roboto-Bold font downloaded: {font_path}")
                                downloaded = True
                                break
                        except:
                            continue
        except Exception as e:
            print(f"   ⚠️ Could not download font: {e}")
    
    # If still no font, try system fonts
    if not os.path.exists(font_path):
        system_fonts = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Impact.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
        for sys_font in system_fonts:
            if os.path.exists(sys_font):
                font_path = sys_font
                print(f"   Using system font: {font_path}")
                break
        else:
            print(f"   ⚠️ No bold font found, TextClip will use default")
            return None
    
    return font_path


def animate_scene(image_path: str, audio_duration: float, output_path: str) -> str:
    """
    Animate a static image with Dynamic Zoom/Pan (Ken Burns effect) - The Animator.
    
    Takes a static Flux-generated image and applies dynamic zoom/pan to create a video clip.
    The clip duration matches exactly the audio duration for that scene.
    
    Args:
        image_path: Path to the static image file
        audio_duration: Duration of the audio clip (in seconds) - video will match this
        output_path: Path to save the animated video clip
        
    Returns:
        Path to the generated video clip
        
    Raises:
        Exception: If animation fails
    """
    print(f"   🎬 The Animator: Creating video from image ({audio_duration:.2f}s)...")
    
    # Load the static image using PIL first (more reliable)
    if not os.path.exists(image_path):
        raise Exception(f"Image file not found: {image_path}")
    
    # Convert image to RGB JPEG using PIL (MoviePy works better with this)
    from PIL import Image as PILImage
    temp_image_path = None
    try:
        pil_img = PILImage.open(image_path)
        # Convert to RGB if needed
        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')
        # Save as temporary JPEG file for MoviePy
        temp_image_path = image_path.replace('.jpg', '_temp_rgb.jpg').replace('.png', '_temp_rgb.jpg')
        if temp_image_path == image_path:
            temp_image_path = image_path + '_temp_rgb.jpg'
        pil_img.save(temp_image_path, 'JPEG', quality=95)
        image_path_to_use = temp_image_path
    except Exception as pil_error:
        # If PIL fails, try original path
        print(f"      ⚠️ PIL conversion failed: {pil_error}, using original image")
        image_path_to_use = image_path
    
    try:
        # Create ImageClip from static image
        image_clip = ImageClip(image_path_to_use, duration=audio_duration)
        
        # Ensure image is 1080x1920 (vertical format)
        target_size = (1080, 1920)
        if image_clip.size != target_size:
            # Resize to target size
            image_clip = image_clip.resized(target_size)
        
        # Apply Dynamic Zoom (Ken Burns Effect)
        # Strategy: Start at 1.0x, zoom in to 1.1x during the clip duration
        print(f"      Applying Cinematic Ken Burns (1.0x -> 1.1x zoom)...")
        
        # Calculate resize function
        # Using a slight zoom-in to keep the viewer moving toward the subject
        duration = audio_duration
        def zoom_func(t):
            return 1 + (0.1 * (t / duration))
        
        # In MoviePy 2.x, we use resize with a function or apply_effect
        try:
            # Try dynamic resize
            animated_clip = image_clip.resize(zoom_func)
            
            # Re-center and crop to target size to maintain vertical 1080x1920
            # We crop after zooming to keep the output resolution constant
            animated_clip = animated_clip.crop(
                x_center=target_size[0]/2, 
                y_center=target_size[1]/2, 
                width=target_size[0], 
                height=target_size[1]
            )
        except Exception as zoom_err:
            print(f"      ⚠️ Dynamic zoom failed: {zoom_err}. Using static scale.")
            # Fallback to static slight scale-up
            animated_clip = image_clip.resized((int(target_size[0]*1.05), int(target_size[1]*1.05)))
            animated_clip = animated_clip.cropped(
                x1=(animated_clip.w - target_size[0])//2,
                y1=(animated_clip.h - target_size[1])//2,
                x2=(animated_clip.w + target_size[0])//2,
                y2=(animated_clip.h + target_size[1])//2
            )
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Write video file
        print(f"      Rendering animated clip...")
        animated_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            bitrate='3000k',
            logger=None
        )
        
        # Cleanup
        animated_clip.close()
        image_clip.close()
        # Clean up temp image if created
        if temp_image_path and os.path.exists(temp_image_path) and temp_image_path != image_path:
            try:
                os.remove(temp_image_path)
            except:
                pass
        
        # Verify output
        if not os.path.exists(output_path):
            raise Exception(f"Animated video was not created at {output_path}")
        
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            raise Exception(f"Animated video is empty at {output_path}")
        
        print(f"   ✓ Animated clip created: {output_path} ({file_size} bytes)")
        return output_path
        
    except Exception as e:
        print(f"   ❌ Animation failed: {e}")
        # Fallback: simple static image to video conversion
        try:
            print("      Falling back to simple image-to-video conversion...")
            # Use PIL to convert image to RGB JPEG
            from PIL import Image as PILImage
            pil_img = PILImage.open(image_path)
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            fallback_temp_path = image_path.replace('.jpg', '_fallback_rgb.jpg').replace('.png', '_fallback_rgb.jpg')
            if fallback_temp_path == image_path:
                fallback_temp_path = image_path + '_fallback_rgb.jpg'
            pil_img.save(fallback_temp_path, 'JPEG', quality=95)
            
            image_clip = ImageClip(fallback_temp_path, duration=audio_duration)
            if image_clip.size != (1080, 1920):
                image_clip = image_clip.resized((1080, 1920))
            
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            image_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                bitrate='3000k',
                logger=None
            )
            image_clip.close()
            # Clean up temp image if created
            if 'fallback_temp_path' in locals() and os.path.exists(fallback_temp_path) and fallback_temp_path != image_path:
                try:
                    os.remove(fallback_temp_path)
                except:
                    pass
            print(f"   ✓ Fallback clip created: {output_path}")
            return output_path
        except Exception as fallback_error:
            raise Exception(f"Animation and fallback both failed: {e}, {fallback_error}")


def assemble_scene_video(scene_video_paths: list, scene_audio_paths: list, all_subtitles: list, scenes: list, output_path: str, image_hook_path: str = None) -> str:
    """
    Assemble final video from scene-based assets (Editor Agent).
    
    Stitches together video_1 + audio_1, video_2 + audio_2, etc., then concatenates all scenes.
    Applies Red Progress Bar and Background Music on top of the whole sequence.
    
    Args:
        scene_video_paths: List of paths to scene video files (scene_1.mp4, scene_2.mp4, etc.)
        scene_audio_paths: List of paths to scene audio files (audio_1.mp3, audio_2.mp3, etc.)
        all_subtitles: List of subtitle lists (one per scene)
        scenes: List of scene dicts with 'id', 'text', 'duration'
        output_path: Path to save final video
        image_hook_path: Optional path to AI-generated image hook (displayed for first 3 seconds)
        
    Returns:
        Path to the assembled video file
        
    Raises:
        Exception: If assembly fails
    """
    print("🎬 Editor Agent: Assembling scene-based video...")
    
    try:
        from moviepy import concatenate_videoclips, concatenate_audioclips
        
        if len(scene_video_paths) != len(scene_audio_paths):
            raise ValueError(f"Mismatch: {len(scene_video_paths)} videos but {len(scene_audio_paths)} audios")
        
        print(f"   Stitching {len(scene_video_paths)} scenes together...")
        
        # Step 1: Combine each scene's video + audio and track actual durations
        scene_clips = []
        scene_durations = []  # Track actual duration of each scene
        
        for i, (video_path, audio_path) in enumerate(zip(scene_video_paths, scene_audio_paths)):
            scene_id = scenes[i].get('id', i + 1) if i < len(scenes) else i + 1
            print(f"   Scene {scene_id}: Combining video + audio...")
            
            # Load video and audio for this scene
            scene_video = VideoFileClip(video_path)
            scene_audio = AudioFileClip(audio_path)
            
            # Get actual durations
            actual_audio_duration = scene_audio.duration
            actual_video_duration = scene_video.duration
            
            # CRITICAL: Use audio duration as the master (subtitles are based on audio)
            # If video is shorter, loop it. If longer, trim it.
            scene_duration = actual_audio_duration
            
            # Adjust video to match audio duration exactly
            if actual_video_duration < scene_duration:
                # Loop video if it's shorter than audio
                num_loops = int(scene_duration / actual_video_duration) + 1
                from moviepy import concatenate_videoclips
                looped_videos = [scene_video] * num_loops
                scene_video = concatenate_videoclips(looped_videos)
                scene_video = scene_video[0:scene_duration]
            elif actual_video_duration > scene_duration:
                # Trim video if it's longer than audio
                scene_video = scene_video[0:scene_duration]
            
            # Audio stays as-is (no trimming needed - it's the master)
            # Don't trim audio - use full duration for subtitle alignment
            
            # Store the audio duration (this is what subtitles are timed to)
            scene_durations.append(actual_audio_duration)
            print(f"      Audio: {actual_audio_duration:.2f}s, Video: {actual_video_duration:.2f}s -> {scene_duration:.2f}s (aligned to audio)")
            
            # Set audio on video
            scene_clip = scene_video.with_audio(scene_audio)
            scene_clips.append(scene_clip)
        
        # Step 2: Concatenate all scene clips
        print(f"   Concatenating {len(scene_clips)} scenes...")
        final_video = concatenate_videoclips(scene_clips, method="compose")
        total_duration = final_video.duration
        
        # Step 3: Generate combined subtitles with adjusted timings
        print(f"   Generating combined subtitles with proper timing alignment...")
        combined_subtitles = []
        cumulative_time = 0.0
        
        for i, scene_subtitles in enumerate(all_subtitles):
            # Get actual scene duration used in the final clip
            actual_scene_duration = scene_durations[i] if i < len(scene_durations) else scenes[i].get('duration', 3.0)
            
            # Adjust each subtitle timing to be relative to video start
            # Also filter out subtitles that extend beyond the actual clip duration
            for sub in scene_subtitles:
                # Only include subtitles that are within the actual clip duration
                if sub.get('start', 0) < actual_scene_duration:
                    adjusted_sub = {
                        'word': sub.get('word', ''),
                        'start': sub.get('start', 0) + cumulative_time,
                        'end': min(sub.get('end', 0), actual_scene_duration) + cumulative_time  # Cap at scene duration
                    }
                    combined_subtitles.append(adjusted_sub)
            
            # Update cumulative time using ACTUAL scene duration used in clip
            # This ensures perfect alignment with the actual audio in the final video
            cumulative_time += actual_scene_duration
            print(f"      Scene {i+1} subtitles: adjusted by {cumulative_time - actual_scene_duration:.2f}s, scene duration: {actual_scene_duration:.2f}s")
        
        # Step 4: Add subtitles, progress bar, and background music
        # (Reuse the subtitle and progress bar logic from assemble_video)
        # Load image hook if provided
        hook_clip = None
        if image_hook_path and os.path.exists(image_hook_path):
            print(f"   Loading image hook: {image_hook_path}")
            hook_duration = min(3.0, total_duration)
            try:
                hook_clip = ImageClip(image_hook_path, duration=hook_duration)
                if hook_clip.size != (1080, 1920):
                    hook_clip = hook_clip.resized((1080, 1920))
                hook_clip = hook_clip.with_position('center')
                hook_clip = hook_clip.with_start(0)
                print(f"   ✓ Image hook will display for {hook_duration:.2f}s at start")
            except Exception as e:
                print(f"   ⚠️ Failed to load image hook: {e}")
                hook_clip = None
        
        # Ensure font exists
        font_path = _ensure_font_exists()
        
        # Generate subtitle clips (reuse logic from assemble_video)
        def group_subtitles(subtitles, max_chars=30):
            if not subtitles:
                return []
            
            phrase_blocks = []
            current_phrase = []
            current_chars = 0
            phrase_start = subtitles[0].get('start', 0)
            
            for sub in subtitles:
                word = sub.get('word', '').strip()
                if not word:
                    continue
                
                word_chars = len(word) + 1
                
                if current_chars + word_chars > max_chars and current_phrase:
                    phrase_text = ' '.join(current_phrase)
                    phrase_end = sub.get('start', phrase_start + 0.5)
                    phrase_blocks.append({
                        'text': phrase_text,
                        'start': phrase_start,
                        'end': phrase_end
                    })
                    current_phrase = [word]
                    current_chars = word_chars
                    phrase_start = sub.get('start', 0)
                else:
                    current_phrase.append(word)
                    current_chars += word_chars
            
            if current_phrase:
                phrase_text = ' '.join(current_phrase)
                phrase_end = subtitles[-1].get('end', phrase_start + 0.5)
                phrase_blocks.append({
                    'text': phrase_text,
                    'start': phrase_start,
                    'end': phrase_end
                })
            
            return phrase_blocks
        
        phrase_blocks = group_subtitles(combined_subtitles, max_chars=30)
        print(f"   Grouped {len(combined_subtitles)} words into {len(phrase_blocks)} phrase blocks")
        
        text_clips = []
        
        # KEYWORD COLORS (Retention Hack)
        SCARY_WORDS = ['scary', 'terrifying', 'disturbing', 'dead', 'death', 'blood', 'ghost', 'demon', 'killer', 'murder', 'horror', 'scream', 'shocking']
        MYSTERY_WORDS = ['unsolved', 'mystery', 'secret', 'hidden', 'vanishing', 'disappeared', 'lost', 'unknown', 'never']
        
        for phrase in phrase_blocks:
            text = phrase.get('text', '').strip()
            start = phrase.get('start', 0)
            end = phrase.get('end', start + 0.5)
            
            if not text or end <= start:
                continue
            
            try:
                # Basic styling
                clip_kwargs = {
                    'text': text,
                    'font_size': 90,  # Larger for mobile
                    'color': '#FFFFFF', # Default White
                    'stroke_color': 'black',
                    'stroke_width': 5,
                    'method': 'caption',
                    'size': (950, None)
                }
                
                # Check if phrase contains keywords to change entire block color (higher impact)
                text_lower = text.lower()
                if any(w in text_lower for w in SCARY_WORDS):
                    clip_kwargs['color'] = '#FF0000' # Blood Red
                elif any(w in text_lower for w in MYSTERY_WORDS):
                    clip_kwargs['color'] = '#FFE500' # Golden Yellow
                
                arial_fonts = [
                    '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
                    '/System/Library/Fonts/Helvetica.ttc',
                    font_path
                ]
                
                txt_clip = None
                for arial_font in arial_fonts:
                    if arial_font and os.path.exists(arial_font):
                        try:
                            txt_clip = TextClip(font=arial_font, **clip_kwargs)
                            break
                        except:
                            continue
                
                if not txt_clip:
                    txt_clip = TextClip(**clip_kwargs)
                
                video_height = final_video.h
                y_position = int(video_height * 0.65) # Higher up for better visibility on mobile
                
                # Dynamic Scale Animation (Pop-in)
                def pop_in(t):
                    # Slight elastic pop at the start of the phrase
                    if t < 0.2:
                        return 0.8 + 1.5 * t # 0.8 -> 1.1 scale
                    elif t < 0.4:
                        return 1.1 - 0.5 * (t - 0.2) # 1.1 -> 1.0 scale
                    return 1.0
                
                txt_clip = txt_clip.resize(pop_in)
                
                txt_clip = txt_clip.with_position(('center', y_position))
                txt_clip = txt_clip.with_start(start)
                txt_clip = txt_clip.with_duration(end - start)
                
                text_clips.append(txt_clip)
                
            except Exception as e:
                print(f"   ⚠️ Warning: Could not create kinetic text clip: {e}")
        
        # Create red progress bar
        print("   Creating red progress bar (retention hack)...")
        progress_bar_height = 10
        progress_bar_color = (255, 0, 0)
        
        segment_duration = 0.1
        num_segments = int(total_duration / segment_duration) + 1
        
        progress_segments = []
        for i in range(num_segments):
            t = i * segment_duration
            if t >= total_duration:
                break
            width = max(1, int(1080 * (t / total_duration)))
            
            segment = ColorClip(
                size=(width, progress_bar_height),
                color=progress_bar_color,
                duration=segment_duration
            )
            progress_segments.append(segment)
        
        if progress_segments:
            progress_bar = concatenate_videoclips(progress_segments)
            progress_bar = progress_bar.with_duration(total_duration)
        else:
            progress_bar = ColorClip(
                size=(1080, progress_bar_height),
                color=progress_bar_color,
                duration=total_duration
            )
        
        video_height = final_video.h
        bottom_y = video_height - progress_bar_height
        progress_bar = progress_bar.with_position((0, bottom_y))
        progress_bar = progress_bar.with_start(0)
        
        # Create subtle dark overlay to make yellow/white text pop (Sigma aesthetic)
        print("   Applying dark cinematic overlay...")
        video_width, video_height = final_video.w, final_video.h
        dark_layer = ColorClip(
            size=(video_width, video_height),
            color=(0, 0, 0),
            duration=total_duration,
        ).with_opacity(0.3)
        
        # Composite final video with dark layer UNDER text but OVER raw footage
        print("   Compositing video, dark overlay, progress bar, and subtitles...")
        composite_clips = [final_video, dark_layer]
        
        if hook_clip:
            composite_clips.insert(0, hook_clip)
        
        composite_clips.extend(text_clips)
        composite_clips.append(progress_bar)
        
        final_composite = CompositeVideoClip(composite_clips)
        
        # Add background music (mix with existing audio)
        # Note: Background music mixing is handled in audio_engine, so final_composite already has mixed audio
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Render final video (use software libx264 to avoid hardware encoder issues)
        print(f"   Rendering to: {output_path} (software libx264)...")
        final_composite.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=30,
            bitrate='6000k',
            audio_bitrate='192k',
            logger=None,
        )
        
        # Cleanup
        for clip in scene_clips:
            clip.close()
        final_composite.close()
        if hook_clip:
            hook_clip.close()
        
        # Verify output
        if not os.path.exists(output_path):
            raise Exception(f"Final video was not created at {output_path}")
        
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            raise Exception(f"Final video is empty at {output_path}")
        
        print(f"✓ Editor Agent: Video assembled: {output_path} ({file_size} bytes)")
        return output_path
        
    except Exception as e:
        print(f"❌ Failed to assemble scene video: {e}")
        raise


def assemble_video(video_path: str, audio_path: str, subtitles: list, output_path: str, image_hook_path: str = None) -> str:
    """
    Assemble final video: combine background video, audio, subtitles, and optional image hook.
    
    Args:
        video_path: Path to background video file
        audio_path: Path to audio file
        subtitles: List of dicts with 'start', 'end', 'word' keys
        output_path: Path to save final video
        image_hook_path: Optional path to AI-generated image hook (displayed for first 3 seconds)
        
    Returns:
        Path to the assembled video file
        
    Raises:
        Exception: If assembly fails
    """
    print("🎬 Assembling final video...")
    
    try:
        # Load clips
        print("   Loading background video and audio...")
        background = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration
        
        # Load image hook if provided (display for first 3 seconds)
        hook_clip = None
        if image_hook_path and os.path.exists(image_hook_path):
            print(f"   Loading image hook: {image_hook_path}")
            hook_duration = min(3.0, audio_duration)  # 3 seconds or audio duration, whichever is shorter
            try:
                hook_clip = ImageClip(image_hook_path, duration=hook_duration)
                # Resize to 1080x1920 if needed
                if hook_clip.size != (1080, 1920):
                    hook_clip = hook_clip.resized((1080, 1920))
                hook_clip = hook_clip.with_position('center')
                hook_clip = hook_clip.with_start(0)
                print(f"   ✓ Image hook will display for {hook_duration:.2f}s at start")
            except Exception as e:
                print(f"   ⚠️ Failed to load image hook: {e}")
                hook_clip = None
        
        print(f"   Background duration: {background.duration:.2f}s")
        print(f"   Audio duration: {audio_duration:.2f}s")
        
        # Loop or trim video to match audio duration
        if background.duration < audio_duration:
            # Loop the video
            num_loops = int(audio_duration / background.duration) + 1
            print(f"   Looping background {num_loops} times...")
            looped_clips = [background] * num_loops
            from moviepy import concatenate_videoclips
            background = concatenate_videoclips(looped_clips)
        
        # Trim to exact audio duration
        if background.duration > audio_duration:
            print(f"   Trimming background to {audio_duration:.2f}s...")
            # MoviePy 2.x uses slicing
            background = background[0:audio_duration]
        else:
            # If still shorter after looping, trim audio instead
            if background.duration < audio_duration:
                print(f"   Trimming audio to {background.duration:.2f}s...")
                audio = audio.subclipped(0, background.duration)
                audio_duration = background.duration
        
        # Apply Ken Burns Effect (Artificial Motion - Fake Zoom)
        print("   Applying Ken Burns effect (subtle zoom)...")
        try:
            # Simple approach: Apply static 1.05x zoom to create subtle movement
            # For dynamic zoom, we'd need to split into segments, but static zoom still adds visual interest
            original_size = background.size
            zoom_factor = 1.05
            new_size = (int(original_size[0] * zoom_factor), int(original_size[1] * zoom_factor))
            
            # Resize and crop to center (Ken Burns effect)
            try:
                # Use resize method if available
                if hasattr(background, 'resized'):
                    background = background.resized(new_size)
                elif hasattr(background, 'resize'):
                    background = background.resize(new_size)
                else:
                    # Fallback: use ffmpeg filter
                    background = background.resize(new_size)
                
                # Crop to center to maintain 1080x1920 aspect
                if background.size != (1080, 1920):
                    # Center crop
                    w, h = background.size
                    target_w, target_h = 1080, 1920
                    x_center = (w - target_w) // 2
                    y_center = (h - target_h) // 2
                    try:
                        background = background.cropped(x1=x_center, y1=y_center, x2=x_center+target_w, y2=y_center+target_h)
                    except:
                        # If cropped method doesn't exist, just resize to target
                        background = background.resized((target_w, target_h))
                
                print("   ✓ Ken Burns effect applied (1.05x zoom, centered crop)")
            except Exception as resize_error:
                print(f"   ⚠️ Resize failed: {resize_error}, skipping zoom")
        except Exception as e:
            print(f"   ⚠️ Failed to apply Ken Burns effect: {e}")
            # Continue without zoom if it fails
        
        # Ensure font exists
        font_path = _ensure_font_exists()
        
        # SCIENTIFIC SUBTITLES: Phrase blocks instead of word-by-word
        print(f"   Creating scientific subtitle phrase blocks...")
        
        def group_subtitles(subtitles, max_chars=30):
            """
            Group words into phrase blocks of 20-30 characters.
            
            Args:
                subtitles: List of subtitle dicts with 'word', 'start', 'end'
                max_chars: Maximum characters per phrase block
                
            Returns:
                List of phrase block dicts with 'text', 'start', 'end'
            """
            if not subtitles:
                return []
            
            phrase_blocks = []
            current_phrase = []
            current_chars = 0
            phrase_start = subtitles[0].get('start', 0)
            
            for sub in subtitles:
                word = sub.get('word', '').strip()
                if not word:
                    continue
                
                word_chars = len(word) + 1  # +1 for space
                
                # If adding this word would exceed max_chars, finalize current phrase
                if current_chars + word_chars > max_chars and current_phrase:
                    phrase_text = ' '.join(current_phrase)
                    phrase_end = sub.get('start', phrase_start + 0.5)  # End at start of next word
                    phrase_blocks.append({
                        'text': phrase_text,
                        'start': phrase_start,
                        'end': phrase_end
                    })
                    # Start new phrase
                    current_phrase = [word]
                    current_chars = word_chars
                    phrase_start = sub.get('start', 0)
                else:
                    # Add word to current phrase
                    current_phrase.append(word)
                    current_chars += word_chars
            
            # Add final phrase
            if current_phrase:
                phrase_text = ' '.join(current_phrase)
                phrase_end = subtitles[-1].get('end', phrase_start + 0.5)
                phrase_blocks.append({
                    'text': phrase_text,
                    'start': phrase_start,
                    'end': phrase_end
                })
            
            return phrase_blocks
        
        # Group subtitles into phrase blocks
        phrase_blocks = group_subtitles(subtitles, max_chars=30)
        print(f"   Grouped {len(subtitles)} words into {len(phrase_blocks)} phrase blocks")
        
        text_clips = []
        
        # KEYWORD COLORS (Retention Hack)
        SCARY_WORDS = ['scary', 'terrifying', 'disturbing', 'dead', 'death', 'blood', 'ghost', 'demon', 'killer', 'murder', 'horror', 'scream', 'shocking']
        MYSTERY_WORDS = ['unsolved', 'mystery', 'secret', 'hidden', 'vanishing', 'disappeared', 'lost', 'unknown', 'never']
        
        # Create TextClip for each phrase block
        for phrase in phrase_blocks:
            text = phrase.get('text', '').strip()
            start = phrase.get('start', 0)
            end = phrase.get('end', start + 0.5)
            
            if not text:
                continue
            
            # Ensure valid timing
            if end <= start:
                end = start + 0.5  # Minimum duration
            
            try:
                # Basic styling
                clip_kwargs = {
                    'text': text,
                    'font_size': 90,
                    'color': '#FFFFFF',
                    'stroke_color': 'black',
                    'stroke_width': 5,
                    'method': 'caption',
                    'size': (950, None)
                }
                
                # Check for keywords and colorize
                text_lower = text.lower()
                if any(w in text_lower for w in SCARY_WORDS):
                    clip_kwargs['color'] = '#FF0000' # Red
                elif any(w in text_lower for w in MYSTERY_WORDS):
                    clip_kwargs['color'] = '#FFE500' # Yellow
                
                # Try preferred fonts
                arial_fonts = [
                    '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
                    '/System/Library/Fonts/Helvetica.ttc',
                    font_path
                ]
                
                txt_clip = None
                for arial_font in arial_fonts:
                    if arial_font and os.path.exists(arial_font):
                        try:
                            txt_clip = TextClip(font=arial_font, **clip_kwargs)
                            break
                        except:
                            continue
                
                if not txt_clip:
                    txt_clip = TextClip(**clip_kwargs)
                
                # Position and Animation
                video_height = background.h
                y_position = int(video_height * 0.65)
                
                # Dynamic Scale Animation (Elastic Pop)
                def pop_in(t):
                    if t < 0.2:
                        return 0.8 + 1.5 * t 
                    elif t < 0.4:
                        return 1.1 - 0.5 * (t - 0.2)
                    return 1.0
                
                txt_clip = txt_clip.resize(pop_in)
                txt_clip = txt_clip.with_position(('center', y_position))
                txt_clip = txt_clip.with_start(start)
                txt_clip = txt_clip.with_duration(end - start)
                
                text_clips.append(txt_clip)
                
            except Exception as e:
                print(f"   ⚠️ Warning: Could not create kinetic text clip: {e}")
        
        print(f"   Created {len(phrase_blocks)} phrase block subtitle clips")
        print(f"   Adding {len(text_clips)} subtitle clips (text + background boxes) to video...")
        
        # Create red progress bar (Retention Hack) - FIXED: Z-Index Force
        print("   Creating red progress bar (retention hack)...")
        progress_bar_height = 10
        progress_bar_color = (255, 0, 0)  # Strict RGB tuple for red
        
        # Create animated progress bar by concatenating small segments
        segment_duration = 0.1
        num_segments = int(audio_duration / segment_duration) + 1
        
        progress_segments = []
        for i in range(num_segments):
            t = i * segment_duration
            if t >= audio_duration:
                break
            progress = min(t / audio_duration, 1.0)
            width = max(1, int(1080 * (t / audio_duration)))  # Strict int() conversion
            
            segment = ColorClip(
                size=(width, progress_bar_height),
                color=progress_bar_color,  # Strict RGB tuple
                duration=segment_duration
            )
            progress_segments.append(segment)
        
        # Concatenate all segments
        if progress_segments:
            from moviepy import concatenate_videoclips
            progress_bar = concatenate_videoclips(progress_segments)
            progress_bar = progress_bar.with_duration(audio_duration)  # Ensure exact duration
        else:
            # Fallback: simple static bar
            progress_bar = ColorClip(
                size=(1080, progress_bar_height),
                color=progress_bar_color,  # Strict RGB tuple
                duration=audio_duration
            )
        
        # Position at BOTTOM of screen - Force absolute bottom position
        video_height = background.h  # Should be 1920 for vertical format
        bottom_y = video_height - progress_bar_height  # Absolute bottom position
        progress_bar = progress_bar.with_position((0, bottom_y))  # Left-bottom anchor
        progress_bar = progress_bar.with_start(0)
        
        print(f"   ✓ Progress bar created (red, {progress_bar_height}px height, animated left-to-right 0→1080px, positioned at BOTTOM: y={bottom_y})")
        
        # Create subtle dark overlay to make text pop (Sigma / moody look)
        print("   Applying dark cinematic overlay...")
        bg_width, bg_height = background.w, background.h
        dark_layer = ColorClip(
            size=(bg_width, bg_height),
            color=(0, 0, 0),
            duration=audio_duration,
        ).with_opacity(0.3)
        
        # Composite final video: background + dark layer, then subtitles + progress bar
        print("   Compositing video, dark overlay, progress bar, audio, and subtitles...")
        composite_clips = [background, dark_layer]
        
        # Add image hook if present (will show for first 3 seconds)
        if hook_clip:
            composite_clips.insert(0, hook_clip)  # Hook at very beginning
        
        # Add text clips (subtitles)
        composite_clips.extend(text_clips)
        
        # Z-INDEX FORCE: Progress bar LAST = rendered on top
        composite_clips.append(progress_bar)
        
        final_video = CompositeVideoClip(composite_clips)
        # MoviePy 2.x: set audio using with_audio method or by setting audio attribute
        try:
            final_video = final_video.with_audio(audio)
        except AttributeError:
            # Fallback: set audio directly
            final_video = final_video.set_audio(audio)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Render final video (Optimized for 8GB M1 MacBook Pro)
        print(f"   🚀 M1-ACCELERATED RENDER: {output_path} (h264_videotoolbox)...")
        
        # Flush memory before heavy render
        gc.collect()
        
        final_video.write_videofile(
            output_path,
            codec='h264_videotoolbox', # Apple Silicon Hardware Encoder
            audio_codec='aac',
            fps=30,
            bitrate='6000k',  # High quality
            audio_bitrate='192k',
            threads=4,        # Optimal thread count for 8GB machine
            logger=None,
        )
        
        # Cleanup
        background.close()
        audio.close()
        if hook_clip:
            hook_clip.close()
        final_video.close()
        
        # Verify output
        if not os.path.exists(output_path):
            raise Exception(f"Final video was not created at {output_path}")
        
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            raise Exception(f"Final video is empty at {output_path}")
        
        print(f"✓ Video assembled: {output_path} ({file_size} bytes)")
        return output_path
        
    except Exception as e:
        print(f"❌ Failed to assemble video: {e}")
        raise


if __name__ == "__main__":
    # Test the render engine
    print("=" * 60)
    print("🧪 TESTING RENDER ENGINE")
    print("=" * 60)
    
    # This would require test files
    print("Note: Run full pipeline test via main.py")

