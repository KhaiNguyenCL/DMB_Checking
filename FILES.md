# Device Monitoring System - Files

## Core Files (DO NOT DELETE)

### Main Scripts
- `monitor_devices.py` - Main monitoring script
- `fetch_data.py` - Data fetching from API
- `auto_login_selenium.py` - Auto-login to get session cookie
- `send_bitrix_notification.py` - Bitrix24 notification module

### Configuration Files  
- `config.py` - API configuration and cookie
- `config_auto.py` - Auto-login credentials
- `config_bitrix.py` - Bitrix24 webhook and chat settings

### Automation Scripts
- `start_monitor.bat` - **Main entry point** - Auto-start monitoring
- `setup_venv.bat` - Setup Python virtual environment

### Data Files
- `data/clone_list_latest.json` - Latest device data from API
- `data/device_states.json` - State tracking for change detection
- `data/Exception_list.txt` - Blacklist of device IDs to exclude
- `logs/monitor_history.log` - Complete monitoring log history

## Helper Files (Optional)

- `cookies.json` - Browser cookies backup
- `requirements.txt` - Python dependencies list
- `README.md` - Project documentation

## Directories

- `venv/` - Python virtual environment (auto-generated)
- `data/` - Data storage
- `logs/` - Log files
- `bitrix-api-test/` - Old Bitrix PHP testing files (can delete if not needed)

## Deleted Files (Old/Unused)

These files were removed as they're no longer needed:
- `send_email_notification.py` - Old email notification system
- `config_email.py` - Email configuration (replaced by Bitrix)
- `compare_data.py` - Manual comparison tool (integrated into monitor)
- `filter_devices.py` - Standalone filter (integrated into monitor)
- Various test/helper scripts for Bitrix development

## Usage

**To start monitoring:**
```batch
start_monitor.bat
```

This will automatically:
1. Activate venv
2. Login to get fresh cookie
3. Start monitoring with Bitrix notifications
