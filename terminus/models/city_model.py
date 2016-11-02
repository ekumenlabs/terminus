from city_element import CityElement
import random


class CityModel(CityElement):
    """City models are city elements that also have an associated name. These
    are useful to be mapped as Gazebo models, but it applies to any entity
    that can be named. If no name is provided on object creation, one is
    automatically generated for the model"""

    incrementing_id = 0

    def __init__(self, name=None):
        super(CityModel, self).__init__()
        if name is None:
            class_name = self.__class__.__name__
            CityModel.incrementing_id += 1
            self.name = (class_name[0].lower() +
                         class_name[1:] +
                         '_' +
                         str(CityModel.incrementing_id))
        else:
            self.name = name
