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
        for node in lane.get_nodes():
            self.stats['lane_nodes_count'] += 1
            if node.is_intersection():
                self.stats['lane_intersections_count'] += 1

    def start_block(self, block):
        self.stats['blocks_count'] += 1

    def start_building(self, building):
        self.stats['buildings_count'] += 1

    def __repr__(self):
        return textwrap.dedent("""
        Roads: {roads_count}
        Intersections: {intersections_count}
        Lanes: {lanes_count}
        Total lane nodes: {lane_nodes_count}
        Total lane intersections: {lane_intersections_count}
        Average lane nodes: {average_lane_nodes}
        Average lane intersections: {average_lane_intersections}
        Buildings: {buildings_count}
        Blocks: {blocks_count}""".format(**self.stats))[1:]

    def _clear_counters(self):
        self.stats = {
            'roads_count': 0,
            'lanes_count': 0,
            'buildings_count': 0,
            'blocks_count': 0,
            'intersections_count': 0,
            'lane_nodes_count': 0,
            'lane_intersections_count': 0,
            'average_lane_intersections': 0,
            'average_lane_nodes': 0
        }

    def _compute_derived_statistics(self):
        lanes_count = float(self.stats['lanes_count'])
        if lanes_count != 0.0:
            self.stats['average_lane_intersections'] = self.stats['lane_intersections_count'] / lanes_count
            self.stats['average_lane_nodes'] = self.stats['lane_nodes_count'] / lanes_count

