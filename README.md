# SpoMoodAgent
# Spotify Mood-Based Music Recommender Agent (ADK + Gemini + Spotify API)

This project is a beginner-friendly, production-ready music recommender agent that uses the Google ADK (Agent Developer Kit) with Gemini 1.5 Flash and the Spotify API. Users input a mood, and the agent intelligently recommends a playlist and songs from Spotify. This project is designed to be easily extensible into a more complex Personalized Memory Assistant System (PMAS).

## ✨ Features

*   **Natural Language Mood Understanding:** The agent understands various user moods like "happy," "sad," "romantic," "energetic," "calm," "angry," or "focus."
*   **Intelligent Spotify Search:** Utilizes a custom ADK tool to interact with the Spotify Search API, fetching relevant playlists and tracks.
*   **Best Playlist Selection:** The Gemini agent, powered by strong instructions, selects the most suitable playlist for the given mood.
*   **Top Song Recommendations:** Provides the top 5 songs from the chosen playlist.
*   **Robust Error Handling:** Catches common issues like invalid moods, API token problems, and rate limits.
*   **Automatic Spotify OAuth:** Handles the refresh token flow to ensure continuous API access without manual intervention.
