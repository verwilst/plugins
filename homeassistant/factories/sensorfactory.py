import json
from ..lists import Sensors
from ..models import Sensor


class SensorFactory(object):

    @classmethod
    def from_webinterface(cls, webinterface) -> Sensors:
        json_sensors = json.loads(webinterface.get_sensor_configurations())

        sensors = Sensors()
        for sensor in json_sensors['config']:
            sensor['value'] = None
            sensors.append(
                Sensor(sensor, webinterface=webinterface)
            )

        return sensors
