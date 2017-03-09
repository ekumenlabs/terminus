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

from city_visitor import CityVisitor
import matplotlib.pyplot as plt
from models.city import City


class StreetPlotGenerator(CityVisitor):

    def write_to(self, destination_file):
        bounding_box = self.city.bounding_box()
        plt.figure(figsize=(bounding_box.width() / 100.0,
                            bounding_box.height() / 100.0),
                   dpi=150)
        self.run()
        plt.savefig(destination_file, dpi=150)

    def draw_lane(self, lane):
        x = []
        y = []
        for point in lane.geometry():
            x.append(point.x)
            y.append(point.y)
        return plt.plot(x, y)

    def start_street(self, street):
        for lane in street.get_lanes():
            line = self.draw_lane(lane)
            plt.setp(line, linewidth=1)

    def start_trunk(self, trunk):
        for lane in trunk.get_lanes():
            line = self.draw_lane(lane)
            plt.setp(line, linewidth=1)
