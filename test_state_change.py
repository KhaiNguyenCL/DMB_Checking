"""
Test script to simulate device state change (ON → OFF)
This will trigger Bitrix notification
"""

import json
import os

STATE_FILE = "data/device_states.json"

def test_state_change():
    """
    Modify state file to simulate a device that was ON is now OFF
    This will trigger notification on next monitor check
    """
    
    print("=" * 60)
    print("🧪 TEST STATE CHANGE - TRIGGER NOTIFICATION")
    print("=" * 60)
    print()
    
    # Load current state
    if not os.path.exists(STATE_FILE):
        print("❌ State file not found. Run monitor first to create it.")
        return
    
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    
    print(f"📊 Current state has {len(state)} devices")
    print()
    
    # Find a device that is currently OFF
    offline_devices = [dev_id for dev_id, status in state.items() if status == "Off"]
    
    if not offline_devices:
        print("⚠️  No offline devices found in state. Cannot simulate ON→OFF.")
        return
    
    # Pick first offline device to simulate as "was ON before"
    test_device = offline_devices[0]
    
    print(f"🎯 Selected test device: {test_device}")
    print(f"   Current state in file: {state[test_device]}")
    print()
    print("🔧 Modifying state to simulate this device was ON...")
    
    # Change state to "On" 
    # Next monitor check will see it as OFF in real data → trigger ON→OFF notification
    state[test_device] = "On"
    
    # Save modified state
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    print("✅ State file updated!")
    print()
    print("=" * 60)
    print("📋 NEXT STEPS:")
    print("=" * 60)
    print()
    print("The next monitor check (within 5 minutes) will:")
    print(f"  1. See device {test_device} is OFF in API data")
    print(f"  2. Compare with state file (shows ON)")
    print(f"  3. Detect ON → OFF transition")
    print(f"  4. 🔔 SEND BITRIX NOTIFICATION!")
    print()
    print("⏰ Wait for next check or restart monitor to test immediately.")
    print()
    print("To revert (after test):")
    print("  - Just wait - monitor will auto-correct state on next check")
    print()
    print("=" * 60)


if __name__ == "__main__":
    test_state_change()
