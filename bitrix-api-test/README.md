# 🚀 Bitrix24 CRM API Test Dashboard

Dashboard để test và lấy data từ các CRM entities của Bitrix24.

## 📋 Mục đích

Tool này giúp bạn:
- Test các API endpoints của Bitrix24 CRM
- Lấy danh sách data từ tất cả các CRM entities
- Xem cấu trúc fields của từng entity
- Hiểu rõ cách dữ liệu được tổ chức trong Bitrix24

## 🎯 Các CRM Entities được hỗ trợ

1. **Leads** (👤 Người tiềm năng)
2. **Contacts** (👥 Người liên hệ)
3. **Companies** (🏢 Công ty)
4. **Deals** (💼 Giao dịch)
5. **Products** (📦 Sản phẩm)
6. **Invoices** (📄 Hóa đơn)
7. **Quotes** (📝 Báo giá - chỉ Enterprise)
8. **Activities** (📅 Hoạt động)

## 💬 Messaging Demo (NEW!)

**Gửi tin nhắn lên Chat/Group trong Bitrix24!**

File: `messaging.html` - UI interactive để:
- ✅ Lấy danh sách tất cả chats/groups
- ✅ Gửi tin nhắn lên chat đã chọn
- ✅ Mention users trong tin nhắn
- ✅ Gửi dưới dạng System Message

**Cách sử dụng:**
1. Mở `http://localhost/local/bitrix-api-test/messaging.html`
2. Nhấn "Tải danh sách Chat" để xem tất cả chats
3. Chọn chat/group muốn gửi
4. Nhập tin nhắn và nhấn "Gửi tin nhắn"

**APIs:**
- `api/test-chat-list.php` - Lấy danh sách chats
- `api/test-send-message.php` - Gửi message (POST)

## 🚀 Cách sử dụng

### 1. Mở Dashboard

Truy cập vào URL:
```
http://your-bitrix24-domain/local/bitrix-api-test/index.html
```

hoặc nếu đang chạy local:
```
http://localhost/local/bitrix-api-test/index.html
```

### 2. Chọn Entity để test

Dashboard hiển thị các card cho từng entity. Mỗi card có 2 nút:

- **"Lấy [Entity]"** - Lấy danh sách records
- **"Lấy Fields"** - Lấy cấu trúc fields của entity

### 3. Điều chỉnh số lượng records

Mỗi card có input field để nhập số lượng records muốn lấy (mặc định: 50)

### 4. Xem kết quả

Kết quả sẽ hiển thị dưới dạng JSON với:
- Tổng số records/fields
- Thời gian xử lý
- Dữ liệu đầy đủ

## 📂 Cấu trúc Files

```
bitrix-api-test/
├── index.html              # Dashboard UI
├── api/
│   ├── test-leads.php      # API test cho Leads
│   ├── test-contacts.php   # API test cho Contacts
│   ├── test-companies.php  # API test cho Companies
│   ├── test-deals.php      # API test cho Deals
│   ├── test-products.php   # API test cho Products
│   ├── test-invoices.php   # API test cho Invoices
│   ├── test-quotes.php     # API test cho Quotes
│   └── test-activities.php # API test cho Activities
└── README.md               # File này
```

## 💡 Ví dụ sử dụng

### Lấy danh sách Deals

1. Nhấp vào card "Deals"
2. Nhập số lượng (ví dụ: 10)
3. Nhấn "Lấy Deals"
4. Kết quả sẽ hiển thị 10 deals mới nhất kèm theo:
   - Thông tin deal
   - User fields
   - Products trong deal

### Xem Fields của Contact

1. Nhấp vào card "Contacts"
2. Nhấn "Lấy Fields"
3. Kết quả sẽ hiển thị tất cả fields có sẵn:
   - Standard fields
   - User fields (custom fields)
   - Kiểu dữ liệu
   - Bắt buộc hay không

## 🔍 Chi tiết về từng API

### Leads API
- **Endpoint**: `api/test-leads.php`
- **Methods**: 
  - `?action=list&count=50` - Lấy danh sách leads
  - `?action=fields` - Lấy fields description
- **Dữ liệu**: Tất cả thông tin lead + user fields

### Contacts API
- **Endpoint**: `api/test-contacts.php`
- **Methods**: Tương tự Leads
- **Dữ liệu**: Thông tin người liên hệ + user fields

### Companies API
- **Endpoint**: `api/test-companies.php`
- **Methods**: Tương tự Leads
- **Dữ liệu**: Thông tin công ty + user fields

### Deals API
- **Endpoint**: `api/test-deals.php`
- **Methods**: Tương tự Leads
- **Dữ liệu**: Thông tin deal + user fields + **products trong deal**

### Products API
- **Endpoint**: `api/test-products.php`
- **Methods**: Tương tự Leads
- **Dữ liệu**: 
  - Danh sách tất cả catalogs
  - Products từ mỗi catalog
  - Properties của products
  - Giá

### Invoices API
- **Endpoint**: `api/test-invoices.php`
- **Methods**: Tương tự Leads
- **Dữ liệu**: Thông tin hóa đơn + user fields + products

### Quotes API
- **Endpoint**: `api/test-quotes.php`
- **Methods**: Tương tự Leads
- **Dữ liệu**: Thông tin báo giá + user fields + products
- **Lưu ý**: ⚠️ Chỉ có sẵn trên Bitrix24 Enterprise

### Activities API
- **Endpoint**: `api/test-activities.php`
- **Methods**: Tương tự Leads
- **Dữ liệu**: 
  - Thông tin activity
  - Loại activity (Call, Meeting, Email, Task)
  - Bindings (liên kết với entity nào)

## 🛠️ Yêu cầu hệ thống

- Bitrix24 on-premise installation
- PHP 7.4+
- CRM module đã được kích hoạt
- Đã đăng nhập vào Bitrix24

## ⚠️ Lưu ý

1. **Authentication**: Tất cả APIs yêu cầu phải đăng nhập vào Bitrix24
2. **Permissions**: User phải có quyền truy cập vào CRM
3. **Performance**: Nên giới hạn số lượng records khi test (50-100 records)
4. **Quotes**: Module Quotes chỉ có trên Enterprise edition

## 🔧 Troubleshooting

### Lỗi "Unauthorized"
- Đảm bảo bạn đã đăng nhập vào Bitrix24
- Refresh lại trang và thử lại

### Lỗi "Module not available"
- Kiểm tra module CRM đã được bật chưa
- Đối với Quotes, cần Bitrix24 Enterprise

### Không có dữ liệu
- Kiểm tra CRM có data không
- Thử giảm số lượng records

### HTTP 500 Error
- Xem PHP error log
- Kiểm tra Bitrix24 có hoạt động bình thường không

## 📚 Tài liệu tham khảo

- [Bitrix24 API Documentation](https://apidocs.bitrix24.com/)
- [Bitrix24 CRM REST API](https://apidocs.bitrix24.com/api-reference/crm/index.html)
- [Bitrix24 Developer Documentation](https://dev.1c-bitrix.ru/rest_help/)

## 🎨 Features của Dashboard

- ✅ Modern, responsive UI
- ✅ Real-time data fetching
- ✅ JSON pretty-print
- ✅ Loading states
- ✅ Error handling
- ✅ Statistics display
- ✅ Execution time tracking

## 📝 Sử dụng trong Project

Sau khi test và hiểu cấu trúc data, bạn có thể:

1. **Copy code logic** từ các file test-*.php vào project của bạn
2. **Sử dụng cấu trúc fields** để build forms
3. **Hiểu relationships** giữa các entities
4. **Tạo reports** dựa trên data structure

## 🔐 Bảo mật

⚠️ **QUAN TRỌNG**: Folder này chỉ nên sử dụng cho mục đích development/testing. 

Trước khi deploy lên production:
- Xóa folder này hoặc
- Thêm authentication riêng hoặc
- Chặn truy cập từ bên ngoài

---

Made with ❤️ for Bitrix24 Development
