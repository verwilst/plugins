import logging
import json

from collections import UserDict

logger = logging.getLogger(__name__)

class Output(UserDict):

    output_type = 'output'

    def __init__(self, *args, webinterface):
        UserDict.__init__(self, *args)
        self._webinterface = webinterface

    def set_state(self, new_state):
        """
        Return False when the changed didn't change, otherwise return True
        """

        if new_state not in ['ON', 'OFF']:
            logger.error('Unknown state received for output {}: '.format(new_state))
            return

        # Check to see if state has actually changed
        if new_state == self.get('state'):
            return

        is_on = False
        if new_state == 'ON':
            is_on = True

        result = json.loads(self._webinterface.set_output(id=self.get('id'), is_on=is_on))
        if result['success'] is False:
            logger.error('Failed to turn {0} output {1}: {2}'.format(new_state,
                                                                     self.get('id'),
                                                                     result.get('msg', 'Unknown error')))
            return

        logger.info('Output {0} ({1}) turned {2}.'.format(self.get('name'),
                                                          self.get('id'),
                                                          new_state,))
        self['state'] = new_state

    def pretty_name(self):
        return self.get('name').replace('_', ' ').title()

    def get_type(self):
        return self.output_type
