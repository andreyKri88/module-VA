#!/usr/bin/env python3
"""
Debug script to identify startup issues
"""
import sys
import os
import traceback

def check_environment():
    """Check system environment"""
    print("=" * 50)
    print("ENVIRONMENT CHECK")
    print("=" * 50)
    
    # Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Python path
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 paths
    
    # Check if we're in the right directory
    required_files = ['settings.ini', 'devices.json', 'app_va/__init__.py']
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}: FOUND")
        else:
            print(f"✗ {file}: NOT FOUND")
    
    print()

def check_imports():
    """Test critical imports step by step"""
    print("=" * 50)
    print("IMPORT CHECK")
    print("=" * 50)
    
    try:
        print("Testing: sys import...")
        import sys
        print("✓ sys imported")
    except Exception as e:
        print(f"✗ sys import failed: {e}")
        return False
    
    try:
        print("Testing: os import...")
        import os
        print("✓ os imported")
    except Exception as e:
        print(f"✗ os import failed: {e}")
        return False
    
    try:
        print("Testing: pathlib import...")
        from pathlib import Path
        print("✓ pathlib imported")
    except Exception as e:
        print(f"✗ pathlib import failed: {e}")
        return False
    
    try:
        print("Testing: flask import...")
        from flask import Flask
        print("✓ flask imported")
    except Exception as e:
        print(f"✗ flask import failed: {e}")
        return False
    
    try:
        print("Testing: tendo import...")
        from tendo import singleton
        print("✓ tendo imported")
    except Exception as e:
        print(f"✗ tendo import failed: {e}")
        return False
    
    try:
        print("Testing: app_va import...")
        from app_va import app_run
        print("✓ app_va imported")
    except Exception as e:
        print(f"✗ app_va import failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False
    
    print()
    return True

def check_configuration():
    """Check configuration files"""
    print("=" * 50)
    print("CONFIGURATION CHECK")
    print("=" * 50)
    
    try:
        import json
        with open('settings.ini', 'r') as f:
            print("✓ settings.ini: readable")
            content = f.read()
            print(f"Settings file size: {len(content)} characters")
    except Exception as e:
        print(f"✗ settings.ini error: {e}")
        return False
    
    try:
        with open('devices.json', 'r') as f:
            data = json.load(f)
            print("✓ devices.json: valid JSON")
            print(f"Servers: {len(data.get('servers', {}))}")
            print(f"Cameras: {len(data.get('cameras', {}))}")
    except Exception as e:
        print(f"✗ devices.json error: {e}")
        return False
    
    print()
    return True

def test_flask_app():
    """Test Flask app creation"""
    print("=" * 50)
    print("FLASK APP TEST")
    print("=" * 50)
    
    try:
        from app_va import app_run
        print("✓ Flask app created successfully")
        print(f"App name: {app_run.name}")
        print(f"App debug: {app_run.debug}")
        return True
    except Exception as e:
        print(f"✗ Flask app creation failed: {e}")
        traceback.print_exc()
        return False

def test_port_availability():
    """Check if port 600 is available"""
    print("=" * 50)
    print("PORT CHECK")
    print("=" * 50)
    
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 600))
        sock.close()
        
        if result == 0:
            print("✗ Port 600: ALREADY IN USE")
        else:
            print("✓ Port 600: AVAILABLE")
    except Exception as e:
        print(f"✗ Port check failed: {e}")
    
    print()

def main():
    """Main debug function"""
    print("SENTINELVA CONTROLLER - DEBUG MODE")
    print("This script will help identify startup issues")
    print()
    
    # Run all checks
    check_environment()
    
    if not check_imports():
        print("IMPORT CHECK FAILED - cannot continue")
        input("Press Enter to exit...")
        return
    
    if not check_configuration():
        print("CONFIGURATION CHECK FAILED - cannot continue")
        input("Press Enter to exit...")
        return
    
    test_flask_app()
    test_port_availability()
    
    print("=" * 50)
    print("DEBUG COMPLETE")
    print("=" * 50)
    print("If all checks passed, try running:")
    print("python run_server.py")
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDebug interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error in debug script: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")
