#!/usr/bin/env python3
"""
Generate videos for TODAY's 4 publishing windows using time-based horror strategy.
Uses the daily_content_generator with num_days=1.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from daily_content_generator import generate_daily_content

if __name__ == "__main__":
    print("=" * 70)
    print("🎬 GENERATING TODAY'S VIDEOS (4X Daily Strategy)")
    print("=" * 70)
    print()
    
    # Generate just today (1 day = 4 videos)
    successful, failed = generate_daily_content(num_days=1)
    
    print()
    print("=" * 70)
    if successful == 4:
        print("✅ ALL 4 VIDEOS GENERATED SUCCESSFULLY!")
    else:
        print(f"⚠️ Generated {successful}/4 videos (failed: {failed})")
    print("=" * 70)
