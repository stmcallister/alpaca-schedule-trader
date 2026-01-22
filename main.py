from scheduler import load_config, build_scheduler
from web_app import app, ensure_config_exists
import threading
import os

def main():
    config_file = "config.yaml"
    
    # Ensure config file exists
    ensure_config_exists()
    
    try:
        config = load_config(config_file)
        # Ensure config has required structure
        if 'timezone' not in config:
            config['timezone'] = 'America/Los_Angeles'
        if 'jobs' not in config:
            config['jobs'] = []
        
        scheduler = build_scheduler(config)
        print("Starting trading scheduler...")
        
        # Start scheduler in a separate thread
        scheduler_thread = threading.Thread(target=scheduler.start, daemon=True)
        scheduler_thread.start()
    except Exception as e:
        print(f"Warning: Could not start scheduler: {e}")
        print("Web UI will still be available, but scheduler may not be running.")
    
    # Start Flask web app in main thread
    print("Starting web UI on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()
