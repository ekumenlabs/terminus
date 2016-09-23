#!/usr/bin/python
from models.simple_city_builder import SimpleCityBuilder

city = SimpleCityBuilder().get_city()

with open("generated_city.world", "w") as f:
    f.write(city.to_sdf())
