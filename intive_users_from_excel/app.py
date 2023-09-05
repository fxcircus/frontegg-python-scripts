import pandas as pd
import requests
import time

file_path = 'emails.xlsx'
vendor_token = 'vendor_token'
tenant_id = 'tenant_id'
role_id = 'role_id'

def send_email_requests(file_path, vendor_token, tenant_id, role_id):
    # Read the Excel file and extract the emails
    df = pd.read_excel(file_path)
    emails = df['Email'].tolist()  # Assuming the email column name is 'Email'
    names = df['Name'].tolist()    # Assuming the name column name is 'Name'

    for email, name in zip(emails, names):
        # Prepare the cURL request with the current email
        url = 'https://api.frontegg.com/identity/resources/users/v2'
        headers = {
            'accept': 'application/json',
            'authorization': 'Bearer ' + vendor_token,
            'content-type': 'application/json',
            'frontegg-tenant-id': tenant_id
        }
        data = {
            "email": email,
            "name": name,
            "provider": "local",
            "roleIds": [role_id],
            "skipInviteEmail": False
        }

        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"Email sent successfully for {name}")
        else:
            print(f"Failed to send email for {email}. Status code: {response}")
        
        time.sleep(3)


send_email_requests(file_path, vendor_token, tenant_id, role_id)