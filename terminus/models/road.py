from city_model import CityModel


class Road(CityModel):
    def __init__(self, width, name=None):
        super(Road, self).__init__(name)
        self.width = width
        self.segments = []

    def add_segment(self, point):
        self.segments.append(point)

    def material_name(self):
        raise NotImplementedError()

    @classmethod
    def template(cls):
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
              <point>{{point.x}} {{point.y}} {{point.z}}</point>
            {% endfor %}
          </road>"""


class Street(Road):
    def __init__(self, name=None):
        super(Street, self).__init__(5, name)

    def material_name(self):
        return 'Gazebo/Residential'


class Trunk(Road):
    def __init__(self, name=None):
        super(Trunk, self).__init__(10, name)

    def material_name(self):
        return 'Gazebo/Trunk'
