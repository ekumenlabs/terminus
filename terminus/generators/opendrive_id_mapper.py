from city_visitor import CityVisitor


# This class is inteded to handle ids of junctions and roads.
# All the ids should be unique, so this class will handle that, and the
# reference to the objects it gives the new id. This class will have
# development further.
class OpenDriveIdMapper(CityVisitor):

    def __init__(self, city):
        super(OpenDriveIdMapper, self).__init__(city)

    def run(self):
        self.id_counter = 0
        self.roads_to_id = {}
        self.create_junctions()
        self.map_roads()

    def get_new_id(self):
        self.id_counter = self.id_counter + 1
        return self.id_counter

    def id_for(self, road):
        road_hash = hash(road)
        if road_hash in self.roads_to_id:
            return self.roads_to_id[road_hash]
        return None

    def create_junctions(self):
        entry_exits = self.create_extryexits()
        self.junctions = []
        for entry_exit in entry_exits:
            _junctions = filter(
                lambda junction:
                    junction.contains_waypoint(entry_exit.entry) or junction.contains_waypoint(entry_exit.exit),
                self.junctions)
            if _junctions:
                _junction = _junctions[0]
            else:
                _junction = Junction(self.get_new_id())
                self.junctions.append(_junction)
            _junction.add_connection(entry_exit)

    def create_extryexits(self):
        connections = []
        for road in self.city.roads:
            exit_waypoints = filter(lambda waypoint: waypoint.is_exit(), road.get_waypoints())
            waypoint_connections = []
            for exit_waypoint in exit_waypoints:
                for entry_waypoint in exit_waypoint.connected_waypoints():
                    connection = Connection(exit_waypoint, entry_waypoint)
                    connections.append(connection)
        return connections

    def map_roads(self):
        for road in self.city.roads:
            self.roads_to_id[hash(road)] = self.get_new_id()


class Junction:

    def __init__(self, _id):
        self.connections = []
        self.id = _id

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


class Connection:

    def __init__(self, _exit, _entry):
        self.entry = _entry
        self.exit = _exit

    def __str__(self):
        return 'entry_' + str(hash(self.entry)) + '_exit_' + str(hash(self.exit))
