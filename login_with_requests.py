"""
Đăng nhập bằng POST request (không dùng trình duyệt)
Hướng dẫn sử dụng: python login_with_requests.py

⚠️ LƯU Ý: Phương pháp này chỉ hoạt động nếu:
- Form login đơn giản (không có JavaScript phức tạp)
- Không có CAPTCHA
- Biết chính xác endpoint và parameters
"""

import requests
import json
import urllib3

# Tắt warning SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def login_with_post(login_url, username, password):
    """
    Đăng nhập bằng POST request
    
    Tham số:
        login_url (str): URL endpoint login
        username (str): Username
        password (str): Password
    
    Trả về:
        requests.Session: Session đã đăng nhập (chứa cookies)
    """
    # Tạo session để lưu cookies
    session = requests.Session()
    
    # Headers giả lập trình duyệt
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": login_url,
    }
    
    # Dữ liệu login (có thể cần thay đổi tùy trang web)
    # Bạn cần inspect form login để biết chính xác field names
    login_data = {
        "username": username,  # Có thể là "login", "email", v.v.
        "password": password,
        # Có thể cần thêm các field khác như:
        # "remember": "1",
        # "csrf_token": "...",
    }
    
    try:
        print(f"🔐 Đang đăng nhập vào: {login_url}")
        print(f"👤 Username: {username}")
        
        # Gửi POST request
        response = session.post(
            login_url,
            data=login_data,
            headers=headers,
            verify=False,  # Bỏ qua SSL verification
            allow_redirects=True,
            timeout=30
        )
        
        # Kiểm tra kết quả
        if response.status_code == 200:
            print(f"✅ Response status: {response.status_code}")
            
            # Kiểm tra có redirect không
            if len(response.history) > 0:
                print(f"🔄 Redirected: {response.url}")
            
            # Kiểm tra cookies
            cookies = session.cookies.get_dict()
            if cookies:
                print(f"🍪 Cookies nhận được: {len(cookies)} cookies")
                return session
            else:
                print("⚠️  Không nhận được cookies!")
                print("💡 Có thể cần kiểm tra lại login endpoint và parameters")
                return None
        else:
            print(f"❌ Lỗi: Status code {response.status_code}")
            return None
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None


def extract_cookies_from_session(session):
    """
    Lấy cookies từ session
    
    Tham số:
        session: requests.Session
    
    Trả về:
        dict: Cookies dictionary
    """
    return session.cookies.get_dict()


def cookies_dict_to_string(cookies_dict):
    """
    Chuyển cookies dictionary thành string
    """
    return "; ".join([f"{name}={value}" for name, value in cookies_dict.items()])


def main():
    """
    Hàm chính
    """
    print("=" * 60)
    print("🔐 ĐĂNG NHẬP BẰNG POST REQUEST")
    print("=" * 60)
    print()
    
    # Cấu hình (thay đổi theo trang web của bạn)
    LOGIN_URL = "https://34.64.189.31/api/login"  # ⚠️ Cần tìm đúng endpoint
    USERNAME = "your_username"
    PASSWORD = "your_password"
    
    # Kiểm tra cấu hình
    if USERNAME == "your_username":
        print("❌ Bạn chưa cấu hình username/password!")
        print()
        print("📝 Hướng dẫn:")
        print("   1. Mở file này (login_with_requests.py)")
        print("   2. Tìm dòng USERNAME và PASSWORD")
        print("   3. Thay đổi giá trị")
        print("   4. Tìm đúng LOGIN_URL endpoint")
        print()
        print("💡 Cách tìm login endpoint:")
        print("   1. Mở Chrome DevTools (F12)")
        print("   2. Tab Network")
        print("   3. Đăng nhập thủ công")
        print("   4. Tìm POST request (thường là /login hoặc /api/login)")
        print("   5. Xem Form Data để biết field names")
        return
    
    # Đăng nhập
    session = login_with_post(LOGIN_URL, USERNAME, PASSWORD)
    
    if session:
        print()
        print("=" * 60)
        print("✅ ĐĂNG NHẬP THÀNH CÔNG!")
        print("=" * 60)
        print()
        
        # Lấy cookies
        cookies_dict = extract_cookies_from_session(session)
        
        # Hiển thị
        print("🍪 Cookies:")
        for name, value in cookies_dict.items():
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"   {name} = {display_value}")
        print()
        
        # Chuyển thành string
        cookie_string = cookies_dict_to_string(cookies_dict)
        
        # Lưu vào file
        with open("cookies.json", "w", encoding="utf-8") as f:
            json.dump(cookies_dict, f, indent=2)
        print("💾 Đã lưu vào: cookies.json")
        print()
        
        # Cập nhật config.py
        try:
            with open("config.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            import re
            pattern = r'COOKIE = ".*?"'
            replacement = f'COOKIE = "{cookie_string}"'
            new_content = re.sub(pattern, replacement, content)
            
            with open("config.py", "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print("✅ Đã cập nhật config.py!")
        except Exception as e:
            print(f"⚠️  Không thể cập nhật config.py: {e}")
            print(f"\n💡 Copy cookie này:\n")
            print(f'COOKIE = "{cookie_string}"\n')
        
        print()
        print("📌 Bước tiếp theo:")
        print("   python fetch_data.py")
    
    else:
        print()
        print("❌ ĐĂNG NHẬP THẤT BẠI!")
        print()
        print("💡 Khuyến nghị:")
        print("   - Dùng Selenium: python auto_login_selenium.py")
        print("   - Hoặc extract từ browser: python extract_browser_cookie.py")


if __name__ == "__main__":
    main()
