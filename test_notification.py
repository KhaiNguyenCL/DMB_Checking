"""
Test Bitrix Notification - Simulate device state change (ON → OFF)
"""

import json

STATE_FILE = "data/device_states.json"

def test_notification():
    print("=" * 70)
    print("🧪 TEST BITRIX NOTIFICATION - SIMULATE STATE CHANGE")
    print("=" * 70)
    print()
    
    # Load state
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    devices = data.get("devices", {})
    print(f"📊 Loaded {len(devices)} devices from state file")
    
    # Find an OFF device (Vietnam) to fake as was ON
    # These are currently OFF, we'll pretend they were ON
    target_devices = [
        "YFUC_1C54E6297CC9",  # Sun World Fansipan MB 03
        "YFUC_1C54E6297CDC",  # Sun World Fansipan MB 01
        "YFUC_1C54E6297CD2",  # Sun World Fansipan MB 02
    ]
    
    modified = []
    for dev_id in target_devices:
        if dev_id in devices:
            print(f"  {dev_id}: {devices[dev_id]} → Setting to 'On' (fake)")
            devices[dev_id] = "On"
            modified.append(dev_id)
    
    if not modified:
        print("⚠️  Target devices not found in state")
        print("    Using first 3 OFF devices instead...")
        
        off_devices = [(k, v) for k, v in devices.items() if v == "Off"][:3]
        for dev_id, _ in off_devices:
            devices[dev_id] = "On"
            modified.append(dev_id)
            print(f"  {dev_id}: Off → On (fake)")
    
    # Save modified state
    data["devices"] = devices
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print()
    print(f"✅ Modified {len(modified)} devices to fake 'On' state")
    print()
    print("=" * 70)
    print("📋 WHAT HAPPENS NEXT:")
    print("=" * 70)
    print()
    print("Next monitor check (within 5 minutes) will:")
    print()
    for i, dev_id in enumerate(modified, 1):
        print(f"  {i}. Device {dev_id}")
        print(f"     - State file says: ON")
        print(f"     - Real API data says: OFF")
        print(f"     - 🎯 Detected: ON → OFF transition")
    print()
    print("  → 🔔 BITRIX NOTIFICATION WILL BE SENT!")
    print()
    print("=" * 70)
    print("⏰ OPTIONS:")
    print("=" * 70)
    print()
    print("A. Wait max 5 minutes for next automatic check")
    print("B. RESTART monitor now (Ctrl+C then run again) to test immediately")
    print()
    print("📱 Check Bitrix24 'DMD Checking Notification' chat for message!")
    print()


if __name__ == "__main__":
    test_notification()
