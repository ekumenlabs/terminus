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
          <width>{{model.width}}</width>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Residential</name>
            </script>
          </material>
        {% for node in model.nodes %}
          <point>{{node.center.x}} {{node.center.y}} {{node.center.z}}</point>
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
        {% for node in model.nodes %}
          <point>{{node.center.x}} {{node.center.y}} {{node.center.z}}</point>
        {% endfor %}
        </road>"""
