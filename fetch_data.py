"""
Script để lấy dữ liệu từ API có authentication
Hướng dẫn sử dụng: python fetch_data.py
"""

import requests
import json
import os
from datetime import datetime
import urllib3

# Import cấu hình
from config import API_URL, HEADERS, PAGINATION, OUTPUT_DIR, LATEST_FILE

# Tắt warning về SSL certificate (vì server dùng self-signed cert)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def build_params(start, length):
    """
    Xây dựng parameters cho API request
    
    API này sử dụng DataTables format với nhiều parameters phức tạp
    Tham số:
        start (int): Vị trí bắt đầu (0, 10, 20, ...)
        length (int): Số lượng records mỗi trang
    
    Trả về:
        dict: Dictionary chứa tất cả parameters
    """
    params = {
        "draw": 2,  # DataTables draw counter (có thể là bất kỳ số nào)
        "start": start,
        "length": length,
        "search[value]": "",  # Không search gì cả, lấy tất cả
        "search[regex]": "false",
        "order[0][column]": 2,  # Sắp xếp theo cột thứ 2
        "order[0][dir]": "desc",  # Giảm dần
    }
    
    # Thêm cấu hình cho 13 cột (columns[0] đến columns[12])
    # Mỗi cột có các thuộc tính: data, name, searchable, orderable, search
    for i in range(13):
        params[f"columns[{i}][data]"] = i
        params[f"columns[{i}][name]"] = ""
        params[f"columns[{i}][searchable]"] = "true"
        params[f"columns[{i}][orderable]"] = "true" if i > 0 else "false"
        params[f"columns[{i}][search][value]"] = ""
        params[f"columns[{i}][search][regex]"] = "false"
    
    return params


def fetch_all_data():
    """
    Lấy toàn bộ dữ liệu từ API (xử lý phân trang tự động)
    
    Trả về:
        list: Danh sách tất cả records
    """
    all_data = []
    start = 0
    length = PAGINATION["length"]
    total_records = None
    
    print(f"🔄 Đang lấy dữ liệu từ API: {API_URL}")
    print(f"📊 Mỗi trang lấy {length} records\n")
    
    page_num = 1
    
    while True:
        # Xây dựng parameters cho request
        params = build_params(start, length)
        
        try:
            # Gửi GET request đến API
            # verify=False: Bỏ qua SSL certificate verification
            # timeout=30: Timeout sau 30 giây
            response = requests.get(
                API_URL,
                headers=HEADERS,
                params=params,
                verify=False,
                timeout=30
            )
            
            # Kiểm tra status code
            if response.status_code != 200:
                print(f"❌ Lỗi: Status code {response.status_code}")
                print(f"Response: {response.text[:200]}")
                break
            
            # Parse JSON response
            data = response.json()
            
            # Lấy thông tin từ response
            records = data.get("data", [])
            total_records = data.get("recordsTotal", 0)
            
            # Thêm records vào danh sách
            all_data.extend(records)
            
            # Hiển thị tiến trình
            current_count = start + len(records)
            print(f"📄 Trang {page_num}: Lấy được {len(records)} records ({start}-{current_count} / {total_records})")
            
            # Kiểm tra xem đã lấy hết chưa
            if current_count >= total_records:
                break
            
            # Chuyển sang trang tiếp theo
            start += length
            page_num += 1
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Lỗi kết nối: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"❌ Lỗi parse JSON: {e}")
            print(f"Response text: {response.text[:200]}")
            break
    
    return all_data


def save_to_file(data, filename):
    """
    Lưu dữ liệu vào file JSON
    
    Tham số:
        data (list): Dữ liệu cần lưu
        filename (str): Tên file
    """
    # Tạo thư mục nếu chưa có
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Đường dẫn đầy đủ
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Chuẩn bị dữ liệu để lưu
    output = {
        "fetch_time": datetime.now().isoformat(),
        "total_records": len(data),
        "data": data
    }
    
    # Lưu vào file với format đẹp (indent=2)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Đã lưu vào: {filepath}")


def main():
    """
    Hàm chính
    """
    print("=" * 60)
    print("🚀 BẮT ĐẦU LẤY DỮ LIỆU")
    print("=" * 60)
    print()
    
    # Kiểm tra cookie đã được cấu hình chưa
    if HEADERS["Cookie"] == "YOUR_COOKIE_HERE":
        print("❌ LỖI: Bạn chưa cấu hình cookie!")
        print("📝 Hướng dẫn:")
        print("   1. Mở file config.py")
        print("   2. Thay YOUR_COOKIE_HERE bằng cookie thật")
        print("   3. Xem README.md để biết cách lấy cookie")
        return
    
    # Lấy dữ liệu
    data = fetch_all_data()
    
    if data:
        print()
        print("=" * 60)
        print(f"✅ HOÀN THÀNH! Tổng cộng: {len(data)} records")
        print("=" * 60)
        print()
        
        # Lưu vào file
        save_to_file(data, LATEST_FILE)
        
        print()
        print("📌 Bước tiếp theo:")
        print("   1. Kiểm tra file data/clone_list_latest.json")
        print("   2. Copy làm file mẫu: copy data\\clone_list_latest.json data\\clone_list_sample.json")
        print("   3. Chạy lại script này để lấy dữ liệu mới")
        print("   4. Chạy compare_data.py để so sánh thay đổi")
    else:
        print()
        print("❌ Không lấy được dữ liệu nào!")
        print("🔍 Kiểm tra:")
        print("   - Cookie có đúng không?")
        print("   - Cookie có hết hạn không?")
        print("   - Kết nối internet có ổn không?")


if __name__ == "__main__":
    main()
