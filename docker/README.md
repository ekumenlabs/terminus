Create a docker image to compile Gazebo 7.

## Using NVIDIA drivers

Edit the variable `NVIDIA_DRIVER` in the Makefile to match your host nvidia driver. We are using the propietary drivers from `ppa:graphics-drivers/ppa`. After that you can execute:

`make gazebo7-nvidia gazebo7-nvidia`


