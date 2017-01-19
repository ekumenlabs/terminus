from city_visitor import CityVisitor

import logging


# This class is inteded to handle ids of junctions and roads.
# All the ids should be unique, so this class will handle that, and the
# reference to the objects it gives the new id. This class will have
# development further.
class OpenDriveIdMapper(CityVisitor):

    def __init__(self, city):
        super(OpenDriveIdMapper, self).__init__(city)

    def run(self):
        self.id = 0
        self.segment_id = 0
        # self.create_junctions()
        # for junction in junctions:
        #    logger.info(junction)

    def id_for(self, object):
        self.segment_id = self.segment_id + 1
        return self.segment_id

    def get_new_id(self):
        self.id = self.id + 1
        return self.id

    def create_junctions(self):
        entry_exits = self.create_extryexits()
        self.junctions = []
        for entry_exit in entry_exits:
            _junction = filter(
                lambda junction:
                    junction.contains_waypoint(entry_exit.entry) or junction.contains_waypoint(entry_exit.exit),
                junctions)
            if _junction is None:
                _junction = Junction(self.get_new_id())
                self.junction.append(_junction)
            _junction.append(entry_exit.entry)
            _junction.append(entry_exit.exit)

    def create_extryexits(self):
        entry_exits = []
        for road in self.city.roads:
            exit_waypoints = filter(lambda waypoint: waypoint.is_exit(), road.get_waypoints())
            waypoint_connections = []
            for exit_waypoint in exit_waypoints:
                for entry_waypoint in exit_waypoint.connected_waypoints():
                    entry_exit = EntryExit(exit_waypoint, entry_waypoint)
                    entry_exits.append(entry_exit)


class Junction:

    def __init__(self, _id):
        self.waypoints = {}
        self.id = _id

    def add_waypoint(self, waypoint):
        self.waypoints[hash(waypoint)] = waypoint

    def contains_waypoint(self, waypoint):
        return self.waypoints[hash(waypoint)] is not None

    def __str__(self):
        hashes = ''
        for waypoint in enumerate(self.waypoints):
            hashes = hashes + ' | ' + hash(waypoint)
        return "junction: " + hashes


class EntryExit:

    def __init__(self, _exit, _entry):
        self.entry = _entry
        self.exit = _exit
