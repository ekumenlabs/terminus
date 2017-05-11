from geometry.point import Point
from geometry.line_segment import LineSegment
from geometry.arc import Arc
from geometry.circle import Circle


class CustomAssertionsMixin(object):

    def assertAlmostEqual(self, first, second, places=7, msg=None, delta=None):
        first_type = type(first)
        if first_type is int or first_type is float:
            return super(CustomAssertionsMixin, self).assertAlmostEqual(first, second, places=places, msg=msg, delta=delta)
        elif first_type is Point:
            return self.assertPointAlmostEqual(first, second, places=places, msg=msg)
        elif first_type is Arc:
            return self.assertArcAlmostEqual(first, second, places=places, msg=msg)
        elif first_type is LineSegment:
            return self.assertLineSegmentAlmostEqual(first, second, places=places, msg=msg)
        elif first_type is list:
            return self.assertListAlmostEqual(first, second, places=places, msg=msg)
        elif first_type is Circle:
            return self.assertCircleAlmostEqual(first, second, places=places, msg=msg)
        else:
            return self.assertEquals(first, second, msg=msg)

    def assertPointAlmostEqual(self, point1, point2, places=7, msg=None):
        if msg:
            x_message = msg
            y_message = msg
        else:
            x_message = "{0} != {1} within {2} places (x coordinate)".format(point1, point2, places)
            y_message = "{0} != {1} within {2} places (y coordinate)".format(point1, point2, places)
        self.assertAlmostEqual(point1.x, point2.x, places=places, msg=x_message)
        self.assertAlmostEqual(point1.y, point2.y, places=places, msg=y_message)

    def assertArcAlmostEqual(self, arc1, arc2, places=7, msg=None):
        if msg:
            start_point_msg = msg
            theta_msg = msg
            radius_msg = msg
            angular_length_msg = msg
        else:
            base_message = "{0} != {1} within {2} places ({3})".format(arc1, arc2, places, '{0}')
            start_point_msg = base_message.format('start_point')
            theta_msg = base_message.format('theta')
            radius_msg = base_message.format('radius')
            angular_length_msg = base_message.format('angular_length')
        self.assertPointAlmostEqual(arc1.start_point(),
                                    arc2.start_point(),
                                    places=places,
                                    msg=start_point_msg)
        self.assertAlmostEqual(arc1.theta(),
                               arc2.theta(),
                               places=places,
                               msg=theta_msg)
        self.assertAlmostEqual(arc1.radius(),
                               arc2.radius(),
                               places=places,
                               msg=radius_msg)
        self.assertAlmostEqual(arc1.angular_length(),
                               arc2.angular_length(),
                               msg=angular_length_msg)

    def assertLineSegmentAlmostEqual(self, segment1, segment2, places=7, msg=None):
        if msg:
            start_point_msg = msg
            end_point_msg = msg
        else:
            base_message = "{0} != {1} within {2} places ({3})".format(segment1, segment2, places, '{0}')
            start_point_msg = base_message.format('start_point')
            end_point_msg = base_message.format('end_point')
        self.assertPointAlmostEqual(segment1.start_point(),
                                    segment2.start_point(),
                                    places=places,
                                    msg=start_point_msg)
        self.assertPointAlmostEqual(segment1.end_point(),
                                    segment2.end_point(),
                                    places=places,
                                    msg=end_point_msg)

    def assertListAlmostEqual(self, list1, list2, places=7, msg=None):
        if len(list1) != len(list2):
            if msg:
                message = msg
            else:
                message = "Lists have different sizes\n{0}\n{1}".format(list1, list2)
            raise AssertionError(message)
        for index, (element1, element2) in enumerate(zip(list1, list2)):
            try:
                self.assertAlmostEqual(element1, element2, places)
            except AssertionError as e:
                if msg:
                    message = msg
                else:
                    message = "Lists differ in index {0}:\n\n{1}\n\n{2}\n{3}".format(index, e.args[0], list1, list2)
                    e.args = (message,)
                    raise

    def assertCircleAlmostEqual(self, circle1, circle2, places=7, msg=None):
        if msg:
            center_msg = msg
            radius_msg = msg
        else:
            base_message = "{0} != {1} within {2} places ({3})".format(circle1, circle2, places, '{0}')
            center_msg = base_message.format('center')
            radius_msg = base_message.format('radius')
        self.assertPointAlmostEqual(circle1.center(),
                                    circle2.center(),
                                    places=places,
                                    msg=center_msg)
        self.assertAlmostEqual(circle1.radius(),
                               circle2.radius(),
                               places=places,
                               msg=radius_msg)
