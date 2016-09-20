import xml.etree.cElementTree as ET

class Road(object):
    def __init__(self, name, width):
        self.name = name
        self.width = width
        self.segments = []

    def add_segment(self, coordinates):
        self.segments.append(coordinates)

    def material_name(self):
        raise NotImplementedError()

    def to_sdf(self, parent_element):
        road_node = ET.SubElement(parent_element, 'road', name=self.name)
        ET.SubElement(road_node, 'width').text = str(self.width)
        material_node = ET.SubElement(road_node, 'material')
        script_node = ET.SubElement(material_node, 'script')
        uri_node = ET.SubElement(script_node, 'uri')
        uri_node.text = 'file://media/materials/scripts/gazebo.material'
        name_node = ET.SubElement(script_node, 'name')
        name_node.text = self.material_name()

        for segment in self.segments:
            segment.to_sdf(road_node)

class Street(Road):
    def __init__(self, name):
        super(Street, self).__init__(name, 5)

    def material_name(self):
        return 'Gazebo/Residential'


class Highway(Road):
    def __init__(self, name):
        super(Highway, self).__init__(name, 10)

    def material_name(self):
        return 'Gazebo/Motorway'




