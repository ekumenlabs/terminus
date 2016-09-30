from city_model import CityModel


class Block(CityModel):
    def __init__(self, origin, vertices, height=0.15, name=None):
        """
        Generates one block of a city with a shape defined by an array of
        vertices and the specified height.
        """
        super(Block, self).__init__(name)
        self.origin = origin
        self.height = height
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
