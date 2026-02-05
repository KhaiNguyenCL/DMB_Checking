# Copilot Instructions for API Scraping & Automation

## Project Overview
This is a **learning project** about authenticated API scraping using Python. The codebase demonstrates:
- Cookie-based authentication with `requests`
- Automated login with Selenium WebDriver
- DataTables pagination handling
- Data comparison and email notifications
- Task scheduling for daily automated runs

## Architecture & Data Flow

### Three Core Authentication Methods
The project implements three distinct cookie acquisition strategies:

1. **Selenium WebDriver** (`auto_login_selenium.py`) - Primary automated approach
   - Launches Chrome browser, fills login form, extracts session cookies
   - Used by `run_auto.bat` for fully automated daily runs
   - Handles headless mode for Task Scheduler execution

2. **Browser Cookie Extraction** (`extract_browser_cookie.py`)
   - Uses `browser-cookie3` to read cookies from running Chrome/Firefox
   - Fast alternative requiring manual login once per browser session
   - Updates `config.py` automatically after extraction

3. **POST Request Login** (`login_with_requests.py`)
   - Direct POST request to login endpoint with credentials
   - Session-based approach - stores cookies in session object
   - Fallback method when Selenium/browser extraction unavailable

### Data Pipeline
```
auto_login_selenium.py → (gets JSESSIONID cookie)
    ↓
config.py (stores cookie)
    ↓
fetch_data.py (API pagination loop) → clone_list_latest.json
    ↓
compare_data.py (compares latest vs sample)
    ↓
send_email_notification.py (notifies on changes)
```

## Key Configuration & Patterns

### Config Files Structure
- **`config.py`** - API credentials, headers, pagination settings (shared across tools)
  - `API_URL`: Target API endpoint with self-signed certificate
  - `COOKIE`: JSESSIONID value (updated by automation scripts)
  - `HEADERS`: Browser mimicry with proper User-Agent and Referer
  - `PAGINATION`: Set to 100 records/request to minimize API hits

- **`config_auto.py`** - Selenium automation credentials
  - `LOGIN_URL`, `USERNAME`, `PASSWORD`, `HEADLESS_MODE`
  - Separate from API config to avoid credential exposure

- **`config_email.py`** - Email notification settings
  - SMTP configuration for Gmail or corporate servers
  - Toggle flags: `NOTIFY_ON_CHANGE`, `NOTIFY_DAILY_SUMMARY`

### DataTables API Specifics
The target API uses DataTables Server-side Processing format:
```python
# Required parameters in build_params() function:
params = {
    "draw": 2,              # DataTables counter
    "start": start,         # Pagination offset
    "length": length,       # Records per page (max 100)
    "columns[i][data]": i   # Column definitions (13 columns total)
}
```
This 13-column structure is hardcoded in `fetch_data.py:build_params()` - change only if API schema changes.

## Common Tasks & Workflows

### Adding New Fields to Collected Data
1. The API returns records as lists (not dictionaries) due to DataTables format
2. To add field mapping, update `fetch_data.py:fetch_all_data()` before `all_data.append()`
3. Also update `compare_data.py` tuple-based comparison logic if needed

### Debugging Authentication Issues
- **401 Errors**: Cookie expired, re-run `auto_login_selenium.py` or use `extract_browser_cookie.py`
- **SSL Certificate Errors**: `verify=False` in `requests.get()` is intentional for self-signed certs
- **Selenium timeouts**: Check `LOGIN_URL`, username/password in `config_auto.py`

### Scheduling with Task Scheduler (Windows)
- `run_auto.bat` encapsulates full workflow with error handling
- Must activate venv in batch: `call venv\Scripts\activate.bat`
- Log output to `logs/run_history.log` for debugging

### Testing Locally
```powershell
# Activate venv
.\venv\Scripts\activate

# Test cookie extraction
python auto_login_selenium.py

# Test API fetch
python fetch_data.py

# Test comparison
python compare_data.py
```

## Code Conventions

### Function Documentation Pattern
Every function includes docstring with "Tham số" (Parameters), "Trả về" (Returns), and Vietnamese comments:
```python
def build_params(start, length):
    """
    Xây dựng parameters cho API request
    Tham số: start (int), length (int)
    Trả về: dict
    """
```
Maintain this bilingual style (Python code + Vietnamese comments) for consistency.

### Error Handling Pattern
- Silent failures with return `None`: `load_json_file()`, `login_and_get_cookies()`
- Always check returns before using: `if not data: return`
- Print user-friendly emoji messages for CLI feedback (✅, ❌, 🔄)

### File I/O Pattern
- JSON files always read/write with `encoding="utf-8"`
- Data structure: `{"data": [[...], [...]], "fetch_time": "..."}`
- Paths use `os.path.join(OUTPUT_DIR, filename)` for cross-platform compatibility

## External Dependencies

### Critical Libraries
- `requests`: HTTP client with SSL ignore capability (`urllib3.disable_warnings()`)
- `selenium`: Browser automation with `webdriver-manager` for auto ChromeDriver download
- `browser-cookie3`: Cookie extraction from system browsers

### SSL Certificate Handling
The target API (`34.64.189.31`) uses self-signed certificate. All requests intentionally set:
```python
response = requests.get(url, verify=False, timeout=30)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```
This is not a security vulnerability - it's a workaround for internal/dev APIs.

## File Organization
- `logs/` - Task Scheduler history (created dynamically)
- `data/` - JSON outputs
  - `clone_list_sample.json` - Baseline for comparison
  - `clone_list_latest.json` - Most recent fetch
- Root scripts are runnable: `python fetch_data.py` from project root

## Important Edge Cases

1. **Empty JSON Files**: `load_json_file()` returns `None` if file doesn't exist - handle explicitly
2. **Data Comparison Logic**: Uses set operations on tuples - works only if records are hashable lists
3. **Pagination Loop**: Never updates `start` parameter when `total_records` changes mid-fetch
4. **Email Attachments**: Not implemented - only HTML body supported

## Documentation Structure
- `INDEX.md` - Entry point with links to all guides
- `README.md` - Detailed 300+ line tutorial on authentication concepts
- `AUTO_COOKIE.md` - Comparison of three cookie methods
- `EXERCISES.md` - Hands-on learning exercises
- All docs include Vietnamese + English with emojis for visual learning
