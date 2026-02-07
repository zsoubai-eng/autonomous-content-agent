"""
SIMPLE RENDER ENGINE (Horror Stories)
Module: Renders horror story videos with real images and background music.

Uses real horror-related images with Ken Burns effect, no subtitles.
"""

import os
import random
import math
from moviepy import AudioFileClip, ImageClip, CompositeVideoClip, ColorClip, TextClip
from typing import List, Optional
import numpy as np


def _ensure_font_exists():
    """
    Ensure a bold font exists for subtitles.
    Priority: Roboto Black > Montserrat SemiBold > Impact > System fonts
    (Expert recommendations for premium horror subtitle design)
    """
    fonts_dir = "fonts"
    os.makedirs(fonts_dir, exist_ok=True)
    
    # Priority order (expert recommendations)
    preferred_fonts = [
        os.path.join(fonts_dir, "Roboto-Black.ttf"),  # Best: Zero latency (Android system font)
        os.path.join(fonts_dir, "Montserrat-SemiBold.ttf"),  # Alternative: Premium feel
        os.path.join(fonts_dir, "Impact.ttf"),  # Fallback: Bold, readable
    ]
    
    # Check preferred fonts first
    for font_path in preferred_fonts:
        if os.path.exists(font_path):
            return font_path
    
    # Try system fonts (Mac/Linux)
    system_fonts = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",  # Mac
        "/System/Library/Fonts/Helvetica.ttc",  # Mac
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
    ]
    for sys_font in system_fonts:
        if os.path.exists(sys_font):
            return sys_font
    
    # No font found - MoviePy will use default
    return None


def _apply_ken_burns_effect(image_clip, duration: float, zoom_start: float = 1.0, zoom_end: float = 1.1):
    """
    Apply Ken Burns effect (zoom/pan) to an image clip.
    
    Args:
        image_clip: ImageClip to animate
        duration: Duration of the clip
        zoom_start: Starting zoom factor (1.0 = no zoom)
        zoom_end: Ending zoom factor (1.1 = 10% zoom in)
        
    Returns:
        Animated ImageClip with Ken Burns effect
    """
    from moviepy import VideoClip
    
    target_size = (1080, 1920)
    
    # Calculate zoom animation
    def make_frame(t):
        # Linear zoom interpolation
        zoom = zoom_start + (zoom_end - zoom_start) * (t / duration)
        
        # Scale image
        w, h = image_clip.size
        new_w = int(w * zoom)
        new_h = int(h * zoom)
        
        # Resize
        from PIL import Image
        import numpy as np
        
        pil_img = image_clip.to_frame(t).astype(np.uint8)
        pil_img = Image.fromarray(pil_img)
        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Crop to center
        crop_x = (new_w - target_size[0]) // 2
        crop_y = (new_h - target_size[1]) // 2
        pil_img = pil_img.crop((crop_x, crop_y, crop_x + target_size[0], crop_y + target_size[1]))
        
        return np.array(pil_img)
    
    # Create animated clip
    animated = VideoClip(make_frame, duration=duration)
    return animated


def render_horror_video(
    narration_audio_path: str,
    background_music_path: str,
    image_path: str = None,
    image_paths: List[str] = None,
    output_path: str = None,
    video_duration: float = None,
    subtitles: List[dict] = None,
    story_title: str = None,
    gameplay_path: str = None
) -> str:
    """
    Render a horror story video with real images, animated subtitles, and background music.
    
    Features:
    - Dual-Visual Split (Optional): Top half content, bottom half satisfying gameplay
    - Multiple images (5-7) with smooth transitions for psychological engagement
    - Ken Burns effect with micro-shake (horror tension)
    - Animated subtitles (fade in/out, slide from bottom)
    - Found Footage Overlay (REC icon + 4K badge)
    - Floating "TRUE STORY" badge
    - Yellow subtitle styling (horror aesthetic)
    
    Args:
        narration_audio_path: Path to TTS narration audio file
        background_music_path: Path to background music file
        image_path: Path to single horror-related image file (backward compatibility)
        image_paths: List of paths to multiple images (5-7 recommended for visual variety)
        output_path: Path to save final video
        video_duration: Optional duration override (if None, uses narration duration)
        subtitles: List of subtitle dicts with 'word', 'start', 'end' (optional)
        story_title: Story title to display in video (optional)
        gameplay_path: Path to satisfying gameplay video for split-screen (Minecraft/GTA)
        
    Returns:
        Path to the rendered video file
    """
    print("🎬 Simple Render: Creating horror video with Dual-Visual AI configuration...")
    
    if gameplay_path:
        print(f"   🧠 MODE: Dual-Visual TikTok Brain (Split Screen Enabled)")
    
    # Support both single image (backward compatibility) and multiple images
    if image_paths is None:
        if image_path is None:
            raise ValueError("Either image_path or image_paths must be provided")
        image_paths = [image_path]
    
    print(f"   📸 Using {len(image_paths)} images for visual variety (Top Screen)...")
    
    try:
        # Use pydub for audio mixing (more reliable than MoviePy for volume control)
        from pydub import AudioSegment
        
        # Load narration
        narration_seg = AudioSegment.from_mp3(narration_audio_path)
        narration_duration_ms = len(narration_seg)
        final_duration = video_duration if video_duration else (narration_duration_ms / 1000.0)
        final_duration_ms = int(final_duration * 1000)
        
        # Trim narration to exact duration if needed
        if narration_duration_ms > final_duration_ms:
            narration_seg = narration_seg[:final_duration_ms]
        
        # Prepare final audio
        if background_music_path and os.path.exists(background_music_path):
            # Load and prepare background music
            bg_music_seg = AudioSegment.from_mp3(background_music_path)
            
            # Loop background music to match duration
            if len(bg_music_seg) < final_duration_ms:
                loops_needed = (final_duration_ms // len(bg_music_seg)) + 1
                bg_music_seg = bg_music_seg * loops_needed
            
            # Trim to exact duration
            bg_music_seg = bg_music_seg[:final_duration_ms]
            
            # Lower background music volume (30% volume = -10.5dB)
            bg_music_seg = bg_music_seg - 10  # Approximate -10dB for 30% volume
            
            # Mix narration + background music (overlay music under narration)
            final_audio_seg = bg_music_seg.overlay(narration_seg)
        else:
            # Use narration as is (assuming it's already mixed or we're skipping music)
            print("   ⚠️ No background music provided or file missing, using narration only.")
            final_audio_seg = narration_seg
        
        # Save mixed audio to temp file
        import tempfile
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_audio_path = temp_audio.name
        temp_audio.close()
        final_audio_seg.export(temp_audio_path, format='mp3')
        
        # Load mixed audio into MoviePy for video composition
        final_audio = AudioFileClip(temp_audio_path)
        
        # Calculate timing for multiple images (distribute evenly with transitions)
        num_images = len(image_paths)
        transition_duration = 0.5  # 0.5 second crossfade between images
        image_duration = (final_duration - (transition_duration * (num_images - 1))) / num_images
        
        print(f"   📊 Image timing: {image_duration:.2f}s per image, {transition_duration}s transitions")
        
        # Prepare all images
        # DUAL-VISUAL LOGIC: If gameplay is provided, content is top-half only
        target_size = (1080, 1920) if not gameplay_path else (1080, 960)
        content_y_pos = 0 if gameplay_path else 0
        image_clips = []
        
        for i, img_path in enumerate(image_paths):
            if not os.path.exists(img_path):
                print(f"   ⚠️ Image {i+1} not found: {img_path}, skipping...")
                continue
            
            print(f"   Loading image {i+1}/{num_images}: {os.path.basename(img_path)}")
            
            # Convert image to RGB if needed
            from PIL import Image as PILImage
            temp_image_path = None
            try:
                pil_img = PILImage.open(img_path)
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                temp_image_path = img_path.replace('.jpg', f'_temp_rgb_{i}.jpg').replace('.png', f'_temp_rgb_{i}.jpg')
                if temp_image_path == img_path:
                    temp_image_path = img_path + f'_temp_rgb_{i}.jpg'
                pil_img.save(temp_image_path, 'JPEG', quality=95)
                image_path_to_use = temp_image_path
            except Exception as e:
                print(f"   ⚠️ PIL conversion failed: {e}, using original image")
                image_path_to_use = img_path
            
            # Load and prepare image
            pil_original = PILImage.open(image_path_to_use)
            if pil_original.mode != 'RGB':
                pil_original = pil_original.convert('RGB')
            
            # Resize to target size
            pil_original = pil_original.resize(target_size, PILImage.Resampling.LANCZOS)
            
            # Create zoomed version for Ken Burns
            zoom_factor = 1.08
            zoomed_size = (int(target_size[0] * zoom_factor), int(target_size[1] * zoom_factor))
            pil_zoomed = pil_original.resize(zoomed_size, PILImage.Resampling.LANCZOS)
            
            # Calculate start time for this image
            start_time = i * (image_duration + transition_duration)
            
            # Create closure to capture image data
            def create_frame_maker(pil_orig, pil_zoom, img_start, img_dur):
                def make_animated_frame(t):
                    # Calculate local time within this image's duration
                    local_t = t - img_start
                    if local_t < 0:
                        local_t = 0
                    if local_t > img_dur:
                        local_t = img_dur
                    
                    # Calculate zoom (from 1.08 to 1.0 - zoom out)
                    progress = local_t / img_dur if img_dur > 0 else 0
                    current_zoom = zoom_factor - (zoom_factor - 1.0) * progress
                    
                    # Calculate pan (subtle horizontal movement)
                    pan_offset_x = int(math.sin(progress * math.pi * 2) * 20)
                    
                    # Calculate shake (micro-movements for horror tension)
                    shake_x = int(math.sin(t * 15) * 2)
                    shake_y = int(math.cos(t * 12) * 2)
                    
                    # Current scaled size
                    current_w = int(target_size[0] * current_zoom)
                    current_h = int(target_size[1] * current_zoom)
                    
                    # Resize to current zoom level
                    pil_frame = pil_zoom.resize((current_w, current_h), PILImage.Resampling.LANCZOS)
                    
                    # Crop to center with pan + shake
                    crop_x = (current_w - target_size[0]) // 2 - pan_offset_x - shake_x
                    crop_y = (current_h - target_size[1]) // 2 - shake_y
                    crop_x = max(0, min(crop_x, current_w - target_size[0]))
                    crop_y = max(0, min(crop_y, current_h - target_size[1]))
                    
                    pil_frame = pil_frame.crop((crop_x, crop_y, crop_x + target_size[0], crop_y + target_size[1]))
                    
                    return np.array(pil_frame)
                return make_animated_frame
            
            # Create animated clip for this image
            from moviepy import VideoClip
            frame_maker = create_frame_maker(pil_original, pil_zoomed, start_time, image_duration)
            animated_clip = VideoClip(frame_maker, duration=image_duration + transition_duration)
            animated_clip = animated_clip.with_start(start_time)
            
            # Note: Fade transitions removed temporarily - will implement properly later
            # For now, images transition directly (still provides visual variety with Ken Burns)
            
            image_clips.append(animated_clip)
        
        # Composite all image clips
        print(f"   🎨 Compositing {len(image_clips)} images with transitions...")
        from moviepy import VideoClip, VideoFileClip
        
        # Horror content (Top half if split, Full screen if not)
        content_video = CompositeVideoClip(image_clips, size=target_size)
        content_video = content_video.with_duration(final_duration)
        
        composite_clips = []
        
        if gameplay_path and os.path.exists(gameplay_path):
            print(f"   🚁 Injecting Satisfying Gameplay (Bottom Half)...")
            try:
                gameplay_clip = VideoFileClip(gameplay_path).without_audio()
                # Loop gameplay if shorter than story
                if gameplay_clip.duration < final_duration:
                    gameplay_clip = gameplay_clip.loop(duration=final_duration)
                else:
                    gameplay_clip = gameplay_clip.with_duration(final_duration)
                
                # Resize and crop to bottom half
                gameplay_clip = gameplay_clip.resized(height=960)
                # Ensure width is exactly 1080 (center crop)
                w, h = gameplay_clip.size
                if w > 1080:
                    gameplay_clip = gameplay_clip.cropped(x1=(w-1080)//2, x2=(w+1080)//2)
                
                gameplay_clip = gameplay_clip.with_position(('center', 960))
                composite_clips.append(gameplay_clip)
                
                # Content goes on top
                content_video = content_video.with_position(('center', 0))
                composite_clips.append(content_video)
                
                # Global size for final composition
                global_size = (1080, 1920)
            except Exception as ge:
                print(f"      ⚠️ Gameplay integration failed: {ge}. Using full-screen fallback.")
                content_video = content_video.resized((1080, 1920))
                composite_clips.append(content_video)
                global_size = (1080, 1920)
        else:
            composite_clips.append(content_video)
            global_size = target_size

        base_video = CompositeVideoClip(composite_clips, size=global_size)
        base_video = base_video.with_audio(final_audio).with_duration(final_duration)
        
        # Add story title overlay (first 3 seconds - shows what the video is about)
        title_clip = None
        title_bg = None
        if story_title:
            print(f"   Creating title overlay: '{story_title}'...")
            font_path = _ensure_font_exists()
            try:
                # Truncate title if too long (max 50 chars for readability)
                display_title = story_title[:50] + "..." if len(story_title) > 50 else story_title
                
                title_clip = TextClip(
                    text=display_title,
                    font_size=70,
                    color='#FFFFFF',
                    stroke_color='#000000',
                    stroke_width=3,
                    font=font_path if font_path and os.path.exists(font_path) else None
                ).with_position(('center', int(1920 * 0.12))).with_start(0).with_duration(3.0)
                title_clip = title_clip.with_opacity(1.0)
                
                # Add semi-transparent background for title
                title_bg = ColorClip(
                    size=(title_clip.w + 40, title_clip.h + 20),
                    color=(0, 0, 0),
                    duration=3.0
                ).with_opacity(0.7).with_position(('center', int(1920 * 0.12) - 10))
                
                print(f"      ✓ Title overlay added: '{display_title}'")
            except Exception as e:
                print(f"      ⚠️ Could not create title overlay: {e}")
                title_clip = None
                title_bg = None
        
        # Add hook overlay (first 2 seconds - critical for retention)
        print(f"   Creating hook overlay (first 2 seconds)...")
        hook_texts = [
            "This story will haunt you...",
            "You won't believe what happened...",
            "This true story is terrifying...",
            "What really happened?",
            "This mystery remains unsolved..."
        ]
        import random
        hook_text = random.choice(hook_texts)
        
        # Get font path for hook
        hook_font_path = _ensure_font_exists()
        
        try:
            hook_clip = TextClip(
                text=hook_text,
                font_size=80,  # Reduced from 120
                color='#FF0000',
                stroke_color='#000000',
                stroke_width=4,  # Reduced from 6
                font=hook_font_path if hook_font_path and os.path.exists(hook_font_path) else None
            ).with_position(('center', int(1920 * 0.20))).with_start(0).with_duration(2.0)  # Moved down to avoid title
            
            # Use static opacity (MoviePy lambda issues)
            hook_clip = hook_clip.with_opacity(1.0)
            
            # Add red background for hook
            hook_bg = ColorClip(
                size=(hook_clip.w + 60, hook_clip.h + 30),
                color=(255, 0, 0),
                duration=2.0
            ).with_opacity(0.9).with_position(('center', int(1920 * 0.20) - 15))
            hook_bg = hook_bg.with_opacity(0.9)
            
            print(f"      ✓ Hook added: '{hook_text}'")
        except Exception as e:
            print(f"      ⚠️ Could not create hook: {e}")
            hook_clip = None
            hook_bg = None
        
        # Add subtitles if provided
        composite_clips = [base_video]
        # Add title overlay first (bottom layer)
        if title_bg:
            composite_clips.append(title_bg)
        if title_clip:
            composite_clips.append(title_clip)
        # Add hook overlay
        if hook_bg:
            composite_clips.append(hook_bg)
        if hook_clip:
            composite_clips.append(hook_clip)
            
        # --- FOUND FOOTAGE OVERLAYS (Market Standard) ---
        print(f"   📹 Applying Found Footage Overlays...")
        try:
            # 1. REC Dot (Static for stability)
            rec_text = TextClip(
                text="🔴 REC",
                font_size=40,
                color='#FFFFFF',
                font=font_path
            ).with_position((50, 50)).with_start(0).with_duration(final_duration).with_opacity(0.8)
            composite_clips.append(rec_text)
            
            # 2. 4K 60FPS Badge
            badge_4k = TextClip(
                text="4K 60FPS",
                font_size=30,
                color='#FFFFFF',
                font=font_path
            ).with_position((50, 100)).with_start(0).with_duration(final_duration).with_opacity(0.6)
            composite_clips.append(badge_4k)
            
            # 3. ISO/Shutter text (Faux Metadata)
            metadata_text = TextClip(
                text="ISO 800  1/120s  f/2.8",
                font_size=25,
                color='#FFFFFF',
                font=font_path
            ).with_position(('center', 1850)).with_start(0).with_duration(final_duration).with_opacity(0.4)
            composite_clips.append(metadata_text)
            
        except Exception as fe:
            print(f"      ⚠️ Found Footage Overlays failed: {fe}")
        
        if subtitles:
            print(f"   Creating professional subtitles ({len(subtitles)} words)...")
            
            # NEW PROFESSIONAL DESIGN (Expert Recommendations):
            # - Yellow text (#FFE500) - highest mobile contrast
            # - Black stroke (6-8px) - maximum readability
            # - NO background box - premium feel, doesn't block visuals
            # - Center positioning (58% from top) - safe zone
            # - Larger font (120px) - mobile-first
            # - High-Emotion Highlighting: Scary words in Red/Uppercase
            
            SCARY_KEYWORDS = [
                'blood', 'ghost', 'kill', 'killer', 'murder', 'dead', 'death', 'horror', 
                'scary', 'terrifying', 'fear', 'dark', 'night', 'demon', 'scream', 
                'shadow', 'evil', 'curse', 'unsolved', 'mystery', 'missing', 'alone',
                'paranormal', 'haunting', 'hell', 'grave', 'buried'
            ]
            
            def group_subtitles_smart(subtitles, max_chars=35):
                """Group words into readable phrase blocks with smart timing."""
                if not subtitles:
                    return []
                
                phrase_blocks = []
                current_phrase = []
                current_chars = 0
                phrase_start = subtitles[0].get('start', 0) if subtitles else 0
                
                for i, sub in enumerate(subtitles):
                    word = sub.get('word', '').strip()
                    if not word:
                        continue
                    
                    word_chars = len(word) + 1  # +1 for space
                    word_start = sub.get('start', phrase_start)
                    word_end = sub.get('end', word_start + 0.3)
                    
                    # Check if we should start a new phrase
                    next_word_gap = 0
                    if i + 1 < len(subtitles):
                        next_start = subtitles[i + 1].get('start', word_end)
                        next_word_gap = next_start - word_end
                    
                    # New phrase if: too long, big gap, or last word
                    if (current_chars + word_chars > max_chars and current_phrase) or \
                       (next_word_gap > 0.4 and current_phrase) or \
                       (i == len(subtitles) - 1 and current_phrase):
                        # Finalize current phrase
                        phrase_text = ' '.join(current_phrase)
                        phrase_end = word_start  # End before this word starts (for gaps)
                        phrase_blocks.append({
                            'text': phrase_text,
                            'start': phrase_start,
                            'end': phrase_end
                        })
                        # Start new phrase
                        current_phrase = [word]
                        current_chars = word_chars
                        phrase_start = word_start
                    else:
                        current_phrase.append(word)
                        current_chars += word_chars
                
                # Add final phrase
                if current_phrase:
                    phrase_text = ' '.join(current_phrase)
                    phrase_end = subtitles[-1].get('end', phrase_start + 0.5) if subtitles else phrase_start + 0.5
                    phrase_blocks.append({
                        'text': phrase_text,
                        'start': phrase_start,
                        'end': phrase_end
                    })
                
                return phrase_blocks
            
            phrase_blocks = group_subtitles_smart(subtitles, max_chars=35)
            print(f"      Grouped into {len(phrase_blocks)} phrase blocks")
            
            font_path = _ensure_font_exists()
            
            # Render professional subtitle clips
            for i, phrase in enumerate(phrase_blocks):
                text = phrase.get('text', '').strip()
                
                # SMART HIGHLIGHTING (Market Logic)
                # Check if phrase contains scary words
                contains_scary = any(word.lower().strip(',.?!') in SCARY_KEYWORDS for word in text.split())
                
                # If scary, make uppercase and change color to RED for impact
                display_text = text.upper() if contains_scary else text
                text_color = '#FF0000' if contains_scary else '#FFE500'
                stroke_width = 6 if contains_scary else 4
                
                start = phrase.get('start', 0)
                end = phrase.get('end', start + 0.5)
                duration = max(0.3, end - start)  # Minimum 0.3s duration
                
                if not text or duration <= 0:
                    continue
                
                try:
                    # Professional subtitle styling (optimized size)
                    clip_kwargs = {
                        'text': display_text,
                        'font_size': 85 if contains_scary else 75, # Pop bigger for scary words
                        'color': text_color,  # Highlights scary phrases
                        'stroke_color': '#000000',  # Black stroke
                        'stroke_width': stroke_width,  # Thicker stroke for red text
                        'method': 'caption',
                        'size': (1000, None)  # Width for readability
                    }
                    
                    if font_path and os.path.exists(font_path):
                        clip_kwargs['font'] = font_path
                    
                    txt_clip = TextClip(**clip_kwargs)
                    
                    # Center positioning (58% from top - safe zone, above center)
                    # This keeps text clear of notch/home indicator and YouTube UI overlays
                    y_position = int(1920 * 0.58)
                    position = ('center', y_position)
                    
                    # Apply position and timing
                    txt_clip = txt_clip.with_position(position)
                    txt_clip = txt_clip.with_start(start)
                    txt_clip = txt_clip.with_duration(duration)
                    txt_clip = txt_clip.with_opacity(1.0)
                    
                    # NO BACKGROUND BOX - removed for premium feel (expert consensus)
                    # Yellow text with thick black stroke provides excellent visibility
                    composite_clips.append(txt_clip)
                    
                except Exception as e:
                    print(f"      ⚠️ Warning: Could not create subtitle clip: {e}")
            
            print(f"      ✓ Created {len(phrase_blocks)} professional subtitle blocks (yellow #FFE500, no background box)")
        
        # Add floating "TRUE STORY" badge
        print(f"   Creating floating 'TRUE STORY' badge...")
        try:
            badge_text = "TRUE STORY"
            badge_clip = TextClip(
                text=badge_text,
                font_size=40,
                color='#FFFFFF',
                stroke_color='#FF0000',
                stroke_width=2,
                font=font_path if font_path and os.path.exists(font_path) else None
            )
            
            # Animate badge position (floating top-right)
            def badge_position(t):
                # Floating animation (subtle movement)
                float_x = 1080 - badge_clip.w - 20 + int(math.sin(t * 2) * 5)
                float_y = 20 + int(math.cos(t * 2) * 3)
                return (float_x, float_y)
            
            badge_clip = badge_clip.with_position(badge_position)
            badge_clip = badge_clip.with_start(0)
            badge_clip = badge_clip.with_duration(final_duration)
            badge_clip = badge_clip.with_opacity(0.9)
            
            # Add background box for badge
            badge_bg = ColorClip(
                size=(badge_clip.w + 20, badge_clip.h + 10),
                color=(0, 0, 0),
                duration=final_duration
            ).with_opacity(0.8)
            badge_bg = badge_bg.with_position(lambda t: (badge_position(t)[0] - 10, badge_position(t)[1] - 5))
            badge_bg = badge_bg.with_start(0)
            badge_bg = badge_bg.with_duration(final_duration)
            
            composite_clips.append(badge_bg)
            composite_clips.append(badge_clip)
            print(f"      ✓ Floating badge created")
        except Exception as e:
            print(f"      ⚠️ Warning: Could not create badge: {e}")
        
        # Add loop-worthy ending (encourages rewatch)
        print(f"   Creating loop-worthy ending...")
        try:
            # Get font path for loop text
            loop_font_path = _ensure_font_exists()
            
            loop_text = "Watch again? 👻"
            loop_clip = TextClip(
                text=loop_text,
                font_size=100,
                color='#FFFFFF',
                stroke_color='#000000',
                stroke_width=4,
                font=loop_font_path if loop_font_path and os.path.exists(loop_font_path) else None
            ).with_position(('center', 'center')).with_start(max(0, final_duration - 1.5)).with_duration(1.5)
            
            # Use static opacity (MoviePy lambda issues)
            loop_clip = loop_clip.with_opacity(1.0)
            
            # Add semi-transparent background
            loop_bg = ColorClip(
                size=(loop_clip.w + 40, loop_clip.h + 20),
                color=(0, 0, 0),
                duration=1.5
            ).with_opacity(0.7).with_position(('center', 'center'))
            loop_bg = loop_bg.with_start(max(0, final_duration - 1.5))
            loop_bg = loop_bg.with_opacity(0.7)
            
            composite_clips.append(loop_bg)
            composite_clips.append(loop_clip)
            print(f"      ✓ Loop ending added")
        except Exception as e:
            print(f"      ⚠️ Warning: Could not create loop ending: {e}")
        
        # Composite everything
        final_video = CompositeVideoClip(composite_clips).with_duration(final_duration)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Render
        print(f"   Rendering to: {output_path}...")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=30,
            bitrate='3000k',
            audio_bitrate='192k',
            logger=None
        )
        
        # Cleanup
        final_audio.close()
        if 'image_clip' in locals():
            image_clip.close()
        if 'animated_image' in locals():
            animated_image.close()
        if 'base_video' in locals():
            base_video.close()
        final_video.close()
        for clip in composite_clips:
            if hasattr(clip, 'close'):
                clip.close()
        
        # Clean up temp files
        try:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            if temp_image_path and os.path.exists(temp_image_path) and temp_image_path != image_path:
                os.remove(temp_image_path)
        except:
            pass
        
        # Verify output
        if not os.path.exists(output_path):
            raise Exception(f"Video was not created at {output_path}")
        
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            raise Exception(f"Video is empty at {output_path}")
        
        print(f"✓ Simple video rendered: {output_path} ({file_size} bytes)")
        return output_path
        
    except Exception as e:
        print(f"❌ Failed to render video: {e}")
        raise


# Legacy function name for backward compatibility
def render_audio_only_video(
    narration_audio_path: str,
    background_music_path: str,
    subtitles: List[dict],
    output_path: str,
    video_duration: float = None
) -> str:
    """
    Legacy function - redirects to render_horror_video.
    Note: This function signature is deprecated. Use render_horror_video instead.
    """
    raise Exception("render_audio_only_video is deprecated. Use render_horror_video with image_path instead.")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING SIMPLE RENDER ENGINE")
    print("=" * 60)
    print("Note: Run full pipeline test via main.py --horror")
