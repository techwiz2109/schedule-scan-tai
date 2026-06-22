# Qualys AI Scan Launcher

A Python script that reads scan configurations from a CSV file and automatically launches scans via the Qualys TotalAI API. Credentials are stored securely in a `.env` file. Designed to be scheduled via **cron** (Linux/macOS) or **Task Scheduler** (Windows).

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installing Python](#installing-python)
- [Project Setup](#project-setup)
- [Installing Dependencies](#installing-dependencies)
- [Configuration](#configuration)
  - [Environment Variables (.env)](#environment-variables-env)
  - [Scan Config File (scan_config.txt)](#scan-config-file-scan_configtxt)
- [Running the Script](#running-the-script)
- [Scheduling](#scheduling)
  - [Linux / macOS (cron)](#linux--macos-cron)
  - [Windows (Task Scheduler)](#windows-task-scheduler)
- [Output Files](#output-files)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.8 or higher
- `pip3` (Python package manager)
- A Qualys account with API access
- Network access to your Qualys gateway URL

---

## Installing Python

### Ubuntu / Debian

Check if Python is already installed:

```bash
python3 --version
```

If not installed, run:

```bash
sudo apt update
sudo apt install python3 python3-pip -y
```

Verify:

```bash
python3 --version
pip3 --version
```

### macOS

macOS usually comes with Python 3. Verify with:

```bash
python3 --version
```

If not installed, install via Homebrew:

```bash
brew install python3
```

### Windows

Download the installer from https://www.python.org/downloads/

During installation, make sure to check **"Add Python to PATH"** before clicking Install.

Verify in Command Prompt:

```cmd
python --version
pip --version
```

---

## Project Setup

Create a folder for the project and place all files inside it:

```bash
mkdir qualys-scan-launcher
cd qualys-scan-launcher
```

Your project folder should look like this:

```
qualys-scan-launcher/
├── launch-scan.py
├── scan_config.csv
├── .env
├── requirements.txt
└── .gitignore
```

---

## Installing Dependencies

The script requires `requests` and `python-dotenv`.

### Standard install

```bash
pip3 install requests python-dotenv
```

### Install from requirements.txt

```bash
pip3 install -r requirements.txt
```

---

## Configuration

### Environment Variables (.env)

Create a `.env` file in the same directory as the script to store your Qualys credentials and config path securely:

```bash
vim /home/ubuntu/.env
```

Add the following, replacing values with your actual details:

```
QUALYS_USERNAME=<YOUR_QUALYS_USERNAME>
QUALYS_PASSWORD=<YOUR_QUALYS_PASSWORD>
QUALYS_BASE_URL=<YOUR_QUALYS_BASE_URL>
SCAN_CONFIG_FILE_PATH=<YOUR_SCAN_CONFIG_FILE_PATH>
```
Save and exit

---

### Scan Config File (scan_config.csv)

This is a CSV file that defines which scans to launch. Each row is one scan.

The path to this file is set via `SCAN_CONFIG_FILE_PATH` in your `.env` file.

**Create the file:**

```bash
nano /home/ubuntu/scan_config.csv
```

**File format:**

```
name,targetModelId,optionProfileId,scannerType,selectedScannerAppliance,selectedScannerTags
```

| Column | Required | Description |
|--------|----------|-------------|
| `name` | Yes | Display name of the scan |
| `targetModelId` | Yes | ID of the AI model to scan |
| `optionProfileId` | No | Option profile ID (leave blank for default) |
| `scannerType` | No | `EXTERNAL` or `INTERNAL` (leave blank for default) |
| `selectedScannerAppliance` | No | Specific scanner appliance ID (used with `INTERNAL`) |
| `selectedScannerTags` | No | Scanner tag IDs, use `\|` to separate multiple tags |

> **Important:** Leave unused columns blank but keep all commas. Every row must have all 6 columns.

---

**Examples for each scan type:**

#### 1. Default option profile and scanner (mandatory fields only)

```
name,targetModelId,optionProfileId,scannerType,selectedScannerAppliance,selectedScannerTags
Scan - Default,80791371,,,,
```

#### 2. Custom option profile with external scanner

```
name,targetModelId,optionProfileId,scannerType,selectedScannerAppliance,selectedScannerTags
Scan - External,80791371,7868565,EXTERNAL,,
```

#### 3. Internal scanner with specific appliance

```
name,targetModelId,optionProfileId,scannerType,selectedScannerAppliance,selectedScannerTags
Scan - Internal,80791371,,INTERNAL,61636497,
```

#### 4. Scanner tags (single tag)

```
name,targetModelId,optionProfileId,scannerType,selectedScannerAppliance,selectedScannerTags
Scan - Tag,81146985,,,,146114424
```

#### 5. Scanner tags (multiple tags, separated by `|`)

```
name,targetModelId,optionProfileId,scannerType,selectedScannerAppliance,selectedScannerTags
Scan - Multi Tag,81146985,,,,146114424|146114425|146114426
```

#### 6. Mixed scans in one file

```
name,targetModelId,optionProfileId,scannerType,selectedScannerAppliance,selectedScannerTags
Scan - test_russ1,759,,,,
Scan - test_russ2,78,783241,EXTERNAL,,
Scan - test_russ3,81146985,,,,146114424|146114425
```

---

## Running the Script

From inside the project folder:

```bash
python3 /home/ubuntu/launch-scan.py
```

You will see output like this in your terminal:

```
[2026-06-22 12:55:00] Starting scan run...
['name', 'targetModelId', 'optionProfileId', 'scannerType', 'selectedScannerAppliance', 'selectedScannerTags']

Launching scan: Scan - test_russ1 (Model 759)
HTTP Status: 200
Response saved to scan_759_20260622_125500.json

Launching scan: Scan - test_russ2 (Model 78)
HTTP Status: 200
Response saved to scan_78_20260622_125501.json

[2026-06-22 12:55:02] Scan run completed.
```

---

## Scheduling

### Linux / macOS (cron)

**Find your Python path:**

```bash
which python3
```

**Open the crontab editor:**

```bash
crontab -e
```

**Add this line at the bottom:**

```
33 7 * * * /usr/bin/python3 /home/ubuntu/launch-scan.py >> /home/ubuntu/scan.log 2>&1
```

- `>> /home/ubuntu/scan.log` — appends all output to a log file
- `2>&1` — also writes errors to the same log file

**If using a virtual environment:**

```
33 7 * * * /home/ubuntu/venv/bin/python3 /home/ubuntu/launch-scan.py >> /home/ubuntu/scan.log 2>&1
```

**Verify the cron job was saved:**

```bash
crontab -l
```

**Check the log after the job runs:**

```bash
cat /home/ubuntu/scan.log
```

**Watch the log live as it runs:**

```bash
tail -f /home/ubuntu/scan.log
```

**Check server time:**

```bash
date
```

**Cron time format:**

```
33  7  *  *  *
│   │  │  │  │
│   │  │  │  └── Day of week  (* = every day)
│   │  │  └───── Month        (* = every month)
│   │  └──────── Day of month (* = every day)
│   └──────────── Hour        (0-23)
└──────────────── Minute      (0-59)
```

**Common schedule examples:**

| IST Time | UTC Time | Cron Expression |
|----------|----------|-----------------|
| 12:00 PM | 06:30 AM | `30 6 * * *` |
| 1:03 PM  | 07:33 AM | `33 7 * * *` |
| 6:00 PM  | 12:30 PM | `30 12 * * *` |
| 11:30 PM | 06:00 PM | `0 18 * * *` |

---

### Windows (Task Scheduler)

Open Command Prompt as Administrator:

```cmd
schtasks /create /tn "QualysScanLauncher" /tr "python C:\path\to\launch-scan.py" /sc daily /st 12:55
```

Or wrap in a `.bat` file to capture logs:

```bat
@echo off
python C:\path\to\qualys-scan-launcher\launch-scan.py >> C:\path\to\qualys-scan-launcher\scan.log 2>&1
```

Then point the task at the `.bat` file:

```cmd
schtasks /create /tn "QualysScanLauncher" /tr "C:\path\to\run_scan.bat" /sc daily /st 12:55
```

---

## Output Files

Each scan launch saves a response file in the directory where the script is run, named:

```
scan_{targetModelId}_{YYYYMMDD_HHMMSS}.json     ← if Qualys returns valid JSON
scan_{targetModelId}_{YYYYMMDD_HHMMSS}.txt      ← if Qualys returns plain text
```

Example:

```
scan_80791371_20260622_125500.json
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'requests'` or `No module named 'dotenv'`**
```bash
pip3 install requests python-dotenv --break-system-packages
```

**`Missing required environment variables in .env file`**
Make sure `.env` exists and contains all four variables:
```
QUALYS_BASE_URL
QUALYS_USERNAME
QUALYS_PASSWORD
SCAN_CONFIG_FILE_PATH
```

**`FileNotFoundError: scan_config.csv`**
Check that `SCAN_CONFIG_FILE_PATH` in your `.env` file points to the correct absolute path, e.g. `/home/ubuntu/scan_config.csv` (not a typo like `/home/ubunut/`).

**Cron job not running / log file not created**
- Verify cron is running: `sudo systemctl status cron`
- Check your crontab: `crontab -l`
- Make sure you used absolute paths in the crontab entry
- Make sure the hour is valid (0–23), e.g. `7` not `50`
- Check server time vs your local time: `date`

**`bad hour` error when saving crontab**
The hour field must be between `0` and `23`. For IST users, always convert to UTC first.

**Script runs but no scan launched**
Check the saved `.json` response file for the error message returned by the Qualys API — it will describe exactly what went wrong (invalid token, wrong model ID, etc.).
