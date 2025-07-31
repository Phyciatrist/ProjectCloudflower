Project Cloudflower 🌸

Project Cloudflower is a web-based game built with a Unity client and a Python backend. The game client runs entirely in a web browser, served by a lightweight Python server that also manages game data and logic.

Technology Stack

    Client (Frontend): C# with the Unity Engine (compiled to WebGL)

    Server (Backend): Python with the Flask framework

    Version Control: Git & GitHub


Project Architecture

This project uses a simple client-server model:

    Python Backend: A Flask server handles API requests for game data and serves the static WebGL game files.

    Unity WebGL Client: The game itself is built in Unity. It runs in the user's browser and communicates with the backend via HTTP requests to its API.
