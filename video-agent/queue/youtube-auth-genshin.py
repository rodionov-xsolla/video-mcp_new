#!/usr/bin/env python3
"""
One-time OAuth flow for genshin_snap YouTube channel.
Gets refresh token + channel ID, prints lines to add to .env

Usage: python3 queue/youtube-auth-genshin.py
"""

import http.server
import json
import os
import subprocess
import sys
import threading
import urllib.parse
import urllib.request

CLIENT_ID = "610183785624-jg6iutd41i7hi9tn9qc437ijo5unk8f5.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8080"
SCOPE = "https://www.googleapis.com/auth/youtube"

captured_code = None
server_done = threading.Event()


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global captured_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            captured_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Done! Return to terminal.</h1>")
            server_done.set()
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No code received.")

    def log_message(self, *args):
        pass


auth_params = urllib.parse.urlencode({
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": SCOPE,
    "access_type": "offline",
    "prompt": "consent",
})
auth_url = f"https://accounts.google.com/o/oauth2/auth?{auth_params}"

print("Opening browser for Google OAuth...")
print(f"\nIf browser doesn't open, go to:\n{auth_url}\n")
subprocess.run(["open", auth_url])

server = http.server.HTTPServer(("localhost", 8080), Handler)
t = threading.Thread(target=server.serve_forever)
t.daemon = True
t.start()

print("Waiting for authorization...")
server_done.wait(timeout=120)
server.shutdown()

if not captured_code:
    print("ERROR: No code received within 2 minutes.")
    sys.exit(1)

# Exchange code for tokens
data = urllib.parse.urlencode({
    "code": captured_code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code",
}).encode()

req = urllib.request.Request(
    "https://oauth2.googleapis.com/token",
    data=data,
    method="POST",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)

ctx = __import__("ssl").create_default_context()
ctx.check_hostname = False
ctx.verify_mode = __import__("ssl").CERT_NONE

try:
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx) as resp:
        tokens = json.loads(resp.read())
except Exception as e:
    print(f"ERROR exchanging code: {e}")
    sys.exit(1)

if "refresh_token" not in tokens:
    print(f"ERROR: no refresh_token in response: {tokens}")
    sys.exit(1)

refresh_token = tokens["refresh_token"]
access_token = tokens["access_token"]

# Get channel info
channel_req = urllib.request.Request(
    "https://www.googleapis.com/youtube/v3/channels?part=id,snippet&mine=true",
    headers={"Authorization": f"Bearer {access_token}"},
)
try:
    with urllib.request.urlopen(channel_req, context=ctx) as resp:
        ch_data = json.loads(resp.read())
        items = ch_data.get("items", [])
        channel_id = items[0]["id"] if items else "UNKNOWN"
        channel_title = items[0]["snippet"]["title"] if items else "UNKNOWN"
except Exception as e:
    channel_id = "UNKNOWN"
    channel_title = "UNKNOWN"
    print(f"Warning: could not fetch channel info: {e}")

print("\n=== Add to video-agent/.env ===\n")
print(f"# {channel_title} ({channel_id})")
print(f"YOUTUBE_REFRESH_TOKEN_GENSHINSNAP={refresh_token}")
print(f"YOUTUBE_CHANNEL_ID_GENSHINSNAP={channel_id}")
print("\n================================\n")
