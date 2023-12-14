import requests
import json
import sys
from datetime import datetime
import re

# Global variables
CLIENT_ID="ClientId" # Client ID from Frontegg Portal ➜ [ENVIRONMENT] ➜ Settings page
API_TOKEN ="APIToken" # API Key from Frontegg Portal ➜ [ENVIRONMENT] ➜ Settings page
TENANT_ID = "TENANT_ID"
ROLE_ID = "ROLE_ID"
REGION = "EU"

if REGION == "US":
    API_URL = "https://api.us.frontegg.com"
elif REGION == "EU":
    API_URL = "https://api.frontegg.com"
elif REGION == "AP":
    API_URL = "https://api.ap.frontegg.com"
else:
    raise ValueError(f"REGION = {REGION} is invalid! change to EU | US | AP\n")

DEFAULT_HEADERS = {"accept": "application/json", "content-type": "application/json"}

# Utility functions
def log_to_execution_file(message):
    with open(EXECUTION_LOG_FILE, "a") as execution_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execution_file.write(f"{timestamp} - {message}\n")

def call_api(method, url, payload, headers):
    log_message = f"* New request:\n{'-' * 100}\nmethod: {method}\nurl: {url}\npayload: {payload}\nheaders: {headers}\n{'-' * 100}\n"
    log_to_execution_file(log_message)

    res = requests.request(method, url, headers=headers, data=payload)

    try:
        json_data = res.json()
        log_message = f"Response:\n{res.text}\n"
        log_to_execution_file(log_message)
        return json_data
    except json.JSONDecodeError as e:
        log_message = f"No response, or error decoding response as JSON:\n{e}"
        log_to_execution_file(log_message)
        return None

def get_vendor_jwt():
    res = call_api(
        "POST",
        API_URL + "/auth/vendor/",
        json.dumps({"clientId": CLIENT_ID, "secret": API_TOKEN}),
        DEFAULT_HEADERS,
    )
    returned_jwt = res.get("token")
    return returned_jwt

def get_users_with_pagination():
    res = call_api(
        "GET",
        API_URL + "/identity/resources/users/v3?includeSubTenants=true&_limit=200",
        {},
        {"authorization": "Bearer " + bearer_token},
    )

    next = res.get("_links").get("next")
    items_arr = res.get("items")

    while next != "":
        log_to_execution_file("Getting next page! " + next)

        # Extract the _offset value from next using regular expression
        offset_match = re.search(r'_offset=(\d+)', next)
        if offset_match:
            offset_value = offset_match.group(1)
            url = API_URL + f"/identity/resources/users/v3?includeSubTenants=true&_limit=200&_offset={offset_value}"

            next_page_res = call_api(
                "GET",
                url,
                {},
                {"authorization": "Bearer " + bearer_token},
            )

            page_items_arr = next_page_res.get("items")
            items_arr = items_arr + page_items_arr
            next = next_page_res.get("_links").get("next")
        else:
            log_to_execution_file("Could not extract offset value from next.")
            break

    result = {"count": len(items_arr), "items": items_arr}

    return result

# Global variable for execution log file
EXECUTION_LOG_FILE = "execution.log"

# Redirect standard output and error to the execution log file
sys.stdout = open(EXECUTION_LOG_FILE, "a")
sys.stderr = open(EXECUTION_LOG_FILE, "a")

# Run script
bearer_token = get_vendor_jwt()
users_result = get_users_with_pagination()

# Write results to user log file
with open("result.log", "w") as file:
    file.write(json.dumps(users_result, indent=4))
    file.write(f"\n\nFinal result:\n\n{users_result}\n")

# Close the redirected standard output and error
sys.stdout.close()
sys.stderr.close()
