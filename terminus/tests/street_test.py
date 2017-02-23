import unittest
import mock

from models.street import Street


class StreetTest(unittest.TestCase):

    def test_accept(self):
        street = Street()
        street.get_nodes = mock.Mock(return_value=[])
        street.get_lanes = mock.Mock(return_value=[])
        generator_mock = mock.Mock()
        calls = [mock.call.start_street(street), mock.call.end_street(street)]
        street.accept(generator_mock)
        generator_mock.assert_has_calls(calls)
