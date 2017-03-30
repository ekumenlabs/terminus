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

import math
import numpy as np
import latlon
import ecef


class Enu(object):

    def __init__(self, e, n, u):
        self.e = e
        self.n = n
        self.u = u

    def __eq__(self, other):
        return self.e == other.e and self.n == other.n and self.u == other.u

    def __hash__(self):
        return hash((self.e, self.n, self.u))

    def to_ecef(self, origin):
        # this doesn't work at the poles because longitude is not uniquely defined there
        sin_lon = origin._sin_lon()
        sin_lat = origin._sin_lat()
        cos_lon = origin._cos_lon()
        cos_lat = origin._cos_lat()
        global_to_ecef_matrix = np.array([[-sin_lon, -cos_lon * sin_lat, cos_lon * cos_lat],
                                          [cos_lon, - sin_lon * sin_lat, sin_lon * cos_lat],
                                          [0, cos_lat, sin_lat]])
        enu_vector = np.array([[self.e], [self.n], [self.u]])
        ecef_vector = np.dot(global_to_ecef_matrix, enu_vector)
        return ecef.Ecef(ecef_vector[0][0], ecef_vector[1][0], ecef_vector[2][0])
