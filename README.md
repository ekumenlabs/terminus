# terminus
Library to procedurally create cities and terrains

## Install

- Clone the repo and run `$ python setup.py develop` to setup package and dependencies. 
- Execute `$ terminus/run_generator.py` to create a new city. In order for the generator to run you **must** specify the builder to use (and its required constructor values). You can optionally specify the output file (if none specified the output will be written to `generated_worlds/city.world`).
Some examples:

    * Get help: `$ terminus/run_generator.py -h` 
    * Generate using the simple city builder `$ terminus/run_generator.py --builder=SimpleCityBuilder`
    * Specify the output file `$ terminus/run_generator.py --builder=SimpleCityBuilder --destination=demo_city.world`
    * Generate the city using the output file from the `procedural_city_generation` package `$ terminus/run_generator.py --builder=ProceduralCityBuilder --destination=procedural.world --parameters filename=../procedural_city_generation/procedural_city_generation/temp/mycity`    

- Open using `$ gazebo generated_worlds/city.world`
