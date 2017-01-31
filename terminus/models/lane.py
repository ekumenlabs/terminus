from math import hypot, copysign
from geometry.point import Point
from geometry.line_segment import LineSegment
from geometry.line import Line
from shapely.geometry import LineString, LinearRing, Polygon
from shapely.geometry.collection import GeometryCollection
from shapely.geometry import Point as ShapelyPoint, MultiPoint
from city_model import CityModel
from lane_simple_node import LaneSimpleNode
from lane_intersection_node import LaneIntersectionNode
from waypoint import Waypoint


class Lane(object):
    def __init__(self, road, width, offset):
        # Note: all these are private properties and should be kept that way
        self._road = road
        self._width = width
        self._offset = offset
        self._geometry = None
        self._nodes = None
        self._waypoints = None

    def offset(self):
        return self._offset

    def width(self):
        return self._width

    def external_offset(self):
        return copysign(abs(self.offset()) + (self.width() / 2.0), self.offset())

    def accept(self, generator):
        generator.start_lane(self)
        generator.end_lane(self)

    def get_nodes(self):
        if self._nodes is None:
            self._nodes = self._build_nodes()
        return self._nodes

    def find_node_matching(self, target_node):
        if target_node in self.get_nodes():
            return target_node
        else:
            return self._find_index_and_node_matching(target_node)[1]

    def previous_node(self, target_node):
        nodes = self.get_nodes()
        try:
            index = nodes.index(target_node)
        except:
            index, _ = self._find_index_and_node_matching(target_node)
        if index - 1 >= 0:
            return nodes[index - 1]
        else:
            return None

    def following_node(self, target_node):
        nodes = self.get_nodes()
        try:
            index = nodes.index(target_node)
        except:
            index, _ = self._find_index_and_node_matching(target_node)
        if index + 1 < len(nodes):
            return nodes[index + 1]
        else:
            return None

    def waypoints_count(self):
        return len(self.get_waypoints())

    def get_waypoints(self):
        if self._waypoints is None:
            self._waypoints = []
            for node in self.get_nodes():
                waypoints = node.get_waypoints_for(self)
                for waypoint in waypoints:
                    if waypoint not in self._waypoints:
                        self._waypoints.append(waypoint)
            geometry_as_line_string = self.geometry_as_line_string()
            self._waypoints = sorted(self._waypoints,
                                     key=lambda waypoint: geometry_as_line_string.project(waypoint.center.to_shapely_point()))
        return self._waypoints

    def geometry_as_line_string(self):
        coords = map(lambda point: (point.x, point.y, point.z), self.geometry())
        return LineString(coords)

    def derived_geometry_as_line_string(self):
        coords = map(lambda point: (point.x, point.y, point.z), self.derived_geometry())
        return LineString(coords)

    def geometry(self):
        if self._geometry is None:
            self._geometry = self.derived_geometry()
            self._geometry = self._extend_edges(list(self._geometry))
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

        # On some cases Shapely leaves a 90deg cap on the border of the line
        # Check the beginning and end of the lane and remove them if present

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

    def _intersecting_lanes_for(self, road_node):
        intersecting_roads = road_node.involved_roads_except(self._road)
        intersecting_lanes = []
        for road in intersecting_roads:
            intersecting_lanes.extend(road.get_lanes())
        return intersecting_lanes

    def _extend_edges(self, geometry):
        '''
        TODO: This definitely needs a refactoring
        '''
        # The first segment of the polyline, pointing outwards
        first_segment = LineSegment(geometry[1], geometry[0])
        # Extend it by an arbitrary amount
        extended_first_segment = first_segment.extend(10)
        # Get also the Shapely version for further testing
        extended_first_segment_as_line_string = LineString([extended_first_segment.a.to_tuple(),
                                                           extended_first_segment.b.to_tuple()])
        # The first node in the road this lane belongs to
        first_road_node = self._road.first_node()
        # Get all the lanes that we should be intersecting
        lanes = self._intersecting_lanes_for(first_road_node)

        points = []
        for lane in lanes:
            lane_geometry_as_line_string = lane.derived_geometry_as_line_string()
            intersection = extended_first_segment_as_line_string.intersection(lane_geometry_as_line_string)
            if isinstance(intersection, GeometryCollection) and len(intersection) == 0:
                lane_geometry = lane.derived_geometry()
                extended_lane_start_segment = LineSegment(lane_geometry[1], lane_geometry[0]).extend(10)
                segment_intersection = extended_lane_start_segment.find_intersection(extended_first_segment)
                if segment_intersection is not None:
                    points.append(segment_intersection)

                extended_lane_end_segment = LineSegment(lane_geometry[-2], lane_geometry[-1]).extend(10)
                segment_intersection = extended_lane_end_segment.find_intersection(extended_first_segment)
                if segment_intersection is not None:
                    points.append(segment_intersection)
            elif isinstance(intersection, GeometryCollection) and len(intersection) > 0:
                pass
            elif isinstance(intersection, MultiPoint):
                for shapely_point in intersection:
                    points.append(Point.from_shapely(shapely_point))
            elif isinstance(intersection, LineString):
                for shapely_point in intersection.coords[:]:
                    points.append(Point.from_tuple(shapely_point))
            elif isinstance(intersection, ShapelyPoint):
                points.append(Point.from_shapely(intersection))
            else:
                raise ValueError("Unexpected intersection", intersection)

        candidate_segments = map(lambda point: LineSegment(geometry[1], point), points)
        candidate_segments.append(first_segment)
        candidate_segments.sort(key=lambda segment: segment.length())
        new_first_point = candidate_segments[-1].b
        geometry[0] = new_first_point

        # The first segment of the polyline, pointing outwards
        last_segment = LineSegment(geometry[-2], geometry[-1])
        # Extend it by an arbitrary amount
        extended_last_segment = last_segment.extend(10)
        # Get also the Shapely version for further testing
        extended_last_segment_as_line_string = LineString([extended_last_segment.a.to_tuple(),
                                                           extended_last_segment.b.to_tuple()])
        # The first node in the road this lane belongs to
        last_road_node = self._road.last_node()
        # Get all the lanes that we should be intersecting
        lanes = self._intersecting_lanes_for(last_road_node)

        points = []
        for lane in lanes:
            lane_geometry_as_line_string = lane.derived_geometry_as_line_string()
            intersection = extended_last_segment_as_line_string.intersection(lane_geometry_as_line_string)
            if isinstance(intersection, GeometryCollection) and len(intersection) == 0:
                lane_geometry = lane.derived_geometry()
                extended_lane_start_segment = LineSegment(lane_geometry[1], lane_geometry[0]).extend(10)
                segment_intersection = extended_lane_start_segment.find_intersection(extended_last_segment)
                if segment_intersection is not None:
                    points.append(segment_intersection)

                extended_lane_end_segment = LineSegment(lane_geometry[-2], lane_geometry[-1]).extend(10)
                segment_intersection = extended_lane_end_segment.find_intersection(extended_last_segment)
                if segment_intersection is not None:
                    points.append(segment_intersection)
            elif isinstance(intersection, GeometryCollection) and len(intersection) > 0:
                pass
            elif isinstance(intersection, MultiPoint):
                for shapely_point in intersection:
                    points.append(Point.from_shapely(shapely_point))
            elif isinstance(intersection, LineString):
                for shapely_point in intersection.coords[:]:
                    points.append(Point.from_tuple(shapely_point))
            elif isinstance(intersection, ShapelyPoint):
                points.append(Point.from_shapely(intersection))
            else:
                raise ValueError("Unexpected intersection", intersection)

        candidate_segments = map(lambda point: LineSegment(geometry[-2], point), points)
        candidate_segments.append(last_segment)
        candidate_segments.sort(key=lambda segment: segment.length())
        new_last_point = candidate_segments[-1].b
        geometry[-1] = new_last_point

        return geometry

    def _build_nodes(self):
        geometry = self.geometry()
        geometry_as_line_string = self.geometry_as_line_string()
        nodes = []
        needs_sorting = False
        intersections = {}
        for index, road_node in enumerate(self._road.get_nodes()):
            intersecting_roads = road_node.involved_roads_except(self._road)
            if not intersecting_roads:
                point = geometry[index]
                node = LaneSimpleNode(point, self, road_node)
                nodes.append(node)
            else:
                needs_sorting = True
                intersecting_lanes = []
                for road in intersecting_roads:
                    intersecting_lanes.extend(road.get_lanes())
                for lane in intersecting_lanes:
                    lane_geometry_as_line_string = lane.geometry_as_line_string()
                    intersection = geometry_as_line_string.intersection(lane_geometry_as_line_string)
                    if isinstance(intersection, GeometryCollection) and len(intersection) == 0:
                        intersection = geometry[index].to_shapely_point()
                    elif isinstance(intersection, MultiPoint):
                        points = map(lambda shapely_point: Point.from_shapely(shapely_point), intersection)
                        intersection = sorted(points, key=lambda point: point.squared_distance_to(geometry[index]))[0].to_shapely_point()
                    elif isinstance(intersection, LineString):
                        distance = intersection.project(geometry[index].to_shapely_point())
                        intersection = intersection.interpolate(distance)

                    if isinstance(intersection, ShapelyPoint):
                        point = Point.from_shapely(intersection)
                        if point not in intersections:
                            node = LaneIntersectionNode(point, self, road_node)
                            node.added_to(lane)
                            nodes.append(node)
                            intersections[point] = node
                        else:
                            intersections[point].added_to(lane)
                    else:
                        raise ValueError("Can't find a suitable location in the lane for the node", road_node)

        if needs_sorting:
            nodes = sorted(nodes,
                           key=lambda node: geometry_as_line_string.project(node.center.to_shapely_point()))
        return nodes

    def _find_index_and_node_matching(self, target_node):
        nodes = self.get_nodes()
        candidate_nodes = []
        for index, node in enumerate(nodes):
            if node.source is target_node.source and node.involves(target_node.main_lane):
                candidate_nodes.append((index, node))
        if not len(candidate_nodes) == 1:
            raise ValueError("Expecting to find a single matching node", target_node, candidate_nodes)
        return candidate_nodes[0]

    def __repr__(self):
        return "%s: " % self.__class__.__name__ + \
            reduce(lambda acc, point: acc + "%s," % str(point), self.get_nodes(), '')
