"""
Tự động đăng nhập và lấy cookie bằng Selenium
Hướng dẫn sử dụng: python auto_login_selenium.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

# Import cấu hình
from config_auto import LOGIN_URL, USERNAME, PASSWORD, HEADLESS_MODE


def setup_driver(headless=False):
    """
    Khởi tạo Chrome WebDriver
    
    Tham số:
        headless (bool): Chạy ẩn (không hiển thị trình duyệt)
    
    Trả về:
        WebDriver: Chrome driver instance
    """
    options = webdriver.ChromeOptions()
    
    if headless:
        options.add_argument('--headless')  # Chạy ẩn
    
    # Các options khác để tránh bị phát hiện là bot
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')  # Bỏ qua SSL errors
    
    # User agent giả lập
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    # Khởi tạo driver (tự động download ChromeDriver nếu chưa có)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver


def login_and_get_cookies(driver, login_url, username, password):
    """
    Đăng nhập và lấy cookies
    
    Tham số:
        driver: WebDriver instance
        login_url (str): URL trang đăng nhập
        username (str): Tên đăng nhập
        password (str): Mật khẩu
    
    Trả về:
        dict: Cookies dưới dạng dictionary
    """
    print(f"🌐 Đang truy cập: {login_url}")
    driver.get(login_url)
    
    # Đợi trang load
    time.sleep(2)
    
    try:
        # Tìm input username (có thể cần thay đổi selector tùy trang web)
        print("🔍 Đang tìm form đăng nhập...")
        
        # Thử các selector phổ biến cho username/email
        username_selectors = [
            "#inputEmailAddress",  # Selector cụ thể cho trang này
            "input[name='username']",
            "input[name='login']",
            "input[name='email']",
            "input[type='email']",
            "input[type='text']",
            "#username",
            "#login"
        ]
        
        username_input = None
        for selector in username_selectors:
            try:
                username_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Tìm thấy email/username input: {selector}")
                break
            except:
                continue
        
        if not username_input:
            print("❌ Không tìm thấy input username!")
            print("💡 Mở trình duyệt thủ công để xem form đăng nhập")
            input("Nhấn Enter sau khi đăng nhập thủ công...")
            return get_cookies_dict(driver)
        
        # Tìm input password
        password_selectors = [
            "#inputPassword",  # Selector cụ thể cho trang này
            "input[name='password']",
            "input[type='password']",
            "#password"
        ]
        
        password_input = None
        for selector in password_selectors:
            try:
                password_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Tìm thấy password input: {selector}")
                break
            except:
                continue
        
        if not password_input:
            print("❌ Không tìm thấy input password!")
            input("Nhấn Enter sau khi đăng nhập thủ công...")
            return get_cookies_dict(driver)
        
        # Nhập username và password
        print(f"⌨️  Đang nhập username: {username}")
        username_input.clear()
        username_input.send_keys(username)
        
        print("⌨️  Đang nhập password...")
        password_input.clear()
        password_input.send_keys(password)
        
        # Tìm nút submit
        submit_selectors = [
            ".login-btn",  # Selector cụ thể cho trang này (div với class login-btn)
            "button[type='submit']",
            "input[type='submit']",
            "button.btn-primary",
            "button.btn-login",
            ".login-button",
            "form button"
        ]
        
        submit_button = None
        for selector in submit_selectors:
            try:
                submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Tìm thấy submit button: {selector}")
                break
            except:
                continue
        
        if submit_button:
            print("🖱️  Đang click nút đăng nhập...")
            submit_button.click()
        else:
            print("⚠️  Không tìm thấy nút submit, thử nhấn Enter...")
            password_input.submit()
        
        # Đợi đăng nhập thành công
        print("⏳ Đang đợi đăng nhập...")
        time.sleep(5)
        
        # Kiểm tra URL có thay đổi không (thường redirect sau khi login)
        current_url = driver.current_url
        if current_url != login_url:
            print(f"✅ Đăng nhập thành công! Redirect đến: {current_url}")
        else:
            print("⚠️  URL không đổi, có thể cần kiểm tra lại")
        
    except Exception as e:
        print(f"⚠️  Lỗi trong quá trình đăng nhập: {e}")
        print("💡 Bạn có thể đăng nhập thủ công...")
        input("Nhấn Enter sau khi đăng nhập xong...")
    
    # Lấy cookies
    return get_cookies_dict(driver)


def get_cookies_dict(driver):
    """
    Lấy cookies từ driver và chuyển thành dictionary
    
    Tham số:
        driver: WebDriver instance
    
    Trả về:
        dict: Cookies với key là tên cookie, value là giá trị
    """
    cookies = driver.get_cookies()
    cookies_dict = {}
    
    for cookie in cookies:
        cookies_dict[cookie['name']] = cookie['value']
    
    return cookies_dict


def cookies_dict_to_string(cookies_dict):
    """
    Chuyển cookies dictionary thành string format
    
    Tham số:
        cookies_dict (dict): Cookies dictionary
    
    Trả về:
        str: Cookie string (format: "name1=value1; name2=value2")
    """
    return "; ".join([f"{name}={value}" for name, value in cookies_dict.items()])


def save_cookies(cookies_dict, filename="cookies.json"):
    """
    Lưu cookies vào file JSON
    
    Tham số:
        cookies_dict (dict): Cookies dictionary
        filename (str): Tên file
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cookies_dict, f, indent=2)
    
    print(f"💾 Đã lưu cookies vào: {filename}")


def update_config_file(cookie_string):
    """
    Cập nhật file config.py với cookie mới
    
    Tham số:
        cookie_string (str): Cookie string
    """
    try:
        # Đọc file config.py
        with open("config.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Thay thế dòng COOKIE
        import re
        pattern = r'COOKIE = ".*?"'
        replacement = f'COOKIE = "{cookie_string}"'
        new_content = re.sub(pattern, replacement, content)
        
        # Ghi lại file
        with open("config.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print("✅ Đã cập nhật config.py với cookie mới!")
        
    except Exception as e:
        print(f"⚠️  Không thể cập nhật config.py: {e}")
        print("💡 Bạn có thể copy cookie thủ công:")
        print(f"\nCOOKIE = \"{cookie_string}\"\n")


def main():
    """
    Hàm chính
    """
    print("=" * 60)
    print("🤖 TỰ ĐỘNG LẤY COOKIE VỚI SELENIUM")
    print("=" * 60)
    print()
    
    # Kiểm tra cấu hình
    if USERNAME == "your_username" or PASSWORD == "your_password":
        print("❌ LỖI: Bạn chưa cấu hình username/password!")
        print("📝 Hướng dẫn:")
        print("   1. Mở file config_auto.py")
        print("   2. Thay your_username và your_password")
        print("   3. Chạy lại script này")
        return
    
    driver = None
    
    try:
        # Khởi tạo driver
        print("🚀 Đang khởi động Chrome...")
        driver = setup_driver(headless=HEADLESS_MODE)
        
        # Đăng nhập và lấy cookies
        cookies_dict = login_and_get_cookies(driver, LOGIN_URL, USERNAME, PASSWORD)
        
        if cookies_dict:
            print()
            print("=" * 60)
            print("✅ LẤY COOKIE THÀNH CÔNG!")
            print("=" * 60)
            print()
            
            # Hiển thị cookies
            print("🍪 Cookies:")
            for name, value in cookies_dict.items():
                print(f"   {name} = {value[:50]}..." if len(value) > 50 else f"   {name} = {value}")
            print()
            
            # Chuyển thành string
            cookie_string = cookies_dict_to_string(cookies_dict)
            
            # Lưu vào file
            save_cookies(cookies_dict)
            
            # Cập nhật config.py
            update_config_file(cookie_string)
            
            print()
            print("📌 Bước tiếp theo:")
            print("   1. Chạy: python fetch_data.py")
            print("   2. Kiểm tra dữ liệu trong data/")
            
        else:
            print("❌ Không lấy được cookie!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            print()
            print("🔒 Đang đóng trình duyệt...")
            time.sleep(2)
            driver.quit()
            print("✅ Hoàn tất!")


if __name__ == "__main__":
    main()
