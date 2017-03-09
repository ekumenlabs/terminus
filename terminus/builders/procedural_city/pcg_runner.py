import os
import sys
import subprocess

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PcgRunner(object):

    def __init__(self):
        self.verticesFilename = ''
        self.polygonsFilename = ''

    def set_size(self, s):
        self.size = s

    def get_vertices_filename(self):
        return self.verticesFilename

    def get_polygons_filename(self):
        return self.polygonsFilename

    def run(self):
        ''' Generate city using the procedural_city_generation library '''
        this_path = os.path.realpath(__file__)
        pcg_path = os.path.join(os.path.dirname(os.path.dirname(this_path)),
                                '../procedural_city_generation')

        pcg_run = 'python {0}/UI.py'.format(pcg_path)

        # Configure roadmap parameters
        command_string = '{0} roadmap --configure plot False ' \
                         'border_x {1} border_y {1}'
        command = command_string.format(pcg_run, int(self.size))

        self._pcg_run_command(command)

        # Generate roadmap
        command = '{0} roadmap run'.format(pcg_run)
        self._pcg_run_command(command)

        # Configure polygons parameters
        command = '{0} polygons --configure plotbool False'.format(pcg_run)
        self._pcg_run_command(command)

        # Generate polygons
        command = '{0} polygons run'.format(pcg_run)
        self._pcg_run_command(command)

        self.temp_path = os.path.join(pcg_path,
                                      'procedural_city_generation/temp/')

        self.verticesFilename = os.path.join(self.temp_path, 'mycity')
        self.polygonsFilename = os.path.join(self.temp_path,
                                             'mycity_polygons.txt')

    def _pcg_run_command(self, command):
        with open(os.devnull, "w") as f:
            result = subprocess.call(command.split(),
                                     stdout=f,
                                     stderr=subprocess.STDOUT)

        if result == 0:
            logger.debug("Command '{0}' executed succesfully".format(command))
        else:
            logger.fatal("Command '{0}' failed to execute".format(command))
            sys.exit(1)
