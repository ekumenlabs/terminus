import unittest

import math

from geometry.latlon import LatLon


class LatLonTest(unittest.TestCase):

    def meters_per_degree_in_maximal_circunference(self):
        return 111319.9

    def degrees_to_meters(self, degrees):
        return degrees * self.meters_per_degree_in_maximal_circunference()

    def degree_to_meters_lon_at_lat(self, lat, degree_lon):
        lat_in_radians = math.radians(lat)
        return math.cos(lat_in_radians) * self.degrees_to_meters(degree_lon)

    def test_eq_on_identical_objects(self):
        point = LatLon(0, 0)
        self.assertTrue(point == point)

    def test_eq_on_non_identical_objects(self):
        point = LatLon(0, 0)
        other_point_with_same_lat_and_lon = LatLon(0, 0)
        self.assertTrue(point == other_point_with_same_lat_and_lon)

    def test_eq_on_different_objects(self):
        point = LatLon(0, 0)
        different_point = LatLon(1, 2)
        self.assertFalse(point == different_point)

    def test_eq_is_commutative(self):
        point = LatLon(25, 190)
        equivalent_point = LatLon(25, -170)
        not_equivalent_point = LatLon(35, -170)
        self.assertEqual(point, equivalent_point)
        self.assertEqual(equivalent_point, point)
        self.assertNotEqual(point, not_equivalent_point)
        self.assertNotEqual(not_equivalent_point, point)

    def test_eq_between_maximal_and_minimal_longitude(self):
        point_with_lon_180 = LatLon(25, 180)
        point_with_same_lat_and_lon_minus180 = LatLon(25, -180)
        self.assertEqual(point_with_lon_180, point_with_same_lat_and_lon_minus180)

    def test_eq_in_north_pole(self):
        point_at_north_pole = LatLon(90, 7)
        point_at_north_pole_with_different_longitude = LatLon(90, 54)
        self.assertEqual(point_at_north_pole,
                         point_at_north_pole_with_different_longitude)

    def test_eq_in_south_pole(self):
        point_at_south_pole = LatLon(-90, 27)
        point_at_south_pole_with_different_longitude = LatLon(-90, 3)
        self.assertEqual(point_at_south_pole,
                         point_at_south_pole_with_different_longitude)

    def test_normalize_on_creation(self):
        # bad lat and lon
        self.assertEqual(LatLon(100, 190).lat, 80)
        self.assertEqual(LatLon(100, 190).lon, 10)
        # lon = -180
        self.assertEqual(LatLon(25, -180).lat, 25)
        self.assertEqual(LatLon(25, -180).lon, 180)
        # already normalized point
        self.assertEqual(LatLon(45, 90).lat, 45)
        self.assertEqual(LatLon(45, 90).lon, 90)
        # lat = lon = 360
        self.assertEqual(LatLon(360, 360).lat, 0)
        self.assertEqual(LatLon(360, 360).lon, 0)
        # negative lat ad lon
        self.assertEqual(LatLon(-100, -30).lat, -80)
        self.assertEqual(LatLon(-100, -30).lon, 150)
        # normalize to negative lat and lon values
        self.assertEqual(LatLon(190, 30).lat, -10)
        self.assertEqual(LatLon(190, 30).lon, -150)

    def test_sum(self):
        point = LatLon(1, 2)
        point_to_sum = LatLon(3, 4)
        expected_result = LatLon(4, 6)
        self.assertEqual(point.sum(point_to_sum), expected_result)

    def test_sum_exceeding_maximal_latitud(self):
        point = LatLon(45, 30)
        point_to_sum = LatLon(60, 20)
        expected_result = LatLon(75, -130)
        self.assertEqual(point.sum(point_to_sum), expected_result)

    def test_translate(self):
        initial_point = LatLon(60, 30)
        expected_point = LatLon(80, 165)
        self.assertEqual(initial_point.translate((2226398.0, 7514093.250000002)),
                         expected_point)

    def test_translate_zero(self):
        point = LatLon(35, 20)
        self.assertEqual(point, point.translate((0, 0)))

    def test_translate_longitudinally_in_north_pole_does_not_move_point(self):
        point_at_north_pole = LatLon(90, 20)
        self.assertEqual(point_at_north_pole.translate((0, 100)), point_at_north_pole)

    def test_translate_longitudinally_in_south_pole_does_not_move_point(self):
        point_at_south_pole = LatLon(-90, 20)
        self.assertEqual(point_at_south_pole.translate((0, 100)), point_at_south_pole)

    def test_translate_lat(self):
        initial_point = LatLon(15, 30)
        delta = self.degrees_to_meters(45)
        expected_point = LatLon(60, 30)
        self.assertEqual(initial_point.translate((delta, 0)), expected_point)

    def test_translate_lon(self):
        initial_point = LatLon(60, 27)
        delta = self.degrees_to_meters(90) * 0.5000000000000001
        expected_point = LatLon(60, 117)
        self.assertEqual(initial_point.translate((0, delta)), expected_point)

    def test_translate_latitud_greater_than_90(self):
        initial_point = LatLon(0, 0)
        delta = self.degrees_to_meters(170)
        expected_point = LatLon(10, 180)
        self.assertEqual(initial_point.translate((delta, 0)), expected_point)

    def test_translate_longitude_greater_than_180(self):
        initial_point = LatLon(0, 0)
        delta = self.degrees_to_meters(190)
        expected_point = LatLon(0, -170)
        self.assertEqual(initial_point.translate((0, delta)), expected_point)

    def test_translate_longitude_greater_than_360(self):
        initial_point = LatLon(0, 0)
        delta = self.degrees_to_meters(450)
        expected_point = LatLon(0, 90)
        self.assertEqual(initial_point.translate((0, delta)), expected_point)

    def test_translate_latitud_greater_than_180(self):
        initial_point = LatLon(0, 0)
        delta = self.degrees_to_meters(190)
        expected_point = LatLon(-10, 180)
        self.assertEqual(initial_point.translate((delta, 0)), expected_point)

    def test_translate_negative_latitud_greater_than_90(self):
        initial_point = LatLon(0, 0)
        delta = self.degrees_to_meters(-135)
        expected_point = LatLon(-45, -180)
        self.assertEqual(initial_point.translate((delta, 0)), expected_point)

    def test_translate_negative_longitude_greater_than_180(self):
        initial_point = LatLon(0, 0)
        delta = self.degrees_to_meters(-190)
        expected_point = LatLon(0, 170)
        self.assertEqual(initial_point.translate((0, delta)), expected_point)

    def test_delta_in_meters_starting_at_0_0(self):
        initial_point = LatLon(0, 0)
        final_point = LatLon(45, 70)
        expected_delta = (self.degrees_to_meters(45), self.degrees_to_meters(70))
        self.assertEqual(initial_point.delta_in_meters(final_point), expected_delta)

    def test_delta_in_meters_finding_the_shortest_path(self):
        self.assertEqual(LatLon(0, -170).delta_in_meters(LatLon(0, 170)),
                         (0, self.degrees_to_meters(-20)))

    def test_delta_in_meters_from_south_pole_to_north_pole(self):
        self.assertEqual(LatLon(-90, 10).delta_in_meters(LatLon(90, 20)),
                         (self.degrees_to_meters(180), 0))

    def test_delta_in_meters_not_starting_at_0_0(self):
        for i in range(0, 2):
            self.assertAlmostEqual(LatLon(-20, 45).delta_in_meters(LatLon(35, -70))[i],
                                   (
                                   self.degrees_to_meters(55),
                                   self.degree_to_meters_lon_at_lat(-20, -115)
                                   )[i])

    def test_delta_in_meters_starting_at_north_pole(self):
        for i in range(0, 2):
            self.assertAlmostEqual(LatLon(90, 0).delta_in_meters(LatLon(35, 60))[i],
                                   (self.degrees_to_meters(-55), 0)[i])
            self.assertEqual(LatLon(90, 0).translate(LatLon(90, 0).delta_in_meters(LatLon(35, 60))),
                             LatLon(35, 60))

    def test_delta_in_meters_going_to_north_pole(self):
        self.assertEqual(LatLon(35, 60).delta_in_meters(LatLon(90, 0)),
                         (self.degrees_to_meters(55), 0))

    def test_translate_with_delta_in_meters(self):
        initial_point = LatLon(25, 64)
        final_point = LatLon(67, 138)
        self.assertEqual(initial_point.translate(initial_point.delta_in_meters(final_point)),
                         final_point)

    def test_midpoint(self):
        self.assertEqual(LatLon(60, 80).midpoint(LatLon(20, 20)), LatLon(40, 50))
        # with midpoint on the 0 meridian
        self.assertEqual(LatLon(-15, 80).midpoint(LatLon(15, -80)), LatLon(0, 0))
        # with midpoint on the 180 meridian
        self.assertEqual(LatLon(-15, 100).midpoint(LatLon(15, -100)), LatLon(0, 180))

    def test_midpont_with_midpoint_near_180_meridian(self):
        # midpoint with positive longitude
        self.assertEqual(LatLon(20, -160).midpoint(LatLon(40, 140)), LatLon(30, 170))
        # midpoint with negative longitude
        self.assertEqual(LatLon(20, -100).midpoint(LatLon(40, 160)), LatLon(30, -150))

    def test_midpoint_of_points_on_the_same_meridian(self):
        self.assertEqual(LatLon(-10, 80).midpoint(LatLon(-30, 80)), LatLon(-20, 80))

    def test_midpoint_of_points_on_the_same_parallel(self):
        self.assertEqual(LatLon(30, -110).midpoint(LatLon(30, -90)), LatLon(30, -100))

    def test_midpoint_of_equal_points(self):
        self.assertEqual(LatLon(35, 80).midpoint(LatLon(35, 80)), LatLon(35, 80))
        self.assertEqual(LatLon(40, 165).midpoint(LatLon(40, 165)), LatLon(40, 165))

    def test_is_inside(self):
        # when it is inside
        self.assertTrue(LatLon(0, 0).is_inside(LatLon(-10, -10), LatLon(10, 10)))
        self.assertTrue(LatLon(0, 180).is_inside(LatLon(-10, -170), LatLon(10, 170)))
        # when it is not inside
        self.assertIsNone(LatLon(0, 0).is_inside(LatLon(-20, -20), LatLon(-40, -40)))
        self.assertIsNone(LatLon(30, 45).is_inside(LatLon(40, 40), LatLon(20, 10)))

    def test_is_inside_in_the_boundary(self):
        self.assertTrue(LatLon(45, -10).is_inside(LatLon(45, -20), LatLon(10, 10)))
        self.assertTrue(LatLon(45, -10).is_inside(LatLon(40, -10), LatLon(50, 10)))
        # in the corner
        self.assertTrue(LatLon(45, -10).is_inside(LatLon(45, -10), LatLon(50, 10)))
