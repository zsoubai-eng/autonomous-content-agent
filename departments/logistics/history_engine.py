"""
THE HISTORY ENGINE
Module: Memory system to prevent duplicate content.

Tracks all generated videos to ensure unique topics and prevent repetition.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional


HISTORY_FILE = "history.json"


def _load_history() -> List[Dict]:
    """
    Load history from history.json file.
    
    Returns:
        List of video history entries
    """
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
            if not isinstance(history, list):
                return []
            return history
    except Exception as e:
        print(f"   ⚠️ Failed to load history: {e}")
        return []


def _save_history(history: List[Dict]) -> None:
    """
    Save history to history.json file.
    
    Args:
        history: List of video history entries
    """
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"   ⚠️ Failed to save history: {e}")


def has_topic_been_used(topic: str) -> bool:
    """
    Check if a topic has already been used.
    
    Args:
        topic: Topic string to check
        
    Returns:
        True if topic exists in history, False otherwise
    """
    history = _load_history()
    
    # Normalize topic for comparison (lowercase, strip whitespace)
    normalized_topic = topic.lower().strip()
    
    for entry in history:
        entry_topic = entry.get('topic', '').lower().strip()
        if entry_topic == normalized_topic:
            return True
    
    return False


def log_video(topic: str, title: str, video_id: Optional[str] = None, filename: str = None) -> None:
    """
    Log a video to history.
    
    Args:
        topic: Topic/script content used
        title: Video title
        video_id: YouTube video ID (if uploaded)
        filename: Local filename (optional)
    """
    history = _load_history()
    
    entry = {
        "topic": topic[:200],  # Truncate to 200 chars
        "title": title,
        "video_id": video_id,
        "filename": filename,
        "date": datetime.now().isoformat()
    }
    
    history.append(entry)
    _save_history(history)
    
    print(f"   ✓ Video logged to history: {title}")


def get_recent_topics(limit: int = 10) -> List[str]:
    """
    Get recent topics from history.
    
    Args:
        limit: Number of recent topics to return
        
    Returns:
        List of recent topic strings
    """
    history = _load_history()
    recent = history[-limit:] if len(history) > limit else history
    return [entry.get('topic', '') for entry in recent]


if __name__ == "__main__":
    # Test the history engine
    print("=" * 60)
    print("🧪 TESTING HISTORY ENGINE")
    print("=" * 60)
    
    # Test topic check
    test_topic = "Dark Psychology mind control"
    has_used = has_topic_been_used(test_topic)
    print(f"Topic '{test_topic}' used: {has_used}")
    
    # Test logging
    log_video(test_topic, "Test Video", "test123", "test.mp4")
    
    # Check again
    has_used_after = has_topic_been_used(test_topic)
    print(f"Topic '{test_topic}' used after logging: {has_used_after}")
    
    # Show recent topics
    recent = get_recent_topics(5)
    print(f"\nRecent topics: {recent}")

