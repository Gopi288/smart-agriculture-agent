"""WSGI entry point for Gunicorn.

Gunicorn imports this module and looks for the 'application' or 'app'
callable. Using a dedicated wsgi.py keeps app.py clean (dev server only)
and makes the Gunicorn start command straightforward:

    gunicorn wsgi:app -c gunicorn.conf.py
"""

import os
from app import create_app

# Create the Flask application instance using the factory.
# The FLASK_ENV environment variable selects the configuration class:
#   production  → ProductionConfig (debug=False)
#   development → DevelopmentConfig (debug=True)
app = create_app()

# Expose as 'application' for maximum WSGI compatibility (PEP 3333).
application = app
