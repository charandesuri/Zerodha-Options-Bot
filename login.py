from kiteconnect import KiteConnect
from config import API_KEY, API_SECRET
import webbrowser
import urllib.parse as urlparse
from urllib.parse import parse_qs
import os

kite = KiteConnect(api_key=API_KEY)

print("Opening login page...")
webbrowser.open(kite.login_url())

redirected_url = input("Paste FULL redirected URL:\n")

parsed = urlparse.urlparse(redirected_url)
request_token = parse_qs(parsed.query)["request_token"][0]

data = kite.generate_session(request_token, api_secret=API_SECRET)
access_token = data["access_token"]

with open("access_token.txt", "w") as f:
    f.write(access_token)

print("Access token saved successfully!")

# Auto start main.py
print("Starting trading bot...")
os.system("python main.py")