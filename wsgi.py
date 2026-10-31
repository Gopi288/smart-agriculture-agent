"""WSGI entry point for Gunicorn and other WSGI servers.

Gunicorn imports this module and looks for the 'app' or 'application' callable.
Both are exposed for maximum compatibility.

Start commands:
  gunicorn wsgi:app -c gunicorn.conf.py          (uses gunicorn.conf.py settings)
  gunicorn wsgi:application --bind 0.0.0.0:$PORT  (inline flags)
"""

import os
from app import create_app

# Create the Flask application instance using the factory.
# FLASK_ENV selects the configuration:
#   production  → ProductionConfig (debug=False)
#   development → DevelopmentConfig (debug=True)
app = create_app()

# Expose as 'application' for PEP 3333 compatibility
application = app

