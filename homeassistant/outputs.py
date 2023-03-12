from .models.light import Light
from .models.output import Output


class Outputs(list):

    def get_lights(self):
        lights = Outputs()
        for output in self:
            if isinstance(output, Light):
                lights.append(output)
        return lights

    def by_id(self, output_id) -> Output:
        return next((item for item in self if item.get('id') == output_id), None)

    def by_state(self, state):
        return [(item for item in self if item.get('state') == state)]