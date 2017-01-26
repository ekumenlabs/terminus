class Waypoint(object):
    def __init__(self, road, source_node, center):
        self.road = road
        self.source_node = source_node
        self.center = center
        self.be_reference()

    @classmethod
    def entry(cls, road, source_node, center):
        waypoint = cls(road, source_node, center)
        waypoint.be_entry()
        return waypoint

    @classmethod
    def exit(cls, road, source_node, center):
        waypoint = cls(road, source_node, center)
        waypoint.be_exit()
        return waypoint

    def is_exit(self):
        return self.type.is_exit()

    def is_entry(self):
        return self.type.is_entry()

    def be_entry(self):
        self.type = EntryPoint()

    def be_exit(self):
        self.type = ExitPoint()

    def be_reference(self):
        self.type = ReferencePoint()

    def connected_waypoints(self):
        return self.source_node.connected_waypoints_for(self)

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and \
               (self.type == other.type) and \
               (self.center == other.center) and \
               (self.road == other.road)
        # (self.source_node == other.source_node)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.type, self.center, self.road))

    def __repr__(self):
        return str(self.type) + "Waypoint at " + str(self.center)


class WaypointType(object):
    def is_exit(self):
        raise NotImplementedError()

    def is_entry(self):
        raise NotImplementedError()

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__class__)


class ReferencePoint(WaypointType):
    def is_exit(self):
        return False

    def is_entry(self):
        return False

    def __repr__(self):
        return ""


class EntryPoint(WaypointType):
    def is_exit(self):
        return False

    def is_entry(self):
        return True

    def __repr__(self):
        return "[ENTRY] "


class ExitPoint(WaypointType):
    def is_exit(self):
        return True

    def is_entry(self):
        return False

    def __repr__(self):
        return "[EXIT] "
