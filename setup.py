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
          'numpy'
      ],
      zip_safe=False)
