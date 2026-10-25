"""Application entrypoint for Smart Agriculture Agent.

Initializes the Flask application instance using the factory pattern
and boots the local development server.
"""

import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development").lower() == "development"
    print(f"[*] Smart Agriculture Agent running on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=debug)
