#!/usr/bin/python
from builders.simple_city_builder import SimpleCityBuilder

city = SimpleCityBuilder().get_city()

with open("generated_worlds/city.world", "w") as f:
    f.write(city.to_sdf())
