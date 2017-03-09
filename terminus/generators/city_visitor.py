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


class CityVisitor(object):

    def __init__(self, city):
        self.city = city

    def run(self):
        self.city.accept(self)

    # Double-dispatching methods. By default do nothing. Override in subclasses
    # to build the required file contents

    def start_city(self, city):
        pass

    def end_city(self, city):
        pass

    def start_street(self, street):
        pass

    def end_street(self, street):
        pass

    def start_trunk(self, trunk):
        pass

    def end_trunk(self, trunk):
        pass

    def start_lane(self, lane):
        pass

    def end_lane(self, lane):
        pass

    def start_ground_plane(self, plane):
        pass

    def end_ground_plane(self, plane):
        pass

    def start_block(self, block):
        pass

    def end_block(self, block):
        pass

    def start_building(self, building):
        pass

    def end_building(self, building):
        pass
