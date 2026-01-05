"""
Script để so sánh dữ liệu mới với dữ liệu mẫu
Hướng dẫn sử dụng: python compare_data.py
"""

import json
import os
from config import OUTPUT_DIR, LATEST_FILE, SAMPLE_FILE


def load_json_file(filename):
    """
    Đọc file JSON
    
    Tham số:
        filename (str): Tên file
    
    Trả về:
        dict hoặc None: Dữ liệu JSON hoặc None nếu lỗi
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"❌ File không tồn tại: {filepath}")
        return None
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi đọc file JSON: {e}")
        return None


def compare_data(sample_data, latest_data):
    """
    So sánh hai bộ dữ liệu
    
    Tham số:
        sample_data (dict): Dữ liệu mẫu
        latest_data (dict): Dữ liệu mới nhất
    """
    sample_records = sample_data.get("data", [])
    latest_records = latest_data.get("data", [])
    
    print("=" * 60)
    print("📊 SO SÁNH DỮ LIỆU")
    print("=" * 60)
    print()
    
    print(f"📅 Thời gian lấy dữ liệu mẫu: {sample_data.get('fetch_time', 'N/A')}")
    print(f"📅 Thời gian lấy dữ liệu mới: {latest_data.get('fetch_time', 'N/A')}")
    print()
    
    print(f"📊 Số lượng records:")
    print(f"   - Dữ liệu mẫu: {len(sample_records)} records")
    print(f"   - Dữ liệu mới:  {len(latest_records)} records")
    print()
    
    # Chuyển đổi thành set để so sánh
    # Mỗi record là một list, chuyển thành tuple để có thể hash
    sample_set = set(tuple(record) for record in sample_records)
    latest_set = set(tuple(record) for record in latest_records)
    
    # Tìm sự khác biệt
    added = latest_set - sample_set  # Có trong latest nhưng không có trong sample
    removed = sample_set - latest_set  # Có trong sample nhưng không có trong latest
    
    print("=" * 60)
    print("🔍 KẾT QUẢ SO SÁNH")
    print("=" * 60)
    print()
    
    if len(added) == 0 and len(removed) == 0:
        print("✅ DỮ LIỆU GIỐNG NHAU HOÀN TOÀN!")
        print("   Không có thay đổi nào giữa hai lần lấy dữ liệu.")
    else:
        print(f"⚠️ PHÁT HIỆN THAY ĐỔI:")
        print(f"   + Thêm mới: {len(added)} records")
        print(f"   - Xóa đi:   {len(removed)} records")
        print()
        
        # Hiển thị chi tiết records thêm mới
        if added:
            print("=" * 60)
            print("➕ RECORDS THÊM MỚI:")
            print("=" * 60)
            for i, record in enumerate(list(added)[:5], 1):  # Chỉ hiển thị 5 records đầu
                # Record[1] thường là tên/ID
                print(f"{i}. {record[1] if len(record) > 1 else record}")
            
            if len(added) > 5:
                print(f"   ... và {len(added) - 5} records khác")
            print()
        
        # Hiển thị chi tiết records bị xóa
        if removed:
            print("=" * 60)
            print("➖ RECORDS BỊ XÓA:")
            print("=" * 60)
            for i, record in enumerate(list(removed)[:5], 1):
                print(f"{i}. {record[1] if len(record) > 1 else record}")
            
            if len(removed) > 5:
                print(f"   ... và {len(removed) - 5} records khác")
            print()
    
    print("=" * 60)


def main():
    """
    Hàm chính
    """
    print()
    
    # Đọc file mẫu
    sample_data = load_json_file(SAMPLE_FILE)
    if not sample_data:
        print()
        print("💡 Hướng dẫn tạo file mẫu:")
        print(f"   copy {OUTPUT_DIR}\\{LATEST_FILE} {OUTPUT_DIR}\\{SAMPLE_FILE}")
        return
    
    # Đọc file mới nhất
    latest_data = load_json_file(LATEST_FILE)
    if not latest_data:
        print()
        print("💡 Hướng dẫn lấy dữ liệu mới:")
        print("   python fetch_data.py")
        return
    
    # So sánh
    compare_data(sample_data, latest_data)
    
    print()
    print("📌 Bước tiếp theo:")
    print("   - Nếu muốn cập nhật dữ liệu mẫu:")
    print(f"     copy {OUTPUT_DIR}\\{LATEST_FILE} {OUTPUT_DIR}\\{SAMPLE_FILE}")
    print("   - Nếu muốn lấy dữ liệu mới:")
    print("     python fetch_data.py")
    print()


if __name__ == "__main__":
    main()
