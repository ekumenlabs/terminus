#!/usr/bin/python

from generators.rndf_generator import RNDFGenerator
from generators.sdf_generator import SDFGenerator
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
                    default='generated_worlds/city.sdf',
                    help='destination file name')
# Extra named parameters passed to the builder when creating it
parser.add_argument('-p',
                    '--parameters',
                    nargs='*',
                    default='',
                    help='extra parameters to pass to the builder. Must be \
                    formatted as <key>=<value> pairs')

arguments = parser.parse_args()

# Get the file name to write to
destination_sdf_file = arguments.destination

# Get the base file name + path to also generate the rndf
base_path = os.path.splitext(destination_sdf_file)[0]

destination_rndf_file = base_path + '.rndf'

# Get the class of the builder to use
builder_class = getattr(sys.modules[__name__], arguments.builder)

# Get the remaining parameters to pass to the builder as <key>=<value> pairs
# as a dictionary
builder_parameters = dict(pair.split('=', 1) for pair in arguments.parameters)

# Create the builder instance. Unpack the parameter dictionary to be used as
# keyword parameters
builder = builder_class(**builder_parameters)

city = builder.get_city()

sdf_generator = SDFGenerator(city)
sdf_generator.write_to(destination_sdf_file)

# For the time being we use an arbitrary (lat,lon) pair as the origin
rndf_generator = RNDFGenerator(city, Point(10, -65))
rndf_generator.write_to(destination_rndf_file)
