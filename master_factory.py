#!/usr/bin/env python3
"""
THE MASTER FACTORY
Orchestrator for the entire AI Shorts Project.

Features:
1. System Audit & Asset Check
2. Market Intelligence (Trending Topics)
3. Batch Generation (Scene-based & High Retention)
4. Automated Scheduling & Upload
5. Post-Production Cleanup
"""

import os
import sys
import argparse
import time
from datetime import datetime, timedelta
import pytz

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config.paths import TEMP_DIR, SHORTS_OUTPUT_DIR, TEMP_LOGS_DIR
from scripts.system_audit import perform_system_audit
from daily_content_generator import generate_daily_content

EST = pytz.timezone('US/Eastern')

def clean_temp_files():
    """Remove temporary files but keep directories and logs."""
    print("\n🧹 Cleanup Agent: Clearing temporary files...")
    count = 0
    for root, dirs, files in os.walk(TEMP_DIR):
        # Don't delete logs
        if "logs" in root:
            continue
        for file in files:
            if file.endswith(('.mp3', '.mp4', '.jpg', '.png', '.json')):
                try:
                    os.remove(os.path.join(root, file))
                    count += 1
                except Exception as e:
                    print(f"   ⚠️ Could not remove {file}: {e}")
    print(f"   ✓ Removed {count} temporary files.")

def run_production_cycle(num_days=1, niche="Horror"):
    """Run a full production cycle."""
    print("=" * 80)
    print(f"🚀 MASTER FACTORY - Starting Production Cycle ({niche})")
    print("=" * 80)
    
    # 1. Audit
    audit_results = perform_system_audit()
    inventory_passed = all(status for status, _ in audit_results.get("Inventory", []))
    tools_passed = all(status for status, _ in audit_results.get("Tools", []))
    
    if not (inventory_passed and tools_passed):
        print("❌ CRITICAL: System audit failed. Please check dependencies.")
        # We continue if it's just warnings, but fail on total department failure
        if not any(status for status, _ in audit_results.get("Tools", [])):
            return False

    # 2. Market Intelligence & Generation
    print(f"\n[🏭 FACTORY] Generating {num_days} days of {niche} content...")
    start_date = datetime.now(EST)
    
    try:
        successful, failed = generate_daily_content(num_days=num_days, start_date=start_date)
        print(f"\n📊 CYCLE SUMMARY: {successful} Successful, {failed} Failed")
    except Exception as e:
        print(f"❌ ERROR in production: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 3. Cleanup
    clean_temp_files()
    
    print("\n" + "=" * 80)
    print("✅ PRODUCTION CYCLE COMPLETE")
    print("=" * 80)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Shorts Master Factory")
    parser.add_argument("--days", type=int, default=1, help="Number of days to generate (4 videos/day)")
    parser.add_argument("--niche", type=str, default="Horror", help="Content niche")
    parser.add_argument("--cleanup-only", action="store_true", help="Only run cleanup")
    parser.add_argument("--audit-only", action="store_true", help="Only run system audit")
    
    args = parser.parse_args()
    
    if args.cleanup_only:
        clean_temp_files()
    elif args.audit_only:
        perform_system_audit()
    else:
        run_production_cycle(num_days=args.days, niche=args.niche)
