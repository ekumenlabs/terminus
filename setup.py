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

from setuptools import setup

setup(name='terminus',
      version='0.1',
      description='City generator for Gazebo',
      url='https://github.com/ekumenlabs/terminus',
      license='MIT',
      packages=['terminus'],
      install_requires=[
          'jinja2',
          'shapely',
          'numpy',
          'imposm.parser',
          'scipy',
          'matplotlib',
          'Pillow',
          'PyYAML',
          'mock',
          'python-slugify'
      ],
      zip_safe=False)
