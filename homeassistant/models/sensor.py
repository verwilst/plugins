import logging
import json
from .entity import Entity
from ..const import MQTT_HOMEASSISTANT_CONFIG_TOPIC, MQTT_SENSOR_STATE_TOPIC, SENSOR_UNIT

logger = logging.getLogger(__name__)


class Sensor(Entity):

    def __init__(self, *args, webinterface):
        Entity.__init__(self, *args)
        self._webinterface = webinterface

    def get_mqtt_state_topic(self):
        return MQTT_SENSOR_STATE_TOPIC.replace('{id}', str(self.get('id')))

    def get_mqtt_state_payload(self):
        return self.get('state')

    def get_mqtt_config_topic(self):
        return MQTT_HOMEASSISTANT_CONFIG_TOPIC.format('sensor', self.get('id'))

    def get_mqtt_config_payload(self):
        sensor_id = self.get('id')
        name = self.get('name')
        physical_quantity = self.get('physical_quantity')
        unit = self.get('unit')
        return json.dumps({
            'device_class': physical_quantity,
            'name': f"{name} {physical_quantity}".title(),
            'unique_id': f'sensor_{sensor_id}',
            'state_topic': f"openmotics/sensor/{sensor_id}/state",
            'unit_of_measurement': SENSOR_UNIT[unit],
            'device': {
                "identifiers": f'sensor_{sensor_id}',
                "name": f"{name} {physical_quantity}".title()
            }
        })
