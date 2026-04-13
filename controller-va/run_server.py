import sys
import time
import traceback
from tendo import singleton

try:
    from app_va import app_run
except ImportError as e:
    print(f"Failed to import app_va: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    input("Press Enter to exit...")
    sys.exit(1)

if __name__ == "__main__":
    print("Starting SentinelVA Controller...")

    try:
        me = singleton.SingleInstance()
        print("Starting Flask server on http://0.0.0.0:600")
        app_run.run(debug=False, use_reloader=False, host="0.0.0.0", port=600)
    except SystemExit:
        print("Application stopped by user or system")
        input("Press Enter to exit...")
    except KeyboardInterrupt:
        print("Application stopped by user (Ctrl+C)")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nFull error details:")
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Check if port 600 is available")
        print("2. Verify all dependencies are installed")
        print("3. Check configuration files (settings.ini, devices.json)")
        print("4. Run 'python -c from app_va import app_run' to test imports")
        input("\nPress Enter to exit...")
        sys.exit(1)
