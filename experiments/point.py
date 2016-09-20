# We may want to use better abstractions in the future
# https://github.com/sbliven/geometry-simple
# https://pypi.python.org/pypi/Shapely

import xml.etree.cElementTree as ET

class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def to_sdf(self, parent_element):
        content = '{} {} {}'.format(self.x, self.y, self.z)
        ET.SubElement(parent_element, 'point').text = content
