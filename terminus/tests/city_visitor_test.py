import unittest
import mock

from generators.city_visitor import CityVisitor


class CityVisitorTest(unittest.TestCase):

    def test_city_accept(self):
        city = mock.Mock()
        visitor = CityVisitor(city)
        visitor.run()
        city.accept.assert_called()
