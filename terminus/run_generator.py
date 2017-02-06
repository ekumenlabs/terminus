#!/usr/bin/python

from __future__ import print_function

from geometry.latlon import LatLon
from generators.monolane_generator import MonolaneGenerator
from generators.rndf_generator import RNDFGenerator
from generators.sdf_generator_gazebo_7 import SDFGeneratorGazebo7
from generators.sdf_generator_gazebo_8 import SDFGeneratorGazebo8
from generators.street_plot_generator import StreetPlotGenerator
from generators.opendrive_generator import OpenDriveGenerator

from builders import OsmCityBuilder
from builders import ProceduralCityBuilder
from builders import SimpleCityBuilder

import argparse
import sys
import os

import logging

logger = logging.getLogger('')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.handlers = []
logger.addHandler(handler)

# For the time being we use an arbitrary (lat, lon) as the origin
RNDF_ORIGIN = LatLon(10, 65)

parser = argparse.ArgumentParser()

# The builder class
parser.add_argument('-b',
                    '--builder',
                    required=True,
                    help='class name of the builder to invoke')
# The output file
parser.add_argument('-d',
                    '--destination',
                    default='generated_worlds/city',
                    help='destination file name')
# Extra named parameters passed to the builder when creating it
parser.add_argument('-p',
                    '--parameters',
                    nargs='*',
                    default='',
                    help='extra parameters to pass to the builder. Must be \
                    formatted as <key>=<value> pairs')
# Extra named parameters passed to the builder when creating it
parser.add_argument('-x',
                    '--debug',
                    action='store_true',
                    help='Generates more output files, useful for debugging')

arguments = parser.parse_args()

# Get the base file name + path to generate the different files
base_path = arguments.destination

destination_rndf_file = base_path + '.rndf'
destination_sdf_7_file = base_path + '_gazebo_7.sdf'
destination_sdf_8_file = base_path + '_gazebo_8.sdf'
destination_street_plot_file = base_path + '_streets.png'
destination_opendrive_file = base_path + '.xodr'
destination_monolane_file = base_path + '.monolane.yaml'

# Get the class of the builder to use
builders_list = [
    OsmCityBuilder,
    ProceduralCityBuilder,
    SimpleCityBuilder
]
assert(arguments.builder in [x.__name__ for x in builders_list])
builder_class = getattr(sys.modules[__name__], arguments.builder)

# Get the remaining parameters to pass to the builder as <key>=<value> pairs
# as a dictionary
builder_parameters = dict(pair.split('=', 1) for pair in arguments.parameters)

# Make sure size is an integer
if 'size' in builder_parameters:
    builder_parameters['size'] = int(builder_parameters['size'])

# Create the builder instance. Unpack the parameter dictionary to be used as
# keyword parameters
builder = builder_class(**builder_parameters)

logger.info("Building city using {0}".format(builder_class.__name__))

city = builder.get_city()

logger.info("Generating Gazebo 7 SDF")
sdf_generator = SDFGeneratorGazebo7(city)
sdf_generator.write_to(destination_sdf_7_file)

logger.info("Generating Gazebo 8 SDF")
# We are using a path that suits the Gazebo 8 plugin. This will change once
# https://bitbucket.org/JChoclin/rndf_gazebo_plugin/issues/53/rndf-file-path-in-world-file
# is fixed
# There is also an offset issue with RNDF vs Gazebo coordinates that will be fixed
# in https://bitbucket.org/JChoclin/rndf_gazebo_plugin/issues/54/add-origin-node-to-world-description
rndf_file_name = os.path.split(destination_rndf_file)[1]
sdf_generator = SDFGeneratorGazebo8(city, RNDF_ORIGIN, '../example/' + rndf_file_name)
sdf_generator.write_to(destination_sdf_8_file)

if arguments.debug:
    logger.info("Generating street plot")
    street_plot_generator = StreetPlotGenerator(city)
    street_plot_generator.write_to(destination_street_plot_file)

logger.info("Generating RNDF file")
rndf_generator = RNDFGenerator(city, RNDF_ORIGIN)
rndf_generator.write_to(destination_rndf_file)

logger.info("Generating OpenDrive file")
opendrive_generator = OpenDriveGenerator(city, RNDF_ORIGIN)
opendrive_generator.write_to(destination_opendrive_file)

logger.info("Generating monolane file")
monolane_generator = MonolaneGenerator(city)
monolane_generator.write_to(destination_monolane_file)
