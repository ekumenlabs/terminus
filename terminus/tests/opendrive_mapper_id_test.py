import unittest

from geometry.point import Point
from models.city import City
from models.road import *
from models.street import Street

from generators.opendrive_id_mapper import OpenDriveIdMapper
from generators.opendrive_id_mapper import Connection
from generators.opendrive_id_mapper import Junction

# class Connection(unittest.TestCase):

#     def setUp(self):
#         self.city = City()

#     def create_cross(self):
#         self.city.add_road(Street.from_points([Point(0, 0), Point(100, 0)]))
#         self.city.add_road(Street.from_points([Point(-50, -50), Point(50, 50)]))

#     def get_connections(self):
#         connections = []
#         for road in self.city.roads:
#             exit_waypoints = filter(lambda waypoint: waypoint.is_exit(), road.get_waypoints())
#             for exit_waypoint in exit_waypoints:
#                 for entry_waypoint in exit_waypoint.connected_waypoints():
#                     connection = Connection(exit_waypoint, entry_waypoint)
#         return connections

#     def test_constructor(self):
#         self.create_cross()
#         assertNotEqual(len(self.get_connections()), 0)
#         for connection in self.get_connections():
#             assertEqual(connection.entry, entry_waypoint)
#             assertEqual(connection.exit, exit_waypoint)

#     def test_eq(self):
#         self.create_cross()
#         connections = self.get_connections()
#         assert(connections[0] == connections[0], True)
#         assert(connections[1] == connections[1], True)
#         assert(connections[0] == connections[1], False)


# class Junction(unittest.TestCase):

#     def setUp(self):
#         self.city = City()

#     def create_cross(self):
#         self.city.add_road(Street.from_points([Point(0, 0), Point(100, 0)]))
#         self.city.add_road(Street.from_points([Point(-50, -50), Point(50, 50)]))

#     def test_add_connection():
#         self.create_cross()
#         connections = self.get_connections()
#         j = Junction(1)
#         for connection in self.get_connections():
#             j.add_connection(connection)
#             assertEqual(j.connections[-1], connection)
