## RNDF visualizer

Generates a .ppm or .svg file for a given RNDF file.

This project depends on:

- simple_svg_1.0.0

### How to compile it

```
cd tools/rndf_visualizer
mkdir build
cd build
cmake ..
make
```

The binary file should be available in the build folder

### How to execute it

To get a .ppm image:

```
./rndf_visualizer -i [RNDF file path]
```

To get a .svg image:

```
./rndf_visualizer -g [RNDF file path]
```

### SVG color references

Waypoints:

1. Exit --> red
2. Entry --> blue
3. Stop --> orange
4. Perimeter --> yellow
5. Checkpoint --> fuchsia
6. Other kinds --> green

Trunks and lanes are dark grey. Connections between entry and exit waypoints are shown in cyan. Also, the area enclosed by perimeter waypoints is light blue now. 

### SVG debug modes

You can use the "debug mode" to print lanes with different colors. Also, you can selectively print waypoints. These options are configured from argument list parameters like:

```
./rndf_visualizer -d -w -g [RNDF file path]
```

Where:

1. -d or --debug for printing lanes with different colors. Connections keep in cyan so as to differentiate from lanes.
2. -w or --waypoinst for turning of waypoints. In case -d is used, waypoints color are the same to the lane they belong to.
 

