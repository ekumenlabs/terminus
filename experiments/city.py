import xml.etree.cElementTree as ET

# For the time being, the city will be our Gazebo world
class City(object):
    def __init__(self):
        self.roads = []

    def add_road(self, road):
        self.roads.append(road)

    def to_sdf(self, parent_element):
        template = ('<world name="default">'
            '<scene><grid>false</grid></scene>'
            '<include><uri>model://sun</uri></include>'
            '<include><uri>model://ground_plane</uri></include>'
            '</world>')

        world_node = ET.fromstring(template)

        for road in self.roads:
            road.to_sdf(world_node)

        parent_element.append(world_node)
