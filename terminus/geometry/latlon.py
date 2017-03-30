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
import ecef
import enu


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

    def __hash__(self):
        return hash((self.lat, self.lon))

    def __repr__(self):
        return 'LatLon(%s, %s)' % (self.lat, self.lon)

    def sum(self, other):
        return LatLon(self.lat + other.lat, self.lon + other.lon)

    def curvature(self):
        # Radius of planet curvature (meters)
        curvature = ecef.Ecef.equatorial_radius() / math.sqrt(1 - ecef.Ecef.first_eccentricity_parameter() ** 2 * self._sin_lat() ** 2)
        return curvature

    def to_ecef(self):
        x = self.curvature() * self._cos_lat() * self._cos_lon()
        y = self.curvature() * self._cos_lat() * self._sin_lon()
        z = ((ecef.Ecef.polar_radius() ** 2) / (ecef.Ecef.equatorial_radius() ** 2)) * self.curvature() * self._sin_lat()
        return ecef.Ecef(x, y, z)

    def translate(self, delta_lat_lon):
        """
        Given LatLon point and a delta_lat_lon tuple, returns a LatLon point
        corresponding to the place where an object would be after starting at
        the LatLon point and moving delta_lat_lon[1] meters in the
        longitudinal direction, and delta_lat_lon[0] meters in the
        latitudinal direction in the plane that is tangent to the Earth on the
        original LatLon point.

        """
        delta_in_enu = enu.Enu(delta_lat_lon[1], delta_lat_lon[0], 0)
        delta_in_ecef = delta_in_enu.to_ecef(self)
        inicial_point_in_ecef = self.to_ecef()
        final_point_in_ecef = inicial_point_in_ecef + delta_in_ecef
        return final_point_in_ecef.to_latlon()

    def delta_in_meters(self, other):
        """
        Given two LatLon objects, it returns an (x, y) tuple that approximates
        how many meters in the latitudinal directon (x) and in the longitudinal
        direction (y) is the second point(other) from the first(self).

        """
        delta_in_enu = other.to_ecef().to_global(self)
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
