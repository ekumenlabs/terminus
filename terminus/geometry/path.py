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

    def length(self):
        return sum(map(lambda element: element.length(), self.elements()))

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

    def __iter__(self):
        return iter(self._elements)

    def __repr__(self):
        parts = ', '.join(map(str, self.elements()))
        return "Path({0})".format(parts)
