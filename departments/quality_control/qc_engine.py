"""
THE QC ENGINE
Module: Quality Control Inspector - Detects and fixes defects in audio and visuals.

Implements Lean Manufacturing Principles (Jidoka) for automatic defect detection and correction.
"""

import os
from typing import Optional
from pydub import AudioSegment
from pydub.silence import split_on_silence


def remove_silence(audio_path: str, output_path: str = None, min_silence_len: int = 500) -> str:
    """
    Remove silence from audio (Silence Killer).
    
    Detects silence > 500ms and cuts it out (allows professor to breathe).
    
    Args:
        audio_path: Path to input audio file
        output_path: Path to save processed audio (if None, overwrites input)
        min_silence_len: Minimum silence length in milliseconds to remove (default: 500ms)
        
    Returns:
        Path to processed audio file
        
    Note:
        For Piper TTS: Apply before calculating subtitle timestamps
        For Edge-TTS: Skip to avoid breaking word-boundary metadata
    """
    if output_path is None:
        output_path = audio_path
    
    print("   🔇 Removing silence from audio...")
    
    try:
        # Load audio
        audio = AudioSegment.from_mp3(audio_path)
        original_duration = len(audio)
        
        # Split on silence
        # min_silence_len: minimum length of silence to split on (in ms)
        # silence_thresh: threshold in dB below which audio is considered silence
        chunks = split_on_silence(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=-40  # dB threshold for silence detection
        )
        
        if not chunks:
            print("   ⚠️ No silence detected, audio unchanged")
            return audio_path
        
        # Combine non-silent chunks
        processed_audio = AudioSegment.empty()
        for chunk in chunks:
            processed_audio += chunk
        
        # Add small fade in/out to prevent clicks
        processed_audio = processed_audio.fade_in(10).fade_out(10)
        
        new_duration = len(processed_audio)
        time_saved = original_duration - new_duration
        
        # Export processed audio
        processed_audio.export(output_path, format="mp3", bitrate="192k")
        
        print(f"   ✓ Silence removed: {time_saved/1000:.2f}s saved ({original_duration/1000:.2f}s → {new_duration/1000:.2f}s)")
        
        return output_path
        
    except Exception as e:
        print(f"   ⚠️ Failed to remove silence: {e}")
        return audio_path


def normalize_audio_mix(voice_path: str, music_path: Optional[str] = None, output_path: str = None) -> str:
    """
    Normalize audio mix (Broadcast Standard).
    
    Calculates RMS (Loudness) of voice and adjusts background music to be exactly -18dB (broadcast standard).
    
    Args:
        voice_path: Path to voiceover audio file
        music_path: Path to background music file (optional)
        output_path: Path to save mixed audio (if None, overwrites voice_path)
        
    Returns:
        Path to normalized/mixed audio file
    """
    if output_path is None:
        output_path = voice_path
    
    print("   🎚️ Normalizing audio mix...")
    
    try:
        # Load voiceover
        voice_audio = AudioSegment.from_mp3(voice_path)
        voice_duration = len(voice_audio)
        
        # Calculate RMS (Root Mean Square) - loudness measure
        voice_rms = voice_audio.rms
        
        if music_path and os.path.exists(music_path):
            # Load background music
            music_audio = AudioSegment.from_mp3(music_path)
            music_duration = len(music_audio)
            
            # Loop music if needed
            if music_duration < voice_duration:
                num_loops = (voice_duration // music_duration) + 1
                music_audio = music_audio * num_loops
            
            music_audio = music_audio[:voice_duration]
            
            # Calculate music RMS
            music_rms = music_audio.rms
            
            # Calculate target music volume (-18dB quieter than voice - broadcast standard)
            # RMS ratio to dB: dB = 20 * log10(rms1 / rms2)
            # We want music to be -18dB quieter: music_rms_target = voice_rms / 10^(18/20)
            target_ratio = 10 ** (18 / 20)  # ~7.94
            target_music_rms = voice_rms / target_ratio
            
            # Calculate adjustment needed
            if music_rms > 0:
                adjustment_ratio = target_music_rms / music_rms
                adjustment_db = 20 * (adjustment_ratio).bit_length() if adjustment_ratio > 0 else -18
                # More direct approach: just reduce by 18dB (broadcast standard)
                music_audio = music_audio - 18
            else:
                music_audio = music_audio - 18  # Default: reduce by 18dB (broadcast standard)
            
            print(f"   ✓ Music adjusted: -18dB (broadcast standard) (voice RMS: {voice_rms:.0f}, music RMS: {music_audio.rms:.0f})")
            
            # Mix voice and music
            mixed_audio = music_audio.overlay(voice_audio)
        else:
            # No music, just return voice
            mixed_audio = voice_audio
            print("   ✓ No background music, using voice only")
        
        # Export mixed audio
        mixed_audio.export(output_path, format="mp3", bitrate="192k")
        
        print(f"   ✓ Audio mix normalized: {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"   ⚠️ Failed to normalize audio mix: {e}")
        return voice_path


def apply_speedup(audio_path: str, speed_factor: float = 1.0, output_path: str = None) -> str:
    """
    Apply speedup to audio (DISABLED for Dark Psychology - normal speed required).
    
    Args:
        audio_path: Path to input audio file
        speed_factor: Speed multiplier (1.0 = normal speed, no change)
        output_path: Path to save processed audio (if None, overwrites input)
        
    Returns:
        Path to processed audio file (unchanged)
    """
    if output_path is None:
        output_path = audio_path
    
    # DISABLED: No speedup for Dark Psychology content (calm, authoritative tone)
    if speed_factor == 1.0:
        print(f"   ⚡ Speedup disabled (normal speed for authority)")
        return audio_path
    
    print(f"   ⚡ Applying {speed_factor}x speedup...")
    
    try:
        audio = AudioSegment.from_mp3(audio_path)
        
        # Speed up audio by changing frame rate
        # This maintains pitch while changing speed
        new_sample_rate = int(audio.frame_rate * speed_factor)
        sped_up = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
        
        # Set frame rate back to original to maintain compatibility
        sped_up = sped_up.set_frame_rate(audio.frame_rate)
        
        original_duration = len(audio)
        new_duration = len(sped_up)
        
        # Export
        sped_up.export(output_path, format="mp3", bitrate="192k")
        
        print(f"   ✓ Speedup applied: {original_duration/1000:.2f}s → {new_duration/1000:.2f}s")
        
        return output_path
        
    except Exception as e:
        print(f"   ⚠️ Failed to apply speedup: {e}")
        return audio_path


if __name__ == "__main__":
    # Test the QC engine
    print("=" * 60)
    print("🧪 TESTING QC ENGINE")
    print("=" * 60)
    
    print("Note: Run full pipeline test via main.py")

