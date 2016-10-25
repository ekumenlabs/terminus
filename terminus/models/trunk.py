from road import Road


class Trunk(Road):
    def __init__(self, name=None):
        super(Trunk, self).__init__(self.default_width(), name)

    @classmethod
    def default_width(cls):
        return 10

    def accept(self, generator):
        generator.start_trunk(self)
        generator.end_trunk(self)
