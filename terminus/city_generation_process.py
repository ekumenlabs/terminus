from generators.monolane_generator import MonolaneGenerator
from generators.rndf_generator import RNDFGenerator
from generators.sdf_generator_gazebo_7 import SDFGeneratorGazebo7
from generators.sdf_generator_gazebo_8 import SDFGeneratorGazebo8
from generators.street_plot_generator import StreetPlotGenerator
from generators.opendrive_generator import OpenDriveGenerator

import logging
import subprocess
import os


class CityGenerationProcess(object):

    def __init__(self, builder, rndf_origin, path, debug_on=False, logger=None):
        self.builder = builder
        self.rndf_origin = rndf_origin
        self.path = path
        self.debug_on = debug_on
        if logger is None:
            self.logger = self._create_default_logger()
        else:
            self.logger = logger

    def run(self):
        self.logger.info("Building city using {0}".format(self.builder.__class__.__name__))

        city = self.builder.get_city()

        if self.debug_on:
            self._run_generator(StreetPlotGenerator(city),
                                'Generating street plot',
                                'city_streets.png')

        self._run_generator(RNDFGenerator(city, self.rndf_origin),
                            'Generating RNDF file',
                            'city.rndf')

        if self.debug_on:
            command = "cd {0}; ../tools/rndf_visualizer/build/rndf_visualizer -g city.rndf".format(self.path)
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            process.wait()
            if process.returncode == 0:
                # If the command executed ok, remove residual file and rename the svg
                try:
                    os.remove(os.path.join(self.path, 'gps.kml'))
                    os.rename(os.path.join(self.path, 'sample.svg'), os.path.join(self.path, 'city.svg'))
                except OSError:
                    pass
            else:
                # Otherwise warn the user
                self.logger.warn("Can't generate SVG file for RNDF. Please make sure rndf_visualizer has been properly built")

        self._run_generator(SDFGeneratorGazebo7(city),
                            "Generating Gazebo 7 SDF",
                            "city_gazebo_7.world")

        # We are using a path that suits the Gazebo 8 plugin. This will change once
        # https://bitbucket.org/JChoclin/rndf_gazebo_plugin/issues/53/rndf-file-path-in-world-file
        # is fixed
        # There is also an offset issue with RNDF vs Gazebo coordinates that will be fixed
        # in https://bitbucket.org/JChoclin/rndf_gazebo_plugin/issues/54/add-origin-node-to-world-description
        generator = SDFGeneratorGazebo8(city, self.rndf_origin, '../example/city.rndf')
        self._run_generator(generator,
                            'Generating Gazebo 8 SDF',
                            'city_gazebo_8.world')

        self._run_generator(OpenDriveGenerator(city),
                            'Generating OpenDrive file',
                            'city.xodr')

        self._run_generator(MonolaneGenerator(city),
                            'Generating monolane file',
                            'city_monolane.yaml')

    def _run_generator(self, generator, log_message, path_extension):
        self.logger.info(log_message)
        destination_file = self.path + path_extension
        generator.write_to(destination_file)

    def _create_default_logger(self):
        logger = logging.getLogger('')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.handlers = []
        logger.addHandler(handler)
        return logger
