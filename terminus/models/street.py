from road import Road


class Street(Road):
    def __init__(self, name=None):
        super(Street, self).__init__(name)
        self.add_lane(0)

    def accept(self, generator):
        generator.start_street(self)
        for lane in self.get_lanes():
            lane.accept(generator)
        generator.end_street(self)
