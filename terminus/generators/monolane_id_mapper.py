from collections import OrderedDict
from math import degrees

from city_visitor import CityVisitor
from models.road_intersection_node import RoadIntersectionNode


class MonolaneIdMapper(CityVisitor):
    """Simple city visitor that generates the Monolane point names ("id's").

    This class refers to "road nodes", which in this case is a unique
    combination of a road (a street or a trunk) with a node.
    The node might be a RoadIntersectionNode, in which case the node might
    be associated with more than one road.
    For the purposes of Monolane, this is not OK, so we create a point name per
    road-node pair.
    """

    def run(self):
        self.point_name_by_road_node_dict = {}
        self.intersection_index = 0
        self.intersection_index_by_node = {}
        self.monolane_points = OrderedDict()
        super(MonolaneIdMapper, self).run()

    def road_node_id(self, road, node):
        """Return a hashable unique identifier for a road node."""
        return (road.name, id(node))

    def get_monolane_points(self):
        return self.monolane_points

    def point_name_by_road_node(self, road, node):
        return self.point_name_by_road_node_dict[self.road_node_id(road, node)]

    def process_road(self, road):
        """Called anytime a road or trunk are visited.

        Each node in the road is given a unique monolane point name which is
        based on both the node and the road name.
        It takes this form:

            <road.name>-<point_index>[-from_Intersection-<intersection_index>]

        The ``point_index`` is unique within a single road, i.e. it is reset
        each time a new road is processed.
        The optional suffix is added if the node is a ``RoadIntersectionNode``.
        The optional suffix uses ``intersection_index`` which is the unique
        number associated with each ``RoadIntersectionNode`` in the city.
        """
        # Iterate over all of the nodes in the road, given them unique
        # monolane point names, and store them for later use.
        point_index = 1  # used to uniquely name the points for this road
        previous_point_name = None
        previous_point_center = None
        previous_heading = 0
        for node in list(road.get_nodes()):
            # Generate a unique name for the point based on the road name.
            point_name = '{}-{}'.format(road.name, point_index)
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
                point_name = '{}-from_Intersection-{}'.format(point_name, index)
            # Get a unique and hash-able identifier for the road node.
            node_ident = self.road_node_id(road, node)
            # Ensure it is unique.
            if node_ident in self.point_name_by_road_node_dict:
                raise RuntimeError("Non-unique road node identifier. This should not happen.")
            # Store the point name using the identifier.
            self.point_name_by_road_node_dict[node_ident] = (point_name, node)
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
                previous_point = self.monolane_points[previous_point_name]['xypoint']
                # Calculate the heading.
                previous_heading = degrees(previous_point_center.yaw(node.center))
                # Store it.
                previous_point[2] = previous_heading
            previous_point_name = point_name
            previous_point_center = node.center
            # Insert the new point.
            self.monolane_points.update(new_monolane_point)
        # end for node in list(road.get_nodes())

        # Update the heading of the last point (last one processed in the for loop).
        if previous_point_name is not None:
            # Use the last heading as the heading of the last point.
            previous_point = self.monolane_points[previous_point_name]['xypoint']
            previous_point[2] = previous_heading

    def start_street(self, street):
        self.process_road(street)

    def start_trunk(self, trunk):
        self.process_road(trunk)
