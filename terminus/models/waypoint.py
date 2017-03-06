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


class Waypoint(object):
    def __init__(self, lane, source_node, center):
        self.lane = lane
        self.source_node = source_node
        self.center = center
        self.be_reference()

    @classmethod
    def entry(cls, lane, source_node, center):
        waypoint = cls(lane, source_node, center)
        waypoint.be_entry()
        return waypoint

    @classmethod
    def exit(cls, lane, source_node, center):
        waypoint = cls(lane, source_node, center)
        waypoint.be_exit()
        return waypoint

    def is_exit(self):
        return self.type.is_exit()

    def is_entry(self):
        return self.type.is_entry()

    def be_entry(self):
        self.type = EntryPoint()

    def be_exit(self):
        self.type = ExitPoint()

    def be_reference(self):
        self.type = ReferencePoint()

    def connected_waypoints(self):
        return self.source_node.connected_waypoints_for(self)

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and \
               (self.type == other.type) and \
               (self.center == other.center) and \
               (self.lane == other.lane) and \
               (self.source_node == other.source_node)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.type, self.center, self.lane, self.source_node))

    def __repr__(self):
        return str(self.type) + "Waypoint at " + str(self.center) + \
            ". Source node " + str(self.source_node)


class WaypointType(object):
    def is_exit(self):
        raise NotImplementedError()

    def is_entry(self):
        raise NotImplementedError()

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__class__)


class ReferencePoint(WaypointType):
    def is_exit(self):
        return False

    def is_entry(self):
        return False

    def __repr__(self):
        return ""


class EntryPoint(WaypointType):
    def is_exit(self):
        return False

    def is_entry(self):
        return True

    def __repr__(self):
        return "[ENTRY] "


class ExitPoint(WaypointType):
    def is_exit(self):
        return True

    def is_entry(self):
        return False

    def __repr__(self):
        return "[EXIT] "
