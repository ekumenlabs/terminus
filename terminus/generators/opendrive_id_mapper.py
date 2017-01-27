from city_visitor import CityVisitor
from models.road import Road
import operator


# This class is inteded to handle ids of junctions and roads.
# All the ids should be unique, so this class will handle that, and the
# reference to the objects it gives the new id. This class will have
# development further.

class OpenDriveIdMapper(CityVisitor):

    def __init__(self, city):
        super(OpenDriveIdMapper, self).__init__(city)

    def run(self):
        self.id_counter = 0
        self.junction_id_max = 0
        self.road_id_max = 0
        self.od_roads = {}
        self.junctions = []
        self.create_junctions()
        self.create_roads()

    def get_new_road_id(self):
        self.id_counter = self.id_counter + 1
        self.road_id_max = self.id_counter
        return self.id_counter

    def get_new_junction_id(self):
        self.id_counter = self.id_counter + 1
        self.junction_id_max = self.id_counter
        return self.id_counter

    def create_junctions(self):
        entry_exits = self.create_connections()
        self.junctions = []
        for entry_exit in entry_exits:
            junctions = filter(
                lambda junction:
                    junction.contains_waypoint(entry_exit.entry) or junction.contains_waypoint(entry_exit.exit),
                self.junctions)
            if junctions:
                junction = junctions[0]
            else:
                junction = Junction(self.get_new_junction_id())
                self.junctions.append(junction)
            junction.add_connection(entry_exit)

    def create_connections(self):
        connections = []
        for road in self.city.roads:
            exit_waypoints = filter(lambda waypoint: waypoint.is_exit(), road.get_waypoints())
            for exit_waypoint in exit_waypoints:
                connections.extend(map(lambda entry_wp: Connection(exit_waypoint, entry_wp), exit_waypoint.connected_waypoints()))
        return connections

    def create_roads(self):
        # Create road cuts from the original roads and insert them
        # into the map
        self.create_road_cuts()
        # Create the roads from the connections. Then, create a link
        # between the road cut and the connection
        self.create_junction_roads()

    def get_od_roads_as_list(self):
        od_roads = self.od_roads.items()
        if not od_roads:
            return []
        _, roads = zip(*od_roads)
        return reduce(operator.add, roads)

    def get_road_cut(self, road_hash, waypoint):
        roads = self.od_roads[road_hash]
        road_cuts = filter(lambda road: self.road_cut_contains_waypoint(road, waypoint), roads)
        if not road_cuts:
            return None
        if waypoint.is_entry and len(road_cuts) == 2:
            return road_cuts[1]
        return road_cuts[0]

    def create_junction_roads(self):
        for junction in self.junctions:
            for conn in junction.connections:
                road = self.create_road_from_connection(conn)
                road.id = self.get_new_road_id()
                road.junction_id = junction.id
                (entry_hash, exit_hash) = conn.get_road_hashes()
                entry_road_cut = self.get_road_cut(entry_hash, conn.entry)
                exit_road_cut = self.get_road_cut(exit_hash, conn.exit)
                if entry_road_cut is not None:
                    entry_road_cut.junction_id = junction.id
                    entry_road_cut.successor = junction.id
                    entry_road_cut.successor_type = "junction"
                    road.predecessor = entry_road_cut.id
                    road.predecessor_type = "road"
                    junction.add_link(Link(entry_road_cut.id, road.id))
                if exit_road_cut is not None:
                    exit_road_cut.junction_id = junction.id
                    exit_road_cut.predecessor = junction.id
                    exit_road_cut.predecessor_type = "junction"
                    road.successor = exit_road_cut.id
                    road.successor_type = "road"
                    junction.add_link(Link(exit_road_cut.id, road.id))
                self.od_roads[hash(road)] = [road]

    def road_cut_contains_waypoint(self, road_cut, waypoint):
        wps = filter(lambda wp: wp.center == waypoint.center, road_cut.get_waypoints())
        return not wps

    def cut_road(self, road, cutting_waypoint_ids):
        cut_roads = []
        for i in range(0, len(cutting_waypoint_ids) - 1):
            cut_road = OpenDriveRoad.from_base_road(road, cutting_waypoint_ids[i][0], cutting_waypoint_ids[i + 1][0])
            cut_road.id = self.get_new_road_id()
            if cutting_waypoint_ids[i][1] is 'exit' or cutting_waypoint_ids[i][1] is 'entry':
                cut_road.predecessor = cut_roads[-1].id
                cut_road.predecessor_type = 'road'
                cut_roads[-1].successor = cut_road.id
                cut_roads[-1].successor_type = 'road'
            cut_roads.append(cut_road)
        if cutting_waypoint_ids[-2][1] is 'exit' or cutting_waypoint_ids[-2][1] is 'entry':
            cut_roads[-1].predecessor = cut_roads[-2].id
            cut_roads[-1].predecessor_type = 'road'
            cut_roads[-2].successor = cut_roads[-1].id
            cut_roads[-2].successor_type = 'road'
        return cut_roads

    def create_road_cuts(self):
        for road in self.city.roads:
            road_hash = hash(road)
            cutting_waypoint_ids = self.get_cutting_waypoints(road)
            cut_roads = self.cut_road(road, cutting_waypoint_ids)
            self.od_roads[road_hash] = cut_roads

    def create_road_from_connection(self, connection):
        width = min(connection.entry.road.width, connection.exit.road.width)
        road = OpenDriveRoad(width)
        road.add_point(connection.exit.center)
        road.add_point(connection.entry.center)
        return road

    def waypoint_type(self, waypoint, waypoints):
        if waypoint == waypoints[0]:
            return 'start'
        if waypoint == waypoints[-1]:
            return 'end'
        if waypoint.is_entry():
            return 'entry'
        if waypoint.is_exit():
            return 'exit'
        return 'other'

    def get_cutting_waypoints(self, road):
        waypoints = road.get_waypoints()
        # Got all the junctions that have a waypoint whose road
        # is the current road in the iteration
        connection_waypoints_ids = map(
            lambda waypoint:
                waypoints.index(waypoint) if self.waypoint_type(waypoint, waypoints) != 'other' else None,
            road.get_waypoints())
        connection_waypoints_ids = filter(lambda id: id is not None, connection_waypoints_ids)

        waypoint_types = []
        for id in connection_waypoints_ids:
            waypoint_types.append(self.waypoint_type(waypoints[id], waypoints))

        return zip(connection_waypoints_ids, waypoint_types)


class OpenDriveRoad(Road):

    def __init__(self, width, name=None, id=None):
        super(OpenDriveRoad, self).__init__(width, name)
        self.id = id
        self.junction_id = -1
        self.predecessor = None
        self.predecessor_type = None
        self.successor = None
        self.successor_type = None

    @classmethod
    def from_base_road(cls, road, initPoint, endPoint):
        r = OpenDriveRoad(road.width, road.name)
        wps = road.get_waypoints()
        for i in range(initPoint, endPoint + 1):
            r.add_point(wps[i].center)
        return r

    def add_points(self, points):
        for point in points:
            self.add_point(point)


class Junction(object):

    def __init__(self, _id):
        self.connections = []
        self.id = _id
        self.links = []

    def add_link(self, link):
        self.links.append(link)

    def add_connection(self, connection):
        self.connections.append(connection)

    def contains_waypoint(self, waypoint):
        connections = filter(
            lambda conn:
                conn.entry == waypoint or conn.exit == waypoint,
            self.connections)
        if connections:
            return True
        return False

    def connection_size(self):
        return len(self.connections)

    def __str__(self):
        hashes = ''
        for connection in self.connections:
            hashes = hashes + '_' + str(connection)
        return "junction: " + hashes


class Link(object):

    def __init__(self, incomming_road=None, connecting_road=None):
        self.incomming_road = incomming_road
        self.connecting_road = connecting_road


class Connection(object):

    def __init__(self, _exit, _entry):
        self.entry = _entry
        self.exit = _exit

    def get_road_hashes(self):
        return (hash(self.entry.road), hash(self.exit.road))

    def __str__(self):
        return 'entry_' + str(hash(self.entry)) + '_exit_' + str(hash(self.exit))

    def __eq__(self, other):
        return self.entry == other.entry and self.exit == other.exit
