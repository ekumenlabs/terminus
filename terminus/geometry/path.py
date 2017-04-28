"""
Copyright (C) 2017 Open Source Robotics Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from geometry.circle import Circle
from geometry.line_segment import LineSegment


class Path(object):
    """A path is a collection of geometry elements where, for two consecutive
    element E_n and E_n+1 it holds that E_n last point == E_n+1 start point
    """

    def __init__(self, elements=None):
        self._elements = []
        if elements:
            self._elements.extend(elements)

    @classmethod
    def polyline_from_points(cls, points):
        if len(points) < 2:
            raise ValueError("{0} points given. At least two points are needed".format(points))
        pairs = zip(points, points[1:])
        segments = map(lambda (p1, p2): LineSegment(p1, p2), pairs)
        return cls(segments)

    def clone(self):
        cloned_elements = map(lambda element: element.clone(), self.elements())
        return Path(cloned_elements)

    def not_empty(self):
        return self.elements_count() > 0

    def is_empty(self):
        return self.elements_count() == 0

    def elements_count(self):
        return len(self._elements)

    def elements(self):
        return self._elements

    def element_at(self, index):
        return self._elements[index]

    def first_element(self):
        return self.element_at(0)

    def last_element(self):
        return self.element_at(-1)

    def start_point(self):
        return self.element_at(0).start_point()

    def end_point(self):
        return self.element_at(-1).end_point()

    def starts_on(self, point):
        return self.start_point() == point

    def ends_on(self, point):
        return self.end_point() == point

    def is_self_closing(self):
        return self.start_point() == self.end_point()

    def length(self):
        return sum(map(lambda element: element.length(), self.elements()))

    def remove_first_element(self):
        return self._elements.pop(0)

    def replace_first_element(self, new_element):
        self._elements[0] = new_element

    def add_element(self, element):
        if self.not_empty() and \
           not self.end_point().almost_equal_to(element.start_point(), 7):
            raise ValueError("{0} start point doesn't match path last point {1}".format(element, self.end_point()))
        self._elements.append(element)

    def reversed(self):
        copied_elements = list(self._elements).reverse()
        return Path(copied_elements)

    def vertices(self):
        points = map(lambda element: element.start_point(), self._elements)
        points.append(self.end_point())
        return points

    def is_valid_path_connection(self):
        return all(element.is_valid_path_connection() for element in self._elements)

    def includes_point(self, point, buffer=1e-7):
        return any(element.includes_point(point, buffer) for element in self._elements)

    def simplify(self):
        """
        Reduce the number of geometric primitives in the path by removing
        redundant ones (e.g. merges two contiguous collinear line segments into
        a single one)
        """
        new_primitives = []
        previous_primitive = self._elements[0]
        index = 1
        while (index < len(self._elements)):
            current_primitive = self._elements[index]
            if previous_primitive.can_be_merged_with(current_primitive):
                previous_primitive = previous_primitive.merge(current_primitive)
            else:
                new_primitives.append(previous_primitive)
                previous_primitive = current_primitive
            index += 1
        new_primitives.append(previous_primitive)
        self._elements = new_primitives

    def trim_to_fit(self, bounding_box):
        paths = [Path()]
        for element in self:
            current_path = paths[-1]
            if element.is_inside(bounding_box):
                current_path.add_element(element)
            elif element.is_outside(bounding_box):
                pass
            else:
                split = element.trim_to_fit(bounding_box)
                for sub_element in split:
                    if current_path.not_empty() and \
                       not current_path.end_point().almost_equal_to(sub_element.start_point(), 7):
                        current_path = Path()
                        paths.append(current_path)
                    current_path.add_element(sub_element)
        return paths

    def heading_at_offset(self, offset):
        # TODO: Refactor with point_at_offset
        remaining_distance = offset
        for element in self.elements():
            if element.length() < remaining_distance:
                remaining_distance -= element.length()
            else:
                return element.heading_at_offset(remaining_distance)
        message = "Provided offset ({0}) is greater that path length ({1})".format(offset, self.length())
        raise ValueError(message)

    def heading_at_point(self, point, start_offset=0.0):
        # TODO: Improve performance
        offset = self.offset_for_point(point, start_offset)
        return self.heading_at_offset(offset)

    def point_at_offset(self, offset):
        remaining_distance = offset
        for element in self.elements():
            if element.length() < remaining_distance:
                remaining_distance -= element.length()
            else:
                return element.point_at_offset(remaining_distance)
        message = "Provided offset ({0}) is greater that path length ({1})".format(offset, self.length())
        raise ValueError(message)

    def offset_for_point(self, point, start_offset=0.0):
        accumulated_distance = 0
        for element in self.elements():
            if element.includes_point(point):
                matching_offset = accumulated_distance + element.offset_for_point(point)
                if matching_offset >= start_offset:
                    return matching_offset
                else:
                    accumulated_distance += element.length()
            else:
                accumulated_distance += element.length()
        message = "Point {0} does not exist in path {1}".format(point, self)
        raise ValueError(message)

    def line_interpolation_points(self):
        points = []
        for element in self.elements():
            new_points = element.line_interpolation_points()
            # Last point of previous element and first point of current
            # one are the same. Avoid having it twice
            if points:
                points.pop()
            points.extend(new_points)
        return points

    def find_intersection(self, other):
        # TODO: For now we only need intersections with circles, but leaving
        # this as a placeholder for the future. Fail loud if other is not a circle.
        if isinstance(other, Circle):
            intersections = []
            for element in self._elements:
                intersections.extend(element.find_intersection(other))
            return intersections
        else:
            raise ValueError("Intersection between {0} and {1} not supported".format(self, other))

    def split_in(self, waypoints):
        primitives = []
        waypoint_index = 0
        for element in self.elements():
            current_center = waypoints[waypoint_index].center()
            pairs = []
            while not current_center.almost_equal_to(element.end_point(), 7):
                waypoint_index += 1
                next_center = waypoints[waypoint_index].center()
                pairs.append((current_center, next_center))
                current_center = next_center
            primitives.extend(element.split_into(pairs))
        return Path(primitives)

    def __iter__(self):
        return iter(self._elements)

    def __repr__(self):
        parts = ', '.join(map(str, self.elements()))
        return "Path({0})".format(parts)
