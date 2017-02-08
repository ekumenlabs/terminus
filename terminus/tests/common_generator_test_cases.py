from geometry.point import Point
from geometry.latlon import LatLon
from models.city import City
from models.street import Street
from models.trunk import Trunk

def generate_empty_city():
    city = City("Empty")
    return city


def generate_simple_street_city():
    city = City("Single street")
    street = Street.from_points([
        Point(0, 0),
        Point(1000, 0),
        Point(2000, 0)
    ])
    street.name = "s1"
    city.add_road(street)
    return city


def generate_cross_intersection_city():
    """
         (0,1)
    (-1,0) + (1,0)
         (0,-1)
    """
    city = City("Cross")

    s1 = Street.from_points([Point(-1000, 0), Point(0, 0), Point(1000, 0)])
    s1.name = "s1"

    s2 = Street.from_points([Point(0, 1000), Point(0, 0), Point(0, -1000)])
    s2.name = "s2"

    city.add_intersection_at(Point(0, 0))

    city.add_road(s1)
    city.add_road(s2)

    return city

def generate_L_intersection_city():
    """
         (0,1)
           +  (1,0)
    """
    city = City("LCross")

    s1 = Street.from_points([Point(0, 1000), Point(0, 0)])
    s1.name = "s1"

    s2 = Street.from_points([Point(0, 0), Point(1000, 0)])
    s2.name = "s2"

    city.add_intersection_at(Point(0, 0))

    city.add_road(s1)
    city.add_road(s2)

    return city


def generate_Y_intersection_one_to_many_city():
    """
              (0,1)
                +
        (-1,-1)   (1,-1)
    """
    city = City("YCross")

    s1 = Street.from_points([Point(0, 1000), Point(0, 0)])
    s1.name = "s1"

    s2 = Street.from_points([Point(0, 0), Point(-1000, -1000)])
    s2.name = "s2"

    s3 = Street.from_points([Point(0, 0), Point(1000, -1000)])
    s3.name = "s3"

    city.add_intersection_at(Point(0, 0))

    city.add_road(s1)
    city.add_road(s2)
    city.add_road(s3)

    return city


def generate_Y_intersection_many_to_one_city():
    """
              (0,1)
                +
        (-1,-1)   (1,-1)
    """
    city = City("YCross Many to One")

    s1 = Street.from_points([Point(0, 0), Point(0, 1000)])
    s1.name = "s1"

    s2 = Street.from_points([Point(-1000, -1000), Point(0, 0)])
    s2.name = "s2"

    s3 = Street.from_points([Point(1000, -1000), Point(0, 0)])
    s3.name = "s3"

    city.add_road(s1)
    city.add_road(s2)
    city.add_road(s3)

    city.add_intersection_at(Point(0, 0))

    return city
