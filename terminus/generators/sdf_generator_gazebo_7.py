"""
/*
 * Copyright (C) 2017 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
"""
from abstract_sdf_generator import AbstractSDFGenerator


class SDFGeneratorGazebo7(AbstractSDFGenerator):
    """This class generates an sdf file that can be loaded using a vanilla
    Gazebo 7 install. The file is self-contained and to model streets it uses
    the built-in <road> tag"""

    def end_street(self, street):
        self._append_to_document(self._contents_for(street))

    def end_trunk(self, trunk):
        self._append_to_document(self._contents_for(trunk))

    def street_template(self):
        return """
        <road name="{{model.name}}">
          <width>{{model.width()}}</width>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Residential</name>
            </script>
          </material>
        {% for node in model._nodes %}
          <point>{{node.center.x}} {{node.center.y}} {{node.center.z}}</point>
        {% endfor %}
        </road>"""

    def trunk_template(self):
        return """
        <road name="{{model.name}}">
          <width>{{model.width()}}</width>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Primary</name>
            </script>
          </material>
        {% for node in model._nodes %}
          <point>{{node.center.x}} {{node.center.y}} {{node.center.z}}</point>
        {% endfor %}
        </road>"""
