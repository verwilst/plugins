import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Entity(ABC, dict):

    @abstractmethod
    def get_mqtt_state_topic(self):
        pass

    @abstractmethod
    def get_mqtt_state_payload(self):
        pass

    @abstractmethod
    def get_mqtt_config_topic(self):
        pass

    @abstractmethod
    def get_mqtt_config_payload(self):
        pass

    @abstractmethod
    def set_state(self, new_state):
        pass

    def publish_state(self, mqttclient):
        try:
            mqttclient.publish(topic=self.get_mqtt_state_topic(),
                         payload=self.get_mqtt_state_payload(),
                         qos=1,
                         retain=True)
        except Exception as ex:
            logger.exception('Error sending data to broker')

    def publish_config(self, mqttclient):
        try:
            mqttclient.publish(self.get_mqtt_config_topic(),
                         payload=self.get_mqtt_config_payload(),
                         qos=1,
                         retain=False)
        except Exception as ex:
            logger.exception('Error sending data to broker')

