import math


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

    def translate(self, delta_lat_lon):
        """
        Given LatLon point and a delt_lat_lon tuple, returns a LatLon point
        corresponding to the place where an object would be after starting at
        the LatLon point and moving first delta_lat_lon[1] meters in the
        longitudinal direction, and then delta_lat_lon[0] meters in the
        latitudinal direction.

        """

        latitude_traslation_in_meters = delta_lat_lon[0]
        longitude_traslation_in_meters = delta_lat_lon[1]
        meters_per_degree_lat = 111319.9
        latitude_in_radians = math.radians(self.lat)
        meters_per_degree_lon = meters_per_degree_lat * math.cos(latitude_in_radians)

        delta_lat = latitude_traslation_in_meters / meters_per_degree_lat
        if meters_per_degree_lon != 0:
            delta_lon = longitude_traslation_in_meters / meters_per_degree_lon
        else:
            delta_lon = 0

        new_lat = self.lat + delta_lat
        new_lon = self.lon + delta_lon

        return LatLon(new_lat, new_lon)

    def delta_in_meters(self, other):
        """
        Given two LatLon objects, it returns an (x, y) tuple that verifies
        self.translate(x, y) = other
        (the answer is not unique, this is just one tuple that verifies).

        """
        delta_lat_in_degrees = other.lat - self.lat
        meters_per_degree_lat = 111319.9
        delta_lat_in_meters = meters_per_degree_lat * delta_lat_in_degrees
        delta_lon_in_degrees = other.lon - self.lon
        if delta_lon_in_degrees > 180:
            delta_lon_in_degrees = delta_lon_in_degrees - 360
        if delta_lon_in_degrees < -180:
            delta_lon_in_degrees = delta_lon_in_degrees + 360
        latitude_in_radians = math.radians(self.lat)
        meters_per_degree_lon = meters_per_degree_lat * math.cos(latitude_in_radians)
        delta_lon_in_meters = delta_lon_in_degrees * meters_per_degree_lon
        if other == LatLon(90, 0):
            return (delta_lat_in_meters, 0)
        else:
            return (delta_lat_in_meters, delta_lon_in_meters)

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
