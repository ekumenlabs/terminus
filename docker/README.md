Create a docker image to compile Gazebo 7.

It is important to have the exact version of the graphics card in your computer and in the docker container. In consequence we have different Dockerfiles for different drivers.

### Using NVIDIA drivers

We are using the propietary drivers from `ppa:graphics-drivers/ppa`. The default driver is `nvidia-367`.

`make gazebo7-nvidia gazebo7-nvidia`

If you are using another one you can use:

`make NVIDIA_DRIVER="nvidia-xxx" gazebo7-nvidia gazebo7-nvidia`

Check that your nvidia driver that is going to be downloaded is the same than the one that you have instaled.

### Using Intel drivers

