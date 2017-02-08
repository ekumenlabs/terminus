from __future__ import print_function

from collections import OrderedDict

import yaml

from .file_generator import FileGenerator
from .monolane_id_mapper import MonolaneIdMapper


class MonolaneGenerator(FileGenerator):
    def __init__(self, city):
        super(MonolaneGenerator, self).__init__(city)

    def start_city(self, city):
        """Called when a visitation of a new city starts."""
        # First run the id mapper
        self.monolane_id_mapper = MonolaneIdMapper(city)
        self.monolane_id_mapper.run()
        # Reset all of the class variables used until stop_city is called.
        self.monolane = {
            'maliput_monolane_builder': OrderedDict([
                ('id', city.name),
                ('lane_bounds', [-2, 2]),
                ('driveable_bounds', [-4, 4]),
                ('position_precision', 0.01),
                ('orientation_precision', 0.5),
                ('points', self.monolane_id_mapper.get_monolane_points()),
                ('connections', OrderedDict()),
                ('groups', OrderedDict()),
            ])
        }

    def point_name_by_road_node(self, road, node):
        return self.monolane_id_mapper.point_name_by_road_node(road, node)

    def new_connection(self, node1, road1, node2, road2):
        """Add a new monolane connection between two road nodes."""
        # Get the point names using the road node combo.
        # These names were created by the id mapper.
        point1 = self.point_name_by_road_node(road1, node1)
        point2 = self.point_name_by_road_node(road2, node2)

        # Create a connection name using the two monolane point names.
        connection_name = "{0}-{1}".format(point1, point2)

        # Create the new connection, explicitly starting with the first point,
        # ending with the second point, and with a length equal to the distance
        # between the points.
        new_monolane_connection = {
            connection_name: OrderedDict([
                ('start',
                    "points.{0}".format(self.point_name_by_road_node(road1, node1))),
                ('length',
                    node1.center.distance_to(node2.center)),
                ('explicit_end',
                    "points.{0}".format(self.point_name_by_road_node(road2, node2))),
            ])
        }
        # Store the new connection in the monolane dictionary.
        self.monolane['maliput_monolane_builder']['connections'].update(
            new_monolane_connection)

    def process_road(self, road):
        """Called anytime a street or trunk are visited."""
        previous_node = None
        for node in road.get_nodes():
            # If this is not the first node in the road, make a
            # connection with the previous node.
            if previous_node is not None:
                self.new_connection(previous_node, road, node, road)
            previous_node = node

    def start_street(self, street):
        self.process_road(street)

    def start_trunk(self, trunk):
        self.process_road(trunk)

    def end_document(self):
        """Called after the document is generated, but before it is written to a file."""
        self.document.write(self.to_string())

    def to_string(self, Dumper=yaml.Dumper, **kwds):
        """Convert the current monolane data into its yaml version.

        Preserves order of the keys inside of 'maliput_monolane_builder'.
        """
        header = """# -*- yaml -*-
---
# distances are meters; angles are degrees.
"""

        class OrderedDumper(yaml.Dumper):
            pass

        def _dict_representer(dumper, data):
            return dumper.represent_mapping(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                data.items())

        OrderedDumper.add_representer(OrderedDict, _dict_representer)
        return header + yaml.dump(self.monolane, None, OrderedDumper, **kwds)
