from geometry.point import Point
from geometry.line_segment import LineSegment
from shapely.geometry import LineString, LinearRing, Polygon
from shapely.geometry import Point as ShapelyPoint
from city_model import CityModel

class Lane(object):
    def __init__(self, road, width, offset):
        self.road = road
        self.width = width
        self.offset = offset
        self.nodes = []
        #self.cached_waypoints = None

    def waypoints(self):
        pass

    def geometry(self):
        if self.road.points_count() < 2:
            return []

        delta = self.offset

        if delta == 0:
            return self.road.geometry()

        road_center = self.road.geometry_as_line_string()
        road_coords = road_center.coords

        if not road_center.is_simple or \
            road_coords[0] == road_coords[-1] or \
            Polygon(road_coords).area > 0.0 and not LinearRing(road_coords).is_valid:
            raise ValueError("Can't derive lanes from self-touching streets")

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
                                           Point.from_tuple( lane_coords[-2]))
        if final_lane_segment.includes_point(Point.from_tuple(road_coords[-1])) and \
            final_lane_segment.is_orthogonal_to(initial_road_segment):
            lane_coords.pop()

        # Re-create to accomodate both reversed lookup and removed items
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
