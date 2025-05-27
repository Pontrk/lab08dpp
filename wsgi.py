"""
WSGI entry point dla production deployment
"""

import os
from app import create_app

# Konfiguracja dla production
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)

if __name__ == "__main__":
    app.run()