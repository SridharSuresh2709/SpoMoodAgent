import base64
from urllib.parse import urlencode
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

CLIENT_ID = input("Enter your SPOTIFY_CLIENT_ID: ").strip()
CLIENT_SECRET = input("Enter your SPOTIFY_CLIENT_SECRET: ").strip()

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "playlist-read-private playlist-read-collaborative"

# Step 1: Generate Authorization URL
auth_url = "https://accounts.spotify.com/authorize?" + urlencode({
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPES
})

print("\n👉 OPEN THIS URL IN YOUR BROWSER:")
print(auth_url)
print("\nThen click 'Agree' when Spotify asks for permissions.\n")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if "code=" not in self.path:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing code in callback.")
            return

        code = self.path.split("code=")[-1]

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"You can close this window now. Token is being generated...")

        print("\nAuthorization code received!")
        print("Exchanging code for refresh token...\n")

        # Step 2: Exchange code for refresh token
        token_url = "https://accounts.spotify.com/api/token"
        auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        }

        r = requests.post(token_url, headers=headers, data=data)
        print("Response:\n", r.json())

        refresh_token = r.json().get("refresh_token")
        if refresh_token:
            print("\n🎉 Your SPOTIFY_REFRESH_TOKEN:\n")
            print(refresh_token)
            print("\nSave this in your .env file!")
        else:
            print("\n❌ Failed to get refresh token. Check your Redirect URI and Scopes.")

        import os
        os._exit(0)  # Stop server immediately


print("Starting local server on http://127.0.0.1:8888/callback...")
server = HTTPServer(("127.0.0.1", 8888), Handler)
server.serve_forever()
