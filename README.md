# terminus
Library to procedurally create cities and terrains

[![Build Status](https://travis-ci.org/ekumenlabs/terminus.svg?branch=master)](https://travis-ci.org/ekumenlabs/terminus)

## Install with virtualenv

Builds are performed against Python 2.7.9 and pep8 v1.7.0. Follow these steps to get such a setup in a separate virtual environment:

- Install `virtualenv` if you don't have it already
```
$ sudo apt-get install python-virtualenv 
```
- Download and compile Python 2.7.9:
```
$ cd ~
$ mkdir PythonInstalls
$ cd PythonInstalls
$ wget http://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
$ tar xfz Python-2.7.9.tgz
$ cd Python-2.7.9/
$ ./configure --prefix /usr/local/lib/python2.7.9 --enable-ipv6
$ make
$ make install
```
- Just to be sure things went ok:
```
$ /usr/local/lib/python2.7.9/bin/python -V
Python 2.7.9
```
- Clone the repo in your machine and `cd` into it:
```
$ cd ~
$ git clone git@github.com:ekumenlabs/terminus.git
$ cd terminus
```
- Setup submodule:
```
git submodule update --init --recursive
```
- Setup virtualenv with the proper binary:
```
$ virtualenv -p /usr/local/lib/python2.7.9/bin/python2.7 env
Running virtualenv with interpreter /usr/local/lib/python2.7.9/bin/python2.7
New python executable in env/bin/python2.7
Also creating executable in env/bin/python
Installing setuptools, pip...done.
```
- Activate the new virtual environment:
```
$ source env/bin/activate
```
- Install pep 8:
```
$ pip install pep8==1.7.0
Downloading/unpacking pep8==1.7.0
  Downloading pep8-1.7.0-py2.py3-none-any.whl (41kB): 41kB downloaded
Installing collected packages: pep8
Successfully installed pep8
Cleaning up...
```
- Setup project dependencies:
```
$ python setup.py develop
```
- Verify tests and pep8 are passing:
```
./run_tests.sh
./run_pep8.sh
```

## Add pre-commit hook

Execute the following to run the tests as a pre-commit hook in your local env:
```
$ ln -s ../../pre-commit.sh .git/hooks/pre-commit
```

## Run generators

- Execute `$ terminus/run_generator.py` to create a new city. In order for the generator to run you **must** specify the builder to use (and its required constructor values). You can optionally specify the output file (if none specified the output will be written to `generated_worlds/city.world`).
Some examples:

    * Get help: `$ terminus/run_generator.py -h`
    * Generate using the simple city builder `$ terminus/run_generator.py --builder=SimpleCityBuilder`
    * Specify the output file `$ terminus/run_generator.py --builder=SimpleCityBuilder --destination=demo_city.world`
    * Generate the city using the `procedural_city_generation` package $ terminus/run_generator.py --builder=ProceduralCityBuilder --parameters size=1500

- Open using `$ gazebo generated_worlds/city.world`

## About the builders

Currently the idea is to have a single, unified City model that knows how to convert itself to an sdf file and that can be generated in different ways. These different ways of building cities are captured in the "builder" classes, which so far are two:

- `SimpleCityBuilder`, which generates a squared city based on a configurable size.
- `ProceduralCityBuilder`, which takes the output file(s) produced by https://github.com/josauder/procedural_city_generation and uses that to build the city model.
