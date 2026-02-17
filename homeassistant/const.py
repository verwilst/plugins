from enum import Enum

OUTPUT_TYPE_OUTLET = 0
OUTPUT_TYPE_DIMMER = 29
OUTPUT_TYPE_SHUTTER = 127
OUTPUT_TYPE_LIGHT = 255

MQTT_OUTPUT_COMMAND_TOPIC = 'renson/output/+/set'
MQTT_OUTPUT_STATE_TOPIC = 'renson/output/+/state'
MQTT_HOMEASSISTANT_STATUS_TOPIC = 'homeassistant/status'
MQTT_HOMEASSISTANT_CONFIG_TOPIC = 'homeassistant/{}/{}/config'
MQTT_SENSOR_STATE_TOPIC = 'renson/sensor/{id}/state'
MQTT_INPUT_STATE_TOPIC = 'renson/input/+/state'

SENSOR_UNIT = {'percent': '%',
               'celcius': '°C'}