This project is a beginner-friendly, production-ready music recommender agent that uses the Google ADK (Agent Developer Kit) with Gemini 1.5 Flash and the Spotify API. Users input a mood, and the agent intelligently recommends a playlist and songs from Spotify. This project is designed to be easily extensible into a more complex Personalized Memory Assistant System (PMAS).

## ✨ Features

*   **Natural Language Mood Understanding:** The agent understands various user moods like "happy," "sad," "romantic," "energetic," "calm," "angry," or "focus."
*   **Intelligent Spotify Search:** Utilizes a custom ADK tool to interact with the Spotify Search API, fetching relevant playlists and tracks.
*   **Best Playlist Selection:** The Gemini agent, powered by strong instructions, selects the most suitable playlist for the given mood.
*   **Top Song Recommendations:** Provides the top 5 songs from the chosen playlist.
*   **Robust Error Handling:** Catches common issues like invalid moods, API token problems, and rate limits.
*   **Automatic Spotify OAuth:** Handles the refresh token flow to ensure continuous API access without manual intervention.

## 🚀 Getting Started

This section will guide you through setting up and running the SpoMoodAgent.

### Prerequisites

*   Python 3.9+
*   A Spotify Developer Account
*   A Google Cloud Project with the Gemini API enabled

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/SpoMoodAgent.git
    cd SpoMoodAgent
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv310
    # On Windows
    venv310\Scripts\activate
    # On macOS/Linux
    source venv310/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install google-adk python-dotenv requests
    ```
    (Or `pip install -r requirements.txt` if available)

### Spotify API Configuration

1.  **Create a Spotify App:**
    *   Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
    *   Click "Create an app".
    *   Set the Redirect URI to `http://127.0.0.1:8888/callback`. (Note: `localhost` is not allowed by Spotify's new validation rules).
    *   Save your app and copy your **Client ID** and **Client Secret**.

2.  **Generate a Spotify Refresh Token:**
    *   Run the provided script:
        ```bash
        python get_refresh_token.py
        ```
    *   Follow the prompts to enter your Client ID and Client Secret.
    *   The script will open a browser window for authorization, start a local server, capture the authorization code, and exchange it for a refresh token.
    *   Once complete, it will print `SPOTIFY_REFRESH_TOKEN=xxxxxxxxxxxxxxxxxxxx`. Save this value.

### Environment Variables

1.  **Create a `.env` file:**
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file** with your credentials:
    ```ini
    GEMINI_API_KEY=your_gemini_api_key_here
    SPOTIFY_CLIENT_ID=your_spotify_client_id
    SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
    SPOTIFY_REFRESH_TOKEN=your_refresh_token_from_step_2
    ```

## 🏃 Running the Agent

With your virtual environment activated and `.env` configured, you can run the agent by providing a mood as a command-line argument:

```bash
python main.py happy
```

**Examples:**

```bash
python main.py sad
python main.py energetic
python main.py "romantic evening"
python main.py "calm peaceful focus"
python main.py "something to help me focus at work"
```

## 📂 Project Structure

```
SpoMoodAgent/
│── main.py                      # Main entry point to run the agent
│── .env                         # Environment variables (Spotify API keys, Gemini API key)
│── .env.example                 # Template for .env file
│── README.md                    # Project documentation
│── get_refresh_token.py         # Script to generate Spotify Refresh Token
│── venv310/                     # Python virtual environment
└── my_agent/
    │── agent.py                 # Defines the ADK agent with Gemini integration and instructions
    │── spotify_tool.py          # Custom ADK tool for Spotify API interactions
    └── __init__.py              # Python package initializer
```

## 🛠️ Components Explained

*   **`main.py`**: This script orchestrates the agent's execution. It loads environment variables, accepts a mood from the command line, initializes the `my_agent`, and prints the final recommendations.
*   **`my_agent/agent.py`**: This file defines the core of your ADK agent. It leverages the Gemini LLM for reasoning, provides clear instructions on how to interpret moods, and intelligently uses the `spotify_tool` to fulfill music requests. It's designed to ensure the best playlist selection and output formatting.
*   **`my_agent/spotify_tool.py`**: A custom tool for the ADK agent that encapsulates all Spotify API interactions. It's responsible for refreshing OAuth tokens, searching for playlists based on keywords, applying heuristics to select the most relevant playlist, and fetching the top N tracks from it.
*   **`get_refresh_token.py`**: A utility script to perform the initial Spotify OAuth flow. It guides the user through obtaining a long-lived refresh token, which is crucial for continuous, authorized access to the Spotify API.

## 🤝 PMAS Integration

This agent is built with extensibility in mind, making it an ideal module for a larger **Personalized Memory Assistant System (PMAS)**.

*   **Memory Module**: Store user mood patterns, preferred genres, liked/disliked tracks, and time-based mood trends for hyper-personalized recommendations.
*   **Emotion Detection**: Feed mood input from external emotion detection modules (e.g., speech sentiment, text analysis, facial recognition) directly to this agent.
*   **Multi-Agent System**: Integrate this Music Agent as a specialized sub-agent within a broader PMAS architecture, complementing other agents like Memory, Emotion, and Context Agents.

## 🌟 Future Enhancements

*   **Web UI (Streamlit/Flask):** Develop a user-friendly web interface for interaction.
*   **Mobile App Integration:** Extend functionality to Android or iOS applications.
*   **Multi-Platform Support:** Add support for other music streaming services like YouTube Music.
*   **Advanced Mood Detection:** Integrate more sophisticated natural language processing models for nuanced mood understanding.
*   **Real-time Voice Control:** Enable voice commands for requesting music.
*   **Reinforcement Learning:** Implement RL techniques to continuously improve personalization based on user feedback.

## 📜 License

This project is intended for educational and research purposes.