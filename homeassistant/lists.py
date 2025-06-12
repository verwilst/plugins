import json
import logging
from .models import Light, Output, Entity

logger = logging.getLogger(__name__)


class Entities(list):

    def by_id(self, entity_id) -> Entity:
        return next((item for item in self if item.get('id') == entity_id), None)

    def publish_state(self, mqttclient) -> None:
        for entity in self:
            entity.publish_state(mqttclient)

    def publish_config(self, mqttclient) -> None:
        for entity in self:
            entity.publish_config(mqttclient)


class Outputs(Entities):

    def get_lights(self):
        return [output for output in self if isinstance(output, Light)]

    def by_state(self, state):
        return [item for item in self if item.get('state') == state]


class Inputs(Entities):
    pass


class Sensors(Entities):
    pass

