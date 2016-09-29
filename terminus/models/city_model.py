from city_element import CityElement


# City models correspond to Gazebo models, and hence need a name
class CityModel(CityElement):

    incrementing_id = 0

    def __init__(self, name=None):
        super(CityModel, self).__init__()
        if name is None:
            class_name = self.__class__.__name__
            CityModel.incrementing_id += 1
            self.name = (class_name[0].lower()
                         + class_name[1:]
                         + '_'
                         + str(CityModel.incrementing_id))
        else:
            self.name = name
