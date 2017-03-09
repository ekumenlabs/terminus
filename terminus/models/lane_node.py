"""
/*
 * Copyright (C) 2017 Open Source Robotics Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
"""
from geometry.point import Point


class LaneNode(object):
    def __init__(self, center, main_lane, road_node):
        self.center = center
        self.main_lane = main_lane
        self.source = road_node
        self.added_to(main_lane)

    def added_to(self, lane):
        raise NotImplementedError()

    def involved_lanes(self):
        raise NotImplementedError()

    def involved_lanes_except(self, target_lane):
        return filter(lambda lane: lane is not target_lane, self.involved_lanes())

    def involves(self, lane):
        return any(lane is other_lane for other_lane in self.involved_lanes())

    def get_waypoints_for(self, lane):
        raise NotImplementedError()

    def get_entry_waypoints_for(self, lane):
        return filter(lambda waypoint: waypoint.is_entry(), self.get_waypoints_for(lane))

    def get_exit_waypoints_for(self, lane):
        return filter(lambda waypoint: waypoint.is_exit(), self.get_waypoints_for(lane))

    def connected_waypoints_for(self, waypoint):
        raise NotImplementedError()

    def __eq__(self, other):
        '''
        To avoid issues with float math errors we round the center to the 5th
        decimal when comparing to another node (see also the __has__ method)
        '''
        return self.__class__ == other.__class__ and \
            self.center.almost_equal_to(other.center, 5) and \
            self.source == other.source and \
            self.main_lane == other.main_lane

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.__class__, self.center.rounded_to(5), self.source, self.main_lane))
