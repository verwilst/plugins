import json
import logging
from ..lists import Inputs
from ..models import Input

logger = logging.getLogger(__name__)


class InputFactory(object):

    @classmethod
    def from_webinterface(cls, webinterface) -> Inputs:
        json_inputs = json.loads(webinterface.get_input_configurations())

        logger.info("GROUP ACTIONS {}".format(webinterface.get_group_action_configurations()))

        # Unable to fetch output configurations correctly
        if json_inputs['success'] is False:
            raise RuntimeError('Failed to get input configurations: {0}'.format(json_inputs))

        inputs = Inputs()
        for input in json_inputs['config']:

            # We DO NOT ignore devices that are not in use. As long as they have a name, we're adding them.
            # We need to assign an empty OM automation otherwise for them to be visible.

            # Remove inputs without a name
            if input['name'] == "":
                continue

            logger.info(input)
            inputs.append(Input(input))

        return inputs
