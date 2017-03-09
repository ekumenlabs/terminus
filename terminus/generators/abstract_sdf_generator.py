"""
Copyright (C) 2017 Open Source Robotics Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from file_generator import FileGenerator


class AbstractSDFGenerator(FileGenerator):

    def end_document(self):
        self._wrap_document_with_template('document')

    def end_city(self, city):
        self._wrap_document_with_contents_for(city)

    def end_block(self, block):
        self._append_to_document(self._contents_for(block))

    def end_building(self, building):
        self._append_to_document(self._contents_for(building))

    def end_ground_plane(self, ground_plane):
        self._append_to_document(self._contents_for(ground_plane))

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
        </world>
        """

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
