"""
Gửi notification lên Bitrix24 chat qua Incoming Webhook
Sử dụng Bitrix24 REST API
"""

import requests
import json
from datetime import datetime
from config_bitrix import (
    WEBHOOK_URL, 
    CHAT_ID, 
    BITRIX_ENABLED, 
    DEVICE_OFFLINE_TEMPLATE,
    TEST_MESSAGE
)


def send_bitrix_message(message, chat_id=None, system=False):
    """
    Gửi message lên Bitrix24 chat qua REST API
    
    Args:
        message (str): Nội dung message
        chat_id (int): ID của chat/group, nếu None sẽ dùng default từ config
        system (bool): Gửi dưới dạng system message (không hiện tên người gửi)
    
    Returns:
        dict: Response từ API với keys: success, error, message_id
    """
    if not BITRIX_ENABLED:
        print("⚠️  Bitrix notification is disabled in config")
        return {"success": False, "error": "Bitrix disabled in config"}
    
    target_chat_id = chat_id or CHAT_ID
    
    if not target_chat_id:
        print("❌ CHAT_ID not configured!")
        print("📝 Hướng dẫn lấy CHAT_ID:")
        print("   1. Mở Bitrix24 messenger")
        print("   2. Vào group chat muốn nhận notification")
        print("   3. Xem URL: https://.../chat/123/ → CHAT_ID = 123")
        print("   4. Hoặc dùng messaging.html để load danh sách chats")
        return {"success": False, "error": "No CHAT_ID configured"}
    
    # Bitrix24 REST API endpoint for sending message
    # API: im.message.add
    api_url = f"{WEBHOOK_URL}im.message.add.json"
    
    params = {
        "DIALOG_ID": f"chat{target_chat_id}",  # Format: chatXX cho group chat
        "MESSAGE": message
    }
    
    # Nếu là system message, thêm flag
    if system:
        params["SYSTEM"] = "Y"
    
    try:
        print(f"📤 Đang gửi message lên Bitrix24 (Chat ID: {target_chat_id})...")
        
        # Gọi API với SSL verify=False cho internal network
        response = requests.post(
            api_url,
            json=params,
            timeout=10,
            verify=False  # Bỏ qua SSL verification cho IP local
        )
        
        # Suppress SSL warning
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        result = response.json()
        
        if result.get("result"):
            message_id = result["result"]
            print(f"✅ Đã gửi message lên Bitrix24 (Message ID: {message_id})")
            return {
                "success": True,
                "message_id": message_id,
                "chat_id": target_chat_id
            }
        else:
            error_msg = result.get("error_description", result.get("error", "Unknown error"))
            print(f"❌ Lỗi từ Bitrix API: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "response": result
            }
        
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL Error: {e}")
        print("💡 Tip: Đảm bảo WEBHOOK_URL đúng hoặc thêm verify=False")
        return {"success": False, "error": f"SSL Error: {str(e)}"}
    
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("💡 Tip: Kiểm tra Bitrix server có đang chạy không")
        return {"success": False, "error": f"Connection Error: {str(e)}"}
    
    except Exception as e:
        print(f"❌ Exception khi gửi Bitrix: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def notify_offline_devices(offline_devices, total_devices):
    """
    Gửi notification về devices offline
    
    Args:
        offline_devices (list): Danh sách devices offline
        total_devices (int): Tổng số devices
    
    Returns:
        dict: Response từ API
    """
    if not offline_devices:
        return {"success": False, "error": "No offline devices"}
    
    # Format device list (SHOW ALL devices)
    device_list = ""
    for idx, device in enumerate(offline_devices, 1):
        device_name = device[1] if len(device) > 1 else "Unknown"
        last_seen = device[6] if len(device) > 6 else "Unknown"
        # Format: "1. Device Name - Last seen: timestamp"
        device_list += f"{idx}. {device_name} - Last seen: {last_seen}\n"
    
    # Format message từ template
    message = DEVICE_OFFLINE_TEMPLATE.format(
        count=len(offline_devices),
        device_list=device_list,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total=total_devices
    )
    
    return send_bitrix_message(message)


def send_test_message():
    """
    Gửi test message để kiểm tra kết nối
    
    Returns:
        dict: Response từ API
    """
    return send_bitrix_message(TEST_MESSAGE)


if __name__ == "__main__":
    # Test khi chạy trực tiếp file này
    print("=" * 60)
    print("🧪 TEST BITRIX NOTIFICATION")
    print("=" * 60)
    print()
    
    result = send_test_message()
    
    print()
    print("=" * 60)
    if result.get("success"):
        print("✅ TEST PASSED!")
        print("🎉 Bitrix notification đã sẵn sàng sử dụng!")
    else:
        print("❌ TEST FAILED!")
        print(f"Error: {result.get('error')}")
    print("=" * 60)
