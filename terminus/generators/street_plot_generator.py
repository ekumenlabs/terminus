from city_visitor import CityVisitor
import matplotlib.pyplot as plt


class StreetPlotGenerator(CityVisitor):

    def write_to(self, destination_file):
        plt.figure(figsize=(10, 10), dpi=100)
        self.run()
        plt.savefig(destination_file, dpi=100)

    def draw_road(self, road):
        x = []
        y = []
        for node in road.nodes:
            center = node.center
            x.append(center.x)
            y.append(center.y)
        return plt.plot(x, y)

    def start_street(self, street):
        line = self.draw_road(street)
        plt.setp(line, linewidth=2)

    def start_trunk(self, trunk):
        line = self.draw_road(trunk)
        plt.setp(line, linewidth=4)
