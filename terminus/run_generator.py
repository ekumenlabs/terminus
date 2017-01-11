#!/usr/bin/python

from generators.rndf_generator import RNDFGenerator
from generators.sdf_generator_gazebo_7 import SDFGeneratorGazebo7
from generators.sdf_generator_gazebo_8 import SDFGeneratorGazebo8
from generators.street_plot_generator import StreetPlotGenerator
from builders import *

import argparse
import sys
import os

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

# Get the class of the builder to use
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

city = builder.get_city()

sdf_generator = SDFGeneratorGazebo7(city)
sdf_generator.write_to(destination_sdf_7_file)

# We are using a path that suits the Gazebo 8 plugin. This will change once
# https://bitbucket.org/JChoclin/rndf_gazebo_plugin/issues/53/rndf-file-path-in-world-file
# is fixed
rndf_file_name = os.path.split(destination_rndf_file)[1]
sdf_generator = SDFGeneratorGazebo8(city, '../example/' + rndf_file_name)
sdf_generator.write_to(destination_sdf_8_file)

if arguments.debug:
    street_plot_generator = StreetPlotGenerator(city)
    street_plot_generator.write_to(destination_street_plot_file)

# For the time being we use an arbitrary (lat,lon) pair as the origin
rndf_generator = RNDFGenerator(city, Point(10, 65))
rndf_generator.write_to(destination_rndf_file)
