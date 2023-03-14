import json
import sys
import logging

paho_mqtt_wheel = '/opt/openmotics/python/plugins/HomeAssistant/paho_mqtt-1.6.1-py3-none-any.whl'
if paho_mqtt_wheel not in sys.path:
    sys.path.insert(0, paho_mqtt_wheel)
import paho.mqtt.client as client

logger = logging.getLogger(__name__)


class MQTTClient(client.Client):

    def send_state(self, entity):
        try:
            self.publish(topic=entity.get_mqtt_state_topic(),
                         payload=entity.get_mqtt_state_payload(),
                         qos=1,
                         retain=True)
        except Exception as ex:
            logger.exception('Error sending data to broker')