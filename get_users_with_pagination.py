import requests
import json

################################################################
#  Global variables
################################################################

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

DEFAULT_HEADERS = { "accept": "application/json", "content-type": "application/json" }

################################################################
#  Utility functions
################################################################

def call_api(method, url, payload, headers):
    print(f"""* New request:
    {'-' * 100}
    method: {method}
    url: {url}
    payload: {payload}
    headers: {headers}
    {'-' * 100}\n""")
    res = requests.request(method, url, headers=headers, data=payload)
    try:
        json_data = res.json()
        print(f"Response:\n{res.text}\n")
        return json_data
    except JSONDecodeError as e:
        print(f"No response, or error decoding response as JSON:\n{e}")
        return None

# Vendor authentication ➜ https://docs.frontegg.com/reference/authenticate_vendor
def get_vendor_jwt():
    res = call_api("POST",
                   API_URL + "/auth/vendor/",
                   json.dumps({"clientId": CLIENT_ID, "secret": API_TOKEN}),
                   DEFAULT_HEADERS)
    returned_jwt = res.get('token')
    return returned_jwt

# Get users V3 API endpoint ➜ https://docs.frontegg.com/reference/userscontrollerv3_getusers
def get_users_with_pagination():
    res = call_api("GET",
                   API_URL + "/identity/resources/users/v3?includeSubTenants=true&_limit=200",
                   {},
                #    {"authorization": "Bearer " + bearer_token, "frontegg-tenant-id": TENANT_ID}) # Pull users of specific tenant
                   {"authorization": "Bearer " + bearer_token}) # pull all users in the environment
    next = res.get('_links').get('next')
    items_arr = res.get('items')
    while next != '':
        print("Getting next page! " + next)
        url = API_URL + "/identity/resources/users/v3?includeSubTenants=true" + next
        next_page_res = call_api("GET",
                                 url,
                                 {},
                                 {"authorization": "Bearer " + bearer_token, "frontegg-tenant-id": TENANT_ID})
        page_items_arr = next_page_res.get('items')
        items_arr = items_arr + page_items_arr
        next = next_page_res.get('_links').get('next')
    return items_arr

################################################################
#  Run script
################################################################

bearer_token = get_vendor_jwt()
users_arr = get_users_with_pagination()

# write results to log file
with open("result.log", "w") as file:
    file.write(json.dumps(users_arr, indent=4))
    file.write(f"\n\nFinal result:\n\n{get_users_with_pagination}\n")

print("Users data and final result written to result.log!")
