# Gazebo 7 compilation image

In order to guarantee that we are all using the same gazebo configuration we have created a docker image that downloads and compiles Gazebo 7.

## Usage

To start the container just execute the script `run_simulator`:

```
$ ./run_simulator [CONTAINER_NAME] [CONTAINER_IMAGE]
```

The image name is the one that you use with the makefile, for now:

* gazebo7-nvidia
* gazebo7-intel

We recommend to use the same name for the container, so you should run one of these commands:

```
$ ./run_simulator gazebo7-nvidia gazebo7-nvidia
$ ./run_simulator gazebo7-intel gazebo7-intel
```

The script `run_simulator` will mount the repository folder into the docker container. We recommend working outside the container and placing the files in folder of the repositorys. Be aware that the CONTAINER WILL BE DELETED EACH TIME THAT YOU EXIT IT. This is done in order to make sure that you are not modifying the image that you are working with, so all the colaborators are working with the same image.


## Gazebo 7 version

This docker compiles Gazebo7 on a previusly declared commit. Please make sure that you are compiling the right commit and branch. You can always check what commit it is using by doing:

```
$ cd /home/gazebo/ws/gazebo
$ hg --debug id -i
```

The commit hash is set on the makefile under the variable `GAZEBO_COMMIT`. Don't change it without consulting with the development team.

## Special considerations regarding the graphic card usage


It is important to have the exact version of the graphics card in your computer and in the docker container. As a result we have different Dockerfiles for different drivers.

### Using NVIDIA drivers

We are using the propietary drivers from `ppa:graphics-drivers/ppa`. The default driver is `nvidia-367`.

`make gazebo7-nvidia gazebo7-nvidia`

If you are using another one you can use:

`make NVIDIA_DRIVER="nvidia-xxx" gazebo7-nvidia gazebo7-nvidia`

Check that your nvidia driver that is going to be downloaded is the same that the one that you have installed.

### Using Intel drivers

For intel, you need to run the following command:
```
make gazebo7-intel gazebo7-intel
```

Make sure that your host computer has the latest version of the package `xserver-xorg-video-intel` that will be downloaded.
