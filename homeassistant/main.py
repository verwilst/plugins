"""
HomeAssistant through MQTT
"""
import json
import logging
import time
import six
import re
import sys

from threading import Thread
from .const import MQTT_OUTPUT_COMMAND_TOPIC, MQTT_HOMEASSISTANT_STATUS_TOPIC

from .factories import OutputFactory, InputFactory, SensorFactory

from plugin_runtime.base import OMPluginBase, PluginConfigChecker, om_expose, output_status, input_status, background_task
if False:  # MYPY
    pass

logger = logging.getLogger(__name__)


class HomeAssistantPlugin(OMPluginBase):
    """
    HomeAssistant plugin using an MQTT broker
    """
    name = 'HomeAssistant'
    version = '0.1.0'
    interfaces = [('config', '1.0')]

    # configuration
    config_description = [
        {'name': 'hostname',
         'type': 'str',
         'description': 'MQTT broker hostname or IP address.'},
        {'name': 'port',
         'type': 'int',
         'description': 'MQTT broker port. Default: 1883'},
        {'name': 'username',
         'type': 'str',
         'description': 'MQTT broker username. Default: openmotics'},
        {'name': 'password',
         'type': 'password',
         'description': 'MQTT broker password.'}
    ]

    default_config = {
        'port': 1883,
        'username': 'openmotics'
    }

    def __init__(self, webinterface, connector):
        super(HomeAssistantPlugin, self).__init__(webinterface=webinterface,
                                                  connector=connector)
        logger.info('Starting %s plugin %s ...', self.name, self.version)

        # set config on default config and instantiate a validator
        self._config = self.read_config(HomeAssistantPlugin.default_config)
        self._config_checker = PluginConfigChecker(HomeAssistantPlugin.config_description)

        self._read_config()

        paho_mqtt_wheel = '/opt/openmotics/python/plugins/HomeAssistant/paho_mqtt-1.6.1-py3-none-any.whl'
        if paho_mqtt_wheel not in sys.path:
            sys.path.insert(0, paho_mqtt_wheel)

        self.mqttclient = None
        self.outputs = None
        self.inputs = None
        self.sensors = None

        self._load_configurations()

        self._try_mqtt_connect()

        logger.info("%s plugin started", self.name)

    def _read_config(self):
        # broker
        self._mqtt_hostname = self._config.get('hostname')
        self._mqtt_port = self._config.get('port')
        self._mqtt_username = self._config.get('username')
        self._mqtt_password = self._config.get('password')

        self._enabled = self._mqtt_hostname is not None and self._mqtt_port is not None


    @om_expose
    def get_config_description(self):
        """
        Returns the config_description.
        Used to render the structure in the gateway portal.
        """
        return json.dumps(self.config_description)

    @om_expose
    def get_config(self):
        """
        Returns the (filled in) config currently loaded.
        When this is the first time, this will be the default config.
        Otherwise, the adapted version in the portal configuration will be retrieved
        """
        return json.dumps(self._config)

    @om_expose
    def set_config(self, config):
        """
        Reads and validates config values from portal and sets new config.
        """
        try:
            config = json.loads(config)
            for key in config:
                if isinstance(config[key], six.string_types):
                    config[key] = str(config[key])
            self._config_checker.check_config(config)
            self._config = config
            self._read_config()
            self.write_config(config)
            if self._enabled:
                thread = Thread(target=self._load_configurations)
                thread.start()
        except Exception as ex:
            logger.exception('Error saving configuration')

        self._try_mqtt_connect()

        return json.dumps({'success': True})

    def _load_configurations(self, replace=False):
        """
        Retry until we have retrieved every available configuration
        """
        should_load = True
        while should_load:
            if self.outputs is None or replace is True:
                try:
                    self.outputs = OutputFactory.from_webinterface(self.webinterface)
                    logger.info('Detected {0} lights'.format(len(self.outputs.get_lights())))
                except RuntimeError as err:
                    logger.error(err)

            if self.inputs is None or replace is True:
                try:
                    self.inputs = InputFactory.from_webinterface(self.webinterface)
                    logger.info('Detected {0} inputs'.format(len(self.inputs)))
                except RuntimeError as err:
                    logger.error(err)

            if self.sensors is None or replace is True:
                try:
                    self.sensors = SensorFactory.from_webinterface(self.webinterface)
                    logger.info('Detected {0} sensors'.format(len(self.sensors)))
                except RuntimeError as err:
                    logger.error(err)

            should_load = not all([self.outputs, self.sensors])
            if should_load:
                logger.info('Retrying loading of configurations')
                time.sleep(15)

    def _try_mqtt_connect(self):
        if self._enabled is True:
            try:
                import paho.mqtt.client as mqtt
                self.mqttclient = mqtt.Client()
                if self._mqtt_username not in [None, '']:
                    logger.info("MQTTClient is using username '{0}' and password".format(self._mqtt_username))
                    self.mqttclient.username_pw_set(self._mqtt_username, self._mqtt_password)
                self.mqttclient.on_message = self.on_message
                self.mqttclient.on_connect = self.on_connect
                self.mqttclient.connect(self._mqtt_hostname, self._mqtt_port, 5)
                self.mqttclient.loop_start()
            except Exception as ex:
                logger.exception('Error connecting to MQTT broker')
        else:
            logger.info('MQTT not enabled.')

    def on_message(self, client, userdata, msg):

        payload = msg.payload.decode("utf-8")

        regexp = MQTT_OUTPUT_COMMAND_TOPIC.replace('+', '(\d+)')
        # Output set command
        if re.search(regexp, msg.topic) is not None:
            output_id = int(re.findall(regexp, msg.topic)[0])

            output = self.outputs.by_id(output_id)

            # Make sure the output exists
            if output is None:
                logger.info('Unknown output {0} ignored'.format(output_id))
                return

            output.set_state(payload)
            output.publish_state(self.mqttclient)

        # HomeAssistant status message
        elif msg.topic == MQTT_HOMEASSISTANT_STATUS_TOPIC:
            if payload == 'online':
                # When HomeAssistant reloads/starts, get the latest configurations to make sure we're up to date.
                self._load_configurations(replace=True)
                self.outputs.publish_config(self.mqttclient)
                self.inputs.publish_config(self.mqttclient)
                self.sensors.publish_config(self.mqttclient)

        else:
            logger.info('Message with topic {0} ignored'.format(msg.topic))

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            logger.error('Error connecting: rc={0}', rc)
            return

        logger.info('Connected to MQTT broker {0}:{1}'.format(self._mqtt_hostname, self._mqtt_port))
        # subscribe to output command topic if provided

        for topic in [MQTT_OUTPUT_COMMAND_TOPIC, MQTT_HOMEASSISTANT_STATUS_TOPIC]:
            try:
                self.mqttclient.subscribe(topic)
                logger.info('Subscribed to {0}'.format(topic))
            except Exception as ex:
                logger.exception(f'Could not subscribe to {topic}')

    @output_status
    def output_status(self, status):
        if self._enabled:
            status_ids = [item[0] for item in status]

            for output in self.outputs:
                if output['id'] in status_ids:
                    if output.get('state') != 'ON':
                        output.set_state('ON')
                        thread = Thread(
                            target=output.publish_state,
                            args=(self.mqttclient,)
                        )
                        thread.start()
                else:
                    if output.get('state') != 'OFF':
                        output.set_state('OFF')
                        thread = Thread(
                            target=output.publish_state,
                            args=(self.mqttclient,)
                        )
                        thread.start()

    @input_status(version=2)
    def input_status(self, data):
        if self._enabled:
            input_id = data.get('input_id')
            input = self.inputs.by_id(input_id)

            if input is None:
                logger.info('Unknown input {0} ignored'.format(input_id))
                return

            state = 'ON' if data.get('status') else 'OFF'

            if input.get('state') != state:
                input.set_state(state)
                input.publish_state(self.mqttclient)


    @background_task
    def background_task_sensor_status(self):
        while True:
            result = json.loads(self.webinterface.get_sensor_status())
            if result['success'] is False:
                logger.error('Failed to get sensor status: {}'.format(result.get('msg', 'Unknown error')))
                return

            for status in result['status']:
                sensor = self.sensors.by_id(status['id'])
                sensor['state'] = status['value']
                thread = Thread(
                    target=sensor.publish_state,
                    args=[self.mqttclient]
                )
                thread.start()

            time.sleep(120)
