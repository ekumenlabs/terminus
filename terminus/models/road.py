from city_model import CityModel

class Road(CityModel):
    def __init__(self, name, width):
        super(Road, self).__init__()
        self.name = name
        self.width = width
        self.segments = []

    def add_segment(self, coordinates):
        self.segments.append(coordinates)

    def material_name(self):
        raise NotImplementedError()

    def template(self):
        return """
          <road name="{{model.name}}">
            <width>{{model.width}}</width>
            <material>
              <script>
                <uri>file://media/materials/scripts/gazebo.material</uri>
                <name>{{model.material_name()}}</name>
              </script>
            </material>
            {% for point in model.segments %}
              {{ point.to_sdf() }}
            {% endfor %}
          </road>"""


class Street(Road):
    def __init__(self, name):
        super(Street, self).__init__(name, 5)

    def material_name(self):
        return 'Gazebo/Residential'


class Trunk(Road):
    def __init__(self, name):
        super(Trunk, self).__init__(name, 10)

    def material_name(self):
        return 'Gazebo/Trunk'
