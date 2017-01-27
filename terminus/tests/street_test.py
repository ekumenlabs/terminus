import unittest
import mock

from models.street import Street


class StreetTest(unittest.TestCase):

    def test_accept(self):
        street = Street()
        generator_mock = mock.Mock()
        calls = [mock.call.start_street(street), mock.call.end_street(street)]
        street.accept(generator_mock)
        generator_mock.assert_has_calls(calls)
