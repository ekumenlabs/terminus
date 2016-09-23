from city_element import CityElement

class Point(CityElement):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def template(self):
        return "<point>{{model.x}} {{model.y}} {{model.z}}</point>"
