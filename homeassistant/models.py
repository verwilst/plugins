import logging
import json
import sys

from collections import UserDict
from .const import MQTT_OUTPUT_STATE_TOPIC, MQTT_HOMEASSISTANT_CONFIG_TOPIC

paho_mqtt_wheel = '/opt/openmotics/python/plugins/HomeAssistant/paho_mqtt-1.6.1-py3-none-any.whl'
if paho_mqtt_wheel not in sys.path:
    sys.path.insert(0, paho_mqtt_wheel)
import paho.mqtt.client as client

logger = logging.getLogger(__name__)


class Output(UserDict):

    output_type = 'output'

    def __init__(self, *args, webinterface):
        UserDict.__init__(self, *args)
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


class Light(Output):

    output_type = 'light'


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