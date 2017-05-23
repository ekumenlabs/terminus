"""
Copyright (C) 2017 Open Source Robotics Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from road import Road


class Trunk(Road):
    def __init__(self, name=None):
        super(Trunk, self).__init__(name)
        self.add_lane(2)
        self.add_lane(-2, reversed=True)

    def accept(self, generator):
        generator.start_trunk(self)
        for lane in self.lanes():
            lane.accept(generator)
        generator.end_trunk(self)
