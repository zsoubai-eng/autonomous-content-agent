"""
THE AUDIO ENGINE
Module 2: Generates high-quality audio from clean script text.

LEAN CASCADE ARCHITECTURE:
- Priority 1: ElevenLabs (Premium, if API key available)
- Priority 2: Edge-TTS (Free, unstoppable, with word timestamps)
"""

import os
import json
import random
import asyncio
import tempfile
import math
from typing import List, Dict, Tuple
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def _generate_smart_subtitles(text: str, audio_duration: float) -> List[Dict]:
    """
    Generate smart subtitles by calculating word timings based on audio duration.
    
    Args:
        text: Input text
        audio_duration: Total duration of audio in seconds
        
    Returns:
        List of subtitle dictionaries with 'word', 'start', 'end' keys
    """
    words = text.split()
    if not words:
        return []
    
    # Calculate time per word
    time_per_word = audio_duration / len(words)
    
    subtitles = []
    current_time = 0.0
    
    for word in words:
        # Each word gets equal time
        start_time = current_time
        end_time = current_time + time_per_word
        
        subtitles.append({
            "word": word,
            "start": start_time,
            "end": end_time
        })
        
        current_time = end_time
    
    return subtitles


def _generate_audio_elevenlabs(text: str, output_path: str) -> Tuple[str, List[Dict]]:
    """
    Generate audio using ElevenLabs (Priority 1 - Premium).
    
    Args:
        text: Input text
        output_path: Path to save audio file
        
    Returns:
        Tuple of (output_path, subtitles_list)
        
    Raises:
        Exception: If ElevenLabs fails (gracefully, will fall back to Edge-TTS)
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        raise Exception("ELEVENLABS_API_KEY not found in .env")
    
    print("   🎙️ Attempting ElevenLabs (Premium)...")
    
    try:
        from elevenlabs import generate, save, set_api_key
        
        # Set API key
        set_api_key(api_key)
        
        # Generate audio (using default voice or specified)
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default: Rachel
        
        print(f"   Using voice: {voice_id}")
        
        # Generate audio
        audio_data = generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2"
        )
        
        # Save to file
        save(audio_data, output_path)
        
        # Verify file was created
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise Exception("ElevenLabs generated empty file")
        
        # Get audio duration
        audio = AudioSegment.from_mp3(output_path)
        
        # OPTIMIZED PACING: Slow down for horror tension (0.96x speed)
        speed_factor = 0.96
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed_factor)
        }).set_frame_rate(audio.frame_rate)
        audio_duration = audio.duration_seconds
        
        # Export with new speed
        audio.export(output_path, format="mp3", bitrate="192k")
        
        # Generate smart subtitles (ElevenLabs doesn't provide word timestamps)
        # Adjust subtitle timings for slower speed
        subtitles = _generate_smart_subtitles(text, audio_duration)
        
        print(f"   ✓ ElevenLabs audio generated: {output_path} ({audio_duration:.2f}s, 0.96x speed)")
        
        return output_path, subtitles
        
    except ImportError:
        raise Exception("elevenlabs library not installed. Run: pip install elevenlabs")
    except Exception as e:
        # Fail gracefully - will fall back to Edge-TTS
        raise Exception(f"ElevenLabs failed: {e}")


async def _generate_audio_edge_tts_async(text: str, output_path: str) -> Tuple[str, List[Dict]]:
    """
    Generate audio using Edge-TTS (Priority 2 - Unstoppable).
    
    Uses streaming to capture WordBoundary events for perfect word-level timestamps.
    
    Args:
        text: Input text
        output_path: Path to save audio file
        
    Returns:
        Tuple of (output_path, subtitles_list with exact word timestamps)
    """
    print("   🌐 Using Edge-TTS (Free, unstoppable)...")
    
    try:
        import edge_tts
        import certifi
        import ssl
        import os as os_module
        
        # Set SSL certificate for macOS compatibility
        os_module.environ['SSL_CERT_FILE'] = certifi.where()
        os_module.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        
        # Use high-quality neural voice
        voice = "en-US-ChristopherNeural"  # Male, clear, professional
        
        print(f"   Voice: {voice}")
        
        # Try streaming first (for word timestamps)
        audio_chunks = []
        subtitles = []
        stream_success = False
        
        try:
            communicate = edge_tts.Communicate(text, voice)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])
                    stream_success = True
                elif chunk["type"] == "WordBoundary":
                    # Capture word timing
                    word_data = chunk.get("offset", {})
                    start_ms = word_data.get("offset", 0) / 10000.0  # Convert to seconds
                    duration_ms = word_data.get("duration", 0) / 10000.0
                    end_ms = start_ms + duration_ms
                    
                    # Get word text
                    word_text = word_data.get("text", "").strip()
                    if word_text:
                        subtitles.append({
                            "word": word_text,
                            "start": start_ms,
                            "end": end_ms
                        })
        except Exception as stream_error:
            # If streaming fails, try simple save method with new communicate object
            print(f"   ⚠️ Streaming failed: {stream_error}, trying simple save...")
            try:
                communicate2 = edge_tts.Communicate(text, voice)
                await communicate2.save(output_path)
                
                # Verify file
                if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                    raise Exception("Edge-TTS generated empty file")
                
                # Get audio duration
                audio = AudioSegment.from_mp3(output_path)
                
                # OPTIMIZED PACING: Slow down for horror tension (0.96x speed)
                speed_factor = 0.96
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * speed_factor)
                }).set_frame_rate(audio.frame_rate)
                audio_duration = audio.duration_seconds
                
                # Export with new speed
                audio.export(output_path, format="mp3", bitrate="192k")
                
                # Generate smart subtitles and adjust timings
                subtitles = _generate_smart_subtitles(text, audio_duration)
                speed_adjustment = 1.0 / speed_factor
                for sub in subtitles:
                    sub['start'] = sub['start'] * speed_adjustment
                    sub['end'] = sub['end'] * speed_adjustment
                
                print(f"   ✓ Edge-TTS audio generated (simple method): {output_path} ({audio_duration:.2f}s, 0.96x speed)")
                return output_path, subtitles
            except Exception as save_error:
                raise Exception(f"Both streaming and save methods failed. Stream: {stream_error}, Save: {save_error}")
        
        # Combine audio chunks
        if not audio_chunks:
            raise Exception("Edge-TTS generated no audio chunks")
        
        # Write audio to file
        with open(output_path, "wb") as f:
            for chunk in audio_chunks:
                f.write(chunk)
        
        # Verify file
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise Exception("Edge-TTS generated empty file")
        
        # Get audio duration
        audio = AudioSegment.from_mp3(output_path)
        
        # OPTIMIZED PACING: Slow down for horror tension (0.96x speed)
        speed_factor = 0.96
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed_factor)
        }).set_frame_rate(audio.frame_rate)
        audio_duration = audio.duration_seconds
        
        # Adjust subtitle timings for slower speed
        speed_adjustment = 1.0 / speed_factor
        if subtitles:
            for sub in subtitles:
                sub['start'] = sub['start'] * speed_adjustment
                sub['end'] = sub['end'] * speed_adjustment
        
        # Export with new speed
        audio.export(output_path, format="mp3", bitrate="192k")
        
        # If no word boundaries captured, generate smart subtitles
        if not subtitles:
            print("   ⚠️ No word boundaries captured, using calculated timings")
            subtitles = _generate_smart_subtitles(text, audio_duration)
        else:
            print(f"   ✓ Captured {len(subtitles)} word timestamps")
        
        print(f"   ✓ Edge-TTS audio generated: {output_path} ({audio_duration:.2f}s, 0.96x speed)")
        
        return output_path, subtitles
        
    except ImportError:
        raise Exception("edge-tts library not installed. Run: pip install edge-tts")
    except Exception as e:
        raise Exception(f"Edge-TTS failed: {e}")


def _get_piper_voice_path() -> str:
    """
    Get the path to the Piper voice model.
    
    Returns:
        Path to the voice model .onnx file
        
    Raises:
        Exception: If voice model is not found
    """
    # Common locations for Piper voice models
    possible_paths = [
        os.path.expanduser("~/.local/share/piper/voices/en_US-lessac-medium/en_US-lessac-medium.onnx"),
        os.path.expanduser("~/piper/en_US-lessac-medium.onnx"),
        os.path.join(os.getcwd(), "en_US-lessac-medium.onnx"),
        os.path.join(os.getcwd(), "voices", "en_US-lessac-medium.onnx"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If not found, raise exception with helpful message
    raise Exception(
        f"Piper voice model not found. Please download it to one of these locations:\n"
        f"  - {possible_paths[0]}\n"
        f"  - {possible_paths[1]}\n"
        f"  - {possible_paths[2]}\n"
        f"\n"
        f"Download command:\n"
        f"  curl -L -o en_US-lessac-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx\n"
        f"  curl -L -o en_US-lessac-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
    )


def _generate_audio_piper(text: str, output_path: str) -> Tuple[str, List[Dict]]:
    """
    Generate audio using Piper TTS (Priority 3 - Local, truly unstoppable).
    
    Args:
        text: Input text
        output_path: Path to save audio file
        
    Returns:
        Tuple of (output_path, subtitles_list with calculated timings)
    """
    print("   🎙️ Using Piper TTS (Local, unstoppable)...")
    
    import wave
    import subprocess
    
    # Get voice model path
    try:
        voice_model_path = _get_piper_voice_path()
        print(f"   Voice model: {voice_model_path}")
    except Exception as e:
        raise Exception(f"Voice model not found: {e}")
    
    # Create temporary WAV file (Piper outputs WAV)
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_wav_path = temp_wav.name
    temp_wav.close()
    
    try:
        # Try using piper-tts Python library first
        try:
            try:
                from piper import PiperVoice
            except ImportError:
                raise Exception("Piper TTS library not installed")
            
            print("   Using Piper Python library...")
            
            # Load voice model
            voice = PiperVoice.load(voice_model_path)
            
            # Generate audio
            audio_chunks = list(voice.synthesize(text))
            
            if not audio_chunks:
                raise Exception("Piper TTS generated no audio chunks")
            
            # Get sample rate and channels from first chunk
            sample_rate = audio_chunks[0].sample_rate
            sample_channels = audio_chunks[0].sample_channels
            
            # Write WAV file
            with wave.open(temp_wav_path, 'wb') as wav_file:
                wav_file.setnchannels(sample_channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                
                # Write all audio chunks
                for chunk in audio_chunks:
                    wav_file.writeframes(chunk.audio_int16_bytes)
            
        except Exception as e:
            # Fallback to subprocess (piper command-line)
            print(f"   Python library failed ({e}), trying command-line piper...")
            
            # Run piper command
            cmd = [
                'piper',
                '--model', voice_model_path,
                '--output_file', temp_wav_path
            ]
            
            result = subprocess.run(
                cmd,
                input=text.encode('utf-8'),
                capture_output=True,
                timeout=60,
                check=True
            )
        
        # Verify WAV file was created
        if not os.path.exists(temp_wav_path):
            raise Exception(f"Piper TTS did not create audio file at {temp_wav_path}")
        
        wav_size = os.path.getsize(temp_wav_path)
        if wav_size == 0:
            raise Exception(f"Piper TTS created empty audio file at {temp_wav_path}")
        
        print(f"   ✓ WAV generated: {temp_wav_path} ({wav_size} bytes)")
        
        # Convert WAV to MP3 and get duration
        audio = AudioSegment.from_wav(temp_wav_path)
        audio_duration = audio.duration_seconds
        
        # OPTIMIZED PACING: Use slower speed (0.96x) for horror tension (expert recommendation)
        # Slower = more tension, better comprehension on mobile (+11% retention)
        speed_factor = 0.96  # 4% slower for horror storytelling
        print(f"   🎭 Using optimized pacing (0.96x speed for horror tension)...")
        
        # Slow down audio using pydub (more reliable than MoviePy)
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed_factor)
        }).set_frame_rate(audio.frame_rate)
        
        # Recalculate duration after speed change
        audio_duration = audio.duration_seconds
        
        # Export as MP3
        audio.export(output_path, format="mp3", bitrate="192k")
        
        # Verify MP3 was created
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise Exception(f"MP3 file was not created at {output_path}")
        
        print(f"   ✓ MP3 converted: {output_path} ({audio_duration:.2f}s)")
        
        # Generate smart subtitles based on audio duration
        subtitles = _generate_smart_subtitles(text, audio_duration)
        
        print(f"   ✓ Piper TTS audio generated: {output_path} ({audio_duration:.2f}s)")
        
        return output_path, subtitles
        
    except Exception as e:
        # Cleanup on error
        if os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except:
                pass
        raise Exception(f"Piper TTS failed: {e}")
    finally:
        # Cleanup temp WAV file
        if os.path.exists(temp_wav_path) and temp_wav_path != output_path:
            try:
                os.remove(temp_wav_path)
            except:
                pass


def generate_scene_audio(scenes: list, output_dir: str = ".") -> Tuple[list, list]:
    """
    Generate individual audio clips for each scene (Audio Agent).
    
    Iterates through scenes and generates a separate audio clip for each scene.
    Uses Edge-TTS (or Piper) for each scene.
    
    Args:
        scenes: List of scene dicts with 'id', 'text', 'visual_prompt', 'duration'
        output_dir: Directory to save scene audio files (default: current directory)
        
    Returns:
        Tuple of (list of audio paths, list of subtitles lists)
        - audio_paths: List of paths to generated audio files (audio_1.mp3, audio_2.mp3, etc.)
        - all_subtitles: List of subtitle lists (one per scene)
    """
    print(f"🎙️ Audio Agent: Generating audio for {len(scenes)} scenes...")
    
    audio_paths = []
    all_subtitles = []
    
    for scene in scenes:
        scene_id = scene.get('id', len(audio_paths) + 1)
        scene_text = scene.get('text', '')
        duration = float(scene.get('duration', 3.0))
        
        output_path = os.path.join(output_dir, f"audio_{scene_id}.mp3")
        
        print(f"   Scene {scene_id}: Generating audio ({duration:.1f}s)...")
        print(f"      Text: {scene_text[:50]}...")
        
        try:
            # Generate audio for this specific scene
            audio_path, subtitles = generate_audio(scene_text, output_path, script_text=scene_text)
            
            # Adjust subtitle timings to be relative to scene start (for later assembly)
            # For now, keep them relative to scene start (0.0)
            audio_paths.append(audio_path)
            all_subtitles.append(subtitles)
            
            print(f"   ✓ Scene {scene_id} audio generated: {audio_path}")
        except Exception as e:
            print(f"   ⚠️ Scene {scene_id} audio generation failed: {e}")
            raise
    
    print(f"✓ Audio Agent: Generated {len(audio_paths)} scene audio clips")
    return audio_paths, all_subtitles


def generate_audio(text: str, output_path: str, voice: str = None, script_text: str = None) -> Tuple[str, List[Dict]]:
    """
    Generate audio from clean script text using LEAN CASCADE architecture.
    
    DEPRECATED: Use generate_scene_audio() for scene-based workflow.
    This function is kept for backward compatibility.
    
    Priority 1: ElevenLabs (if API key available)
    Priority 2: Edge-TTS (unstoppable fallback with word timestamps)
    
    Args:
        text: Clean script text (no metadata, no stage directions)
        output_path: Path to save audio file (.mp3)
        voice: Voice parameter (optional, used by ElevenLabs)
        
    Returns:
        Tuple of (output_path, subtitles_list)
        subtitles_list: List of dicts with 'word', 'start', 'end' keys
        
    Raises:
        Exception: If both ElevenLabs and Edge-TTS fail
    """
    print(f"🔊 Generating audio (LEAN CASCADE)...")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    # Ensure .mp3 extension
    if not output_path.endswith('.mp3'):
        output_path = output_path.replace('.wav', '.mp3').replace('.mp4', '.mp3')
        if not output_path.endswith('.mp3'):
            output_path += '.mp3'
    
    # PRIORITY 1: Try ElevenLabs
    try:
        audio_path, subtitles = _generate_audio_elevenlabs(text, output_path)
        
        # Save subtitles to JSON
        json_path = output_path.replace('.mp3', '.json')
        with open(json_path, 'w') as f:
            json.dump(subtitles, f, indent=2)
        
        # Mix with background music (SFX Brain)
        final_audio_path = mix_background_music(audio_path, audio_path, subtitles, script_text if script_text else text)
        
        return final_audio_path, subtitles
        
    except Exception as e:
        print(f"   ⚠️ ElevenLabs failed: {e}")
        print("   → Falling back to Edge-TTS...")
    
    # PRIORITY 2: Use Edge-TTS (unstoppable)
    try:
        # Run async function
        audio_path, subtitles = asyncio.run(_generate_audio_edge_tts_async(text, output_path))
        
        # Save subtitles to JSON
        json_path = output_path.replace('.mp3', '.json')
        with open(json_path, 'w') as f:
            json.dump(subtitles, f, indent=2)
        
        print(f"✓ Subtitles: {len(subtitles)} words with timing")
        
        # Mix with background music (SFX Brain)
        final_audio_path = mix_background_music(audio_path, audio_path, subtitles, script_text if script_text else text)
        
        return final_audio_path, subtitles
        
    except Exception as e:
        print(f"   ⚠️ Edge-TTS failed: {e}")
        print("   → Falling back to Piper TTS (local, unstoppable)...")
    
    # PRIORITY 3: Use Piper TTS (local, truly unstoppable)
    try:
        audio_path, subtitles = _generate_audio_piper(text, output_path)
        
        # Save subtitles to JSON
        json_path = output_path.replace('.mp3', '.json')
        with open(json_path, 'w') as f:
            json.dump(subtitles, f, indent=2)
        
        print(f"✓ Subtitles: {len(subtitles)} words with timing")
        
        # Mix with background music (SFX Brain)
        final_audio_path = mix_background_music(audio_path, audio_path, subtitles, script_text if script_text else text)
        
        return final_audio_path, subtitles
        
    except Exception as e:
        raise Exception(f"All audio engines failed (ElevenLabs, Edge-TTS, Piper). Last error: {e}")


def apply_binaural_panning(audio: AudioSegment, cycle_ms: int = 4000) -> AudioSegment:
    """
    Applies a dynamic panning effect (Left to Right oscillation) to create a creepy binaural feel.
    
    Args:
        audio: Pydub AudioSegment
        cycle_ms: Duration of one full left-to-right-to-left cycle in milliseconds
        
    Returns:
        AudioSegment with dynamic panning applied
    """
    chunk_ms = 100  # 10 samples per second for smooth-enough panning
    chunks = []
    
    for i in range(0, len(audio), chunk_ms):
        chunk = audio[i:i+chunk_ms]
        if len(chunk) == 0:
            continue
            
        # Sine wave panning: swings between -0.9 (Left) and 0.9 (Right)
        # Using i as the current millisecond marker
        pan_val = 0.9 * math.sin(2 * math.pi * i / cycle_ms)
        chunks.append(chunk.pan(pan_val))
        
    if not chunks:
        return audio
        
    return sum(chunks)


def mix_background_music(voice_file: str, output_file: str, subtitles: List[Dict] = None, script_text: str = None) -> str:
    """
    Mix background music with voiceover audio and sound effects (SFX Brain).
    
    SFX Brain Logic:
    1. Hook (0.0s): Random riser or heavy impact at start
    2. Pacing: Pop/click at start of each new sentence (-30dB)
    3. Vibe: Background music as usual
    
    Args:
        voice_file: Path to voiceover audio file
        output_file: Path to save mixed audio file
        subtitles: List of subtitle dicts (for sentence detection)
        script_text: Original script text (for sentence boundary detection)
        
    Returns:
        Path to the mixed audio file (or original voice_file if no music available)
    """
    music_dir = "assets/music"
    sfx_dir = "assets/sfx"
    
    # Load voiceover
    try:
        voice_audio = AudioSegment.from_mp3(voice_file)
        voice_duration = len(voice_audio)
    except Exception as e:
        print(f"   ⚠️ Failed to load voiceover: {e}")
        return voice_file
    
    # Mix background music if available
    if os.path.exists(music_dir):
        music_files = [f for f in os.listdir(music_dir) if f.endswith('.mp3')]
        
        if music_files:
            print("🎵 Mixing background music...")
            try:
                selected_music = random.choice(music_files)
                music_path = os.path.join(music_dir, selected_music)
                print(f"   Using: {selected_music}")
                
                music_audio = AudioSegment.from_mp3(music_path)
                music_duration = len(music_audio)
                
                # Loop music if needed
                if music_duration < voice_duration:
                    num_loops = (voice_duration // music_duration) + 1
                    print(f"   Looping music {num_loops} times")
                    music_audio = music_audio * num_loops
                
                music_audio = music_audio[:voice_duration]
                # OPTIMIZED VOLUME MIX (expert recommendation):
                # Music: -22 to -26dB (was -18dB) - lower for better voice clarity
                # Voice: -3dB boost for prominence
                music_volume = random.randint(-26, -22)  # Randomize between -22 and -26dB
                music_audio = music_audio + music_volume
                
                # Boost voice slightly for prominence
                voice_audio = voice_audio + 3  # +3dB boost
                
                voice_audio = music_audio.overlay(voice_audio)
            except Exception as e:
                print(f"   ⚠️ Failed to mix music: {e}")
    
    # SFX BRAIN: Enhanced sound effects
    if os.path.exists(sfx_dir):
        print("🎧 SFX Brain: Adding intelligent sound design...")
        
        # 1. THE HOOK (0.0s): Random riser or heavy impact
        risers_dir = os.path.join(sfx_dir, "risers")
        impacts_dir = os.path.join(sfx_dir, "impacts")
        
        hook_sfx = None
        hook_path = None
        
        # Try risers first, then impacts
        if os.path.exists(risers_dir):
            riser_files = [f for f in os.listdir(risers_dir) if f.endswith(('.mp3', '.wav'))]
            if riser_files:
                hook_path = os.path.join(risers_dir, random.choice(riser_files))
                print(f"   🎯 Hook: Using riser at 0.0s")
        
        if not hook_path and os.path.exists(impacts_dir):
            impact_files = [f for f in os.listdir(impacts_dir) if f.endswith(('.mp3', '.wav'))]
            if impact_files:
                hook_path = os.path.join(impacts_dir, random.choice(impact_files))
                print(f"   🎯 Hook: Using heavy impact at 0.0s")
        
        # Fallback to old whoosh if new SFX not available
        if not hook_path:
            whoosh_path = os.path.join(sfx_dir, "whoosh.mp3")
            if os.path.exists(whoosh_path):
                hook_path = whoosh_path
                print(f"   🎯 Hook: Using whoosh at 0.0s (fallback)")
        
        if hook_path:
            try:
                hook_sfx = AudioSegment.from_file(hook_path)
                voice_audio = voice_audio.overlay(hook_sfx, position=0)
                print(f"   ✓ Hook SFX added at 0.0s")
            except Exception as e:
                print(f"   ⚠️ Failed to add hook SFX: {e}")
        
        # 2. RULE-BASED SFX (Expert Recommendation): Keyword-triggered sound effects
        if subtitles and script_text:
            # Define keyword-to-SFX mapping for horror content
            keyword_sfx_map = {
                'footstep': ['footstep', 'step', 'walked', 'walking', 'stomped'],
                'door': ['door', 'knocked', 'knocking', 'opened', 'slammed'],
                'scream': ['scream', 'shrieked', 'yelled', 'cried'],
                'impact': ['suddenly', 'crash', 'bang', 'loud', 'exploded'],
                'tension': ['silence', 'quiet', 'nothing', 'heard']
            }
            
            # SFX directories
            sfx_mapping = {
                'footstep': os.path.join(sfx_dir, "footsteps"),
                'door': os.path.join(sfx_dir, "doors"),
                'scream': os.path.join(sfx_dir, "screams"),
                'impact': os.path.join(sfx_dir, "impacts"),
                'tension': os.path.join(sfx_dir, "tension")
            }
            
            script_lower = script_text.lower()
            
            # Add keyword-triggered SFX
            for sfx_type, keywords in keyword_sfx_map.items():
                for keyword in keywords:
                    if keyword in script_lower:
                        # Find word position in subtitles
                        for sub in subtitles:
                            if sub['word'].lower() == keyword:
                                sfx_dir_path = sfx_mapping.get(sfx_type)
                                if sfx_dir_path and os.path.exists(sfx_dir_path):
                                    sfx_files = [f for f in os.listdir(sfx_dir_path) if f.endswith(('.mp3', '.wav'))]
                                    if sfx_files:
                                        try:
                                            sfx_path = os.path.join(sfx_dir_path, random.choice(sfx_files))
                                            sfx_audio = AudioSegment.from_file(sfx_path)
                                            sfx_audio = sfx_audio - 16  # -16dB (audible but not overwhelming)
                                            sfx_position_ms = int(sub['start'] * 1000)
                                            if sfx_position_ms < voice_duration:
                                                voice_audio = voice_audio.overlay(sfx_audio, position=sfx_position_ms)
                                                print(f"   ✓ SFX: {sfx_type} at {sub['start']:.2f}s (keyword: '{keyword}')")
                                                break  # Only add once per keyword type
                                        except Exception as e:
                                            pass  # Silent fail for missing SFX
            
            # 3. SILENCE BEFORE TWIST (Expert Recommendation: +retention spike)
            # Find potential "twist" moments (last 5 seconds, words like "but", "then", "revealed")
            twist_keywords = ['but', 'then', 'revealed', 'discovered', 'found', 'realized', 'was', 'were']
            for sub in subtitles:
                word = sub['word'].lower().strip('.,!?')
                if word in twist_keywords and sub['start'] >= voice_duration / 1000 - 5:
                    # Add 0.5s silence before twist word
                    silence_ms = int((sub['start'] - 0.5) * 1000)
                    if silence_ms > 0 and silence_ms < voice_duration:
                        silence = AudioSegment.silent(duration=500)  # 0.5s silence
                        # Insert silence by splitting audio and inserting
                        before = voice_audio[:silence_ms]
                        after = voice_audio[silence_ms:]
                        voice_audio = before + silence + after
                        print(f"   ✓ Added 0.5s silence before twist at {sub['start']:.2f}s")
                        break  # Only add once
        
        # 4. THE PACING: Pop/click at start of each new sentence (keep existing logic)
        if subtitles and script_text:
            # Detect sentence boundaries from script
            import re
            sentences = re.split(r'[.!?]+\s+', script_text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Find sentence start times by matching first words
            sentence_starts = []
            script_words = script_text.split()
            
            for sentence in sentences:
                if not sentence:
                    continue
                # Find first word of sentence in subtitles
                first_words = sentence.split()[:3]  # Check first 3 words for matching
                for i, sub in enumerate(subtitles):
                    if i < len(subtitles) - 2:
                        # Check if subtitle matches sentence start
                        subtitle_words = [sub['word'].lower() for sub in subtitles[i:i+3]]
                        if any(word.lower() in subtitle_words for word in first_words):
                            sentence_starts.append(sub['start'])
                            break
            
            # Add pop/click at sentence starts
            pop_dir = os.path.join(sfx_dir, "whooshes")  # Check whooshes folder for pops/clicks
            pop_files = []
            
            if os.path.exists(pop_dir):
                pop_files = [f for f in os.listdir(pop_dir) if f.endswith(('.mp3', '.wav'))]
            
            # Fallback to root sfx folder
            if not pop_files:
                pop_path = os.path.join(sfx_dir, "pop.mp3")
                if os.path.exists(pop_path):
                    pop_files = [pop_path]
            
            if pop_files and sentence_starts:
                try:
                    pop_path = random.choice(pop_files) if isinstance(pop_files, list) and len(pop_files) > 1 else pop_files[0]
                    pop_audio = AudioSegment.from_file(pop_path)
                    pop_audio = pop_audio - 30  # Very quiet (-30dB)
                    
                    for sentence_start in sentence_starts:
                        pop_position_ms = int(sentence_start * 1000)
                        if pop_position_ms < voice_duration and pop_position_ms > 0:
                            voice_audio = voice_audio.overlay(pop_audio, position=pop_position_ms)
                    
                    print(f"   ✓ Pacing SFX: Added pop/click at {len(sentence_starts)} sentence starts")
                except Exception as e:
                    print(f"   ⚠️ Failed to add pacing SFX: {e}")
                    
        # 5. BINAURAL AMBIENCE (3D Soundscape Update)
        ambience_dir = os.path.join(sfx_dir, "ambience")
        if os.path.exists(ambience_dir):
            ambience_files = [f for f in os.listdir(ambience_dir) if f.endswith(('.mp3', '.wav'))]
            if ambience_files:
                print("🌬️ SFX Brain: Applying Binaural Ambience (3D Fear)...")
                try:
                    amb_path = os.path.join(ambience_dir, random.choice(ambience_files))
                    amb_audio = AudioSegment.from_file(amb_path)
                    
                    # Loop and match duration
                    if len(amb_audio) < voice_duration:
                        amb_audio = amb_audio * (voice_duration // len(amb_audio) + 1)
                    amb_audio = amb_audio[:voice_duration]
                    
                    # Apply creepy 3D panning oscillation
                    amb_audio = apply_binaural_panning(amb_audio, cycle_ms=5000)
                    
                    # Very quiet background layer: -28dB
                    amb_audio = amb_audio - 28
                    voice_audio = voice_audio.overlay(amb_audio)
                    print(f"   ✓ 3D Ambience added (Binaural panning cycle: 5s)")
                except Exception as e:
                    print(f"   ⚠️ Failed to add Binaural Ambience: {e}")
    
    # Export final mixed audio
    try:
        voice_audio.export(output_file, format="mp3", bitrate="192k")
        print(f"✓ Mixed audio with SFX Brain saved: {output_file}")
        return output_file
    except Exception as e:
        print(f"   ⚠️ Failed to export mixed audio: {e}")
        return voice_file


if __name__ == "__main__":
    # Test the audio engine
    print("=" * 60)
    print("🧪 TESTING AUDIO ENGINE (LEAN CASCADE)")
    print("=" * 60)
    
    test_text = "This is a test of the lean cascade audio engine. It should try ElevenLabs first, then fall back to Edge-TTS."
    
    try:
        audio_path, subtitles = generate_audio(test_text, "test_audio.mp3")
        
        print(f"\n✓ Audio created at: {audio_path}")
        print(f"\n📝 First 5 subtitle entries:")
        for sub in subtitles[:5]:
            print(f"  {sub['word']}: {sub['start']:.2f}s - {sub['end']:.2f}s")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
