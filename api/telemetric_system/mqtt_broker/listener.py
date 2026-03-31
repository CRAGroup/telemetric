#!/usr/bin/env python3
"""
MQTT Listener Service
Subscribes to MQTT topics and routes messages to handlers
"""

import logging
import time
import sys
import signal
import paho.mqtt.client as mqtt

from telemetric_system.mqtt_broker.handlers import handle_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MQTTListener:
    """MQTT client that listens for vehicle telemetry and routes to handlers"""

    def __init__(self, broker_host='0.0.0.0', broker_port=1883, client_id='telemetrics_listener'):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.client = None
        self.running = False

    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info("✓ Connected to MQTT broker %s:%d", self.broker_host, self.broker_port)

            # Subscribe to all vehicle topics
            topics = [
                ("vehicles/+/telemetry", 1),
                ("vehicles/+/alert_ack", 1),
                ("vehicles/+/config", 1),
                ("vehicles/+/cmd_resp", 1),
                ("vehicles/+/heartbeat", 0),
            ]

            for topic, qos in topics:
                client.subscribe(topic, qos)
                logger.info("✓ Subscribed to %s (QoS %d)", topic, qos)

        else:
            logger.error("✗ Connection failed with code %d", rc)
            error_messages = {
                1: "Incorrect protocol version",
                2: "Invalid client identifier",
                3: "Server unavailable",
                4: "Bad username or password",
                5: "Not authorized"
            }
            logger.error("  Reason: %s", error_messages.get(rc, "Unknown error"))

    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        if rc != 0:
            logger.warning("⚠️  Unexpected disconnection (code %d). Reconnecting...", rc)
        else:
            logger.info("Disconnected from MQTT broker")

    def on_message(self, client, userdata, msg):
        """Callback when a message is received"""
        try:
            logger.debug("📥 Received message on topic: %s", msg.topic)

            # Call the handler
            handle_message(msg.topic, msg.payload)

            logger.debug("✓ Message processed successfully")

        except Exception as e:
            logger.exception("✗ Error processing message on topic %s: %s", msg.topic, e)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback when subscription is confirmed"""
        logger.debug("Subscription confirmed (mid=%d, qos=%s)", mid, granted_qos)

    def on_log(self, client, userdata, level, buf):
        """Callback for MQTT client logs (optional, for debugging)"""
        # Uncomment to see detailed MQTT client logs
        # logger.debug("MQTT: %s", buf)
        pass

    def start(self):
        """Start the MQTT listener"""
        logger.info("=" * 70)
        logger.info("Starting MQTT Listener Service")
        logger.info("=" * 70)
        logger.info("Broker: %s:%d", self.broker_host, self.broker_port)
        logger.info("Client ID: %s", self.client_id)
        logger.info("=" * 70)

        # Create MQTT client
        self.client = mqtt.Client(client_id=self.client_id)

        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_log = self.on_log

        # Enable automatic reconnection
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)

        try:
            # Connect to broker
            logger.info("Connecting to MQTT broker...")
            self.client.connect(self.broker_host, self.broker_port, 60)

            # Start the network loop
            self.running = True
            self.client.loop_forever()

        except KeyboardInterrupt:
            logger.info("\n⚠️  Interrupted by user")
            self.stop()
        except Exception as e:
            logger.exception("✗ Fatal error: %s", e)
            self.stop()
            sys.exit(1)

    def stop(self):
        """Stop the MQTT listener"""
        if self.client and self.running:
            logger.info("Stopping MQTT listener...")
            self.running = False
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("✓ MQTT listener stopped")


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info("\n⚠️  Received signal %d, shutting down...", signum)
    sys.exit(0)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='MQTT Listener Service')
    parser.add_argument('--broker', default='0.0.0.0',
                        help='MQTT broker host (default: localhost)')
    parser.add_argument('--port', type=int, default=1883,
                        help='MQTT broker port (default: 1883)')
    parser.add_argument('--client-id', default='telemetrics_listener',
                        help='MQTT client ID (default: telemetrics_listener)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')

    args = parser.parse_args()

    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and start listener
    listener = MQTTListener(
        broker_host=args.broker,
        broker_port=args.port,
        client_id=args.client_id
    )

    try:
        listener.start()
    except Exception as e:
        logger.exception("Failed to start listener: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()