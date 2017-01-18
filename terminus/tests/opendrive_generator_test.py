import unittest

from geometry.point import Point
from geometry.latlon import LatLon
from models.city import City
from models.road import *
from models.street import Street
from models.trunk import Trunk
import math
import textwrap

from generators.opendrive_generator import OpenDriveGenerator


class OpenDriveGeneratorTest(unittest.TestCase):

    def setUp(self):
        pass

    def _get_sample_generator(self):
        city = City("Empty")
        latlon = LatLon(45.0, 45.0)
        return OpenDriveGenerator(city, latlon)

    def _generate_output(self):
        self.generated_contents = self.generator.generate()

    def _assert_contents_are(self, expected_contents):
        expected = textwrap.dedent(expected_contents)[1:]
        self.assertMultiLineEqual(self.generated_contents, expected)

    def test_empty_city(self):
        self.generator = self._get_sample_generator()
        self._generate_output()
        self._assert_contents_are("""
<?xml version="1.0" standalone="yes"?>
  <OpenDRIVE xmlns="http://www.opendrive.org">
    <header revMajor="1" revMinor="1" name="Empty" version="1.00" north="0.0000000000000000e+00" south="0.0000000000000000e+00" east="0.0000000000000000e+00" west="0.0000000000000000e+00" maxRoad="0" maxJunc="0" maxPrg="0">
    </header>

</OpenDRIVE>""")

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

    def test_road_legnth(self):
        generator = self._get_sample_generator()
        points = []
        points.append(Point(-1.0, 0.0))
        points.append(Point(0.0, 0.0))
        points.append(Point(0.0, 1.0))

        distances = generator._get_distances(points)
        road_length = generator._road_length(distances)
        self.assertEqual(2.0, road_length)
        self.assertEqual(0.0, generator._road_length([]))

    def test_yaw(self):
        generator = self._get_sample_generator()
        pA = Point(0.0, 0.0)
        pB = Point(1.0, 0.0)

        angle = generator._yaw(pA, pB)
        self.assertEqual(0.0, angle)

        pB = Point(1.0, 1.0)
        angle = generator._yaw(pA, pB)
        self.assertEqual(math.pi / 4.0, angle)

        pB = Point(0.0, 1.0)
        angle = generator._yaw(pA, pB)
        self.assertEqual(math.pi / 2.0, angle)

        pB = Point(-1.0, 1.0)
        angle = generator._yaw(pA, pB)
        self.assertEqual(3.0 * math.pi / 4.0, angle)

        pB = Point(-1.0, 0.0)
        angle = generator._yaw(pA, pB)
        self.assertEqual(math.pi, angle)

        pB = Point(-1.0, -1.0)
        angle = generator._yaw(pA, pB)
        self.assertEqual(- 3.0 * math.pi / 4.0, angle)

        pB = Point(0.0, -1.0)
        angle = generator._yaw(pA, pB)
        self.assertEqual(- math.pi / 2.0, angle)

        pB = Point(1.0, -1.0)
        angle = generator._yaw(pA, pB)
        self.assertEqual(- math.pi / 4.0, angle)

    def test_yaws(self):
        generator = self._get_sample_generator()
        points = []
        points.append(Point(0.0, 0.0))
        points.append(Point(1.0, 1.0))
        points.append(Point(2.0, 0.0))
        points.append(Point(2.0, 1.0))

        _angles = []
        _angles.append(math.pi / 4.0)
        _angles.append(-math.pi / 4.0)
        _angles.append(math.pi / 2.0)

        angles = generator._yaws(points)

        self.assertEqual(len(_angles), len(angles))
        for i in range(0, len(angles)):
            self.assertEqual(_angles[i], angles[i])
