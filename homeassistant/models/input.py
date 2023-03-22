import logging
import json
from .entity import Entity
from ..const import MQTT_INPUT_STATE_TOPIC, MQTT_HOMEASSISTANT_CONFIG_TOPIC

logger = logging.getLogger(__name__)


class Input(Entity):

    def get_mqtt_state_topic(self):
        return MQTT_INPUT_STATE_TOPIC.replace('+', str(self.get('id')))

    def get_mqtt_state_payload(self):
        return self.get('state')

    def get_mqtt_config_topic(self):
        return MQTT_HOMEASSISTANT_CONFIG_TOPIC.format(self.get_type(), self.get('id'))

    def get_mqtt_config_payload(self):
        input_id = self.get('id')
        payload = {
            "~": f'openmotics/input/{input_id}',
            "name": self.pretty_name(),
            "unique_id": f'input_{input_id}',
            "state_topic": "~/state",
            "device": {
                "identifiers": f'input_{input_id}',
                "name": self.pretty_name()
            }
        }

        if self.get_class() is not None:
            payload['device_class'] = self.get_class()

        return json.dumps(payload)

    def get_type(self):
        return "binary_sensor"

    def get_class(self):
        """
        Get device class of binary sensor
        """
        if self.get('name').startswith('door_'):
            return 'door'
        elif self.get('name').startswith('window_'):
            return 'window'
        elif self.get('name').startswith('motion_'):
            return 'motion'
        return None

    def pretty_name(self):
        return self.get('name').replace('_', ' ').title()

    def set_state(self, new_state):

        if new_state not in ['ON', 'OFF']:
            logger.error('Unknown state received for input {}: '.format(new_state))
            return

        # Check to see if state has actually changed
        if new_state == self.get('state'):
            return

        self['state'] = new_state
        logger.info('Input {0} ({1}) turned {2}.'.format(self.get('name'),
                                                          self.get('id'),
                                                          new_state))

