"""
Gửi email thông báo khi có thay đổi dữ liệu
Hướng dẫn sử dụng: python send_email_notification.py
"""

import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Import cấu hình
try:
    from config_email import (
        SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL,
        SMTP_SERVER, SMTP_PORT,
        NOTIFY_ON_CHANGE, NOTIFY_DAILY_SUMMARY
    )
except ImportError:
    print("❌ Lỗi: Không tìm thấy file config_email.py")
    print("📝 Hướng dẫn:")
    print("   1. Mở file config_email.py")
    print("   2. Điền thông tin email")
    print("   3. Chạy lại script này")
    exit(1)


def load_json_file(filename):
    """Đọc file JSON"""
    filepath = os.path.join("data", filename)
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def compare_data(sample_data, latest_data):
    """So sánh dữ liệu và trả về thống kê"""
    if not sample_data or not latest_data:
        return None
    
    sample_records = sample_data.get("data", [])
    latest_records = latest_data.get("data", [])
    
    # Chuyển thành set để so sánh
    sample_set = set(tuple(record) for record in sample_records)
    latest_set = set(tuple(record) for record in latest_records)
    
    # Tìm sự khác biệt
    added = latest_set - sample_set
    removed = sample_set - latest_set
    
    return {
        "sample_count": len(sample_records),
        "latest_count": len(latest_records),
        "added_count": len(added),
        "removed_count": len(removed),
        "added": list(added)[:10],  # Chỉ lấy 10 records đầu
        "removed": list(removed)[:10],
        "has_changes": len(added) > 0 or len(removed) > 0,
        "sample_time": sample_data.get("fetch_time", "N/A"),
        "latest_time": latest_data.get("fetch_time", "N/A")
    }


def create_email_body(stats):
    """Tạo nội dung email HTML"""
    
    if stats["has_changes"]:
        status_icon = "⚠️"
        status_text = "PHÁT HIỆN THAY ĐỔI"
        status_color = "#ff9800"
    else:
        status_icon = "✅"
        status_text = "KHÔNG CÓ THAY ĐỔI"
        status_color = "#4caf50"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: {status_color}; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
            .content {{ background: #f5f5f5; padding: 20px; margin-top: 20px; border-radius: 5px; }}
            .stats {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid {status_color}; }}
            .changes {{ background: white; padding: 15px; margin: 10px 0; }}
            .added {{ color: #4caf50; }}
            .removed {{ color: #f44336; }}
            .footer {{ text-align: center; margin-top: 20px; color: #999; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{status_icon} {status_text}</h1>
                <p>Báo cáo tự động từ API Scraping</p>
            </div>
            
            <div class="content">
                <div class="stats">
                    <h2>📊 Thống Kê</h2>
                    <p><strong>Thời gian lấy dữ liệu mẫu:</strong> {stats['sample_time']}</p>
                    <p><strong>Thời gian lấy dữ liệu mới:</strong> {stats['latest_time']}</p>
                    <p><strong>Số lượng records (mẫu):</strong> {stats['sample_count']}</p>
                    <p><strong>Số lượng records (mới):</strong> {stats['latest_count']}</p>
                </div>
    """
    
    if stats["has_changes"]:
        html += f"""
                <div class="changes">
                    <h2>🔍 Chi Tiết Thay Đổi</h2>
                    <p class="added"><strong>➕ Thêm mới:</strong> {stats['added_count']} records</p>
                    <p class="removed"><strong>➖ Xóa đi:</strong> {stats['removed_count']} records</p>
        """
        
        if stats['added']:
            html += "<h3 class='added'>Records Thêm Mới:</h3><ul>"
            for record in stats['added'][:5]:
                html += f"<li>{record[1] if len(record) > 1 else record}</li>"
            html += "</ul>"
        
        if stats['removed']:
            html += "<h3 class='removed'>Records Bị Xóa:</h3><ul>"
            for record in stats['removed'][:5]:
                html += f"<li>{record[1] if len(record) > 1 else record}</li>"
            html += "</ul>"
        
        html += "</div>"
    else:
        html += """
                <div class="changes">
                    <h2>✅ Kết Quả</h2>
                    <p>Dữ liệu giống nhau hoàn toàn. Không có thay đổi nào.</p>
                </div>
        """
    
    html += """
            </div>
            
            <div class="footer">
                <p>Email tự động từ hệ thống API Scraping</p>
                <p>Được tạo lúc: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def send_email(subject, body_html):
    """Gửi email"""
    
    # Kiểm tra cấu hình
    if SENDER_EMAIL == "your_email@gmail.com":
        print("❌ Lỗi: Bạn chưa cấu hình email!")
        print("📝 Mở file config_email.py và điền thông tin email")
        return False
    
    try:
        # Tạo message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVER_EMAIL
        
        # Thêm HTML body
        html_part = MIMEText(body_html, "html")
        message.attach(html_part)
        
        # Gửi email
        print(f"📧 Đang gửi email đến: {RECEIVER_EMAIL}")
        
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        
        print("✅ Đã gửi email thành công!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Lỗi xác thực email!")
        print("💡 Kiểm tra:")
        print("   - Email và password có đúng không?")
        print("   - Đã dùng App Password chưa? (không phải password Gmail thường)")
        print("   - Xem hướng dẫn trong config_email.py")
        return False
        
    except Exception as e:
        print(f"❌ Lỗi khi gửi email: {e}")
        return False


def main():
    """Hàm chính"""
    print("=" * 60)
    print("📧 GỬI EMAIL THÔNG BÁO")
    print("=" * 60)
    print()
    
    # Đọc dữ liệu
    sample_data = load_json_file("clone_list_sample.json")
    latest_data = load_json_file("clone_list_latest.json")
    
    if not sample_data or not latest_data:
        print("❌ Không tìm thấy file dữ liệu!")
        return
    
    # So sánh
    stats = compare_data(sample_data, latest_data)
    
    if not stats:
        print("❌ Lỗi khi so sánh dữ liệu!")
        return
    
    # Quyết định có gửi email không
    should_send = False
    
    if stats["has_changes"] and NOTIFY_ON_CHANGE:
        should_send = True
        subject = "⚠️ Cảnh báo: Phát hiện thay đổi dữ liệu"
        print("⚠️  Phát hiện thay đổi dữ liệu!")
    elif NOTIFY_DAILY_SUMMARY:
        should_send = True
        subject = "📊 Báo cáo hàng ngày: API Scraping"
        print("📊 Gửi báo cáo hàng ngày...")
    else:
        print("✅ Không có thay đổi, không gửi email.")
        return
    
    if should_send:
        # Tạo nội dung email
        body_html = create_email_body(stats)
        
        # Gửi email
        send_email(subject, body_html)
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
