from road import Road


class Trunk(Road):
    def __init__(self, width=10, name=None):
        super(Trunk, self).__init__(width, name)
        self.add_lane(2)
        self.add_lane(-2)

    def accept(self, generator):
        generator.start_trunk(self)
        generator.end_trunk(self)
