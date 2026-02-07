"""
ZERO-COST CONTENT FACTORY
Main Controller: Orchestrates the entire content generation pipeline.

Generates viral YouTube Shorts autonomously using cloud APIs and local processing.
"""

import os
import sys
import time
import random
import argparse
import tempfile
import shutil
import platform
import gc
from dotenv import load_dotenv

# Voice Model Check (Piper TTS)
def ensure_voice_model():
    """Ensure Piper voice model is available."""
    voice_path = os.path.expanduser("~/.local/share/piper/voices/en_US-lessac-medium/en_US-lessac-medium.onnx")
    if not os.path.exists(voice_path):
        print("⚠️ Piper voice model not found. Downloading...")
        try:
            import subprocess
            # Try to download using piper-tts
            from piper.download import ensure_voice_exists
            ensure_voice_exists("en_US-lessac-medium", [os.path.dirname(voice_path)], None)
            print("✓ Voice model downloaded")
        except Exception as e:
            print(f"⚠️ Could not auto-download voice model: {e}")
            print(f"   Please download manually to: {voice_path}")
    else:
        print(f"✓ Voice model found: {voice_path}")

# Load environment variables
load_dotenv()

# Import system audit
from scripts.system_audit import perform_system_audit
from config.paths import TEMP_DIR, SHORTS_OUTPUT_DIR, TEMP_THUMBNAILS_DIR, TEMP_IMAGES_DIR

# Import all departments
from departments.intelligence.research_engine import get_viral_topics
from departments.intelligence.script_engine import generate_script
from departments.production.audio_engine import generate_audio
from departments.production.visual_engine import get_visual_content
from departments.production.image_engine import generate_image_hook
from departments.production.render_engine import assemble_video
from departments.logistics.upload_engine import upload_video


def generate_monetization_comment(title: str, script_text: str, tags: list) -> str:
    """
    Generate an engagement-driven pinned comment based on video topic.
    
    Uses questions to drive engagement (raises Trust Score) instead of just links.
    
    Args:
        title: Video title
        script_text: Script content (for context)
        tags: Video tags
        
    Returns:
        Formatted pinned comment text with engagement questions
    """
    import random
    
    # Extract key topic from title/script for context-aware questions
    script_preview = script_text[:100].lower() if script_text else ""
    
    # Engagement question templates (rotate for variety)
    engagement_questions = [
        "Have you ever felt this? Answer below 👇",
        "What's your experience with this? Drop a comment! 👇",
        "Has this ever happened to you? Share your story 👇",
        "What do you think? Let me know in the comments 👇",
        "Do you agree? Answer with YES or NO 👇",
        "Have you noticed this? Share your thoughts 👇",
        "What's your take on this? Comment below 👇",
        "Have you experienced this before? Tell me 👇",
        "Does this resonate with you? Drop a comment 👇",
        "What's your opinion? Share below 👇",
    ]
    
    # Select random question
    question = random.choice(engagement_questions)
    
    # Generate engagement-focused comment (question first, then optional link)
    comment = f"""{question}

Want to dive deeper? 🧠
Get the 'Dark Psychology Audiobook' for FREE here: [YOUR LINK]

💬 Keep the conversation going! 🚀"""
    
    return comment


def run_horror_factory(video_number: int = 1, total_videos: int = 1, schedule_time: str = None, trend_guidance: str = None, niche_category: str = None):
    """
    Horror Story Factory: Generate horror story → TTS Narration → Background Music → Subtitles → Publish
    
    Simplified workflow: No visuals, just audio + music + subtitles.
    
    Args:
        video_number: Current video number in batch
        total_videos: Total number of videos in batch
        schedule_time: Optional ISO 8601 datetime for scheduled publishing (e.g. 2026-01-17T15:00:00-05:00)
        trend_guidance: Optional social media trend (e.g. 'The Mimic')
        niche_category: Optional niche override ('political', 'business', 'sports')
    
    Returns:
        0 on success, 1 on failure
    """
    print("=" * 60)
    print("👻 HORROR STORY FACTORY - Starting Production")
    print("=" * 60)
    
    try:
        # Step 1: Generate Horror Story
        print("\n[📖 HORROR STORY] Generating real horror story...")
        from departments.intelligence.horror_story_engine import generate_horror_story
        
        # Prepare niche override if category provided
        niche_override = None
        if niche_category:
            # Map simple category names to full niche dicts manually if needed, 
            # or rely on logic to find them. For now, let's look them up from the engine logic or construct them.
            # actually we can import the engine's list but that's private.
            # Let's construct a temp one or modify engine to accept string.
            # simpler: Let's just pass the string trend_guidance was used for similar things?
            # No, let's construct the dict here based on the requested categories
            
            if niche_category.lower() == 'political':
                niche_override = {
                    "category": "Political Dark Secrets",
                    "focus": "Vanished whistleblowers, secret summits, or historical conspiracies",
                    "keywords": ["Classified", "Government", "Evidence", "Cover-up"]
                }
            elif niche_category.lower() == 'business':
                niche_override = {
                    "category": "Corporate Horror",
                    "focus": "Cursed bankruptcies, billionaire hideouts, or corporate espionage gone wrong",
                    "keywords": ["Business", "Billionaire", "Bankruptcy", "Corporate"]
                }
            elif niche_category.lower() == 'sports':
                niche_override = {
                    "category": "Sports Enigmas",
                    "focus": "Athletes who vanished mid-game, cursed stadiums, or rigged occult games",
                    "keywords": ["Stadium", "Athlete", "Mystery", "Unexplained"]
                }
                
        story_data = generate_horror_story(
            force=getattr(args, 'force', False),
            trend_guidance=trend_guidance,
            niche_override=niche_override
        )
        title = story_data.get('title', 'Horror Story')
        # Support both 'story' and 'script' fields
        story_text = story_data.get('story') or story_data.get('script', '')
        story_source = story_data.get('source', '')
        tags = story_data.get('tags', ['horror', 'horror stories', 'scary stories'])
        
        print(f"✓ Story generated: {title}")
        print(f"   Length: {len(story_text.split())} words")
        
        # Step 2: Generate TTS Narration
        print("\n[🎙️ NARRATION] Generating TTS audio...")
        from departments.production.audio_engine import generate_audio
        
        audio_output = os.path.join(TEMP_DIR, f"temp_horror_audio_{video_number}.mp3")
        audio_path, subtitles = generate_audio(story_text, audio_output, script_text=story_text)
        
        # Get actual audio duration
        from moviepy import AudioFileClip
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        audio_clip.close()
        
        print(f"✓ Narration generated: {audio_path}")
        print(f"   Duration: {audio_duration:.2f}s")
        print(f"   Subtitles: {len(subtitles)} words")
        
        # Step 3: Prepare Background Music
        # We now use the Assets folder which contains our pre-downloaded high-quality horror music
        # This allows the Audio Engine to handle 3D Binaural mixing during Step 2
        bg_music_path = os.path.join("assets", "music", "horror_ambient.mp3")
        if not os.path.exists(bg_music_path):
            print("\n[🎵 BACKGROUND MUSIC] Downloading horror background music fallback...")
            from departments.production.youtube_audio_engine import get_horror_background_music
            bg_music_output = os.path.join(TEMP_DIR, f"temp_horror_bg_music_{video_number}.mp3")
            bg_music_path = get_horror_background_music(bg_music_output, audio_duration)
        else:
            print(f"✓ Using premium background music asset: {bg_music_path}")
            
        # NOTE: In our optimized workflow, the Audio Engine (generate_audio) already 
        # mixes the voice with music and binaural SFX if assets are present.
        # We pass None to the render engine to avoid double-mixing.
        
        # Step 4: Download Multiple Horror-Related Images (5-7 for visual variety)
        print("\n[🖼️ IMAGE SEARCH] Finding multiple horror-related images...")
        from departments.production.image_search_engine import download_multiple_horror_images
        import tempfile
        
        # Create temp directory for images
        temp_image_dir = tempfile.mkdtemp(prefix="horror_images_")
        
        # Download 6 images (optimal for 30-second videos: ~5 seconds per image)
        num_images = 6
        image_paths = download_multiple_horror_images(
            story_text=story_text,
            story_title=title,
            output_dir=temp_image_dir,
            num_images=num_images,
            width=1080,
            height=1920
        )
        
        # Step 4.5: Download Gameplay for Split-Screen (Satisfying Content)
        gameplay_path = None
        if hasattr(args, 'split_screen') and args.split_screen:
            print("\n[🎮 GAMEPLAY] Sourcing satisfying background footage (Dual-Visual Mode)...")
            from departments.production.gameplay_engine import download_gameplay_video
            gameplay_path = download_gameplay_video()
            if gameplay_path:
                print(f"✓ Gameplay ready for split-screen: {gameplay_path}")
            else:
                print("⚠️ Gameplay download failed, falling back to full-screen mode.")
        
        if not image_paths or len(image_paths) < 3:
            print(f"   ⚠️ Only {len(image_paths) if image_paths else 0} images downloaded, using single image fallback...")
            from departments.production.image_search_engine import download_horror_image
            if total_videos > 1:
                image_output = f"temp_horror_image_{video_number}.jpg"
            else:
                image_output = "temp_horror_image.jpg"
            fallback_image = download_horror_image(
                story_text=story_text,
                story_title=title,
                output_path=image_output,
                width=1080,
                height=1920
            )
            if fallback_image:
                image_paths = [fallback_image]
            else:
                raise Exception("Failed to download horror images")
        
        print(f"✓ Downloaded {len(image_paths)} images for visual variety")
        
        # Step 5: Render Horror Video (Image + Audio + Background Music, NO subtitles)
        print("\n[🎬 RENDERING] Creating horror video with images...")
        from departments.production.simple_render_engine import render_horror_video
        
        # Create output folder structure
        from datetime import datetime
        output_dir = SHORTS_OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename with story title (sanitized)
        import re
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)[:50]  # Limit length
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{safe_title}_{timestamp}.mp4"
        output_path = os.path.join(output_dir, output_filename)
        
        render_horror_video(
            narration_audio_path=audio_path,
            background_music_path=None,  # Music already mixed in narration_audio_path
            image_paths=image_paths,  # Pass multiple images for visual variety
            output_path=output_path,
            video_duration=None,
            subtitles=subtitles,  # Pass subtitles for animated display
            story_title=title,  # Pass title for overlay
            gameplay_path=gameplay_path
        )
        print(f"✓ Video rendered: {output_path}")
        
        # Step 6: Generate Description with Source (Horror-optimized)
        description = f"""👻 {title}

{story_text}

{story_source if story_source else 'Based on a real horror story.'}

💀 This is a TRUE horror story that will give you chills.

🔔 Subscribe for more scary horror stories every day!

💬 What did you think of this story? Let me know in the comments below!

⚠️ WARNING: This story may be disturbing for some viewers. Viewer discretion is advised.

#HorrorStories #ScaryStories #TrueHorror #HorrorShorts #CreepyStories #UrbanLegends"""
        
        # Step 7: Upload to YouTube (optional, with Trust Score protection)
        if hasattr(args, 'skip_upload') and args.skip_upload:
            print("\n[📊 LOGISTICS DEPT] Skipping YouTube upload (--skip-upload enabled)")
            video_id = None
        else:
            print("\n[📊 LOGISTICS DEPT] Uploading to YouTube...")
            video_id = None
            
            try:
                from departments.logistics.upload_engine import upload_video
                
                video_id = upload_video(
                    file_path=output_path,
                    title=title,
                    description=description,
                    tags=tags,
                    category_id="24",  # Entertainment category
                    horror_mode=True,  # Enable horror-specific tags
                    schedule_time=schedule_time
                )
                
                # Log to history
                if video_id:
                    from departments.logistics.history_engine import log_video
                    log_video(
                        topic=story_text[:200],
                        title=title,
                        video_id=video_id,
                        filename=output_path
                    )
                
            except Exception as e:
                print(f"⚠️ WARNING: YouTube upload failed: {e}")
                print("   Video saved locally for manual upload")
        
        # Generate pinned comment (engagement-driven)
        print("\n[💬 ENGAGEMENT] Generating pinned comment...")
        engagement_comment = f"""Did this story scare you? Share your thoughts below 👇

Have you heard similar stories? Tell me in the comments! 👻

💬 Keep the conversation going!"""
        
        print("=" * 60)
        print("✅ HORROR STORY VIDEO COMPLETE")
        print("=" * 60)
        print(f"   File: {output_path}")
        print(f"   Title: {title}")
        if video_id:
            print(f"   YouTube: https://www.youtube.com/watch?v={video_id}")
        print(f"\n📝 PINNED COMMENT:")
        print(engagement_comment)
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"❌ ERROR: Horror factory failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def run_factory(video_number: int = 1, total_videos: int = 1):
    """
    Main factory function: Generate script → Audio → Visuals → Assemble → Upload
    
    Args:
        video_number: Current video number in batch (for unique file naming)
        total_videos: Total number of videos in batch
    
    Returns:
        0 on success, 1 on failure
    """
    print("=" * 60)
    
    # 8GB M1 Optimization Banner
    if platform.processor() == 'arm' and platform.system() == 'Darwin':
        print("🍏 M1 DETECTED: Activating 8GB RAM Optimization Profile...")
        print("   - Low-Memory MPS compute (int8_float16)")
        print("   - VideoToolbox Hardware Accelerated Encoding")
        print("   - Sequential Garbage Collection / VRAM Flushing")
        gc.collect()
    
    # System Audit (Chief of Staff)
    perform_system_audit()
    
    # Check voice model
    ensure_voice_model()
    
    temp_files = []
    temp_dirs = []
    
    try:
        # Step 0: Market Intelligence - Research Viral Topics
        print("\n[🧠 INTELLIGENCE DEPT] Researching viral topics...")
        viral_titles = []
        try:
            viral_titles = get_viral_topics("Dark Psychology", min_views=100000)
            if viral_titles:
                print(f"✓ Found {len(viral_titles)} viral topics for analysis")
            else:
                print("   ⚠️ No viral topics found, continuing without market intelligence")
        except Exception as e:
            print(f"⚠️ WARNING: Market research failed: {e}")
            print("   Continuing without viral topic data...")
        
        # Step 1: Generate Viral Content
        print("\n[🧠 INTELLIGENCE DEPT] Drafting strategy...")
        try:
            script_data = generate_script(viral_titles=viral_titles)
            
            # Check if scene-based format (new) or old format
            if 'scenes' in script_data:
                # NEW: Scene-based format
                scenes = script_data['scenes']
                script_text = ' '.join([scene.get('text', '') for scene in scenes])
                title = script_data.get('title', 'AI Generated Short')
                tags = script_data.get('tags', [])
                
                print(f"✓ Storyboard generated: {len(scenes)} scenes")
                print(f"   Title: {title}")
                print(f"   Total words: {len(script_text.split())}")
                for i, scene in enumerate(scenes[:3]):  # Show first 3 scenes
                    print(f"   Scene {scene.get('id', i+1)}: {scene.get('text', '')[:50]}...")
            else:
                # OLD: Linear script format (backward compatibility)
                script_text = script_data.get('script', '')
                title = script_data.get('title', 'AI Generated Short')
                tags = script_data.get('tags', [])
                
                print(f"✓ Script generated: {len(script_text.split())} words")
                print(f"   Title: {title}")
                print(f"   Preview: {script_text[:100]}...")
        except Exception as e:
            print(f"❌ ERROR: Failed to generate script: {e}")
            return 1
        
        # Step 1.5: Generate Image Hook
        print("\n[🏭 PRODUCTION DEPT] Generating AI image hook...")
        image_hook_path = None
        try:
            # Extract topic from title or script
            topic = title if title else script_text[:50]
            image_hook_path = f"temp_hook_{video_number}.jpg"
            generate_image_hook(topic, image_hook_path)
            temp_files.append(image_hook_path)
            print(f"✓ Image hook generated: {image_hook_path}")
        except Exception as e:
            print(f"⚠️ WARNING: Failed to generate image hook: {e}")
            print("   Continuing without image hook...")
            image_hook_path = None
        
        # Step 2: Check if scene-based or old format
        if 'scenes' in script_data:
            # NEW AGENTIC WORKFLOW (The Infinite Factory)
            scenes = script_data['scenes']
            
            print("\n" + "=" * 60)
            print("🏭 THE INFINITE FACTORY - AGENTIC WORKFLOW")
            print("=" * 60)
            
            # Step 1: The Strategist (already done - Cerebras generated storyboard)
            print(f"\n[🧠 THE STRATEGIST] Storyboard ready: {len(scenes)} scenes")
            
            # Step 2: The Narrator - Generate Audio for each scene
            print("\n[🎙️ THE NARRATOR] Generating scene audio clips...")
            try:
                from departments.production.audio_engine import generate_scene_audio
                
                temp_audio_dir = f"temp_audio_{video_number}"
                os.makedirs(temp_audio_dir, exist_ok=True)
                temp_dirs.append(temp_audio_dir)
                
                scene_audio_paths, all_subtitles = generate_scene_audio(scenes, temp_audio_dir)
                temp_files.extend(scene_audio_paths)
                
                # Calculate total duration
                total_duration = sum([float(scene.get('duration', 3.0)) for scene in scenes])
                print(f"✓ Narrator: Generated {len(scene_audio_paths)} audio clips ({total_duration:.2f}s total)")
            except Exception as e:
                print(f"❌ ERROR: Narrator failed: {e}")
                return 1
            
            # Step 3: The Artist - Generate Flux Image for each scene
            print("\n[🎨 THE ARTIST] Generating Flux images for each scene...")
            try:
                from departments.production.flux_engine import generate_scene_image
                
                temp_image_dir = f"temp_images_{video_number}"
                os.makedirs(temp_image_dir, exist_ok=True)
                temp_dirs.append(temp_image_dir)
                
                scene_image_paths = []
                for i, scene in enumerate(scenes):
                    scene_id = scene.get('id', i + 1)
                    visual_prompt = scene.get('visual_prompt', 'Cinematic dark noir, moody lighting, hyper-realistic, 8k')
                    
                    print(f"   Generating Scene {scene_id}...")
                    image_path = os.path.join(temp_image_dir, f"scene_{scene_id}.jpg")
                    
                    scene_image = generate_scene_image(visual_prompt, image_path)
                    scene_image_paths.append(scene_image)
                    temp_files.append(scene_image)
                
                print(f"✓ Artist: Generated {len(scene_image_paths)} Flux images")
            except Exception as e:
                print(f"❌ ERROR: Artist failed: {e}")
                return 1
            
            # Step 4: The Animator - Convert Images to Video Clips
            print("\n[🎬 THE ANIMATOR] Converting images to animated video clips...")
            try:
                from departments.production.render_engine import animate_scene
                
                temp_video_dir = f"temp_video_{video_number}"
                os.makedirs(temp_video_dir, exist_ok=True)
                temp_dirs.append(temp_video_dir)
                
                scene_video_paths = []
                for i, (scene, image_path) in enumerate(zip(scenes, scene_image_paths)):
                    scene_id = scene.get('id', i + 1)
                    scene_duration = float(scene.get('duration', 3.0))
                    
                    print(f"   Animating Scene {scene_id} ({scene_duration:.1f}s)...")
                    video_path = os.path.join(temp_video_dir, f"scene_{scene_id}.mp4")
                    
                    animated_video = animate_scene(image_path, scene_duration, video_path)
                    scene_video_paths.append(animated_video)
                    temp_files.append(animated_video)
                
                print(f"✓ Animator: Created {len(scene_video_paths)} animated video clips")
            except Exception as e:
                print(f"❌ ERROR: Animator failed: {e}")
                return 1
            
            # Step 5: The Editor - Stitch all clips together + Background Music + Progress Bar
            print("\n[✂️ THE EDITOR] Assembling final video...")
            try:
                from departments.production.render_engine import assemble_scene_video
                
                # Unique output filename for batch mode
                if total_videos > 1:
                    output_path = f"final_short_{video_number}.mp4"
                else:
                    output_path = "final_short.mp4"
                
                assemble_scene_video(
                    scene_video_paths, 
                    scene_audio_paths, 
                    all_subtitles, 
                    scenes, 
                    output_path, 
                    image_hook_path
                )
                print(f"✓ Editor: Final video assembled: {output_path}")
                
                # Log video to history to prevent duplicates
                from departments.logistics.history_engine import log_video
                log_video(
                    topic=script_text[:200],  # First 200 chars of script
                    title=title,
                    video_id=None,  # Not uploaded yet
                    filename=output_path
                )
            except Exception as e:
                print(f"❌ ERROR: Editor failed: {e}")
                return 1
            
            # Set audio_duration for later use
            audio_duration = total_duration
            
        else:
            # OLD LINEAR WORKFLOW (backward compatibility)
            # Step 2: Create Audio
            print("\n[🏭 PRODUCTION DEPT] Generating audio (LEAN CASCADE)...")
            try:
                audio_path = f"temp_audio_{video_number}.mp3"
                audio_path, subtitles = generate_audio(script_text, audio_path, script_text=script_text)
                temp_files.append(audio_path)
                
                # Get audio duration from subtitles
                if subtitles:
                    audio_duration = subtitles[-1]['end']
                else:
                    # Estimate from word count
                    words = script_text.split()
                    audio_duration = len(words) / 2.5
                
                print(f"✓ Audio generated: {audio_duration:.2f} seconds")
            except Exception as e:
                print(f"❌ ERROR: Failed to generate audio: {e}")
                return 1
            
            # Step 2.5: Quality Control - Audio Processing
            print("\n[🔬 QUALITY CONTROL DEPT] Processing audio...")
            try:
                from departments.quality_control.qc_engine import remove_silence, normalize_audio_mix, apply_speedup
                
                pacing = script_data.get('pacing', 'Normal')
                
                # Normalize audio mix (voice + background music)
                music_dir = "assets/music"
                music_files = [f for f in os.listdir(music_dir) if os.path.exists(music_dir) and f.endswith('.mp3')]
                if music_files:
                    import random
                    music_path = os.path.join(music_dir, random.choice(music_files))
                    audio_path = normalize_audio_mix(audio_path, music_path, audio_path)
                else:
                    audio_path = normalize_audio_mix(audio_path, None, audio_path)
                
                print(f"✓ Audio QC complete")
            except Exception as e:
                print(f"⚠️ WARNING: QC audio processing failed: {e}")
                print("   Continuing with original audio...")
            
            # Step 3: Source Visuals (SUPER-CASCADE)
            print("\n[🏭 PRODUCTION DEPT] Sourcing background video (SUPER-CASCADE)...")
            try:
                video_path = f"temp_background_{video_number}.mp4"
                pacing = script_data.get('pacing', 'Normal')
                video_path = get_visual_content(audio_duration, video_path, script_data, pacing)
                temp_files.append(video_path)
                print(f"✓ Background video ready")
            except Exception as e:
                print(f"❌ ERROR: Failed to get background video: {e}")
                return 1
            
            # Step 4: Assemble Video
            print("\n[🏭 PRODUCTION DEPT] Rendering video...")
            try:
                # Unique output filename for batch mode
                if total_videos > 1:
                    output_path = f"final_short_{video_number}.mp4"
                else:
                    output_path = "final_short.mp4"
                assemble_video(video_path, audio_path, subtitles, output_path, image_hook_path)
                print(f"✓ Final video assembled: {output_path}")
                
                # Log video to history to prevent duplicates
                from departments.logistics.history_engine import log_video
                log_video(
                    topic=script_text[:200],  # First 200 chars of script
                    title=title,
                    video_id=None,  # Not uploaded yet
                    filename=output_path
                )
            except Exception as e:
                print(f"❌ ERROR: Failed to assemble video: {e}")
                return 1
        
        # Step 5: Generate Monetization Comment
        print("\n[5/6] Generating monetization comment...")
        try:
            monetization_comment = generate_monetization_comment(title, script_text, tags)
            print("✓ Monetization comment generated")
        except Exception as e:
            print(f"⚠️ Could not generate monetization comment: {e}")
            monetization_comment = None
        
        # Step 6: Upload to YouTube
        if hasattr(args, 'skip_upload') and args.skip_upload:
            print("\n[📊 LOGISTICS DEPT] Skipping YouTube upload (--skip-upload enabled)")
            video_id = None
        else:
            print("\n[📊 LOGISTICS DEPT] Uploading to YouTube...")
            video_id = None
            
            try:
                from departments.logistics.upload_engine import upload_video
                
                # Generate optimized description with trending hashtags
                trending_hashtags = [
                    "#psychology", "#darkpsychology", "#mindtricks", "#psychologyfacts",
                    "#humanbehavior", "#manipulation", "#influence", "#mindset",
                    "#youtubeshorts", "#viral", "#shorts", "#psychologyhacks",
                    "#behavioralpsychology", "#socialpsychology", "#psychologytips"
                ]
                
                # Create description
                description = f"""🧠 {title}

{script_text[:200]}...

🔔 Subscribe for more psychology insights!

📌 Trending Hashtags:
{' '.join(trending_hashtags[:10])}

💡 Learn the secrets of human psychology and protect yourself from manipulation.

#psychology #darkpsychology #mindtricks #psychologyfacts #humanbehavior #manipulation #influence #mindset #youtubeshorts #viral #shorts #psychologyhacks #behavioralpsychology #socialpsychology #psychologytips #psychology101 #mentalhealth #selfimprovement #personality #psychologyvideos"""
                
                # Enhanced tags with trending keywords
                enhanced_tags = tags + [
                    "psychology", "dark psychology", "mind tricks", "psychology facts",
                    "human behavior", "manipulation", "influence", "mindset",
                    "YouTube Shorts", "viral", "shorts", "psychology hacks",
                    "behavioral psychology", "social psychology", "psychology tips",
                    "psychology 101", "mental health", "self improvement"
                ]
                
                video_id = upload_video(
                    file_path=output_path,
                    title=title,
                    description=description,
                    tags=enhanced_tags[:500],  # YouTube limit
                    category_id="26"  # Howto & Style (better for psychology content)
                )
                
                # Update history with video ID
                if video_id:
                    from departments.logistics.history_engine import _load_history, _save_history
                    history = _load_history()
                    if history and len(history) > 0:
                        history[-1]['video_id'] = video_id
                        _save_history(history)
                        print(f"   ✓ Video ID logged to history: {video_id}")
                
            except Exception as e:
                print(f"⚠️ WARNING: YouTube upload failed: {e}")
                print("   Video saved locally for manual upload")
            video_id = None
        
        # --- TIKTOK PACK GENERATION ---
        print("\n" + "=" * 60)
        print("📱 TIKTOK CONTENT - Ready for Manual Upload")
        print("=" * 60)
        
        try:
            # Generate TikTok caption with trending hashtags
            trending_hashtags_tiktok = [
                "#psychology", "#darkpsychology", "#mindtricks", "#psychologyfacts",
                "#humanbehavior", "#manipulation", "#influence", "#mindset",
                "#psychologyhacks", "#behavioralpsychology", "#socialpsychology",
                "#psychologytips", "#psychology101", "#mentalhealth", "#selfimprovement",
                "#personality", "#psychologyvideos", "#fyp", "#foryou", "#foryoupage",
                "#viral", "#trending", "#psychologytok", "#mindset", "#selfawareness"
            ]
            
            # Create TikTok caption (first line is hook)
            tiktok_caption = f"""{title} 🧠

{script_text[:200]}...

💭 What do you think? Drop a comment! 👇

{' '.join(trending_hashtags_tiktok)}"""
            
            # Generate overlay text (for on-screen text)
            hook_words = title.split()[:5]
            overlay_text = " ".join(hook_words)
            if len(title.split()) > 5:
                overlay_text += " 🛑"
            
            print(f"\n📝 TIKTOK CAPTION (Copy & Paste):")
            print("=" * 60)
            print(tiktok_caption)
            print("=" * 60)
            
            print(f"\n📝 OVERLAY TEXT (Optional - Type on screen):")
            print(f"   {overlay_text}")
            
            print(f"\n🏷️  TRENDING HASHTAGS ({len(trending_hashtags_tiktok)} tags):")
            print(f"   {' '.join(trending_hashtags_tiktok)}")
            
            print(f"\n🎵 TRENDING SOUND TIP:")
            print(f"   Add a Trending Sound at 1% Volume for maximum reach")
            
            print(f"\n💡 TIKTOK UPLOAD CHECKLIST:")
            print(f"   ✓ Upload video: {output_path}")
            print(f"   ✓ Paste caption above")
            print(f"   ✓ Add trending sound at 1% volume")
            print(f"   ✓ Use all hashtags for maximum reach")
            print("\n" + "=" * 60)
            
        except Exception as e:
            print(f"⚠️ Could not generate TikTok pack: {e}")
        
        # Cleanup temporary files
        print("\n🧹 Cleaning up temporary files...")
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    print(f"   Removed: {temp_file}")
                except Exception as e:
                    print(f"   ⚠️ Could not remove {temp_file}: {e}")
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    print(f"   Removed: {temp_dir}")
                except Exception as e:
                    print(f"   ⚠️ Could not remove {temp_dir}: {e}")
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS: Video generated successfully!")
        print("=" * 60)
        print(f"\n📊 Final Output:")
        print(f"   File: {output_path}")
        print(f"   Title: {title}")
        print(f"   Duration: ~{audio_duration:.2f} seconds")
        print(f"   Size: {os.path.getsize(output_path)} bytes")
        if video_id:
            print(f"   YouTube URL: https://www.youtube.com/watch?v={video_id}")
            print(f"   Status: ✅ Uploaded and Public")
            print(f"   History: ✅ Logged to history.json")
        else:
            print(f"\n📋 Video saved to: {os.path.abspath(output_path)}")
            print("   Status: ⚠️ Saved locally (upload failed or skipped)")
        
        # Display Monetization Box
        if monetization_comment:
            print("\n" + "=" * 60)
            print("💰 MONETIZATION BOX - PINNED COMMENT")
            print("=" * 60)
            print("\n📝 Copy this comment and pin it on your video:")
            print("-" * 60)
            print(monetization_comment)
            print("-" * 60)
            print("\n💡 TIP: Pin this comment after uploading to maximize engagement!")
            print("=" * 60)
        
        # --- ASSISTANT MODE (Post-Upload) ---
        # Only run if upload was successful
        if video_id:
            import pyperclip
            import json
            import random
            
            try:
                # 1. Load Config
                config_path = "config/monetization.json"
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        config = json.load(f)
                    
                    # 2. Pick a comment & Insert Link
                    comment_template = random.choice(config["comments"])
                    final_comment = comment_template.replace("{link}", config["safe_link"])
                    
                    # 3. Copy to Clipboard
                    pyperclip.copy(final_comment)
                    
                    # 4. Notify User
                    print("\n" + "="*50)
                    print("✅ VIDEO UPLOADED! Comment copied to clipboard!")
                    print("👇 PASTE THIS IN YOUR PINNED COMMENT 👇")
                    print("-" * 20)
                    print(final_comment)
                    print("-" * 20)
                    print("="*50 + "\n")
                    
                    # Voice Alert (Mac Only)
                    try:
                        os.system('say "Video uploaded. Comment copied to clipboard."')
                    except:
                        pass  # Silently fail if say command not available
                else:
                    print(f"\n⚠️ Assistant Mode: Config file not found at {config_path}")
                    print("   Skipping clipboard automation.")
                    
            except Exception as e:
                print(f"\n⚠️ Assistant Mode Error: {e}")
                print("   Please check config/monetization.json")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Zero-Cost Content Factory - Generate YouTube Shorts automatically"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of videos to generate in batch (default: 1, use 0 for infinite loop)"
    )
    parser.add_argument(
        "--marathon",
        action="store_true",
        help="Create marathon compilation video from existing Shorts (long-form RPM)"
    )
    parser.add_argument(
        "--marathon-horizontal",
        action="store_true",
        help="Create horizontal marathon compilation (1920x1080) for better mid-roll ad revenue"
    )
    parser.add_argument(
        "--marathon-videos",
        type=int,
        default=7,
        help="Number of videos to include in marathon compilation (5-10, default: 7)"
    )
    parser.add_argument(
        "--horror",
        action="store_true",
        help="Generate horror story video (audio-only with background music, no visuals)"
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Skip YouTube upload (save video locally only)"
    )
    parser.add_argument(
        "--split-screen",
        action="store_true",
        help="Use split-screen layout with satisfying gameplay (Minecraft/GTA)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force generation even if title/story is in history"
    )
    parser.add_argument(
        "--skip-slots",
        type=int,
        default=0,
        help="Number of schedule slots to skip in batch mode"
    )
    parser.add_argument(
        "--trend",
        type=str,
        default=None,
        help="Target a specific social media trend (e.g. 'The Mimic', 'Reality Glitches')"
    )
    
    args = parser.parse_args()
    
    # Handle marathon mode
    if args.marathon or args.marathon_horizontal:
        from departments.production.marathon_engine import create_marathon_compilation
        print("=" * 60)
        print("🎬 MARATHON MODE - Creating Long-Form Compilation")
        print("=" * 60)
        try:
            output_path = create_marathon_compilation(
                num_videos=args.marathon_videos,
                horizontal=args.marathon_horizontal
            )
            print(f"\n✓ Marathon compilation created: {output_path}")
            print(f"   Format: {'Horizontal (1920x1080)' if args.marathon_horizontal else 'Vertical (1080x1920)'}")
            print(f"   💰 Higher RPM potential: {'Yes (mid-roll ads enabled)' if args.marathon_horizontal else 'No (Shorts format)'}")
            exit(0)
        except Exception as e:
            print(f"\n❌ Marathon compilation failed: {e}")
            exit(1)
    
    video_count = args.count
    
    # INFINITE LOOP MODE: If count is 0, run forever
    infinite_mode = (video_count == 0)
    
    if infinite_mode:
        print("=" * 60)
        print("♾️  INFINITE PRODUCTION MODE - Running Forever")
        print("=" * 60)
        print("Press Ctrl+C to stop")
        print()
        
        video_num = 0
        success_count = 0
        failed_count = 0
        
        try:
            while True:
                video_num += 1
                print("\n" + "=" * 60)
                print(f"🎬 VIDEO #{video_num} (Infinite Mode)")
                print("=" * 60)
                print()
                
                # Run factory for this video
                result = run_factory(video_number=video_num, total_videos=0)
                
                if result == 0:
                    success_count += 1
                else:
                    failed_count += 1
                
                # Random sleep before next video (Trust Score protection: 5-20 minutes)
                sleep_seconds = random.randint(300, 1200)  # 5-20 minutes
                sleep_minutes = sleep_seconds / 60
                print("\n" + "=" * 60)
                print(f"💤 Random sleep for {sleep_minutes:.1f} minutes ({sleep_seconds}s) before next video...")
                print(f"   (Trust Score Protection: Mimicking human behavior)")
                print(f"   Stats: ✅ {success_count} successful | ❌ {failed_count} failed")
                print("=" * 60)
                time.sleep(sleep_seconds)
                
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("⚠️  INFINITE LOOP STOPPED BY USER")
            print("=" * 60)
            print(f"📊 Final Stats:")
            print(f"   Total videos generated: {video_num}")
            print(f"   ✅ Successful: {success_count}")
            print(f"   ❌ Failed: {failed_count}")
            print("=" * 60)
            exit(0)
    
    # Check for horror mode
    if args.horror:
        print("=" * 60)
        print("👻 HORROR STORY MODE")
        print("=" * 60)
        print()
        
        # BATCH MODE for horror: Generate specified number of videos
        video_count = max(1, video_count)  # Ensure at least 1
        
        if video_count > 1:
            print("=" * 60)
            print(f"📦 BATCH MODE: Generating {video_count} horror videos")
            print("=" * 60)
            print()
        
        success_count = 0
        failed_count = 0
        
        # Dynamic Scheduling Logic (Multi-day support)
        # Windows: 11 AM, 2 PM, 5 PM, 8 PM, 11 PM (High Density Strategy)
        import datetime
        now = datetime.datetime.now()
        # Start scheduling from TOMORROW by default to ensure full coverage
        base_date = now.date() + datetime.timedelta(days=1)
        windows = ["11:00:00", "14:00:00", "17:00:00", "20:00:00", "23:00:00"]
        
        for video_num in range(1, video_count + 1):
            if video_count > 1:
                print("\n" + "=" * 60)
                print(f"🎬 HORROR VIDEO {video_num}/{video_count}")
                print("=" * 60)
                print()
            
            # Calculate slot and day
            total_slot_idx = (video_num - 1) + getattr(args, 'skip_slots', 0)
            days_offset = total_slot_idx // len(windows)
            window_idx = total_slot_idx % len(windows)
            
            target_date = base_date + datetime.timedelta(days=days_offset)
            time_str = windows[window_idx]
            
            # Target US EST (UTC-5)
            schedule_time = f"{target_date.isoformat()}T{time_str}-05:00"
            print(f"📅 TARGET SLOT: {schedule_time} (Day +{days_offset}, Slot {window_idx + 1})")
            
            # Determine Niche based on slot index (Round Robin)
            # Order: Political -> Business -> Sports
            niches_ordered = ["political", "business", "sports"]
            niche_idx = total_slot_idx % len(niches_ordered)
            current_niche = niches_ordered[niche_idx]
            print(f"🎯 TARGET NICHE: {current_niche.upper()}")
            
            # Run horror factory for this video
            result = run_horror_factory(
                video_number=video_num, 
                total_videos=video_count,
                schedule_time=schedule_time,
                trend_guidance=getattr(args, 'trend', None),
                niche_category=current_niche
            )
            
            if result == 0:
                success_count += 1
            else:
                failed_count += 1
            
            # Random sleep between videos (Trust Score protection: 10-30 seconds for batch)
            if video_num < video_count:  # Don't sleep after last video
                sleep_seconds = random.randint(10, 30)
                sleep_minutes = sleep_seconds / 60
                print("\n" + "=" * 60)
                print(f"💤 Random sleep for {sleep_minutes:.1f} minutes ({sleep_seconds}s) before next video...")
                print(f"   (Trust Score Protection: Mimicking human behavior)")
                print(f"   Progress: ✅ {success_count} successful | ❌ {failed_count} failed")
                print("=" * 60)
                time.sleep(sleep_seconds)
        
        # Final summary
        print("\n" + "=" * 60)
        print("📊 HORROR BATCH COMPLETE")
        print("=" * 60)
        print(f"   Total videos: {video_count}")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Failed: {failed_count}")
        print("=" * 60)
        exit(0 if failed_count == 0 else 1)
    
    # BATCH MODE: Generate specified number of videos (non-horror)
    video_count = max(1, video_count)  # Ensure at least 1
    
    if video_count > 1:
        print("=" * 60)
        print(f"📦 BATCH MODE: Generating {video_count} videos")
        print("=" * 60)
        print()
    
    success_count = 0
    failed_count = 0
    
    for video_num in range(1, video_count + 1):
        if video_count > 1:
            print("\n" + "=" * 60)
            print(f"🎬 VIDEO {video_num}/{video_count}")
            print("=" * 60)
            print()
        
        # Run factory for this video
        result = run_factory(video_number=video_num, total_videos=video_count)
        
        if result == 0:
            success_count += 1
        else:
            failed_count += 1
        
        # Random sleep between videos (except after the last one) - Trust Score protection
        if video_num < video_count:
            sleep_seconds = random.randint(300, 1200)  # 5-20 minutes
            sleep_minutes = sleep_seconds / 60
            print("\n" + "=" * 60)
            print(f"⏳ Random sleep for {sleep_minutes:.1f} minutes ({sleep_seconds}s) before next video...")
            print(f"   (Trust Score Protection: Mimicking human behavior)")
            print("=" * 60)
            time.sleep(sleep_seconds)
    
    # Final summary
    if video_count > 1:
        print("\n" + "=" * 60)
        print("📊 BATCH PRODUCTION SUMMARY")
        print("=" * 60)
        print(f"   Total videos: {video_count}")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Failed: {failed_count}")
        print("=" * 60)
    
    exit(0 if failed_count == 0 else 1)

