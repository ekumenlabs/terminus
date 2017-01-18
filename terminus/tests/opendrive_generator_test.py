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
