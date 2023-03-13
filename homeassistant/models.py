import logging
import json
import sys

from collections import UserDict
from .const import MQTT_OUTPUT_STATE_TOPIC, MQTT_HOMEASSISTANT_CONFIG_TOPIC, MQTT_SENSOR_STATE_TOPIC, SENSOR_UNIT

paho_mqtt_wheel = '/opt/openmotics/python/plugins/HomeAssistant/paho_mqtt-1.6.1-py3-none-any.whl'
if paho_mqtt_wheel not in sys.path:
    sys.path.insert(0, paho_mqtt_wheel)
import paho.mqtt.client as client

logger = logging.getLogger(__name__)


class Entity(dict):
    pass

class Output(Entity):

    output_type = 'output'

    def __init__(self, *args, webinterface):
        Entity.__init__(self, *args)
        self._webinterface = webinterface

    def set_state(self, new_state):
        """
        Return False when the changed didn't change, otherwise return True
        """

        if new_state not in ['ON', 'OFF']:
            logger.error('Unknown state received for output {}: '.format(new_state))
            return

        # Check to see if state has actually changed
        if new_state == self.get('state'):
            return

        is_on = False
        if new_state == 'ON':
            is_on = True

        result = json.loads(self._webinterface.set_output(id=self.get('id'), is_on=is_on))
        if result['success'] is False:
            logger.error('Failed to turn {0} output {1}: {2}'.format(new_state,
                                                                     self.get('id'),
                                                                     result.get('msg', 'Unknown error')))
            return

        logger.info('Output {0} ({1}) turned {2}.'.format(self.get('name'),
                                                          self.get('id'),
                                                          new_state,))
        self['state'] = new_state

    def pretty_name(self):
        return self.get('name').replace('_', ' ').title()

    def get_type(self):
        return self.output_type

    def get_mqtt_state_topic(self):
        return MQTT_OUTPUT_STATE_TOPIC.replace('+', str(self.get('id')))

    def get_mqtt_state_payload(self):
        return self.get('state')

    def get_mqtt_config_topic(self):
        return MQTT_HOMEASSISTANT_CONFIG_TOPIC.format(self.get_type(), self.get('id'))

    def get_mqtt_config_payload(self):
        output_id = self.get('id')
        return {
            "~": f'openmotics/output/{output_id}',
            "name": self.pretty_name(),
            "unique_id": f'output_{output_id}',
            "state_topic": "~/state",
            "command_topic": "~/set",
            "device": {
                "identifiers": output_id,
                "name": self.pretty_name()
            }
        }

class Light(Output):

    output_type = 'light'


class Sensor(Entity):

    def __init__(self, *args, webinterface):
        Entity.__init__(self, *args)
        self._webinterface = webinterface

    def get_mqtt_state_topic(self):
        return MQTT_SENSOR_STATE_TOPIC.replace('{id}', str(self.get('id')))

    def get_mqtt_state_payload(self):
        return self.get('value')

    def get_mqtt_config_topic(self):
        return MQTT_HOMEASSISTANT_CONFIG_TOPIC.format('sensor', self.get('id'))

    def get_mqtt_config_payload(self):
        sensor_id = self.get('id')
        name = self.get('name')
        physical_quantity = self.get('physical_quantity')
        unit = self.get('unit')
        return {
            'device_class': physical_quantity,
            'name': f"{name} {physical_quantity}".title(),
            'unique_id': f'sensor_{sensor_id}',
            'state_topic': f"openmotics/sensor/{sensor_id}/state",
            'unit_of_measurement': SENSOR_UNIT[unit],
            'device': {
                "identifiers": f'sensor_{sensor_id}',
                "name": f"{name} {physical_quantity}".title()
            }
        }


class MQTTClient(client.Client):

    def send_configs(self, entities):
        for entity in entities:
            try:
                self.publish(entity.get_mqtt_config_topic(),
                             payload=json.dumps(entity.get_mqtt_config_payload()),
                             qos=1,
                             retain=False)
            except Exception as ex:
                logger.exception('Error sending data to broker')

    def send_state(self, entity):
        try:
            self.publish(topic=entity.get_mqtt_state_topic(),
                         payload=entity.get_mqtt_state_payload(),
                         qos=1,
                         retain=True)
        except Exception as ex:
            logger.exception('Error sending data to broker')
