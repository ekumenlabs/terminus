from city_visitor import CityVisitor
import matplotlib.pyplot as plt


class StreetPlotGenerator(CityVisitor):

    def write_to(self, destination_file):
        plt.figure(figsize=(20, 20), dpi=150)
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
