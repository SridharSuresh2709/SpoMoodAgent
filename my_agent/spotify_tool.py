# my_agent/spotify_tool.py
"""
spotify_tool.py

Provides SpotifySearchTool, an ADK-style tool wrapper that:
- Retrieves an OAuth access token using a stored refresh token
- Searches Spotify for playlists matching a mood
- Fetches top tracks from chosen playlist
- Returns top 5 tracks as recommendations

This file is written to be importable by an ADK Agent or used directly.
"""

import base64
import os
import time
from typing import Dict, List, Any, Optional

import requests

# Constants for Spotify
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"
SPOTIFY_PLAYLIST_TRACKS_URL = "https://api.spotify.com/v1/playlists/{playlist_id}/tracks"


class SpotifyAuthError(Exception):
    pass


class SpotifySearchError(Exception):
    pass


class SpotifySearchTool:
    """
    A minimal tool wrapper to be used by an ADK Agent.
    The Agent can call spotify_tool.search_by_mood(mood).
    """

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None,
                 refresh_token: Optional[str] = None, token_cache_seconds: int = 300):
        """
        Initialize tool with credentials (can be None; we'll read from env if so).
        token_cache_seconds: caches access token for this many seconds (reduce requests).
        """
        self.client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")
        self.refresh_token = refresh_token or os.getenv("SPOTIFY_REFRESH_TOKEN")
        self._access_token = None
        self._token_expires_at = 0
        self.token_cache_seconds = token_cache_seconds

    def _refresh_access_token(self) -> str:
        """
        Exchange refresh token for an access token using Spotify's OAuth endpoint.
        Uses HTTP Basic auth with client_id:client_secret.
        Raises SpotifyAuthError on failure.
        """
        if not (self.client_id and self.client_secret and self.refresh_token):
            raise SpotifyAuthError("Spotify client ID / secret / refresh token not provided.")

        # If cached and not expired, return cached
        now = time.time()
        if self._access_token and now < self._token_expires_at:
            return self._access_token

        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}

        r = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data, timeout=10)
        # Add debug logging
        #print("\n===== DEBUG: SPOTIFY TOKEN RESPONSE =====")
        #print("STATUS:", r.status_code)
        #print("BODY:", r.text)
        if r.status_code != 200:
            raise SpotifyAuthError(f"Failed to refresh token: {r.status_code} {r.text}")

        token_response = r.json()
        access_token = token_response.get("access_token")
        expires_in = token_response.get("expires_in", 3600)

        if not access_token:
            raise SpotifyAuthError(f"Refresh response missing access_token: {token_response}")

        # cache token
        self._access_token = access_token
        self._token_expires_at = now + min(expires_in, self.token_cache_seconds)
        return access_token

    def _call_spotify(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Helper that ensures a valid access token and calls Spotify API.
        """
        token = self._refresh_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(url, headers=headers, params=params, timeout=10)
        #print("\n===== DEBUG: SPOTIFY GET RESPONSE =====")
        #print("URL:", r.url)
        #print("STATUS:", r.status_code)
        #print("BODY:", r.text[:500], "...")   # avoid huge output
        #print("========================================\n")

        # Basic rate-limit and error handling
        if r.status_code == 429:
            # Rate limited
            retry_after = int(r.headers.get("Retry-After", "1"))
            raise SpotifySearchError(f"Rate limited by Spotify. Retry after {retry_after} seconds.")
        if r.status_code >= 400:
            raise SpotifySearchError(f"Spotify API error: {r.status_code} - {r.text}")
        return r.json()

    def search_playlists(self, mood: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search Spotify for playlists matching the mood string.
        Returns a list of playlist objects (as returned by Spotify).
        """
        if not mood or not mood.strip():
            raise ValueError("Invalid mood value (empty).")

        q = f"{mood} playlist"
        params = {"q": q, "type": "playlist", "limit": limit}
        resp = self._call_spotify(SPOTIFY_SEARCH_URL, params=params)
        #print("\n===== DEBUG: RAW SPOTIFY SEARCH RESPONSE =====")
        #print(resp)
        #print("==============================================\n")

        playlists = resp.get("playlists", {}).get("items", [])

        # 🚀 FIX: Remove None values returned by Spotify
        playlists = [p for p in playlists if p is not None]

        return playlists

    def get_playlist_top_tracks(self, playlist_id: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Given playlist_id, fetch its tracks and return top_n tracks simplified list:
        Each item: {name, artists (comma string), preview_url, track_url}
        """
        url = SPOTIFY_PLAYLIST_TRACKS_URL.format(playlist_id=playlist_id)
        params = {"limit": 50}
        resp = self._call_spotify(url, params=params)
        items = resp.get("items", [])

        tracks = []
        for it in items:
            track = it.get("track")
            if not track:
                continue
            name = track.get("name")
            artists = ", ".join([a.get("name", "") for a in track.get("artists", [])])
            preview_url = track.get("preview_url")
            external_urls = track.get("external_urls", {}).get("spotify")
            tracks.append({
                "name": name,
                "artists": artists,
                "preview_url": preview_url,
                "track_url": external_urls
            })
            if len(tracks) >= top_n:
                break
        return tracks

    def choose_best_playlist(self, playlists: List[Dict[str, Any]], mood: str) -> Optional[Dict[str, Any]]:
        """
        A simple heuristic to choose the best playlist:
        - prefer playlists with mood keyword in name/description
        - prefer playlists with higher follower_count (if available)
        """
        if not playlists:
            return None

        mood_lower = mood.lower()
        scored = []
        for p in playlists:
            score = 0
            name = p.get("name", "").lower()
            desc = p.get("description", "").lower()
            # keyword match
            if mood_lower in name:
                score += 50
            if mood_lower in desc:
                score += 30
            # follower_count is nested under 'followers' sometimes not available in search results
            followers = p.get("followers", {}).get("total", 0)
            score += min(followers // 1000, 20)  # add up to 20 points
            scored.append((score, p))

        # sort desc by score
        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][1]
        return best

    def search_by_mood(self, mood: str, playlists_limit: int = 10, top_n: int = 5) -> Dict[str, Any]:
        """
        Primary method agent should call:
        Input: mood string
        Output: dict containing selected playlist metadata + recommended tracks
        """
        # validate
        if not mood or not mood.strip():
            raise ValueError("Mood cannot be empty.")

        # 1) search playlists
        playlists = self.search_playlists(mood, limit=playlists_limit)
        if not playlists:
            raise SpotifySearchError(f"No playlists found for mood '{mood}'.")

        # 2) choose best playlist
        best = self.choose_best_playlist(playlists, mood)
        if not best:
            best = playlists[0]  # fallback

        playlist_id = best.get("id")
        playlist_info = {
            "id": playlist_id,
            "name": best.get("name"),
            "description": best.get("description"),
            "external_url": best.get("external_urls", {}).get("spotify"),
            "owner": best.get("owner", {}).get("display_name")
        }

        # 3) fetch top tracks
        tracks = self.get_playlist_top_tracks(playlist_id, top_n=top_n)

        return {"playlist": playlist_info, "tracks": tracks}
