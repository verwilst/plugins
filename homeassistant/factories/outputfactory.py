import json
import logging
from ..lists import Outputs
from ..models import Light

from ..const import OUTPUT_TYPE_LIGHT

logger = logging.getLogger(__name__)


class OutputFactory(object):

    @classmethod
    def from_webinterface(cls, webinterface) -> Outputs:

        json_outputs = json.loads(webinterface.get_output_configurations())
        json_status = json.loads(webinterface.get_output_status())

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

            # Light
            if output['type'] == OUTPUT_TYPE_LIGHT:

                # Set default state
                status = next((item['status'] for item in json_status['status'] if item.get('id') == output.get('id')))
                if status == 0:
                    output['state'] = 'OFF'
                else:
                    output['state'] = 'ON'

                outputs.append(
                    Light(output, webinterface=webinterface)
                )
        return outputs
