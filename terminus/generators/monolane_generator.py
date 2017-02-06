from __future__ import print_function

from collections import OrderedDict
from math import atan2
from math import degrees
import yaml

from .city_visitor import CityVisitor
from models.road_intersection_node import RoadIntersectionNode


class MonolaneGenerator(CityVisitor):
    def start_city(self, city):
        """Called when a visitation of a new city starts."""
        # Reset all of the class variables used until stop_city is called.
        self.monolane = {
            'maliput_monolane_builder': OrderedDict([
                ('id', city.name),
                ('lane_bounds', [-2, 2]),
                ('driveable_bounds', [-4, 4]),
                ('position_precision', 0.01),
                ('orientation_precision', 0.5),
                ('points', OrderedDict()),
                ('connections', OrderedDict()),
                ('groups', OrderedDict()),
            ])
        }
        self.streets = []
        self.point_name_by_street_node_dict = {}
        self.intersection_index = 0
        self.intersection_index_by_node = {}

    def node_ident(self, street, node):
        """Return a hashable unique identifier for a street node."""
        return (street.name, id(node))

    def point_name_by_street_node(self, node, street):
        """Return the monolane point name for a given street node."""
        ident = self.node_ident(street, node)
        return self.point_name_by_street_node_dict[ident][0]

    def new_connection(self, node1, street1, node2, street2):
        """Add a new monolane connection between two street nodes."""
        # Get the point names using the street node combo.
        # These names should have been created while streets were being processed.
        point1 = self.point_name_by_street_node(node1, street1)
        point2 = self.point_name_by_street_node(node2, street2)

        # Create a connection name using the two monolane point names.
        connection_name = "{0}-{1}".format(point1, point2)

        # Create the new connection, explicitly starting with the first point,
        # ending with the second point, and with a length equal to the distance
        # between the points.
        new_monolane_connection = {
            connection_name: OrderedDict([
                ('start',
                    "points.{0}".format(self.point_name_by_street_node(node1, street1))),
                ('length',
                    node1.center.distance_to(node2.center)),
                ('explicit_end',
                    "points.{0}".format(self.point_name_by_street_node(node2, street2))),
            ])
        }
        # Store the new connection in the monolane dictionary.
        self.monolane['maliput_monolane_builder']['connections'].update(
            new_monolane_connection)

    def end_city(self, city):
        """Called when a city has been completely visited."""
        # Iterate over all the visited streets (again) and make connections.
        # This second iteration is required so that connections between streets
        # can be made, as all nodes of all streets have already been assigned
        # point names.
        for street in self.streets:
            previous_node = None
            for node in street.get_nodes():
                # If this is not the first node in the street, make a
                # connection with the previous node.
                if previous_node is not None:
                    self.new_connection(previous_node, street, node, street)
                previous_node = node

    def process_street(self, street):
        """Called anytime a street or trunk are visited."""
        # Add the street to a list of streets to be iterated over when
        # end_city() is called.
        self.streets.append(street)
        # Iterate over all of the nodes in the street, given them unique
        # monolane names, and add them to the points section in the monolane
        # dictionary.
        point_index = 1  # used to uniquely name the points for this street
        previous_point_name = None  # used to update the heading of the point
        previous_point_center = None  # used to calculate the heading
        previous_heading = 0
        for node in list(street.get_nodes()):
            # Generate a unique name for the point based on the street name.
            point_name = '{}-{}'.format(street.name, point_index)
            point_index += 1
            # If this is an "RoadIntersectionNode", adjust the name to indicate it.
            if isinstance(node, RoadIntersectionNode):
                # Get the index associated with the intersection.
                if id(node) not in self.intersection_index_by_node:
                    # Assign an index if this is the first appearance.
                    self.intersection_index_by_node[id(node)] = self.intersection_index
                    self.intersection_index += 1
                index = self.intersection_index_by_node[id(node)]
                # Adjust the name to include the intersection.
                point_name = '{}-from_Intersection-{}'.format(point_name, self.intersection_index)
            # Get a unique and hashable identifier for the street node.
            node_ident = self.node_ident(street, node)
            # Ensure it is unique.
            if node_ident in self.point_name_by_street_node_dict:
                raise RuntimeError("Non-unique street node identifier. This should not happen.")
            # Store the point name using the identifier.
            self.point_name_by_street_node_dict[node_ident] = (point_name, node)
            # Put the point into the monolane dictionary.
            new_monolane_point = {
                point_name: OrderedDict([
                    ('xypoint', [  # x, y, heading
                        float(node.center.x),
                        float(node.center.y),
                        0  # will be set later using heading between this point and the next
                    ]),
                    ('zpoint', [  # z, zdot, theta (superelevation), thetadot
                        float(node.center.z),
                        0,
                        0,
                        0
                    ]),
                ])
            }
            # If there was a previous point, calculate the heading from it to this point.
            if previous_point_name is not None:
                # Get the previous point's center by name.
                previous_point = \
                    self.monolane['maliput_monolane_builder']['points'][previous_point_name]['xypoint']
                # Calculate the heading.
                previous_heading = degrees(previous_point_center.yaw(node.center))
                # Store it.
                previous_point[2] = previous_heading
            previous_point_name = point_name
            previous_point_center = node.center
            # Insert the new point.
            self.monolane['maliput_monolane_builder']['points'].update(new_monolane_point)
        # end for node in list(street.get_nodes())
        # Update the heading of the last point (last one processed in the for loop).
        if previous_point_name is not None:
            # Use the last heading as the heading of the last point.
            previous_point = \
                self.monolane['maliput_monolane_builder']['points'][previous_point_name]['xypoint']
            previous_point[2] = previous_heading

    def start_street(self, street):
        self.process_street(street)

    def start_trunk(self, trunk):
        self.process_street(trunk)

    def to_string(self, stream=None, Dumper=yaml.Dumper, **kwds):
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
        return header + yaml.dump(self.monolane, stream, OrderedDumper, **kwds)
