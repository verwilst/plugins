from .models import Light, Output, Entity

class Entities(list):

    def by_id(self, entity_id) -> Entity:
        return next((item for item in self if item.get('id') == entity_id), None)

class Outputs(Entities):

    def get_lights(self):
        lights = Outputs()
        for output in self:
            if isinstance(output, Light):
                lights.append(output)
        return lights

    def by_state(self, state):
        return [(item for item in self if item.get('state') == state)]


class Sensors(Entities):
    pass

