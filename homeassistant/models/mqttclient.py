import sys
import logging
import json

paho_mqtt_wheel = '/opt/openmotics/python/plugins/HomeAssistant/paho_mqtt-1.6.1-py3-none-any.whl'
if paho_mqtt_wheel not in sys.path:
    sys.path.insert(0, paho_mqtt_wheel)
import paho.mqtt.client as client
from ..const import MQTT_OUTPUT_STATE_TOPIC, MQTT_HOMEASSISTANT_CONFIG_TOPIC

logger = logging.getLogger(__name__)


class MQTTClient(client.Client):

    def send_configs(self, outputs):
        for output in outputs:
            try:
                self.publish(MQTT_HOMEASSISTANT_CONFIG_TOPIC.format(output.get_type(),
                                                                    output.get('name').lower()),
                             payload=json.dumps({
                                 "~": "openmotics/output/{}".format(output.get('id')),
                                 "name": output.pretty_name(),
                                 "unique_id": output.get('name').lower(),
                                 "state_topic": "~/state",
                                 "command_topic": "~/set",
                                 "device": {
                                     "identifiers": output.get('name').lower(),
                                     "name": output.pretty_name()
                                 }
                             }),
                             qos=1,
                             retain=False)
            except Exception as ex:
                logger.exception('Error sending data to broker')

    def send_state(self, output):
        try:
            self.publish(topic=MQTT_OUTPUT_STATE_TOPIC.replace('+', str(output.get('id'))),
                         payload=output.get('state'),
                         qos=1,
                         retain=True)
        except Exception as ex:
            logger.exception('Error sending data to broker')
