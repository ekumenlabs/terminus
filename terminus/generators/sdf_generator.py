from file_generator import FileGenerator
try:
    from cStringIO import StringIO
except:
    from io import StringIO

class SDFGenerator(FileGenerator):

    def generate(self):
        self.document = StringIO()
        self.city.accept(self)
        self._wrap_document_contents()
        return self.document.getvalue()

    def _wrap_document_contents(self):
        template = self._get_cached_template('document')
        new_contents = template.render(inner_contents=self.document.getvalue())
        self.document = StringIO(new_contents)

    def end_city(self, city):
        new_contents = self._contents_for(city, inner_contents=self.document.getvalue())
        self.document = StringIO(new_contents)

    def end_street(self, street):
        self.document.write(self._contents_for(street))

    def end_trunk(self, trunk):
        self.document.write(self._contents_for(trunk))

    def end_block(self, block):
        self.document.write(self._contents_for(block))

    def end_building(self, building):
        self.document.write(self._contents_for(building))

    def end_ground_plane(self, ground_plane):
        self.document.write(self._contents_for(ground_plane))

    def city_template(self):
        return """
        <world name="{{model.name}}">
        <gui fullscreen='0'>
          <camera name='city_camera'>
            <pose frame=''>
              -0.065965 0.276379 1005.72 2e-06 1.5538 1.5962
            </pose>
          </camera>
        </gui>
        <include>
          <uri>model://sun</uri>
        </include>
          {{inner_contents}}
        </world>"""

    def street_template(self):
        return """
        <road name="{{model.name}}">
          <width>{{model.width}}</width>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Residential</name>
            </script>
          </material>
        {% for point in model.points %}
          <point>{{point.x}} {{point.y}} {{point.z}}</point>
        {% endfor %}
        </road>"""

    def trunk_template(self):
        return """
        <road name="{{model.name}}">
          <width>{{model.width}}</width>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Trunk</name>
            </script>
          </material>
        {% for point in model.points %}
          <point>{{point.x}} {{point.y}} {{point.z}}</point>
        {% endfor %}
        </road>"""

    def block_template(self):
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

    def building_template(self):
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

    def ground_plane_template(self):
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

    def document_template(self):
        return """
        <?xml version="1.0" ?>
        <sdf version="1.5">
          {{inner_contents}}
        </sdf>"""
