import os
import requests
import json
import csv
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(".env")

# Configuration
BASE_URL = os.getenv("QUALYS_BASE_URL")
USERNAME = os.getenv("QUALYS_USERNAME")
PASSWORD = os.getenv("QUALYS_PASSWORD")
CONFIG_FILE = os.getenv("SCAN_CONFIG_FILE_PATH")

AUTH_URL = f"{BASE_URL}/auth"
SCAN_URL = f"{BASE_URL}/tai/api/1.0/scan/launch"



def get_auth_token():
    """
    Authenticate and return bearer token.
    """

    auth_response = requests.post(
        AUTH_URL,
        data={
            "username": USERNAME,
            "password": PASSWORD
        },
        timeout=30
    )

    auth_response.raise_for_status()

    token = auth_response.text.strip()

    if not token:
        raise Exception("Authentication returned empty token")

    return token


def build_payload(scan):
    """
    Build API payload dynamically from config row.
    """

    payload = {
        "name": scan["name"].strip(),
        "targetModelId": int(scan["targetModelId"])
    }

    if scan.get("optionProfileId", "").strip():
        payload["optionProfileId"] = int(
            scan["optionProfileId"]
        )

    if scan.get("scannerType", "").strip():
        payload["scannerType"] = scan["scannerType"].strip()

    if scan.get("selectedScannerAppliance", "").strip():
        payload["selectedScannerAppliance"] = int(
            scan["selectedScannerAppliance"]
        )

    if scan.get("selectedScannerTags", "").strip():

        payload["selectedScannerTags"] = [
            {
                "id": int(tag.strip())
            }
            for tag in scan["selectedScannerTags"].split("|")
        ]

    return payload


def launch_scan():
    """
    Launch scans for all rows in config file.
    Returns True if the run completed without a fatal error,
    False otherwise (used to set the process exit code for cron).
    """

    try:

        print(
            f"\n[{datetime.now()}] "
            f"Starting scan run..."
        )

        token = get_auth_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        with open(CONFIG_FILE, newline="") as file:

            reader = csv.DictReader(file)
            print(reader.fieldnames)

            for scan in reader:
                if not scan["targetModelId"].strip():
                    continue

                payload = build_payload(scan)

                model_id = payload["targetModelId"]

                print(
                    f"\nLaunching scan:"
                    f" {payload['name']}"
                    f" (Model {model_id})"
                )

                response = requests.post(
                    SCAN_URL,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                print(
                    f"HTTP Status: {response.status_code}"
                )

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                try:

                    response_json = response.json()

                    filename = (
                        f"scan_{model_id}_"
                        f"{timestamp}.json"
                    )

                    with open(filename, "w") as f:
                        json.dump(
                            response_json,
                            f,
                            indent=4
                        )

                    print(
                        f"Response saved to "
                        f"{filename}"
                    )

                except ValueError:

                    filename = (
                        f"scan_{model_id}_"
                        f"{timestamp}.txt"
                    )

                    with open(filename, "w") as f:
                        f.write(response.text)

                    print(
                        f"Non-JSON response saved to "
                        f"{filename}"
                    )

        print(f"\n[{datetime.now()}] Scan run completed.")
        return True

    except requests.exceptions.RequestException as e:

        print(
            f"[{datetime.now()}] "
            f"Request failed: {e}"
        )
        return False

    except Exception as e:

        print(
            f"[{datetime.now()}] "
            f"Unexpected error: {e}"
        )
        return False


if __name__ == "__main__":
    success = launch_scan()
    sys.exit(0 if success else 1)