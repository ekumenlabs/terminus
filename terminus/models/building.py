from city_model import CityModel


class Building(CityModel):
    def __init__(self, origin, size, height, name=None):
        """
        Generates a square building of base (size * size) and the given height,
        located at position 'origin'.
        """
        super(Building, self).__init__(name)
        self.origin = origin
        self.size = size
        self.height = height

    def box_base(self):
        return self.origin.z + self.height / 2

    @classmethod
    def template(cls):
        return """
          <model name="{{model.name}}">
             <static>1</static>
             <link name="{{model.name}}_link">
                <pose frame="">
                  {{model.origin.x}} {{model.origin.y}} {{model.box_base()}}
                  0 0 0
                </pose>
                <collision name="{{model.name}}_collision">
                   <geometry>
                      <box>
                        <size>
                          {{model.size}} {{model.size}} {{model.height}}
                        </size>
                      </box>
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
                      <box>
                        <size>
                          {{model.size}} {{model.size}} {{model.height}}
                        </size>
                      </box>
                   </geometry>
                </visual>
             </link>
          </model>"""
