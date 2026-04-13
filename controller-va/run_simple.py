#!/usr/bin/env python3
"""
Simple server launcher without complex initialization
"""
import sys
import os
import traceback
from tendo import singleton

def create_minimal_app():
    """Create minimal Flask app for testing"""
    print("=" * 60)
    print("CREATING MINIMAL FLASK APP")
    print("=" * 60)
    
    try:
        # Basic Flask import
        from flask import Flask, jsonify
        print("✓ Flask imported")
        
        # Create app
        app = Flask(__name__)
        app.config["JSON_SORT_KEYS"] = False
        print("✓ Flask app created")
        
        # Basic routes
        @app.route('/')
        def home():
            return "SentinelVA Controller - Running"
        
        @app.route('/ping')
        def ping():
            return jsonify({
                "status": True,
                "senderModuleId": 107,
                "vendor": "SentinelVA",
                "module": "Sentinel CONNECT",
                "version": "1.0.0"
            })
        
        @app.route('/status')
        def status():
            return jsonify({
                "status": True,
                "server": "running",
                "port": 600
            })
        
        print("✓ Basic routes created")
        return app
        
    except Exception as e:
        print(f"✗ Minimal app creation failed: {e}")
        traceback.print_exc()
        return None

def test_port_simple():
    """Simple port test"""
    print("=" * 60)
    print("PORT TEST")
    print("=" * 60)
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', 600))
        sock.close()
        print("✓ Port 600: Available")
        return True
    except OSError as e:
        print(f"✗ Port 600: In use - {e}")
        return False
    except Exception as e:
        print(f"✗ Port test failed: {e}")
        return False

def main():
    """Main function"""
    print("SENTINELVA CONTROLLER - SIMPLE MODE")
    print("Minimal Flask app without complex initialization")
    print()
    
    # Test port
    if not test_port_simple():
        print("Port 600 is not available")
        input("Press Enter to exit...")
        return
    
    # Create app
    app = create_minimal_app()
    if not app:
        print("Failed to create Flask app")
        input("Press Enter to exit...")
        return
    
    print("=" * 60)
    print("STARTING MINIMAL SERVER")
    print("=" * 60)
    print("Server will be available at: http://localhost:600")
    print("Test endpoints:")
    print("  - http://localhost:600/")
    print("  - http://localhost:600/ping")
    print("  - http://localhost:600/status")
    print()
    
    try:
        # Singleton check
        me = singleton.SingleInstance()
        
        # Start server
        app.run(
            debug=False,
            use_reloader=False,
            host='0.0.0.0',
            port=600,
            threaded=True
        )
        
    except SystemExit:
        print("Server stopped")
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        traceback.print_exc()
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")
