# my_agent/agent.py
"""
agent.py

Defines an ADK Agent that uses Gemini (via ADK python) and integrates the SpotifySearchTool.
- The agent's instruction is crafted to FORCE use of the spotify_search_tool for mood -> playlist selection.
- If ADK Agent tool integration is available, we register the tool. If not, we provide a helper to call the tool directly.
"""

import os
from typing import Any

# Import the ADK Agent class you already used in your project
# Keep the import path you showed in your snippet.
try:
    from google.adk.agents.llm_agent import Agent
except Exception as e:
    Agent = None  # We'll still provide local fallback behavior if ADK isn't loaded

from .spotify_tool import SpotifySearchTool, SpotifySearchError

# Create the tool instance (reads env by default)
spotify_tool = SpotifySearchTool()

# Root agent definition. We pick a Gemini flash model as requested (1.5/Flash).
# The exact model name can be modified per your ADK/Gemini availability.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

root_agent = None

# Build a clear instruction that forces the agent to use the tool for retrieving playlists.
AGENT_INSTRUCTION = """
You are a music recommendation assistant. When the user provides a mood (for example: happy, sad, romantic, energetic, calm, angry, focus),
you MUST use the provided tool named 'spotify_search_tool' to find appropriate playlists and tracks from Spotify.
Do NOT guess tracks — always consult the tool. After the tool returns the playlist and tracks, present a friendly, concise response
to the user with the top 5 recommended songs, artists, and a short reason why they fit the mood.
If the tool raises an error, handle it gracefully and inform the user with helpful debugging suggestions (check tokens, retry later).
"""

# Try to instantiate an ADK Agent (if google.adk is present)
if Agent is not None:
    try:
        # Many ADK agent constructors accept parameters like model, name, description, instruction and tools.
        # We attempt to follow that pattern. If your ADK requires different params, update accordingly.
        root_agent = Agent(
            model=MODEL_NAME,
            name="spotify_mood_agent",
            description="ADK agent for recommending Spotify playlists/tracks based on user mood.",
            instruction=AGENT_INSTRUCTION,
            # If your ADK accepts a tools argument, pass it. If not, this will be ignored by ADK or raise,
            # in which case we still provide the spotify_tool for manual calls.
            tools=[spotify_tool] if hasattr(Agent, "__call__") or True else None
        )
    except Exception as e:
        # If ADK-agent creation fails, set to None and fallback to direct usage
        root_agent = None
        # Do not raise — we'll fallback to calling spotify_tool directly in main.py.

def handle_mood_with_agent(mood: str) -> str:
    """
    Primary helper: intended to be used by main.py
    Prefer to ask ADK agent to orchestrate tool call (if agent supports tool usage).
    Fallback: call SpotifySearchTool directly.
    Returns a formatted user-facing string.
    """
    # 1) If ADK agent exists and supports a run/execute API that accepts tools invocation, try that.
    if root_agent:
        try:
            # Many ADK Agent APIs provide a `run()` or `respond()` method that accepts user text.
            # We'll attempt to call "run" (common pattern). If your ADK variant uses a different method,
            # replace this with your library's call (e.g., root_agent.call or root_agent.execute).
            user_prompt = f"User mood: {mood}\nAction: Use spotify_search_tool to find the best playlist and return top 5 tracks."
            if hasattr(root_agent, "run"):
                # Some ADK Agents may return an object; ensure a string is returned for printing.
                response = root_agent.run(user_prompt)
                # If response is not a string, convert
                return str(response)
            elif hasattr(root_agent, "respond"):
                return str(root_agent.respond(user_prompt))
            else:
                # ADK agent doesn't have expected run/respond API — fallback
                raise RuntimeError("ADK agent present but lacks run/respond method.")
        except Exception as e:
            # Fallback: call the tool directly. But include the ADK error info in returned message.
            fallback_reason = f"(Agent orchestration failed with: {e})\nFalling back to direct Spotify call.\n"
            try:
                result = spotify_tool.search_by_mood(mood)
                return fallback_reason + format_result(result)
            except Exception as e2:
                return fallback_reason + f"Also failed to get data from Spotify: {e2}"
    else:
        # No ADK agent available: call the tool directly
        try:
            result = spotify_tool.search_by_mood(mood)
            return format_result(result)
        except SpotifySearchError as se:
            return f"Spotify API error: {se}"
        except Exception as ex:
            return f"Unexpected error: {ex}"

def format_result(result: dict) -> str:
    """
    Convert the spotify_tool output into a clean, friendly string for the user.
    """
    playlist = result.get("playlist", {})
    tracks = result.get("tracks", [])
    lines = []
    lines.append(f"Recommended playlist: {playlist.get('name')} (by {playlist.get('owner')})")
    if playlist.get("external_url"):
        lines.append(f"Playlist link: {playlist.get('external_url')}")
    if playlist.get("description"):
        lines.append(f"Description: {playlist.get('description')}")
    lines.append("\nTop recommendations:")
    if not tracks:
        lines.append("No tracks found in the playlist.")
    for i, t in enumerate(tracks, start=1):
        preview = t.get("preview_url") or t.get("track_url") or "No preview"
        lines.append(f"{i}. {t.get('name')} — {t.get('artists')}  |  Preview/Link: {preview}")
    return "\n".join(lines)
