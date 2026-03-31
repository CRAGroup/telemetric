
import time
import json

from telemetric_system.services.data_collector.obd_reader import ObdConfig, ObdReader


def main():
    # Set your actual adapter port here
    config = ObdConfig(
        port="/dev/ttyUSB0",  # change this if your adapter differs
     #   baudrate=9600,
        fast=True,
    #    timeout_s=5,
     #   max_retries=3,
      #  backoff_s=2,
    )

    reader = ObdReader(config)

    print("Connecting to OBD-II adapter...")
    if not reader.connect():
        print("❌ Failed to connect to the OBD-II adapter.")
        return

    print("✅ Connected successfully!\n")

    try:
        # Keep reading data every few seconds
        while True:
            reading = reader.read_parameters()
            print(json.dumps(reading, indent=2))
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    finally:
        reader.disconnect()
        print("Disconnected from OBD adapter.")

if __name__ == "__main__":
    main()
