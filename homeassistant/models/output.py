import logging
import json
from .device import Device
from ..const import MQTT_OUTPUT_STATE_TOPIC, MQTT_HOMEASSISTANT_CONFIG_TOPIC, OUTPUT_TYPE_DIMMER

logger = logging.getLogger(__name__)


class Output(Device):

    output_type = 'output'

    def __init__(self, *args, webinterface):
        Device.__init__(self, *args)
        self._webinterface = webinterface

    def set_state(self, new_state):

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
        if self.get('module_type') in ["o", "O"]:
            return "light"
        elif self.get('module_type') in ["d"]:
            return "number"

    def get_mqtt_state_topic(self):
        return MQTT_OUTPUT_STATE_TOPIC.replace('+', str(self.get('id')))

    def get_mqtt_state_payload(self):
        return self.get('state')

    def get_mqtt_config_topic(self):
        return MQTT_HOMEASSISTANT_CONFIG_TOPIC.format(self.get_type(), self.get('id'))

    def get_mqtt_config_payload(self):
        output_id = self.get('id')
        payload = {
            "~": f'renson/output/{output_id}',
            "name": self.pretty_name(),
            "unique_id": f'renson_output_{output_id}',
            "object_id": f'renson_output_{output_id}',
            "state_topic": "~/state",
            "command_topic": "~/set",
            "device": {
                "identifiers": [f'renson_output_{output_id}'],
                "name": self.pretty_name(),
                "manufacturer": "Renson",
                "suggested_area": "Bedroom"
            }
        }
        if self.get('module_type') == "d":
            logger.info("Dimmer")
            logger.info(self)
            payload.update({"mode": "box"})
            #payload.update({"percentage_state_topic": "~/speed/percentage_state",
             #   "percentage_command_topic": "~/speed/percentage"})
    #         payload.update({"brightness_scale": self.get("dimmer"),
    #         "brightness_state_topic": "~/brightness/state",
    # "brightness_command_topic": "~/brightness/set"})
        return json.dumps(payload)
