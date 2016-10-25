from road import Road


class Street(Road):
    def __init__(self, name=None):
        super(Street, self).__init__(self.default_width(), name)

    @classmethod
    def default_width(cls):
        return 5

    def accept(self, generator):
        generator.start_street(self)
        generator.end_street(self)
