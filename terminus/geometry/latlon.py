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


class LatLon(object):

    def _antimeridian_longitude(self, longitude):
        if longitude >= 0:
            return longitude - 180
        else:
            return longitude + 180

    def _normalize(self):
        self.lat = self.lat % 360
        self.lon = self.lon % 360

        if 0 <= self.lon <= 180:
            self.lon = self.lon
        else:
            self.lon = self.lon - 360

        if 0 <= self.lat <= 90:
            self.lat = self.lat
        elif 90 < self.lat <= 270:
            self.lat = 180 - self.lat
            self.lon = self._antimeridian_longitude(self.lon)
        else:
            self.lat = self.lat - 360

        if self.lat == 90 or self.lat == -90:
            self.lon = 0

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
        self._normalize()

    def __eq__(self, other):
        if self.lat != other.lat:
            return False
        else:
            return (self.lon == other.lon) or \
                   (abs(self.lon) == 180 and abs(other.lon) == 180) or \
                abs(self.lat) == 90

    def __repr__(self):
        return 'LatLon(%s, %s)' % (self.lat, self.lon)

    def sum(self, other):
        return LatLon(self.lat + other.lat, self.lon + other.lon)

    def curvature(self):
        # Radius of planet curvature (meters)
        curvature = Ecef.equatorial_radius() / math.sqrt(1 - Ecef.first_eccentricity_parameter() ** 2 * self._sin_lat() ** 2)
        return curvature

    def latlon_to_ecef(self):
        x = self.curvature() * self._cos_lat() * self._cos_lon()
        y = self.curvature() * self._cos_lat() * self._sin_lon()
        z = ((Ecef.polar_radius() ** 2) / (Ecef.equatorial_radius() ** 2)) * self.curvature() * self._sin_lat()
        return Ecef(x, y, z)

    def global_to_ecef_rotation(self, enu):
        # this doesn't work at the poles because longitude is not uniquely defined there
        sin_lon = self._sin_lon()
        sin_lat = self._sin_lat()
        cos_lon = self._cos_lon()
        cos_lat = self._cos_lat()
        global_to_ecef_matrix = np.array([[-sin_lon, -cos_lon * sin_lat, cos_lon * cos_lat],
                                          [cos_lon, - sin_lon * sin_lat, sin_lon * cos_lat],
                                          [0, cos_lat, sin_lat]])
        enu_vector = np.array([[enu.e], [enu.n], [enu.u]])
        ecef_vector = np.dot(global_to_ecef_matrix, enu_vector)
        return Ecef(ecef_vector[0][0], ecef_vector[1][0], ecef_vector[2][0])

    def ecef_to_global(self, ecef):
        # this doesn't work at the poles because longitude is not uniquely defined there
        sin_lon = self._sin_lon()
        sin_lat = self._sin_lat()
        cos_lon = self._cos_lon()
        cos_lat = self._cos_lat()
        local_vector_in_ecef = ecef - self.latlon_to_ecef()
        ecef_vector = np.array([[local_vector_in_ecef.x],
                                [local_vector_in_ecef.y],
                                [local_vector_in_ecef.z]])
        ecef_to_global_matrix = np.array([[-sin_lon, cos_lon, 0.0],
                                          [-cos_lon * sin_lat, -sin_lon * sin_lat, cos_lat],
                                          [cos_lon * cos_lat, sin_lon * cos_lat, sin_lat]])
        enu_vector = np.dot(ecef_to_global_matrix, ecef_vector)
        return Enu(enu_vector[0][0], enu_vector[1][0], enu_vector[2][0])

    def translate(self, delta_lat_lon):
        """
        Given LatLon point and a delta_lat_lon tuple, returns a LatLon point
        corresponding to the place where an object would be after starting at
        the LatLon point and moving delta_lat_lon[1] meters in the
        longitudinal direction, and delta_lat_lon[0] meters in the
        latitudinal direction in the plane that is tangent to the Earth on the
        original LatLon point.

        """
        delta_in_enu = Enu(delta_lat_lon[1], delta_lat_lon[0], 0)
        delta_in_ecef = self.global_to_ecef_rotation(delta_in_enu)
        inicial_point_in_ecef = self.latlon_to_ecef()
        final_point_in_ecef = inicial_point_in_ecef + delta_in_ecef
        return final_point_in_ecef.ecef_to_latlon()

    def delta_in_meters(self, other):
        """
        Given two LatLon objects, it returns an (x, y) tuple that approximates
        how many meters in the latitudinal directon (x) and in the longitudinal
        direction (y) is the second point(other) from the first(self).

        """
        delta_in_enu = self.ecef_to_global(other.latlon_to_ecef())
        return (delta_in_enu.n, delta_in_enu.e)

    def midpoint(self, other):
        '''
        This method gives an approximation of the midpoint between two LatLon
        objects (we assume a plane instead of a sphere for point calculations).
        We are not considering the possibility of a pole lying in the part of
        the city that has this LatLon points as opposite corners (The South Pole
        is in Antarctica, and the North Pole lies in the water)
        '''
        if abs(self.lon - other.lon) < 180:
            mid_point = LatLon((self.lat + other.lat) / 2,
                               (self.lon + other.lon) / 2)
        else:
            # in case the city intersects the 180 meridian.
            if self.lon + other.lon <= 0:
                mid_point = LatLon((self.lat + other.lat) / 2,
                                   (self.lon + other.lon) / 2 + 180)
            else:
                mid_point = LatLon((self.lat + other.lat) / 2,
                                   (self.lon + other.lon) / 2 - 180)
        return mid_point

    def is_inside(self, origin, corner):
        '''
        Given three LatLon objects, it returns True if the first one is inside
        a 'rectangular' region that has the second and the third one as opposite
        corners. There are many possible 'rectangular' regions on a sphere with
        the the same two points as opposite corners. We are considering the
        smallest one (except a pole lies inside it. In that case, we consider
        the second smallest).
        '''
        if abs(origin.lon - corner.lon) < 180:
            if (self.lat - origin.lat) * (self.lat - corner.lat) <= 0 and \
               (self.lon - origin.lon) * (self.lon - corner.lon) <= 0:
                return True
        else:
            # in case the region intersects the 180 meridian.
            if (self.lat - origin.lat) * (self.lat - corner.lat) <= 0 and \
               (self.lon - origin.lon) * (self.lon - corner.lon) >= 0:
                return True

    def _latitude_in_radians(self):
        return math.radians(self.lat)

    def _longitude_in_radians(self):
        return math.radians(self.lon)

    def _sin_lat(self):
        return math.sin(self._latitude_in_radians())

    def _sin_lon(self):
        return math.sin(self._longitude_in_radians())

    def _cos_lat(self):
        return math.cos(self._latitude_in_radians())

    def _cos_lon(self):
        return math.cos(self._longitude_in_radians())


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
        return math.sqrt(1.0 - (Ecef.polar_radius() ** 2) / (Ecef.equatorial_radius() ** 2))

    @classmethod
    def second_eccectricity_parameter(cls):
        # https://en.wikipedia.org/wiki/Eccentricity_(mathematics)#Ellipses
        return math.sqrt((Ecef.equatorial_radius() ** 2) / (Ecef.polar_radius() ** 2) - 1.0)

    def ecef_to_latlon(self):
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
        return LatLon(lat_in_degrees, lon_in_degrees)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __add__(self, other):
        return Ecef(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Ecef(self.x - other.x, self.y - other.y, self.z - other.z)


class Enu(object):

    def __init__(self, e, n, u):
        self.e = e
        self.n = n
        self.u = u

    def __eq__(self, other):
        return self.e == other.e and self.n == other.n and self.u == other.u
