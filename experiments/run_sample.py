#!/usr/bin/python

import xml.etree.cElementTree as ET
import xml.dom.minidom

from city import City
from road import Street, Highway
from point import Point

root = ET.Element("sdf", version="1.5")

city = City()

road_1 = Street("1")
road_1.add_segment(Point(-50,0,0.05))
road_1.add_segment(Point(50,0,0.05))
city.add_road(road_1)

road_2 = Highway("2")
road_2.add_segment(Point(0,-50,0.05))
road_2.add_segment(Point(0,50,0.05))
city.add_road(road_2)

city.to_sdf(root)

xmlstr = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
with open("sample_roads.sdf", "w") as f:
    f.write(xmlstr)
