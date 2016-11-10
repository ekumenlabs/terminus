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

