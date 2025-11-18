# main.py
"""
Entry point for the Spotify Mood Agent.
Usage:
    python main.py happy
    OR
    python main.py --mood "relaxed and sleepy"
This script reads env vars for GEMINI_API_KEY and Spotify credentials, then calls the agent.
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
from my_agent.agent import handle_mood_with_agent

def print_usage():
    print("Usage: python main.py <mood>")
    print("Example: python main.py happy")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    mood = " ".join(sys.argv[1:]).strip()
    print(f"Getting recommendations for mood: '{mood}'\n")

    # Run agent/tool
    result_text = handle_mood_with_agent(mood)
    print(result_text)

if __name__ == "__main__":
    main()
