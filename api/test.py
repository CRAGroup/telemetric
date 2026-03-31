"""
Vehicle Data Simulator
Simulates OBD-II and GPS data for testing without actual hardware
"""

import time
import json
import random
import requests
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
from dataclasses import dataclass
import math
import argparse
import sys


@dataclass
class VehicleSimulator:
    vehicle_id: str
    api_url: str
    mqtt_broker: str
    mqtt_port: int
    api_token: str

    # Starting position (Nairobi CBD)
    latitude: float = -1.286389
    longitude: float = 36.817223
    speed: float = 0.0
    heading: float = 0.0
    rpm: float = 800.0
    fuel_level: float = 75.0
    engine_temp: float = 90.0

    def __post_init__(self):
        """Initialize MQTT client"""
        self.mqtt_client = mqtt.Client(client_id=f"simulator_{self.vehicle_id}")
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.connected = False

        # Connect to MQTT
        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            print(f"⚠️  MQTT connection failed: {e}")
            print("   Will use HTTP only")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✓ MQTT connected to {self.mqtt_broker}:{self.mqtt_port}")
            self.connected = True
        else:
            print(f"✗ MQTT connection failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        print("⚠️  MQTT disconnected")
        self.connected = False

    def simulate_movement(self):
        """Simulate vehicle movement"""
        # Random movement pattern
        if random.random() < 0.3:  # 30% chance to change behavior
            if self.speed < 5:
                # Start moving
                self.speed = random.uniform(20, 80)
                self.rpm = 1500 + (self.speed * 30)
            elif random.random() < 0.2:
                # Stop
                self.speed = 0
                self.rpm = 800
            else:
                # Change speed
                self.speed += random.uniform(-10, 10)
                self.speed = max(0, min(120, self.speed))
                self.rpm = 800 + (self.speed * 40)

        # Update position based on speed and heading
        if self.speed > 0:
            # Distance in degrees (very rough approximation)
            distance = self.speed * 0.00001  # km to degrees

            self.latitude += distance * math.cos(math.radians(self.heading))
            self.longitude += distance * math.sin(math.radians(self.heading))

            # Randomly change heading slightly
            self.heading += random.uniform(-15, 15)
            self.heading = self.heading % 360

        # Fuel consumption (very simplified)
        if self.speed > 0:
            self.fuel_level -= random.uniform(0.01, 0.05)
            self.fuel_level = max(0, self.fuel_level)

        # Engine temperature
        if self.speed > 60:
            self.engine_temp = min(105, self.engine_temp + 0.5)
        else:
            self.engine_temp = max(85, self.engine_temp - 0.2)

    def generate_telemetry(self):
        """Generate telemetry data packet in correct format"""
        return {
            'vehicle_id': self.vehicle_id,
            'timestamp': datetime.now(timezone.utc).timestamp(),
            'vehicle': {
                'lat': round(self.latitude, 6),
                'lon': round(self.longitude, 6),
                'speed_kph': round(self.speed, 1),
                'heading_deg': round(self.heading, 1),
                'alt_m': round(random.uniform(1600, 1700), 1)
            },
            'engine': {
                'rpm': round(self.rpm, 0),
                'engine_temp_c': round(self.engine_temp, 1),
                'throttle_pos_pct': round((self.speed / 120) * 100, 1),
                'engine_load_pct': round((self.speed / 120) * 100, 1),
                'fuel_level_pct': round(self.fuel_level, 1),
                'battery_voltage_v': round(random.uniform(12.5, 14.5), 1)
            }
        }

    def send_via_mqtt(self, data):
        """Send data via MQTT"""
        if not self.connected:
            return False

        try:
            topic = f"vehicles/{self.vehicle_id}/telemetry"
            payload = json.dumps(data)
            result = self.mqtt_client.publish(topic, payload, qos=1)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"✗ MQTT send error: {e}")
            return False

    def send_via_http(self, data):
        """Send data via HTTP API"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_token}'
            }

            response = requests.post(
                f'{self.api_url}/api/v1/telemetry',
                json=data,
                headers=headers,
                timeout=10
            )

            return response.status_code in [200, 201]
        except Exception as e:
            print(f"✗ HTTP send error: {e}")
            return False

    def run(self, duration=None, interval=5):
        """Run the simulator"""
        print(f"\n{'=' * 60}")
        print(f"🚗 Vehicle Data Simulator Started")
        print(f"{'=' * 60}")
        print(f"Vehicle ID:    {self.vehicle_id}")
        print(f"API URL:       {self.api_url}")
        print(f"MQTT Broker:   {self.mqtt_broker}:{self.mqtt_port}")
        print(f"Interval:      {interval}s")
        if duration:
            print(f"Duration:      {duration}s")
        print(f"{'=' * 60}\n")

        start_time = time.time()
        iteration = 0

        try:
            while True:
                iteration += 1

                # Check duration
                if duration and (time.time() - start_time) > duration:
                    print(f"\n✓ Simulation completed ({duration}s)")
                    break

                # Simulate movement
                self.simulate_movement()

                # Generate telemetry
                telemetry = self.generate_telemetry()

                # Try sending via MQTT first, fallback to HTTP
                sent = False
                if self.connected:
                    sent = self.send_via_mqtt(telemetry)
                    method = "MQTT"

                if not sent:
                    sent = self.send_via_http(telemetry)
                    method = "HTTP"

                # Display status
                status = "✓" if sent else "✗"
                print(f"{status} [{iteration:4d}] {method:5s} | "
                      f"Speed: {self.speed:5.1f} km/h | "
                      f"RPM: {self.rpm:5.0f} | "
                      f"Fuel: {self.fuel_level:5.1f}% | "
                      f"Pos: ({self.latitude:.4f}, {self.longitude:.4f})")

                # Wait for next iteration
                time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n\n⚠️  Simulation stopped by user")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup MQTT connection"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        print("\n✓ Cleanup completed\n")


class MultiVehicleSimulator:
    """Simulate multiple vehicles"""

    def __init__(self, num_vehicles, api_url, mqtt_broker, mqtt_port, api_token):
        self.vehicles = []

        # Create multiple vehicle simulators
        vehicle_names = [
             "KAA_123X","test", "KBB_456Y", "KCC_789Z",
            "KDD_012A", "KEE_345B", "KFF_678C",
            "KGG_901D", "KHH_234E", "KII_567F", "KJJ_890G"
        ]

        # Starting positions around Nairobi
        positions = [
            (-1.286389, 36.817223),  # CBD
            (-1.292066, 36.821945),  # Westlands
            (-1.319167, 36.886389),  # Eastleigh
            (-1.223889, 36.885833),  # Thika Road
            (-1.352083, 36.682778),  # Karen
        ]

        for i in range(min(num_vehicles, len(vehicle_names))):
            vehicle_id = vehicle_names[i]
            pos = positions[i % len(positions)]

            simulator = VehicleSimulator(
                vehicle_id=vehicle_id,
                api_url=api_url,
                mqtt_broker=mqtt_broker,
                mqtt_port=mqtt_port,
                api_token=api_token
            )

            # Set different starting positions
            simulator.latitude = pos[0] + random.uniform(-0.01, 0.01)
            simulator.longitude = pos[1] + random.uniform(-0.01, 0.01)
            simulator.speed = random.uniform(0, 60)
            simulator.heading = random.uniform(0, 360)
            simulator.fuel_level = random.uniform(30, 90)

            self.vehicles.append(simulator)

    def run(self, duration=None, interval=5):
        """Run all simulators"""
        print(f"\n{'=' * 60}")
        print(f"🚗 Multi-Vehicle Simulator")
        print(f"{'=' * 60}")
        print(f"Number of vehicles: {len(self.vehicles)}")
        print(f"Update interval:    {interval}s")
        if duration:
            print(f"Duration:           {duration}s")
        print(f"{'=' * 60}\n")

        start_time = time.time()
        iteration = 0

        try:
            while True:
                iteration += 1

                # Check duration
                if duration and (time.time() - start_time) > duration:
                    print(f"\n✓ Simulation completed ({duration}s)")
                    break

                print(f"\n--- Iteration {iteration} ---")

                # Update each vehicle
                for vehicle in self.vehicles:
                    vehicle.simulate_movement()
                    telemetry = vehicle.generate_telemetry()

                    # Send data
                    sent = False
                    if vehicle.connected:
                        sent = vehicle.send_via_mqtt(telemetry)
                        method = "MQTT"

                    if not sent:
                        sent = vehicle.send_via_http(telemetry)
                        method = "HTTP"

                    status = "✓" if sent else "✗"
                    print(f"{status} {vehicle.vehicle_id:12s} | {method:5s} | "
                          f"Speed: {vehicle.speed:5.1f} km/h | "
                          f"Fuel: {vehicle.fuel_level:5.1f}%")

                time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n\n⚠️  Simulation stopped by user")
        finally:
            for vehicle in self.vehicles:
                vehicle.cleanup()


def main():
    parser = argparse.ArgumentParser(description='Vehicle Data Simulator')
    parser.add_argument('--vehicle-id', default='test',
                        help='Vehicle ID (default: KAA_123X)')
    parser.add_argument('--api-url', default='http://localhost:8000',
                        help='Backend API URL (default: http://localhost:8000)')
    parser.add_argument('--mqtt-broker', default='localhost',
                        help='MQTT broker host (default: localhost)')
    parser.add_argument('--mqtt-port', type=int, default=1883,
                        help='MQTT broker port (default: 1883)')
    parser.add_argument('--api-token', default='',
                        help='API authentication token')
    parser.add_argument('--interval', type=int, default=5,
                        help='Update interval in seconds (default: 5)')
    parser.add_argument('--duration', type=int, default=None,
                        help='Simulation duration in seconds (default: infinite)')
    parser.add_argument('--multi', type=int, default=0,
                        help='Number of vehicles to simulate (default: 1)')

    args = parser.parse_args()

    # Install required packages check
    try:
        import paho.mqtt.client as mqtt
        import requests
    except ImportError:
        print("✗ Missing required packages!")
        print("\nInstall with:")
        print("  pip install paho-mqtt requests")
        sys.exit(1)

    # Run simulator
    if args.multi > 1:
        # Multi-vehicle simulation
        simulator = MultiVehicleSimulator(
            num_vehicles=args.multi,
            api_url=args.api_url,
            mqtt_broker=args.mqtt_broker,
            mqtt_port=args.mqtt_port,
            api_token=args.api_token
        )
    else:
        # Single vehicle simulation
        simulator = VehicleSimulator(
            vehicle_id=args.vehicle_id,
            api_url=args.api_url,
            mqtt_broker=args.mqtt_broker,
            mqtt_port=args.mqtt_port,
            api_token=args.api_token
        )

    simulator.run(duration=args.duration, interval=args.interval)


if __name__ == "__main__":
    main()