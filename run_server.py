#!/usr/bin/env python3
"""
Skrypt uruchamiający serwer Flask z różnymi opcjami
"""

import os
import sys
from app import create_app

def main():
    # Domyślne ustawienia
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    print(f"🚀 Uruchamianie HEX Flask Server...")
    print(f"📍 URL: http://{host}:{port}")
    print(f"⚙️  Konfiguracja: {config_name}")
    print(f"🔧 Debug: {debug}")
    print(f"💾 Storage: {os.environ.get('STORAGE_TYPE', 'memory')}")
    print(f"📁 Storage Dir: {os.environ.get('STORAGE_DIR', 'saved_games')}")
    
    try:
        app = create_app(config_name)
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"❌ Błąd uruchamiania serwera: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()