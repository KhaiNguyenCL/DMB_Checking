"""
Lấy cookie từ trình duyệt đang chạy (Chrome/Firefox)
Hướng dẫn sử dụng: python extract_browser_cookie.py
"""

import browser_cookie3
import json


def get_cookies_from_chrome(domain):
    """
    Lấy cookies từ Chrome
    
    Tham số:
        domain (str): Domain cần lấy cookie (ví dụ: "34.64.189.31")
    
    Trả về:
        dict: Cookies dictionary
    """
    try:
        # Lấy tất cả cookies từ Chrome
        cookies = browser_cookie3.chrome(domain_name=domain)
        
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie.name] = cookie.value
        
        return cookies_dict
    
    except Exception as e:
        print(f"❌ Lỗi khi lấy cookie từ Chrome: {e}")
        return None


def get_cookies_from_firefox(domain):
    """
    Lấy cookies từ Firefox
    
    Tham số:
        domain (str): Domain cần lấy cookie
    
    Trả về:
        dict: Cookies dictionary
    """
    try:
        cookies = browser_cookie3.firefox(domain_name=domain)
        
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie.name] = cookie.value
        
        return cookies_dict
    
    except Exception as e:
        print(f"❌ Lỗi khi lấy cookie từ Firefox: {e}")
        return None


def cookies_dict_to_string(cookies_dict):
    """
    Chuyển cookies dictionary thành string
    
    Tham số:
        cookies_dict (dict): Cookies dictionary
    
    Trả về:
        str: Cookie string
    """
    return "; ".join([f"{name}={value}" for name, value in cookies_dict.items()])


def update_config_file(cookie_string):
    """
    Cập nhật file config.py với cookie mới
    
    Tham số:
        cookie_string (str): Cookie string
    """
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
        print(f"\n💡 Copy cookie này vào config.py:\n")
        print(f'COOKIE = "{cookie_string}"\n')


def main():
    """
    Hàm chính
    """
    print("=" * 60)
    print("🍪 LẤY COOKIE TỪ TRÌNH DUYỆT")
    print("=" * 60)
    print()
    
    # Domain cần lấy cookie
    domain = "34.64.189.31"
    
    print(f"🔍 Đang tìm cookies cho domain: {domain}")
    print()
    
    # Thử Chrome trước
    print("🌐 Đang thử lấy từ Chrome...")
    cookies_dict = get_cookies_from_chrome(domain)
    
    # Nếu không có, thử Firefox
    if not cookies_dict or len(cookies_dict) == 0:
        print("🦊 Đang thử lấy từ Firefox...")
        cookies_dict = get_cookies_from_firefox(domain)
    
    if cookies_dict and len(cookies_dict) > 0:
        print()
        print("=" * 60)
        print("✅ LẤY COOKIE THÀNH CÔNG!")
        print("=" * 60)
        print()
        
        # Hiển thị cookies
        print("🍪 Cookies tìm thấy:")
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
        update_config_file(cookie_string)
        
        print()
        print("📌 Bước tiếp theo:")
        print("   python fetch_data.py")
        
    else:
        print()
        print("❌ KHÔNG TÌM THẤY COOKIE!")
        print()
        print("💡 Nguyên nhân có thể:")
        print("   1. Bạn chưa đăng nhập vào trang web trên trình duyệt")
        print("   2. Cookie đã hết hạn")
        print("   3. Trình duyệt đang đóng")
        print()
        print("🔧 Giải pháp:")
        print("   1. Mở Chrome hoặc Firefox")
        print("   2. Đăng nhập vào https://34.64.189.31")
        print("   3. Chạy lại script này")
        print()
        print("   Hoặc dùng: python auto_login_selenium.py")


if __name__ == "__main__":
    main()
