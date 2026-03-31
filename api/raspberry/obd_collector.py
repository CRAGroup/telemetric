#!/usr/bin/env python3
"""
Vehicle Data Collector
Reads OBD-II and GPS data and sends to backend
Supports modular operation via command-line arguments
"""

import obd
import serial
import time
import json
import requests
import paho.mqtt.client as mqtt
import argparse
from datetime import datetime
from dotenv import load_dotenv
import os
import logging

# Load configuration
load_dotenv()

# Configuration
VEHICLE_ID = os.getenv('VEHICLE_ID', 'TEST_VEHICLE_001')
API_URL = os.getenv('API_URL', 'http://172.168.100.179:8000')
MQTT_BROKER = os.getenv('MQTT_BROKER', '172.168.100.179')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
API_TOKEN = os.getenv('API_TOKEN', '')
GPS_PORT = os.getenv('GPS_PORT', '/dev/serial0')
GPS_BAUDRATE = int(os.getenv('GPS_BAUDRATE', 115200))
COLLECTION_INTERVAL = int(os.getenv('COLLECTION_INTERVAL', 5))  # seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VehicleDataCollector:
    def __init__(self, enable_obd=True, enable_gps=True, enable_mqtt=True):
        self.enable_obd = enable_obd
        self.enable_gps = enable_gps
        self.enable_mqtt = enable_mqtt

        self.obd_connection = None
        self.gps_serial = None
        self.mqtt_client = None

        self.current_location = {
            'latitude': 0.0,
            'longitude': 0.0,
            'speed': 0.0,
            'heading': 0.0,
            'altitude': 0.0
        }
        self.current_obd_data = {}
        self.gps_fix = False

    def connect_obd(self):
        """Connect to OBD-II adapter"""
        if not self.enable_obd:
            logger.info("OBD module disabled")
            return False

        try:
            logger.info("Connecting to OBD-II...")
            # Try common ports
            ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/rfcomm0']

            for port in ports:
                try:
                    self.obd_connection = obd.OBD(port)
                    if self.obd_connection.is_connected():
                        logger.info(f"OBD-II connected on {port}")
                        return True
                except:
                    continue

            # Try async connection
            self.obd_connection = obd.Async()
            if self.obd_connection.is_connected():
                logger.info("OBD-II connected (async)")
                return True

            logger.warning("Could not connect to OBD-II")
            return False

        except Exception as e:
            logger.error(f"OBD connection error: {e}")
            return False

    def connect_gps(self):
        """Connect to GPS module (AT command-based)"""
        if not self.enable_gps:
            logger.info("GPS module disabled")
            return False

        try:
            logger.info(f"Connecting to GPS on {GPS_PORT} at {GPS_BAUDRATE} baud...")
            self.gps_serial = serial.Serial(
                GPS_PORT,
                baudrate=GPS_BAUDRATE,
                timeout=1
            )
            time.sleep(0.5)

            # Test connection
            response = self.send_at_command("AT")
            if "OK" in response or "AT" in response:
                logger.info("GPS module responding")

                # Enable GPS
                logger.info("Enabling GPS...")
                response = self.send_at_command("AT+CGPS=1")
                logger.info(f"GPS enable response: {response.strip()}")

                return True
            else:
                logger.warning("GPS module not responding properly")
                return False

        except Exception as e:
            logger.error(f"GPS connection error: {e}")
            return False

    def send_at_command(self, command, delay=0.5):
        """Send AT command and return response"""
        if not self.gps_serial:
            return ""

        try:
            self.gps_serial.write((command + "\r\n").encode())
            time.sleep(delay)
            response = self.gps_serial.read_all().decode(errors='ignore')
            return response
        except Exception as e:
            logger.debug(f"AT command error: {e}")
            return ""

    def connect_mqtt(self):
        """Connect to MQTT broker"""
        if not self.enable_mqtt:
            logger.info("MQTT module disabled")
            return False

        try:
            logger.info(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT}...")
            self.mqtt_client = mqtt.Client(client_id=f"vehicle_{VEHICLE_ID}")

            if MQTT_USERNAME and MQTT_PASSWORD:
                self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_disconnect = self.on_mqtt_disconnect

            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()

            logger.info("MQTT connected")
            return True
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")
            return False

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connection successful")
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def on_mqtt_disconnect(self, client, userdata, rc):
        logger.warning("MQTT disconnected")

    def _safe_query(self, command):
        """Safely query OBD command and return value"""
        try:
            response = self.obd_connection.query(command)
            if response and response.value is not None:
                # Convert to numeric value or return as is
                if hasattr(response.value, 'magnitude'):
                    return float(response.value.magnitude)
                else:
                    return response.value
        except Exception as e:
            logger.debug(f"Query failed for {command}: {e}")
        return None

    def read_obd_data(self):
        """Read data from OBD-II"""
        if not self.obd_connection or not self.obd_connection.is_connected():
            return {}

        try:
            data = {
                "rpm": self._safe_query(obd.commands.RPM),
                "speed_kph": self._safe_query(obd.commands.SPEED),
                "fuel_level_pct": self._safe_query(obd.commands.FUEL_LEVEL),
                "coolant_temp_c": self._safe_query(obd.commands.COOLANT_TEMP),
                "engine_load_pct": self._safe_query(obd.commands.ENGINE_LOAD),
                "throttle_pos_pct": self._safe_query(obd.commands.THROTTLE_POS),
                "intake_temp_c": self._safe_query(obd.commands.INTAKE_TEMP),
                "maf_gps": self._safe_query(obd.commands.MAF),
                "barometric_kpa": self._safe_query(obd.commands.BAROMETRIC_PRESSURE),
                "fuel_status": self._safe_query(obd.commands.FUEL_STATUS),
                "engine_runtime": self._safe_query(obd.commands.RUN_TIME),
                "engine_oil_temperature": self._safe_query(obd.commands.OIL_TEMP),
            }

            return data

        except Exception as e:
            logger.error(f"OBD read error: {e}")
            return {}

    def read_gps_data(self):
        """Read GPS data using AT commands"""
        if not self.gps_serial:
            return

        try:
            response = self.send_at_command("AT+CGPSINFO", delay=0.3)

            if "+CGPSINFO:" in response:
                # Parse response: +CGPSINFO: lat,lat_dir,lon,lon_dir,date,time,altitude,speed,course
                # Example: +CGPSINFO: 0115.735314,S,03645.993231,E,141025,114452.0,1812.7,0.0,45.2

                try:
                    # Extract data after the colon
                    data_part = response.split(":")[1].strip()
                    parts = [p.strip() for p in data_part.split(",")]

                    if len(parts) >= 4:
                        lat_raw = parts[0]
                        lat_dir = parts[1]
                        lon_raw = parts[2]
                        lon_dir = parts[3]

                        # Check if we have valid coordinates
                        if lat_raw and lon_raw and lat_raw != "" and lon_raw != "":
                            # Convert from DDMM.MMMMMM to decimal degrees
                            # Latitude format: DDMM.MMMMMM (2 digits for degrees)
                            lat_deg = float(lat_raw[:2]) + float(lat_raw[2:]) / 60
                            if lat_dir == "S":
                                lat_deg = -lat_deg

                            # Longitude format: DDDMM.MMMMMM (3 digits for degrees)
                            lon_deg = float(lon_raw[:3]) + float(lon_raw[3:]) / 60
                            if lon_dir == "W":
                                lon_deg = -lon_deg

                            self.current_location['latitude'] = lat_deg
                            self.current_location['longitude'] = lon_deg
                            self.gps_fix = True

                            # Parse additional fields if available
                            if len(parts) >= 7 and parts[6]:
                                # Altitude in meters
                                self.current_location['altitude'] = float(parts[6])

                            if len(parts) >= 8 and parts[7]:
                                # Speed in knots, convert to km/h
                                speed_knots = float(parts[7])
                                self.current_location['speed'] = speed_knots * 1.852

                            if len(parts) >= 9 and parts[8]:
                                # Course/heading
                                self.current_location['heading'] = float(parts[8])

                            logger.debug(f"GPS Fix: Lat={lat_deg:.6f}, Lon={lon_deg:.6f}")
                        else:
                            if self.gps_fix:
                                logger.debug("GPS fix lost")
                            self.gps_fix = False

                except (ValueError, IndexError) as e:
                    logger.debug(f"GPS parse error: {e}")
                    self.gps_fix = False
            else:
                logger.debug("No GPS response")

        except Exception as e:
            logger.debug(f"GPS read error: {e}")

    def combine_data(self):
        """Combine OBD and GPS data into telemetry packet"""
        timestamp = datetime.utcnow().isoformat() + 'Z'

        telemetry = {
            'vehicle_id': VEHICLE_ID,
            'timestamp': timestamp,
            'location': {
                'latitude': self.current_location['latitude'],
                'longitude': self.current_location['longitude'],
                'altitude': self.current_location['altitude'],
                'speed': self.current_location['speed'],
                'heading': self.current_location['heading'],
                'gps_fix': self.gps_fix
            },
            'engine': {
                'rpm': self.current_obd_data.get('rpm'),
                'speed_kph': self.current_obd_data.get('speed_kph'),
                'fuel_level_pct': self.current_obd_data.get('fuel_level_pct'),
                'coolant_temp_c': self.current_obd_data.get('coolant_temp_c'),
                'engine_load_pct': self.current_obd_data.get('engine_load_pct'),
                'throttle_pos_pct': self.current_obd_data.get('throttle_pos_pct'),
                'intake_temp_c': self.current_obd_data.get('intake_temp_c'),
                'maf_gps': self.current_obd_data.get('maf_gps'),
                'oil_pressure': self.current_obd_data.get('barometric_kpa'),
                'fuel_status': self.current_obd_data.get('fuel_status'),
                'engine_runtime': self.current_obd_data.get('engine_runtime'),
                'temperature': self.current_obd_data.get('engine_oil_temperature')
            }
        }

        return telemetry

    def send_via_mqtt(self, data):
        """Send data via MQTT"""
        if not self.mqtt_client:
            return False

        try:
            topic = f"vehicles/{VEHICLE_ID}/telemetry"
            payload = json.dumps(data)
            result = self.mqtt_client.publish(topic, payload, qos=1)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Data sent via MQTT to {topic}")
                return True
            else:
                logger.warning(f"MQTT publish failed: {result.rc}")
                return False

        except Exception as e:
            logger.error(f"MQTT send error: {e}")
            return False

    def send_via_http(self, data):
        """Send data via HTTP API"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_TOKEN}'
            }

            response = requests.post(
                f'{API_URL}/api/v1/telemetry',
                json=data,
                headers=headers,
                timeout=10
            )

            if response.status_code in [200, 201]:
                logger.debug("Data sent via HTTP")
                return True
            else:
                logger.warning(f"HTTP send failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"HTTP send error: {e}")
            return False

    def run(self):
        """Main collection loop"""
        logger.info("Starting Vehicle Data Collector...")
        logger.info(f"Vehicle ID: {VEHICLE_ID}")
        logger.info(f"Collection Interval: {COLLECTION_INTERVAL}s")
        logger.info(f"Modules: OBD={self.enable_obd}, GPS={self.enable_gps}, MQTT={self.enable_mqtt}")

        # Connect to enabled devices
        obd_connected = self.connect_obd() if self.enable_obd else False
        gps_connected = self.connect_gps() if self.enable_gps else False
        mqtt_connected = self.connect_mqtt() if self.enable_mqtt else False

        if not (obd_connected or gps_connected):
            logger.error("No data sources available. Exiting.")
            return

        logger.info("Data collection started")

        try:
            while True:
                # Read OBD data
                if obd_connected:
                    self.current_obd_data = self.read_obd_data()

                # Read GPS data
                if gps_connected:
                    self.read_gps_data()

                # Combine and send data
                telemetry = self.combine_data()

                # Try MQTT first, fall back to HTTP
                success = False
                if mqtt_connected:
                    success = self.send_via_mqtt(telemetry)

                if not success and API_TOKEN:
                    success = self.send_via_http(telemetry)

                if success:
                    gps_status = "✓" if self.gps_fix else "✗"
                    rpm = telemetry['obd']['rpm'] or 0
                    speed = telemetry['location']['speed']
                    logger.info(f"Telemetry sent: GPS{gps_status} "
                                f"Lat={telemetry['location']['latitude']:.6f}, "
                                f"Lon={telemetry['location']['longitude']:.6f}, "
                                f"Speed={speed:.1f} km/h, "
                                f"RPM={rpm:.0f}")

                # Wait before next collection
                time.sleep(COLLECTION_INTERVAL)

        except KeyboardInterrupt:
            logger.info("\nShutting down...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup connections"""
        if self.obd_connection:
            try:
                self.obd_connection.close()
                logger.info("OBD connection closed")
            except:
                pass

        if self.gps_serial:
            try:
                # Turn off GPS before closing
                self.send_at_command("AT+CGPS=0")
                self.gps_serial.close()
                logger.info("GPS connection closed")
            except:
                pass

        if self.mqtt_client:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                logger.info("MQTT connection closed")
            except:
                pass


def main():
    parser = argparse.ArgumentParser(
        description='Vehicle Data Collector - Modular OBD-II and GPS telemetry',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all modules (default)
  python vehicle_collector.py

  # Run only OBD module
  python vehicle_collector.py --obd-only

  # Run only GPS module
  python vehicle_collector.py --gps-only

  # Run OBD and GPS without MQTT
  python vehicle_collector.py --no-mqtt

  # Custom module combination
  python vehicle_collector.py --enable-obd --enable-gps --no-mqtt
        """
    )

    # Module selection arguments
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--obd-only',
        action='store_true',
        help='Run only the OBD-II module'
    )
    mode_group.add_argument(
        '--gps-only',
        action='store_true',
        help='Run only the GPS module'
    )

    # Individual module flags
    parser.add_argument(
        '--enable-obd',
        action='store_true',
        default=None,
        help='Enable OBD-II module'
    )
    parser.add_argument(
        '--disable-obd',
        action='store_true',
        help='Disable OBD-II module'
    )
    parser.add_argument(
        '--enable-gps',
        action='store_true',
        default=None,
        help='Enable GPS module'
    )
    parser.add_argument(
        '--disable-gps',
        action='store_true',
        help='Disable GPS module'
    )
    parser.add_argument(
        '--no-mqtt',
        action='store_true',
        help='Disable MQTT (will use HTTP only)'
    )

    # Logging level
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine which modules to enable
    enable_obd = True
    enable_gps = True
    enable_mqtt = True

    if args.obd_only:
        enable_obd = True
        enable_gps = False
    elif args.gps_only:
        enable_obd = False
        enable_gps = True
    else:
        # Use individual flags
        if args.enable_obd:
            enable_obd = True
        if args.disable_obd:
            enable_obd = False
        if args.enable_gps:
            enable_gps = True
        if args.disable_gps:
            enable_gps = False

    if args.no_mqtt:
        enable_mqtt = False

    # Create and run collector
    collector = VehicleDataCollector(
        enable_obd=enable_obd,
        enable_gps=enable_gps,
        enable_mqtt=enable_mqtt
    )
    collector.run()


if __name__ == "__main__":
    main()