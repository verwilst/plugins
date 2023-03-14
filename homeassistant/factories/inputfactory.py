import json
import logging
from ..lists import Inputs

logger = logging.getLogger(__name__)


class InputFactory(object):

    @classmethod
    def from_webinterface(cls, webinterface) -> Inputs:
        json_inputs = json.loads(webinterface.get_input_configurations())
        logger.info(json_inputs)

        # Unable to fetch output configurations correctly
        if json_inputs['success'] is False:
            raise RuntimeError('Failed to get input configurations: {0}'.format(json_inputs))

        return Inputs()
