from road import Road


class Street(Road):
    def __init__(self, width=5, name=None):
        super(Street, self).__init__(width, name)

    def accept(self, generator):
        generator.start_street(self)
        generator.end_street(self)
