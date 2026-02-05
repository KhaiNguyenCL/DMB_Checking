"""
Monitor devices real-time
Fetch data mỗi 5 phút và check devices Off ở Vietnam
"""

import subprocess
import time
import json
import os
from datetime import datetime

# Bitrix notification
try:
    from send_bitrix_notification import notify_offline_devices
    BITRIX_AVAILABLE = True
except ImportError:
    BITRIX_AVAILABLE = False
    print("⚠️  Warning: Bitrix notification module not found. Notifications disabled.")

# Config
DATA_DIR = "data"
LATEST_FILE = os.path.join(DATA_DIR, "clone_list_latest.json")
STATE_FILE = os.path.join(DATA_DIR, "device_states.json")  # State tracking file
EXCEPTION_LIST_FILE = os.path.join(DATA_DIR, "Exception_list.txt")  # Blacklist device IDs
LOG_FILE = os.path.join("logs", "monitor_history.log")
INTERVAL = 5 * 60  # 5 phút = 300 giây

# Field indices
DEVICE_NAME_IDX = 1
STATUS_IDX = 2
REGION_IDX = 8
DEVICE_ID_IDX = 12
LAST_SEEN_IDX = 6


def log_to_file(message):
    """Lưu log vào file"""
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{message}\n")


def print_and_log(message):
    """Print ra console và lưu vào file"""
    print(message)
    log_to_file(message)


def load_exception_list():
    """
    Load device IDs từ exception list (blacklist)
    
    Returns:
        set: Set of device IDs to exclude from monitoring
    """
    if not os.path.exists(EXCEPTION_LIST_FILE):
        return set()
    
    try:
        with open(EXCEPTION_LIST_FILE, "r", encoding="utf-8") as f:
            # Đọc từng dòng, strip whitespace, bỏ qua dòng trống
            device_ids = {line.strip() for line in f if line.strip()}
        
        if device_ids:
            print_and_log(f"📋 Loaded {len(device_ids)} device IDs from exception list")
        
        return device_ids
    except Exception as e:
        print_and_log(f"⚠️  Không load được exception list: {e}")
        return set()


def load_json_file(filepath):
    """Load JSON file"""
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return None


def filter_offline_vietnam_devices(data, exception_list=None):
    """
    Filter devices với Status = "Off" và Region = "Vietnam"
    Loại bỏ devices trong exception list
    
    Args:
        data: JSON data containing device list
        exception_list: Set of device IDs to exclude (optional)
    
    Returns:
        list: Filtered devices
    """
    if not data or "data" not in data:
        return []
    
    if exception_list is None:
        exception_list = set()
    
    devices = data["data"]
    filtered = []
    excluded_count = 0
    
    for device in devices:
        if len(device) < 9:
            continue
        
        status = device[STATUS_IDX].strip()
        region = device[REGION_IDX].strip()
        device_id = device[DEVICE_ID_IDX].strip() if len(device) > DEVICE_ID_IDX else ""
        
        # Check if device is in exception list
        if device_id in exception_list:
            excluded_count += 1
            continue
        
        if status == "Off" and region == "Vietnam":
            filtered.append(device)
    
    if excluded_count > 0:
        print_and_log(f"🚫 Excluded {excluded_count} devices from exception list")
    
    return filtered


def load_previous_state():
    """Load previous device states từ file"""
    if not os.path.exists(STATE_FILE):
        return {}
    
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("devices", {})
    except Exception as e:
        print_and_log(f"⚠️  Không load được previous state: {e}")
        return {}


def save_current_state(devices):
    """Save current device states vào file"""
    state_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "devices": {}
    }
    
    # Build state dict - OPTIMIZATION: only Vietnam devices
    for device in devices:
        if len(device) > max(DEVICE_ID_IDX, REGION_IDX):
            region = device[REGION_IDX].strip()
            # Only save Vietnam devices
            if region == "Vietnam":
                device_id = device[DEVICE_ID_IDX].strip()
                status = device[STATUS_IDX].strip()
                state_data["devices"][device_id] = status
    
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print_and_log(f"⚠️  Không save được state: {e}")


def get_newly_offline_devices(current_offline_devices, previous_state):
    """
    Tìm devices vừa chuyển từ ON → OFF
    
    Args:
        current_offline_devices: list devices hiện đang OFF
        previous_state: dict {device_id: status} từ lần check trước
    
    Returns:
        list devices vừa transition ON → OFF
    """
    newly_offline = []
    
    for device in current_offline_devices:
        if len(device) <= DEVICE_ID_IDX:
            continue
        
        device_id = device[DEVICE_ID_IDX].strip()
        
        # Check previous state
        prev_status = previous_state.get(device_id)
        
        # Newly offline if:
        # - Previous state was "On", OR
        # - Device chưa từng được track (first time seeing it)
        if prev_status == "On" or prev_status is None:
            newly_offline.append(device)
    
    return newly_offline


def fetch_data():
    """Chạy script fetch_data.py"""
    try:
        import sys
        import os
        
        # Fix: Set UTF-8 encoding để hỗ trợ emoji trong output
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            [sys.executable, "fetch_data.py"],
            capture_output=True,
            text=True,
            timeout=120,
            env=env  # Use modified environment
        )
        
        # Debug: Print detailed error info
        if result.returncode != 0:
            print_and_log(f"\n⚠️  Fetch script failed with return code: {result.returncode}")
            if result.stdout:
                print_and_log(f"STDOUT:\n{result.stdout[:500]}")
            if result.stderr:
                print_and_log(f"STDERR:\n{result.stderr[:500]}")
        
        return result.returncode == 0
    except Exception as e:
        print_and_log(f"❌ Lỗi khi fetch data: {e}")
        return False


def display_results(filtered_devices, fetch_time, total_records):
    """Hiển thị kết quả"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print_and_log(f"\n{'='*80}")
    print_and_log(f"🔍 CHECK DEVICES - {timestamp}")
    print_and_log(f"{'='*80}")
    print_and_log(f"📊 Thời gian fetch: {fetch_time}")
    print_and_log(f"📊 Tổng số devices: {total_records}")
    print_and_log(f"🔴 Số devices OFF ở Vietnam: {len(filtered_devices)}")
    print_and_log(f"{'='*80}")
    
    if len(filtered_devices) == 0:
        print_and_log("✅ Không có device nào offline ở Vietnam")
    else:
        print_and_log(f"\n{'#':<3} {'Device Name':<40} {'Device ID':<20} {'Status':<8} {'Region':<12} {'Last Seen':<20}")
        print_and_log("-" * 120)
        
        for idx, device in enumerate(filtered_devices, 1):
            name = device[DEVICE_NAME_IDX].strip()[:38]
            device_id = device[DEVICE_ID_IDX].strip()
            status = device[STATUS_IDX].strip()
            region = device[REGION_IDX].strip()
            last_seen = device[LAST_SEEN_IDX].strip()
            
            print_and_log(f"{idx:<3} {name:<40} {device_id:<20} {status:<8} {region:<12} {last_seen:<20}")
        
        print_and_log("-" * 120)
    
    print_and_log(f"✅ Hoàn thành! Tìm thấy {len(filtered_devices)} device(s)\n")


def countdown(seconds):
    """Hiển thị đếm ngược"""
    for i in range(seconds, 0, -1):
        mins = i // 60
        secs = i % 60
        print(f"\r⏳ Check tiếp theo trong {mins}:{secs:02d} ...", end="", flush=True)
        time.sleep(1)
    print()


def main():
    """Main loop"""
    print_and_log("=" * 80)
    print_and_log(f"🚀 BẮT ĐẦU MONITOR DEVICES")
    print_and_log(f"📋 Fetch data mỗi 5 phút")
    print_and_log(f"⏱️  Thời gian bắt đầu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_and_log("=" * 80)
    print_and_log("Nhấn CTRL+C để dừng\n")
    
    try:
        check_count = 0
        
        while True:
            check_count += 1
            
            print(f"\n[Check #{check_count}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Fetch data
            print("📥 Đang fetch data...")
            if not fetch_data():
                print_and_log(f"❌ Lỗi khi fetch data")
                print("⏳ Sẽ thử lại sau 5 phút...\n")
                countdown(INTERVAL)
                continue
            
            print("✅ Fetch data thành công")
            
            # Load data
            data = load_json_file(LATEST_FILE)
            if not data:
                print_and_log(f"❌ Không load được file data")
                print("⏳ Sẽ thử lại sau 5 phút...\n")
                countdown(INTERVAL)
                continue
            
            # Load exception list
            exception_list = load_exception_list()
            
            # Filter offline devices (exclude exception list)
            filtered_devices = filter_offline_vietnam_devices(data, exception_list)
            
            # STATE TRACKING: Load previous state
            previous_state = load_previous_state()
            
            # STATE TRACKING: Identify newly offline devices (ON → OFF transitions)
            newly_offline = get_newly_offline_devices(filtered_devices, previous_state)
            
            # Display results
            fetch_time = data.get("fetch_time", "Unknown")
            total_records = data.get("total_records", 0)
            display_results(filtered_devices, fetch_time, total_records)
            
            # STATE TRACKING: Send Bitrix notification ONLY for newly offline devices
            if len(newly_offline) > 0 and BITRIX_AVAILABLE:
                print_and_log(f"\n🔔 Phát hiện {len(newly_offline)} thiết bị VỪA chuyển từ ON → OFF")
                print_and_log("📤 Đang gửi notification lên Bitrix24...")
                try:
                    result = notify_offline_devices(newly_offline, total_records)
                    if result.get("success"):
                        message_id = result.get("message_id")
                        print_and_log(f"✅ Đã gửi notification lên Bitrix24 (Message ID: {message_id})")
                    else:
                        error = result.get("error", "Unknown error")
                        print_and_log(f"⚠️  Không gửi được Bitrix notification: {error}")
                except Exception as e:
                    print_and_log(f"❌ Lỗi khi gửi Bitrix notification: {e}")
            elif len(filtered_devices) > 0 and len(newly_offline) == 0:
                print_and_log(f"\n💡 {len(filtered_devices)} thiết bị offline nhưng ĐÃ được báo trước đó (không gửi lại)")
            elif len(newly_offline) > 0 and not BITRIX_AVAILABLE:
                print_and_log("\n⚠️  Bitrix notification bị tắt (module không có)")
            
            # STATE TRACKING: Save current state for next iteration
            # OPTIMIZATION: Only save Vietnam devices for performance
            all_devices = data.get("data", [])
            save_current_state(all_devices)
            vietnam_count = sum(1 for d in all_devices if len(d) > REGION_IDX and d[REGION_IDX].strip() == "Vietnam")
            print_and_log(f"💾 Đã lưu state của {vietnam_count} Vietnam devices")
            
            # Countdown
            print(f"\n⏳ Check tiếp theo trong 5 phút...")
            countdown(INTERVAL)
            
    except KeyboardInterrupt:
        print_and_log(f"\n\n{'='*80}")
        print_and_log(f"⛔ DỪNG MONITOR")
        print_and_log(f"📋 Thống kê:")
        print_and_log(f"   - Số lần check: {check_count}")
        print_and_log(f"   - Thời gian dừng: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print_and_log(f"{'='*80}\n")


if __name__ == "__main__":
    main()
