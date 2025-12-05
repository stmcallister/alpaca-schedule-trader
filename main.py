from scheduler import load_config, build_scheduler

def main():
    config_file = "config.yaml"
    config = load_config(config_file)
    scheduler = build_scheduler(config)
    print("Starting trading scheduler...")
    scheduler.start()

if __name__ == "__main__":
    main()
