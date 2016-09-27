#!/usr/bin/python

# We should take as parameters the builder class and the required parameters
#Old:
#from builders.simple_city_builder import SimpleCityBuilder
#city = SimpleCityBuilder().get_city()

# New:
from builders.procedural_city_builder import ProceduralCityBuilder
path = "/home/andres/Creativa77/OSRF/procedural_city_generation/procedural_city_generation/temp/mycity"
city = ProceduralCityBuilder(path).get_city()

with open("generated_worlds/city.world", "w") as f:
    f.write(city.to_sdf())
