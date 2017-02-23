#!/usr/bin/python

from geometry.latlon import LatLon

from builders import OsmCityBuilder
from builders import ProceduralCityBuilder
from builders import SimpleCityBuilder
from city_generation_process import CityGenerationProcess

import argparse
import sys
import os

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
                    default='generated_worlds/',
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
                    help='Generates extra output files, useful for debugging')

arguments = parser.parse_args()

# Get the base path to generate the different files (join to make sure it has
# a trailing slash)
base_path = os.path.join(arguments.destination, '')

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

process = CityGenerationProcess(builder, RNDF_ORIGIN, base_path, arguments.debug)
process.run()
