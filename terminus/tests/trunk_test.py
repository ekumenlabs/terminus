import unittest
import mock

from models.trunk import Trunk


class TrunklTest(unittest.TestCase):

    def test_trunk(self):
        trunk = Trunk()
        generator_mock = mock.Mock()
        trunk.accept(generator_mock)
        calls = [mock.call.start_trunk(trunk), mock.call.end_trunk(trunk)]
        generator_mock.assert_has_calls(calls)
