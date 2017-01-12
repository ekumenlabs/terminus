from abstract_sdf_generator import AbstractSDFGenerator


class SDFGeneratorGazebo8(AbstractSDFGenerator):
    """This class generates an sdf file that loads the road network from an RNDF
    file. In order to use this you will need Gazebo 8 and the plugin to render
    RNDF"""

    def __init__(self, city, rndf_origin, rndf_path):
        super(SDFGeneratorGazebo8, self).__init__(city)
        self.rndf_path = rndf_path
        self.rndf_origin = rndf_origin

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
        <plugin name='rndf_gazebo_plugin0' filename='librndf_gazebo_plugin0.so.0.0.1'>
          <rndf>{{generator.rndf_path}}</rndf>
          <lanes>true</lanes>
          <waypoints>true</waypoints>
          <junctions>true</junctions>
          <waypoints_material>Gazebo/White</waypoints_material>
          <origin>{{generator.rndf_origin.lat}} {{generator.rndf_origin.lon}} 0.0</origin>
        </plugin>
          {{inner_contents}}
        </world>
        """
