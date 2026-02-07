"""
TIME-BASED HORROR CONTENT STRATEGY
Matches horror content type to viewer's psychological state at different times of day.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import pytz

EST = pytz.timezone('US/Eastern')


def get_time_based_horror_type(publish_time: datetime) -> Dict[str, str]:
    """
    Determine horror content type based on publishing time.
    
    Args:
        publish_time: Datetime when video will be published
        
    Returns:
        Dict with 'time_window', 'horror_type', 'intensity', 'description', 'examples'
    """
    if isinstance(publish_time, str):
        # Parse ISO format
        publish_time = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
    
    # Convert to EST if needed
    if publish_time.tzinfo is None:
        publish_time = EST.localize(publish_time)
    elif publish_time.tzinfo != EST:
        publish_time = publish_time.astimezone(EST)
    
    hour = publish_time.hour
    
    # Morning Horror (6:00 AM - 11:00 AM EST)
    if 6 <= hour < 12:
        return {
            'time_window': 'morning',
            'horror_type': 'psychological_existential',
            'intensity': 'mild',
            'viewer_state': 'Awake, alert, logical, low anxiety, higher energy',
            'content_style': 'Mild, clever, slightly unsettling horror',
            'goal': 'Curiosity + subtle tension (not heart attacks)',
            'types': [
                'Psychological Horror - small twist, "what if this is happening?"',
                'Existential Horror - concept-based, thought-provoking',
                'Background Horror - hidden details in ordinary places'
            ],
            'examples': [
                'Character notices subtle changes in house after waking up',
                '"If you slept for a year, what if the world moved on without you?"',
                'Quiet office scene with figure subtly in background'
            ],
            'prompt_guidance': 'Create a clever, thought-provoking horror story. Focus on subtle unease, psychological twists, and existential questions. Avoid jump scares. Make it analytical and intriguing.'
        }
    
    # Afternoon Horror (12:00 PM - 5:00 PM EST)
    elif 12 <= hour < 18:
        return {
            'time_window': 'afternoon',
            'horror_type': 'suspense_minimalist',
            'intensity': 'light',
            'viewer_state': 'Moderate energy, slightly distracted, more social',
            'content_style': 'Light suspense, humor-tinged, mild jump scares',
            'goal': 'Grab attention in short bursts without discomfort',
            'types': [
                'Suspense / Anticipatory Horror - quick build-up, short release',
                'Minimalist Horror - subtle weirdness, small glitch',
                'Human Threat / Stalker Horror - relatable fear, low gore'
            ],
            'examples': [
                'Lights flicker behind someone walking down hallway',
                'Coffee cup moves by itself for a second',
                '"Someone is watching your live feed"'
            ],
            'prompt_guidance': 'Create a quick, snackable horror story. Focus on suspense, subtle weirdness, or relatable threats. Keep it light - viewers are multitasking. Quick build-up, short release.'
        }
    
    # Evening Horror (6:00 PM - 9:00 PM EST)
    elif 18 <= hour < 22:
        return {
            'time_window': 'evening',
            'horror_type': 'supernatural_psychological',
            'intensity': 'moderate',
            'viewer_state': 'More relaxed, low energy, open to immersive experiences',
            'content_style': 'Moderate tension, supernatural hints, immersive',
            'goal': 'Pull them into a story without exhausting them',
            'types': [
                'Supernatural / Paranormal Horror - ghosts, entities, flickering lights',
                'POV Horror - immersive, relatable situations',
                'Psychological Horror - deeper twists'
            ],
            'examples': [
                'Mirror shows figure that isn\'t there when turning back',
                'POV walking into dark hallway with whispering',
                '"You\'re not alone... and they know your secrets"'
            ],
            'prompt_guidance': 'Create an immersive horror story with moderate tension. Focus on supernatural elements, POV experiences, or deeper psychological twists. Viewers are relaxed and open to being pulled into the story.'
        }
    
    # Night Horror (10:00 PM - 5:00 AM EST)
    else:  # 22 <= hour or hour < 6
        return {
            'time_window': 'night',
            'horror_type': 'intense_unresolved',
            'intensity': 'intense',
            'viewer_state': 'Low energy, heightened imagination, more emotional, vulnerable',
            'content_style': 'Intense horror, unresolved tension, fear of the unknown',
            'goal': 'Exploit imagination; leave lingering unease',
            'types': [
                'Supernatural / Paranormal Horror - ghosts, shadows, unexplained noises',
                'Psychological Horror - existential dread, subtle paranoia',
                'Background Horror / Hidden Detail - subtle, terrifying details',
                'Found Footage Horror - realism increases fear at night'
            ],
            'examples': [
                'POV in dark room, breathing sounds, shadow moves, "It\'s closer than you think"',
                'Existential dread about being watched',
                'Found footage of unexplained events'
            ],
            'prompt_guidance': 'Create an intense horror story with unresolved tension. Focus on supernatural elements, existential dread, or hidden terrifying details. Exploit nighttime imagination. Leave viewers with lingering unease. This is the most intense time slot.'
        }


def get_4x_daily_schedule(start_date: datetime = None, num_days: int = 7) -> list:
    """
    Get 4x daily publishing schedule with time-based horror types.
    
    Returns:
        List of (datetime, label, horror_type_dict) tuples
    """
    if start_date is None:
        start_date = datetime.now(EST)
    else:
        if start_date.tzinfo is None:
            start_date = EST.localize(start_date)
        elif start_date.tzinfo != EST:
            start_date = start_date.astimezone(EST)
    
    schedule = []
    current_date = start_date.date()
    
    for day_offset in range(num_days):
        target_date = current_date + timedelta(days=day_offset)
        
        # 4 publishing windows per day
        times = [
            (datetime.combine(target_date, datetime.strptime('07:30', '%H:%M').time()).replace(tzinfo=EST), '7:30 AM EST - Morning Horror'),
            (datetime.combine(target_date, datetime.strptime('14:00', '%H:%M').time()).replace(tzinfo=EST), '2:00 PM EST - Afternoon Horror'),
            (datetime.combine(target_date, datetime.strptime('20:00', '%H:%M').time()).replace(tzinfo=EST), '8:00 PM EST - Evening Horror ⭐'),
            (datetime.combine(target_date, datetime.strptime('22:30', '%H:%M').time()).replace(tzinfo=EST), '10:30 PM EST - Night Horror'),
        ]
        
        for publish_time, label in times:
            horror_type = get_time_based_horror_type(publish_time)
            schedule.append((publish_time, label, horror_type))
    
    return schedule


if __name__ == "__main__":
    from datetime import timedelta
    
    # Test
    print("=" * 70)
    print("🧪 TESTING TIME-BASED HORROR STRATEGY")
    print("=" * 70)
    print()
    
    test_times = [
        datetime(2026, 1, 1, 7, 30, tzinfo=EST),  # Morning
        datetime(2026, 1, 1, 14, 0, tzinfo=EST),  # Afternoon
        datetime(2026, 1, 1, 20, 0, tzinfo=EST),  # Evening
        datetime(2026, 1, 1, 22, 30, tzinfo=EST),  # Night
    ]
    
    for test_time in test_times:
        horror_type = get_time_based_horror_type(test_time)
        print(f"⏰ {test_time.strftime('%I:%M %p %Z')}:")
        print(f"   Window: {horror_type['time_window']}")
        print(f"   Type: {horror_type['horror_type']}")
        print(f"   Intensity: {horror_type['intensity']}")
        print(f"   Goal: {horror_type['goal']}")
        print()
