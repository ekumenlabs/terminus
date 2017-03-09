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
from road_node import RoadNode
from waypoint import Waypoint


class RoadSimpleNode(RoadNode):

    def __init__(self, center, name=None):
        super(RoadSimpleNode, self).__init__(center, name)
        self.road = None

    def is_intersection(self):
        return False

    def added_to(self, road):
        self.road = road

    def removed_from(self, road):
        self.road = None

    def involved_roads(self):
        return [self.road]

    def __repr__(self):
        return "RoadSimpleNode @ " + str(self.center)
