import unittest
import mock

from models.trunk import Trunk


class TrunklTest(unittest.TestCase):

    def test_accept(self):
        trunk = Trunk()
        generator_mock = mock.Mock()
        trunk.get_nodes = mock.Mock(return_value=[])
        trunk.lanes = mock.Mock(return_value=[])
        calls = [mock.call.start_trunk(trunk), mock.call.end_trunk(trunk)]
        trunk.accept(generator_mock)
        generator_mock.assert_has_calls(calls)
