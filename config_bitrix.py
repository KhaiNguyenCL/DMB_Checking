"""
Cấu hình Bitrix24 Messaging
"""

# ============================================
# BITRIX24 WEBHOOK CONFIGURATION
# ============================================

# Webhook URL (Incoming Webhook)
# Lấy từ: Bitrix24 Settings → Webhooks → Incoming webhook
WEBHOOK_URL = "https://erp.dnsvn.com/rest/78/7wnm544kois2k008/"

# Chat ID của group muốn gửi notification
# Workgroup: DMD Checking Notification (Group ID: 169)
# Chat ID được lấy tự động từ API
CHAT_ID = 911

# Enable/Disable Bitrix notification
BITRIX_ENABLED = True

# ============================================
# MESSAGE TEMPLATES
# ============================================

# Template cho notification thiết bị offline
DEVICE_OFFLINE_TEMPLATE = """🔴 THIẾT BỊ OFFLINE - VIETNAM

Phát hiện {count} thiết bị offline:
{device_list}

⏰ Thời gian: {timestamp}
📊 Tổng thiết bị: {total}
"""

# Template cho test message
TEST_MESSAGE = "🤖 TEST: Bitrix notification system đang hoạt động!"
