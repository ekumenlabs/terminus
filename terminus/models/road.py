from city_model import CityModel
import random
from pprint import pprint

class Road(CityModel):
    def __init__(self, width, name=None):
        super(Road, self).__init__(name)
        self.width = width
        self.points = []

    @classmethod
    def from_points(cls, array_of_points):
        road = cls(cls.default_width())
        for point in array_of_points:
            road.add_point(point)
        return road

    def add_point(self, point):
        self.points.append(point)

    def material_name(self):
        raise NotImplementedError()

    def __eq__(self, other):

        return (self.__class__ == other.__class__) and \
               (self.width == other.width) and \
               (self.points == other.points)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self):
        return "Road: " + reduce(lambda acc, point: acc + str(point), self.points, '')

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
            {% for point in model.points %}
              <point>{{point.x}} {{point.y}} {{point.z}}</point>
            {% endfor %}
          </road>"""


class Street(Road):
    def __init__(self, name=None):
        super(Street, self).__init__(self.default_width(), name)

    @classmethod
    def default_width(cls):
        return 5

    def material_name(self):
        colors = ['Red', 'Blue', 'White', 'Yellow', 'Green', 'Black', 'Purple']
        return 'Gazebo/' + random.choice(colors)
        #return 'Gazebo/Residential'


class Trunk(Road):
    def __init__(self, name=None):
        super(Trunk, self).__init__(self.default_width(), name)

    @classmethod
    def default_width(cls):
        return 10

    def material_name(self):
        return 'Gazebo/Trunk'
