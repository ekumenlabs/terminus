import xml.etree.cElementTree as ET

# For the time being, the city will be our Gazebo world
class City(object):
    def __init__(self):
        self.roads = []

    def add_road(self, road):
        self.roads.append(road)

    def to_sdf(self, parent_element):
        template = ('<world name="default">'
            '<scene>'
              '<grid>false</grid>'
              '<ambient>1.000000 1.000000 1.000000 1.000000</ambient>'
              '<background>0.700000 0.700000 0.700000 1.000000</background>'
              '<shadows>1</shadows>'
            '</scene>'
            '<physics type="ode">'
              '<gravity>0.000000 -1.000000 -1.000000</gravity>'
              '<ode>'
                '<solver>'
                  '<type>quick</type>'
                  '<iters>50</iters>'
                  '<precon_iters>0</precon_iters>'
                  '<sor>1.300000</sor>'
                '</solver>'
                '<constraints>'
                  '<cfm>0.000000</cfm>'
                  '<erp>0.200000</erp>'
                  '<contact_max_correcting_vel>100.000000</contact_max_correcting_vel>'
                  '<contact_surface_layer>0.001000</contact_surface_layer>'
                '</constraints>'
              '</ode>'
              '<real_time_update_rate>0.000000</real_time_update_rate>'
              '<max_step_size>0.001000</max_step_size>'
            '</physics>            '
            '<include>'
              '<uri>model://sun</uri>'
            '</include>'
            '<include>'
              '<uri>model://ground_plane</uri>'
            '</include>'
            '</world>')

        world_node = ET.fromstring(template)

        for road in self.roads:
            road.to_sdf(world_node)

        parent_element.append(world_node)
