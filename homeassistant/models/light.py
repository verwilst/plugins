import logging
from .output import Output

logger = logging.getLogger(__name__)


class Light(Output):

    output_type = 'light'

