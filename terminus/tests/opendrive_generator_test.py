import unittest

from geometry.point import Point
from geometry.latlon import LatLon
from models.city import City
from models.road import *
from models.street import Street
from models.trunk import Trunk

from generators.opendrive_generator import OpenDriveGenerator


class OpenDriveGeneratorTest(unittest.TestCase):

    def setUp(self):
        pass

    def _get_sample_generator(self):
        city = City("Empty")
        latlon = LatLon(45.0, 45.0)
        return OpenDriveGenerator(city, latlon)

    def test_distance(self):
        generator = self._get_sample_generator()
        pA = Point(1.0, 0.0)
        pB = Point(-1.0, 0.0)
        d = generator._distance(pA, pB)
        self.assertEqual(d, 2.0)

    def test_distances(self):
        generator = self._get_sample_generator()
        points = []
        points.append(Point(-1.0, 0.0))
        points.append(Point(0.0, 0.0))
        points.append(Point(0.0, 1.0))

        distances = generator._get_distances(points)
        self.assertEqual(2, len(distances))
        self.assertEqual(1.0, distances[0])
        self.assertEqual(1.0, distances[1])
