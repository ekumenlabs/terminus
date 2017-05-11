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

import matplotlib.pyplot as plt

from models.polyline_geometry import PolylineGeometry
from models.lines_and_arcs_geometry import LinesAndArcsGeometry
from city_visitor import CityVisitor
from models.city import City


class StreetPlotGenerator(CityVisitor):

    def write_to(self, destination_file):
        bounding_box = self.city.bounding_box()
        figure1 = plt.figure(1, figsize=self._compute_figure_size(), dpi=150)
        figure2 = plt.figure(2, figsize=self._compute_figure_size(), dpi=150)
        self.run()
        plt.figure(1)
        plt.savefig(destination_file + '_streets_polyline.png', dpi=150)
        plt.close(figure1)
        plt.figure(2)
        plt.savefig(destination_file + '_streets_lines_and_arcs.png', dpi=150)
        plt.close(figure2)

    def start_street(self, street):
        self._plot_road(street)

    def start_trunk(self, trunk):
        self._plot_road(trunk)

    def _plot_road(self, road):
        for lane in road.lanes():
            self._draw_geometry(1, lane.path_for(PolylineGeometry))
            self._draw_geometry(2, lane.path_for(LinesAndArcsGeometry))

    def _draw_geometry(self, image_id, path):
        plt.figure(image_id)
        x = []
        y = []
        for point in path.line_interpolation_points():
            x.append(point.x)
            y.append(point.y)
        polyline = plt.plot(x, y)
        plt.setp(polyline, linewidth=1)

    def _compute_figure_size(self):
        bounding_box = self.city.bounding_box()
        area = bounding_box.width() * bounding_box.height()
        if area < 1e3:
            divisor = 5.0
        elif area < 1e4:
            divisor = 10.0
        elif area < 1e5:
            divisor = 25.0
        elif area < 1e6:
            divisor = 50.0
        else:
            divisor = 100.0
        return (bounding_box.width() / divisor,
                bounding_box.height() / divisor)
