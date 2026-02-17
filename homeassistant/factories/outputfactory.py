import json
import logging
from ..lists import Outputs
from ..models import Light, Output

from ..const import OUTPUT_TYPE_LIGHT, OUTPUT_TYPE_DIMMER

logger = logging.getLogger(__name__)


class OutputFactory(object):

    @classmethod
    def from_webinterface(cls, webinterface) -> Outputs:

        json_outputs = json.loads(webinterface.get_output_configurations())
        logger.info(json.dumps(json_outputs))
        json_status = json.loads(webinterface.get_output_status())
        logger.info(json.dumps(json_status))

        # Unable to fetch output configurations correctly
        if json_outputs['success'] is False:
            raise RuntimeError('Failed to get output configurations: {0}'.format(json_outputs))

        if json_status['success'] is False:
            raise RuntimeError('Failed to get output status: {0}'.format(json_status))

        outputs = Outputs()
        for output in json_outputs['config']:

            # Ignore unused outputs
            if not output['in_use']:
                continue

            # Remove outputs without a name
            if output['name'] == "":
                continue

            status = next((item for item in json_status['status'] if item["id"] == output.get('id')), None)

            # Light
            if output['module_type'] == "d":
                output['dimmer'] = status["dimmer"]

            # Set default state
            if status["status"] == 0:
                output['state'] = 'OFF'
            else:
                output['state'] = 'ON'

            outputs.append(
                Output(output, webinterface=webinterface)
            )
        return outputs
