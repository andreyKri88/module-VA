from tendo import singleton
from app_va import app_run

if __name__ == "__main__":
    me = singleton.SingleInstance()
    try:
        app_run.run(debug=False, use_reloader=False, host='0.0.0.0', port=600)
    except Exception as e:
        print(f"Exception: {e}\nExit!")
