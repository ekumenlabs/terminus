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

import textwrap

from generators.city_visitor import CityVisitor
from models.polyline_geometry import PolylineGeometry
from models.lines_and_arcs_geometry import LinesAndArcsGeometry


class CityStatistics(CityVisitor):

    def __init__(self, city):
        super(CityStatistics, self).__init__(city)
        self._clear_counters()

    def run(self):
        self._clear_counters()
        super(CityStatistics, self).run()
        self._compute_derived_statistics()
        return self.get_values()

    def get_values(self):
        return self.stats

    def start_city(self, city):
        self.stats['intersections_count'] = city.intersections_count()

    def start_street(self, street):
        self.stats['roads_count'] += 1

    def start_trunk(self, trunk):
        self.stats['roads_count'] += 1

    def start_lane(self, lane):
        self.stats['lanes_count'] += 1
        for waypoint in lane.waypoints_for(PolylineGeometry):
            self.stats['polyline_waypoints_count'] += 1
            if waypoint.is_intersection():
                self.stats['polyline_intersections_count'] += 1
        for waypoint in lane.waypoints_for(LinesAndArcsGeometry):
            self.stats['lines_and_arcs_waypoints_count'] += 1
            if waypoint.is_intersection():
                self.stats['lines_and_arcs_intersections_count'] += 1

    def start_block(self, block):
        self.stats['blocks_count'] += 1

    def start_building(self, building):
        self.stats['buildings_count'] += 1

    def __repr__(self):
        return textwrap.dedent("""
        Roads: {roads_count}
        Intersections: {intersections_count}
        Lanes: {lanes_count}
        Buildings: {buildings_count}
        Blocks: {blocks_count}
        Polyline Geometry
          Waypoints: {polyline_waypoints_count}
          Intersections: {polyline_intersections_count}
          Average waypoints: {average_polyline_waypoints}
          Average intersections: {average_polyline_intersections}
        Lines and Arcs Geometry
          Waypoints: {lines_and_arcs_waypoints_count}
          Intersections: {lines_and_arcs_intersections_count}
          Average waypoints: {average_lines_and_arcs_waypoints}
          Average intersections: {average_lines_and_arcs_intersections}""".format(**self.stats))[1:]

    def _clear_counters(self):
        self.stats = {
            'roads_count': 0,
            'lanes_count': 0,
            'buildings_count': 0,
            'blocks_count': 0,
            'intersections_count': 0,
            'polyline_waypoints_count': 0,
            'polyline_intersections_count': 0,
            'average_polyline_intersections': 0,
            'average_polyline_waypoints': 0,
            'lines_and_arcs_waypoints_count': 0,
            'lines_and_arcs_intersections_count': 0,
            'average_lines_and_arcs_intersections': 0,
            'average_lines_and_arcs_waypoints': 0
        }

    def _compute_derived_statistics(self):
        lanes_count = float(self.stats['lanes_count'])
        if lanes_count != 0.0:
            self.stats['average_polyline_intersections'] = self.stats['polyline_intersections_count'] / lanes_count
            self.stats['average_polyline_waypoints'] = self.stats['polyline_waypoints_count'] / lanes_count
            self.stats['average_lines_and_arcs_intersections'] = self.stats['lines_and_arcs_intersections_count'] / lanes_count
            self.stats['average_lines_and_arcs_waypoints'] = self.stats['lines_and_arcs_waypoints_count'] / lanes_count
