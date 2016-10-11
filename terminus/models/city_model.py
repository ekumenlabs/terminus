from city_element import CityElement
import random


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

    def material(self):
        return """<script>
          <uri>
            file://media/materials/scripts/gazebo.material
          </uri>
          <name>Gazebo/Grey</name>
        </script>"""

    def _material_with_random_color(self):
        """This is mostly for debugging / visualization purposes. Do not rely
        on the existence of this method, we will eventually remove it"""
        colors = ['Red', 'Blue', 'White', 'Yellow', 'Green', 'Black', 'Purple']
        return """<script>
          <uri>
            file://media/materials/scripts/gazebo.material
          </uri>
          <name>Gazebo/{0}</name>
        </script>""".format(random.choice(colors))
