from city_model import CityModel

class Building(CityModel):
    def __init__(self, origin):
        super(Building, self).__init__()
        self.origin = origin
        self.height = 40
        self.zBase = self.origin.z + self.height / 2

    def template(self):
        return """
          <model name="{{model.name}}">
             <static>1</static>
             <link name="{{model.name}}_link">
                <pose frame="">{{model.origin.x}} {{model.origin.y}} {{model.zBase}} 0 0 0</pose>
                <collision name="{{model.name}}_collision">
                   <geometry>
                      <box>
                         <size>12 12 {{model.height}}</size>
                      </box>
                   </geometry>
                </collision>
                <visual name="{{model.name}}_visual">
                   <material>
                      <script>
                         <uri>file://media/materials/scripts/gazebo.material</uri>
                         <name>Gazebo/Grey</name>
                      </script>
                      <ambient>1 1 1 1</ambient>
                   </material>
                   <meta>
                      <layer>0</layer>
                   </meta>
                   <geometry>
                      <box>
                         <size>12 12 {{model.height}}</size>
                      </box>
                   </geometry>
                </visual>
             </link>
          </model>"""
