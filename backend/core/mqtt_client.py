import json
import logging

import paho.mqtt.client as mqtt

from ..modules.cards import service as cards_service
from ..modules.scanners import service as scanners_service
from ..modules.tracking import service as tracking_service
from .database import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_SCANS = "rfid/scans"
MQTT_TOPIC_RESPONSES = "rfid/responses/"
MQTT_TOPIC_DISCOVERY = "tracking/discovery"
MQTT_TOPIC_HEARTBEAT = "tracking/heartbeat"

class RFIDMQTTClient:
    def __init__(self):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.discovered_tags = {} # MAC -> {rssi, timestamp}

    def on_connect(self, client, userdata, flags, rc, properties):
        logger.info(f"Connected to MQTT Broker with result code {rc}")
        client.subscribe(MQTT_TOPIC_SCANS)
        client.subscribe(MQTT_TOPIC_DISCOVERY)
        client.subscribe(MQTT_TOPIC_HEARTBEAT)

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic

            if topic == MQTT_TOPIC_SCANS:
                uid = payload.get("uid")
                if uid:
                    self.process_scan(uid)
            elif topic == MQTT_TOPIC_DISCOVERY:
                self.process_discovery(payload)
        except json.JSONDecodeError:
            logger.exception("Error decoding MQTT message")
        except Exception:
            logger.exception("Error processing MQTT message")

    def process_discovery(self, payload):
        from datetime import datetime as dt
        mac = payload.get("mac")
        rssi = payload.get("rssi")
        scanner = payload.get("scanner", "unknown")
        if not mac:
            return

        self.discovered_tags[mac] = {
            "rssi": rssi,
            "scanner": scanner,
            "timestamp": dt.now().isoformat(),
        }
        self.process_tracking(mac, rssi, scanner)
        self.cleanup_discovery()

    def cleanup_discovery(self):
        from datetime import datetime as dt
        from datetime import timedelta
        cutoff = dt.now() - timedelta(minutes=1)
        stale_keys = []
        for mac, info in self.discovered_tags.items():
            timestamp = info.get("timestamp")
            if not timestamp:
                stale_keys.append(mac)
                continue
            try:
                seen_at = dt.fromisoformat(timestamp)
            except ValueError:
                stale_keys.append(mac)
                continue
            if seen_at < cutoff:
                stale_keys.append(mac)

        for mac in stale_keys:
            self.discovered_tags.pop(mac, None)

    def process_tracking(self, mac, rssi, scanner_id):
        db = SessionLocal()
        try:
            # Update scanner info via service
            scanners_service.get_or_create_scanner(db, scanner_id)
            scanners_service.update_scanner_last_seen(db, scanner_id)

            # Log tracking via service
            result = tracking_service.log_tracking(db, mac, rssi, scanner_id)
            if result:
                log, student_name = result
                logger.info(f"Tracking logged for {student_name}: {log.zone} ({rssi}dBm) via {scanner_id}")

        except Exception as e:
            logger.error(f"Error logging tracking: {e}")
            db.rollback()
        finally:
            db.close()

    def process_scan(self, uid):
        db = SessionLocal()
        try:
            # Delegate business logic to cards service
            authorized, name, status = cards_service.process_card_scan(db, uid)

            # Publish response
            response_topic = f"{MQTT_TOPIC_RESPONSES}{uid}"
            response_payload = {
                "authorized": authorized,
                "name": name
            }
            self.client.publish(response_topic, json.dumps(response_payload))
            logger.info(f"Published response for {uid}: {status}")

        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
        finally:
            db.close()

    def start(self):
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            logger.info("MQTT Client loop started")
        except Exception as e:
            logger.error(f"Could not connect to MQTT Broker: {e}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT Client disconnected")

mqtt_client = RFIDMQTTClient()
