from math import hypot
from geometry.point import Point
from geometry.line_segment import LineSegment
from geometry.line import Line
from shapely.geometry import LineString, LinearRing, Polygon
from shapely.geometry.collection import GeometryCollection
from shapely.geometry import Point as ShapelyPoint
from city_model import CityModel
from simple_node import SimpleNode
from intersection_node import IntersectionNode
from waypoint import Waypoint


class Lane(object):
    def __init__(self, road, width, offset):
        # Note: all these are private properties and should be kept that way
        self._road = road
        self._width = width
        self._offset = offset
        self._geometry = None

    def offset(self):
        return self._offset

    def width(self):
        return self._width

    def distance_to_road(self):
        return abs(self.offset) + (self.width / 2.0)

    def get_nodes(self):
        return self._build_nodes()

    def previous_node(self, node):
        nodes = self.get_nodes()
        index = nodes.index(node)
        if index - 1 >= 0:
            return nodes[index - 1]
        else:
            return None

    def following_node(self, node):
        nodes = self.get_nodes()
        index = nodes.index(node)
        if index + 1 < len(nodes):
            return nodes[index + 1]
        else:
            return None

    def get_waypoints(self):
        waypoints = []
        for node in self.get_nodes():
            waypoints.extend(node.get_waypoints_for(self))
        geometry_as_line_string = self.geometry_as_line_string()
        waypoints = sorted(waypoints,
                           key=lambda waypoint: geometry_as_line_string.project(waypoint.center.to_shapely_point()))
        return waypoints

    def geometry_as_line_string(self, decimal_places=5):
        # Shapely behaves weirdly with very precise coordinates sometimes,
        # so we round to 5 decimals by default
        # http://gis.stackexchange.com/questions/50399/how-best-to-fix-a-non-noded-intersection-problem-in-postgis
        # http://freigeist.devmag.net/r/691-rgeos-topologyexception-found-non-noded-intersection-between.html
        coords = map(lambda point: (round(point.x, decimal_places),
                                    round(point.y, decimal_places),
                                    round(point.z, decimal_places)
                                    ), self.geometry())
        return LineString(coords)

    def derived_geometry_as_line_string(self, decimal_places=5):
        # Shapely behaves weirdly with very precise coordinates sometimes,
        # so we round to 5 decimals by default
        # http://gis.stackexchange.com/questions/50399/how-best-to-fix-a-non-noded-intersection-problem-in-postgis
        # http://freigeist.devmag.net/r/691-rgeos-topologyexception-found-non-noded-intersection-between.html
        coords = map(lambda point: (round(point.x, decimal_places),
                                    round(point.y, decimal_places),
                                    round(point.z, decimal_places)
                                    ), self.derived_geometry())
        return LineString(coords)

    def geometry(self):
        if self._geometry is None:
            self._geometry = self.derived_geometry()
            self._extend_edges()
        return self._geometry

    def derived_geometry(self):
        if self._road.points_count() < 2:
            return []

        delta = self._offset

        if delta == 0:
            return self._road.geometry()

        road_center = self._road.geometry_as_line_string()
        road_coords = road_center.coords

        if not road_center.is_simple:
            raise ValueError("""Can't derive lanes from self-touching streets.
                             Road is not a simple line string""", list(road_coords))
        if road_coords[0] == road_coords[-1]:
            raise ValueError("""Can't derive lanes from self-touching streets.
                             First and last point overlap""", list(road_coords))

        if delta > 0:
            side = 'right'
            reverse_lookup = True
        else:
            side = 'left'
            reverse_lookup = False

        mitre_limit = delta ** 2

        lane_center = road_center.parallel_offset(abs(delta), side, join_style=2, mitre_limit=100)

        if reverse_lookup:
            lane_coords = list(reversed(lane_center.coords))
        else:
            lane_coords = lane_center.coords

        lane_geometry = []

        lane_index = 0

        initial_road_segment = LineSegment(Point.from_tuple(road_coords[0]),
                                           Point.from_tuple(road_coords[1]))
        initial_lane_segment = LineSegment(Point.from_tuple(lane_coords[0]),
                                           Point.from_tuple(lane_coords[1]))
        if initial_lane_segment.includes_point(Point.from_tuple(road_coords[0])) and \
           initial_lane_segment.is_orthogonal_to(initial_road_segment):
            lane_coords.pop(0)

        final_road_segment = LineSegment(Point.from_tuple(road_coords[-1]),
                                         Point.from_tuple(road_coords[-2]))
        final_lane_segment = LineSegment(Point.from_tuple(lane_coords[-1]),
                                         Point.from_tuple(lane_coords[-2]))
        if final_lane_segment.includes_point(Point.from_tuple(road_coords[-1])) and \
           final_lane_segment.is_orthogonal_to(initial_road_segment):
            lane_coords.pop()

        # Re-create to accommodate both reversed lookup and removed items
        lane_center = LineString(lane_coords)

        for index, road_coord in enumerate(road_coords):
            road_point = ShapelyPoint(road_coord)
            lane_point = ShapelyPoint(lane_coords[lane_index])
            road_point_distance = road_center.project(road_point, True)
            lane_point_distance = lane_center.project(lane_point, True)
            # If the difference in the relative distance inside the polyline
            # is less than 1%, use it.
            if abs(road_point_distance - lane_point_distance) < 0.01:
                lane_geometry.append(Point.from_shapely(lane_point))
                lane_index += 1
            # Otherwise we assume that the line was simplified and the node removed,
            # hence we do the interpolation and not increase the index, waiting to
            # find the next matching node later on.
            else:
                center_distance = road_center.project(road_point, True)
                lane_point = lane_center.interpolate(center_distance, True)
                lane_geometry.append(Point.from_shapely(lane_point))

        return lane_geometry

    def change_geometry_start(self, point):
        self._geometry[0] = point
        # self._cached_nodes = None

    def change_geometry_end(self, point):
        self._geometry[-1] = point
        # self._cached_nodes = None

    def _extend_edges(self):
        '''
        BIG TODO: Refactor this and make it more understandable / easier to
        maintain.
        '''
        my_first_node = self._road.first_node()
        intersecting_roads = my_first_node.involved_roads_except(self._road)
        intersecting_lanes = []
        for road in intersecting_roads:
            intersecting_lanes.extend(road.lanes)

        for lane in intersecting_lanes:
            my_geometry_as_line_string = self.geometry_as_line_string()
            derived_lane_geometry_as_line_string = lane.derived_geometry_as_line_string()
            intersection = my_geometry_as_line_string.intersection(derived_lane_geometry_as_line_string)
            # If there is no intersection we need to analyze three cases and
            # extend the geometry accordingly
            if isinstance(intersection, GeometryCollection) and len(intersection) == 0:
                # Case one: the node is the first node of the other lane
                if lane._road.is_first_node(my_first_node):
                    # Take the first line segment of each lane
                    my_geometry_coords = list(my_geometry_as_line_string.coords[0:2])
                    lane_geometry_coords = list(derived_lane_geometry_as_line_string.coords[0:2])
                    # Create lines from these segments
                    my_extending_line = Line.from_tuples(my_geometry_coords[0], my_geometry_coords[1])
                    lane_extending_line = Line.from_tuples(lane_geometry_coords[0], lane_geometry_coords[1])
                    # Find where these two lines intersect
                    intersection = my_extending_line.intersection(lane_extending_line)
                    # If we don't already include that point, set it as the new starting point
                    if not LineSegment.from_tuples(my_geometry_coords[0], my_geometry_coords[1]).includes_point(intersection):
                        self.change_geometry_start(intersection)
                # Case two: the node is the last node of the other lane
                elif lane._road.is_last_node(my_first_node):
                    # Take the first line segment of each lane
                    my_geometry_coords = list(my_geometry_as_line_string.coords[0:2])
                    lane_geometry_coords = list(derived_lane_geometry_as_line_string.coords[-2:])
                    # Create lines from these segments
                    my_extending_line = Line.from_tuples(my_geometry_coords[0], my_geometry_coords[1])
                    lane_extending_line = Line.from_tuples(lane_geometry_coords[0], lane_geometry_coords[1])
                    # Find where these two lines intersect
                    intersection = my_extending_line.intersection(lane_extending_line)
                    # If we don't already include that point, set it as the new starting point
                    if not LineSegment.from_tuples(my_geometry_coords[0], my_geometry_coords[1]).includes_point(intersection):
                        self.change_geometry_start(intersection)
                # Case three: the node is in the middle of the road
                else:
                    my_geometry_coords = list(my_geometry_as_line_string.coords[:])
                    # Get the first line segment, inverted direction
                    starting_point = Point.from_tuple(my_geometry_coords[1])
                    ending_point = Point.from_tuple(my_geometry_coords[0])
                    segment = LineSegment(starting_point, ending_point)
                    # Extend it by an arbitrary value and get the new ending point
                    my_new_first_coords = segment.extend(30).b.to_tuple()
                    # Make it the new first point
                    my_geometry_coords[0] = my_new_first_coords
                    # Re-create a line string
                    my_geometry_as_line_string = LineString(my_geometry_coords)
                    # Find the intersection
                    intersection = my_geometry_as_line_string.intersection(derived_lane_geometry_as_line_string)
                    if isinstance(intersection, ShapelyPoint):
                        point = Point.from_shapely(intersection)
                        # Set it as the new starting point
                        self.change_geometry_start(point)
                    else:
                        print intersection
                        raise ValueError("Can't find intersection between lanes")

        my_last_node = self._road.last_node()
        intersecting_roads = my_last_node.involved_roads_except(self._road)
        intersecting_lanes = []
        for road in intersecting_roads:
            intersecting_lanes.extend(road.lanes)
        for lane in intersecting_lanes:
            my_geometry_as_line_string = self.geometry_as_line_string()
            derived_lane_geometry_as_line_string = lane.derived_geometry_as_line_string()
            intersection = my_geometry_as_line_string.intersection(derived_lane_geometry_as_line_string)
            # If there is no intersection we need to analyze three cases and
            # extend the geometry accordingly
            if isinstance(intersection, GeometryCollection) and len(intersection) == 0:
                # Case one: the node is the first node of the other lane
                if lane._road.is_first_node(my_last_node):
                    # Take the segments of each lane
                    my_geometry_coords = list(my_geometry_as_line_string.coords[-2:])
                    lane_geometry_coords = list(derived_lane_geometry_as_line_string.coords[0:2])
                    # Create lines from these segments
                    my_extending_line = Line.from_tuples(my_geometry_coords[0], my_geometry_coords[1])
                    lane_extending_line = Line.from_tuples(lane_geometry_coords[0], lane_geometry_coords[1])
                    # Find where these two lines intersect
                    intersection = my_extending_line.intersection(lane_extending_line)
                    # If we don't already include that point, set it as the new ending point
                    if not LineSegment.from_tuples(my_geometry_coords[0], my_geometry_coords[1]).includes_point(intersection):
                        self.change_geometry_end(intersection)
                # Case two: the node is the last node of the other lane
                elif lane._road.is_last_node(my_last_node):
                    # Take the last line segment of each lane
                    my_geometry_coords = list(my_geometry_as_line_string.coords[-2:])
                    lane_geometry_coords = list(derived_lane_geometry_as_line_string.coords[-2:])
                    # Create lines from these segments
                    my_extending_line = Line.from_tuples(my_geometry_coords[0], my_geometry_coords[1])
                    lane_extending_line = Line.from_tuples(lane_geometry_coords[0], lane_geometry_coords[1])
                    # Find where these two lines intersect
                    intersection = my_extending_line.intersection(lane_extending_line)
                    # If we don't already include that point, set it as the new ending point
                    if not LineSegment.from_tuples(my_geometry_coords[0], my_geometry_coords[1]).includes_point(intersection):
                        self.change_geometry_end(intersection)
                # Case three: the node is in the middle of the road
                else:
                    my_geometry_coords = list(my_geometry_as_line_string.coords[:])
                    # Get the last line segment
                    starting_point = Point.from_tuple(my_geometry_coords[-2])
                    ending_point = Point.from_tuple(my_geometry_coords[-1])
                    segment = LineSegment(starting_point, ending_point)
                    # Extend it by an arbitrary value and get the new ending point
                    my_new_last_coords = segment.extend(30).b.to_shapely_point()
                    # Make it the new last point
                    my_geometry_coords[-1] = my_new_last_coords
                    # Re-create a line string
                    my_geometry_as_line_string = LineString(my_geometry_coords)
                    # Find the intersection
                    intersection = my_geometry_as_line_string.intersection(derived_lane_geometry_as_line_string)
                    if isinstance(intersection, ShapelyPoint):
                        point = Point.from_shapely(intersection)
                        # Set it as the new starting point
                        self.change_geometry_end(point)
                    else:
                        print intersection
                        raise ValueError("Can't find intersection between lanes")

    def _build_nodes(self):
        geometry = self.geometry()
        geometry_as_line_string = self.geometry_as_line_string()
        nodes = []
        needs_sorting = False
        intersections = {}
        for index, node in enumerate(self._road.nodes):
            # Lets hack this for now
            if isinstance(node, SimpleNode):
                point = geometry[index]
                node = SimpleNode(point)
                node.added_to(self)
                nodes.append(node)
            else:
                needs_sorting = True
                intersecting_roads = node.involved_roads_except(self._road)
                intersecting_lanes = []
                for road in intersecting_roads:
                    intersecting_lanes.extend(road.lanes)
                for lane in intersecting_lanes:
                    lane_geometry_as_line_string = lane.geometry_as_line_string()
                    intersection = geometry_as_line_string.intersection(lane_geometry_as_line_string)

                    if isinstance(intersection, ShapelyPoint):
                        point = Point.from_shapely(intersection)
                        if point not in intersections:
                            node = IntersectionNode(point)
                            node.added_to(self)
                            node.added_to(lane)
                            nodes.append(node)
                            intersections[point] = node
                        else:
                            intersections[point].added_to(lane)
                    elif isinstance(intersection, GeometryCollection) and len(intersection) == 0:
                        raise ValueError("Expected lanes to intersect")
                    else:
                        raise ValueError("Only 1-point road intersection is supported")

        if needs_sorting:
            nodes = sorted(nodes,
                           key=lambda node: geometry_as_line_string.project(node.center.to_shapely_point()))
        return nodes

    def __repr__(self):
        return "%s: " % self.__class__.__name__ + \
            reduce(lambda acc, point: acc + "%s," % str(point), self.geometry(), '')
