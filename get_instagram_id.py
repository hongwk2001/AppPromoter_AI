import os
import requests

# Quick env loader
env = {}
if os.path.exists('.env'):
  with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
      trimmed = line.strip()
      if trimmed and not trimmed.startswith('#'):
        key, *parts = trimmed.split('=')
        if key:
          env[key.strip()] = '='.join(parts).strip()

token = env.get("INSTAGRAM_ACCESS_TOKEN")

if not token:
  print("Error: Please add 'INSTAGRAM_ACCESS_TOKEN=your_token_here' to your .env file first.")
  exit(1)

print("Fetching linked Facebook Pages...")
#url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={token}"
url = f"https://graph.facebook.com/v25.0/me/accounts?access_token={token}"
res = requests.get(url).json()

if "error" in res:
  print("API Error:", res["error"]["message"])
  exit(1)

pages = res.get("data", [])
if not pages:
  print("No Facebook Pages found. Make sure your Facebook profile has a Page and it is linked to your Instagram professional account.")
  exit(1)

for page in pages:
  page_id = page["id"]
  page_name = page["name"]
  print(f"\nChecking Page: '{page_name}' (ID: {page_id})...")
  
  # Fetch linked Instagram Business Account ID
  details_url = f"https://graph.facebook.com/v25.0/{page_id}?fields=instagram_business_account&access_token={token}"
  details = requests.get(details_url).json()
  
  insta_acc = details.get("instagram_business_account")
  if insta_acc:
    print(f"--> Found linked Instagram Business Account ID: {insta_acc['id']}")
    print(f"Please add this to your .env file:")
    print(f"INSTAGRAM_ACCOUNT_ID={insta_acc['id']}")
  else:
    print("--> No Instagram business account linked to this Facebook Page.")
