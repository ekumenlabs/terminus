from city_model import CityModel
from geometry.point import Point


class Block(CityModel):
    def __init__(self, origin, vertices, height=0.15, name=None):
        """
        Generates one block of a city with a shape defined by an array of
        vertices and the specified height.
        """
        super(Block, self).__init__(name)
        self.origin = origin
        self.height = height
        # TODO: review using 3D points when polyline only uses 2D.
        self.vertices = vertices

    @classmethod
    def template(cls):
        return """
          <model name="{{model.name}}">
             <static>1</static>
             <allow_auto_disable>1</allow_auto_disable>
             <link name="{{model.name}}_link">
                <pose frame="">
                  {{model.origin.x}} {{model.origin.y}} {{model.origin.z}}
                  0 0 0
                </pose>
                <collision name="{{model.name}}_collision">
                   <geometry>
                        <polyline>
                        {% for vertex in model.vertices %}
                            <point>{{vertex.x}} {{vertex.y}}</point>
                        {% endfor %}
                        <height>{{model.height}}</height>
                        </polyline>
                   </geometry>
                </collision>
                <visual name="{{model.name}}_visual">
                   <material>
                      <script>
                          <uri>
                            file://media/materials/scripts/gazebo.material
                          </uri>
                         <name>Gazebo/Grey</name>
                      </script>
                      <ambient>1 1 1 1</ambient>
                   </material>
                   <meta>
                      <layer>0</layer>
                   </meta>
                   <geometry>
                        <polyline>
                        {% for vertex in model.vertices %}
                            <point>{{vertex.x}} {{vertex.y}}</point>
                        {% endfor %}
                        <height>{{model.height}}</height>
                        </polyline>
                   </geometry>
                </visual>
             </link>
          </model>"""

    @staticmethod
    def square(origin, size):
        """
        Generate a square block of the given size and in the given position.
        """
        w = size / 2.0
        vertices = [
            Point(w, w, 0),
            Point(-w, w, 0),
            Point(-w, -w, 0),
            Point(w, -w, 0)
        ]
        return Block(origin, vertices)
