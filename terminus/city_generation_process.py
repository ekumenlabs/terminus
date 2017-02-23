"""
Copyright (C) 2017 Open Source Robotics Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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

    def __init__(self, builder, rndf_origin, path, debug_on=False,
                 base_name='city', logger=None):
        self.builder = builder
        self.rndf_origin = rndf_origin
        self.path = path
        self.base_name = base_name
        self.debug_on = debug_on
        if logger is None:
            self.logger = self._create_default_logger()
        else:
            self.logger = logger

    def run(self):
        self.logger.info("Building city using {0}".format(self.builder.name()))

        city = self.builder.get_city()

        # Make sure the path exists
        try:
            os.makedirs(self.path)
        except OSError:
            pass

        if self.debug_on:
            self._run_generator(StreetPlotGenerator(city),
                                'Generating street plot',
                                self.base_name + '_streets.png')

        self._run_generator(RNDFGenerator(city, self.rndf_origin),
                            'Generating RNDF file',
                            self.base_name + '.rndf')

        if self.debug_on:
            # Generate SVG file from RNDF if binary available
            depth = 0
            to_process = self.path
            while True:
                to_process, leaf = os.path.split(to_process)
                if not leaf and not to_process:
                    break
                else:
                    depth = depth + 1
            parent_path = '/'.join(map(lambda x: '..', range(1, depth)))
            command = "cd {0}; {1}/tools/rndf_visualizer/build/rndf_visualizer -g {2}.rndf".format(self.path, parent_path, self.base_name)
            self.logger.info("Generating SVG for RNDF")
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            process.wait()
            if process.returncode == 0:
                # If the command executed ok, remove residual file and rename the svg
                try:
                    os.remove(os.path.join(self.path, 'gps.kml'))
                    os.rename(os.path.join(self.path, 'sample.svg'), os.path.join(self.path, self.base_name + '.svg'))
                except OSError:
                    pass
            else:
                # Otherwise warn the user
                self.logger.warn("Can't generate SVG file for RNDF. Please make sure rndf_visualizer has been properly built")

        self._run_generator(SDFGeneratorGazebo7(city),
                            "Generating Gazebo 7 SDF",
                            self.base_name + '_gazebo_7.world')

        # We are using a path that suits the Gazebo 8 plugin. This will change once
        # https://bitbucket.org/JChoclin/rndf_gazebo_plugin/issues/53/rndf-file-path-in-world-file
        # is fixed
        # There is also an offset issue with RNDF vs Gazebo coordinates that will be fixed
        # in https://bitbucket.org/JChoclin/rndf_gazebo_plugin/issues/54/add-origin-node-to-world-description
        generator = SDFGeneratorGazebo8(city, self.rndf_origin, '../example/city.rndf')
        self._run_generator(generator,
                            'Generating Gazebo 8 SDF',
                            self.base_name + '_gazebo_8.world')

        self._run_generator(OpenDriveGenerator(city),
                            'Generating OpenDrive file',
                            self.base_name + '.xodr')

        self._run_generator(MonolaneGenerator(city),
                            'Generating monolane file',
                            self.base_name + '_monolane.yaml')

        if self.debug_on and os.environ['DRAKE_DISTRO']:
            # Generate OBJ from monolane if binary is available
            binary = os.path.join(os.environ['DRAKE_DISTRO'], 'build/drake/automotive/maliput/utility/yaml_to_obj')
            monolane_file = self.path + self.base_name + '_monolane.yaml'
            params = "-yaml_file=\"{0}\" -obj_dir=\"{1}\" -obj_file=\"{2}\"".format(monolane_file, self.path, self.base_name + '_monolane')
            command = "{0} {1}".format(binary, params)
            self.logger.info("Generating OBJ for monolane")
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            if process.returncode != 0:
                output = process.stderr.read()
                self.logger.warn("Can't generate OBJ file for monolane. Command attempted:")
                self.logger.warn(command)
                self.logger.warn(output)

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
