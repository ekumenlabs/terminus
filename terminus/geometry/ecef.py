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
import enu


class Ecef(object):

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def equatorial_radius(cls):
        # Semi-major axis of the WGS84 spheroid (meters)
        return 6378137.0

    @classmethod
    def polar_radius(cls):
        # Semi-minor axis of the wgs84 spheroid (meters)
        return 6356752.314245

    @classmethod
    def first_eccentricity_parameter(cls):
        # https://en.wikipedia.org/wiki/Eccentricity_(mathematics)#Ellipses
        # As a reference, this constant was computed as math.sqrt(1.0 - (Ecef.polar_radius() ** 2) / (Ecef.equatorial_radius() ** 2))
        return 0.08181919084296556

    @classmethod
    def second_eccectricity_parameter(cls):
        # https://en.wikipedia.org/wiki/Eccentricity_(mathematics)#Ellipses
        # As a reference, this constant was computed as math.sqrt((Ecef.equatorial_radius() ** 2) / (Ecef.polar_radius() ** 2) - 1.0)
        return 0.08209443795004348

    def to_latlon(self):
        lon_in_radians = math.atan2(self.y, self.x)
        lon_in_degrees = math.degrees(lon_in_radians)
        xy_norm = math.sqrt(self.x ** 2 + self.y ** 2)
        a = Ecef.equatorial_radius()
        b = Ecef.polar_radius()
        p = Ecef.second_eccectricity_parameter()
        e = Ecef.first_eccentricity_parameter()
        angle = math.atan((self.z * a) / (xy_norm * b))
        lat_in_radians = math.atan((self.z + ((p ** 2) * b * (math.sin(angle) ** 3))) /
                                   (xy_norm - (e ** 2) * a * (math.cos(angle) ** 3)))
        lat_in_degrees = math.degrees(lat_in_radians)
        return latlon.LatLon(lat_in_degrees, lon_in_degrees)

    def to_global(self, origin):
        # this doesn't work at the poles because longitude is not uniquely defined there
        sin_lon = origin._sin_lon()
        sin_lat = origin._sin_lat()
        cos_lon = origin._cos_lon()
        cos_lat = origin._cos_lat()
        local_vector_in_ecef = self - origin.to_ecef()
        ecef_vector = np.array([[local_vector_in_ecef.x],
                                [local_vector_in_ecef.y],
                                [local_vector_in_ecef.z]])
        ecef_to_global_matrix = np.array([[-sin_lon, cos_lon, 0.0],
                                          [-cos_lon * sin_lat, -sin_lon * sin_lat, cos_lat],
                                          [cos_lon * cos_lat, sin_lon * cos_lat, sin_lat]])
        enu_vector = np.dot(ecef_to_global_matrix, ecef_vector)
        return enu.Enu(enu_vector[0][0], enu_vector[1][0], enu_vector[2][0])

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __add__(self, other):
        return Ecef(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Ecef(self.x - other.x, self.y - other.y, self.z - other.z)
