import unittest
import mock

from models.street import Street


class StreetTest(unittest.TestCase):

    def test_street(self):
        street = Street()
        generator_mock = mock.Mock()
        street.accept(generator_mock)
        calls = [mock.call.start_street(street), mock.call.end_street(street)]
        generator_mock.assert_has_calls(calls)
