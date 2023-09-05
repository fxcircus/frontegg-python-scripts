import requests
import json
import subprocess 

CLIENT_ID="CLIENT_ID" # Client ID from Frontegg Portal ➜ [ENVIRONMENT] ➜ Settings page
API_TOKEN ="API_TOKEN" # API Key from Frontegg Portal ➜ [ENVIRONMENT] ➜ Settings page
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


def get_vendor_jwt():
    res = call_api("POST",
                   API_URL + "/auth/vendor/",
                   json.dumps({"clientId": CLIENT_ID, "secret": API_TOKEN}),
                   DEFAULT_HEADERS)
    returned_jwt = res.get('token')
    return returned_jwt


def get_users_with_pagination():
    res = call_api("GET",
                   API_URL + "/identity/resources/users/v3?includeSubTenants=true&_limit=200",
                   {},
                   {"authorization": "Bearer " + bearer_token, "frontegg-tenant-id": TENANT_ID})
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


def build_users_param(users_arr):
    ids = [user['id'] for user in users_arr]  # Extracting 'id' from each JSON
    id_params = ','.join(ids)  # Joining ids with commas
    return f"?ids={id_params}"


def get_roles_for_users(users_param):
    res = call_api("GET",
                   API_URL + "/identity/resources/users/v3/roles" + users_param,
                   {},
                   {"authorization": "Bearer " + bearer_token, "frontegg-tenant-id": TENANT_ID})
    return res


def filter_by_roles(user_roles_arr):
    filtered_array = []
    for user in user_roles_arr:
        if ROLE_ID in user['roleIds']:
            filtered_array.append(user)
    return filtered_array


def compare_and_compile_results(users_arr, filtered_results):
    filtered_users_with_email = []
    for res in filtered_results:
        for user in users_arr:
            if res['userId'] == user['id']:
                filtered_users_with_email.append(
                    {
                        'userId': user['id'],
                        'email': user['email'],
                        'tenantId': res['tenantId'],
                        'roleIds': res['roleIds']
                    }
                )
    return filtered_users_with_email


bearer_token = get_vendor_jwt()
users_arr = get_users_with_pagination()
users_param = build_users_param(users_arr)
user_roles_arr = get_roles_for_users(users_param)
filtered_results = filter_by_roles(user_roles_arr)
filtered_users_with_email = compare_and_compile_results(users_arr, filtered_results)

print(f"Final result:\n\n{filtered_users_with_email}")

# Convert the list to string and copy to clipboard
filtered_users_with_email_str = str(filtered_users_with_email)
subprocess.run("pbcopy", text=True, input=filtered_users_with_email_str)
print("\ncopied to clipboard!\n")