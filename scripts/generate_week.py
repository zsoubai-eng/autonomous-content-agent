#!/usr/bin/env python3
"""
Generate and schedule videos for the next 4 days using 4x daily strategy.
"""

import sys
import os
from datetime import datetime, timedelta
import pytz

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from daily_content_generator import generate_daily_content

EST = pytz.timezone('US/Eastern')

if __name__ == "__main__":
    today = datetime.now(EST)
    
    print("=" * 70)
    print("🎬 GENERATING VIDEOS FOR NEXT 4 DAYS")
    print("=" * 70)
    print(f"Current Date: {today.strftime('%A, %B %d, %Y at %I:%M %p %Z')}")
    print()
    print("Strategy: 4x Daily Time-Based Horror")
    print("  • 7:30 AM EST - Morning Horror (Mild)")
    print("  • 2:00 PM EST - Afternoon Horror (Light)")
    print("  • 8:00 PM EST - Evening Horror (Moderate)")
    print("  • 10:30 PM EST - Night Horror (Intense)")
    print()
    print("Total: 16 videos (4 per day × 4 days)")
    print("=" * 70)
    print()
    
    # Generate for next 4 days (starting tomorrow)
    # Note: generate_daily_content uses "next N days" from today, so we pass 4
    successful, failed = generate_daily_content(num_days=4)
    
    print()
    print("=" * 70)
    if successful == 16:
        print("✅ ALL 16 VIDEOS GENERATED SUCCESSFULLY!")
    else:
        print(f"⚠️ Generated {successful}/16 videos (failed: {failed})")
    print("=" * 70)
