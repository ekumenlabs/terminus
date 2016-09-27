from city_model import CityModel


class GroundPlane(CityModel):
    def __init__(self, size, origin, name=None):
        super(GroundPlane, self).__init__(name)
        self.size = size
        self.origin = origin

    def template(self):
        return """
          <model name="{{model.name}}">
            <static>1</static>
            <pose frame=''>{{model.origin.x}} {{model.origin.y}} 0 0 0 0</pose>
            <link name='{{model.name}}_link'>
              <collision name='{{model.name}}'>
                <geometry>
                  <plane>
                    <normal>0 0 1</normal>
                    <size>{{model.size}} {{model.size}}</size>
                  </plane>
                </geometry>
                <surface>
                  <friction>
                    <ode>
                      <mu>100</mu>
                      <mu2>50</mu2>
                    </ode>
                    <torsional>
                      <ode/>
                    </torsional>
                  </friction>
                  <contact>
                    <ode/>
                  </contact>
                  <bounce/>
                </surface>
                <max_contacts>10</max_contacts>
              </collision>
              <visual name='{{model.name}}'>
                <cast_shadows>0</cast_shadows>
                <geometry>
                  <plane>
                    <normal>0 0 1</normal>
                    <size>{{model.size}} {{model.size}}</size>
                  </plane>
                </geometry>
                <material>
                  <script>
                    <uri>file://media/materials/scripts/gazebo.material</uri>
                    <name>Gazebo/Grey</name>
                  </script>
                </material>
                <transparency>1</transparency>
              </visual>
              <self_collide>0</self_collide>
              <kinematic>0</kinematic>
            </link>
          </model>"""
