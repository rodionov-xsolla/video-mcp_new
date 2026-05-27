#!/usr/bin/env python3
"""
One-time OAuth flow to get a YouTube refresh token.

Usage:
  pip install google-auth-oauthlib
  python3 queue/youtube-auth.py

Prerequisites:
  1. Go to Google Cloud Console → august-jigsaw-497612-b1
  2. APIs & Services → Enable "YouTube Data API v3"
  3. APIs & Services → Credentials → Create OAuth 2.0 Client ID
     - Type: Desktop application
     - Download JSON → save as queue/oauth-client.json

After running this script, paste the printed YOUTUBE_REFRESH_TOKEN into video-agent/.env
"""

import json
import os
import sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("ERROR: missing dependency. Run: pip install google-auth-oauthlib")
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), "oauth-client.json")

if not os.path.exists(CLIENT_SECRETS):
    print(f"ERROR: {CLIENT_SECRETS} not found.")
    print("Download OAuth 2.0 client JSON from Google Cloud Console and save it there.")
    sys.exit(1)

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
creds = flow.run_local_server(port=0)

print("\n=== Copy these into video-agent/.env ===\n")
print(f"YOUTUBE_CLIENT_ID={creds.client_id}")
print(f"YOUTUBE_CLIENT_SECRET={creds.client_secret}")
print(f"YOUTUBE_REFRESH_TOKEN={creds.refresh_token}")
print("\n========================================\n")
