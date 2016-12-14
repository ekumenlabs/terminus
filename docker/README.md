# Gazebo 7 compilation image

In order to guarantee that we are all using the same gazebo configuration we have created a docker image that downloads and compiles Gazebo 7.

## Usage

To start the container just execute the script `run_simulator`:

```
cd {REPOSITORY_PATH}/terminus/docker
$ ./run_simulator [CONTAINER_NAME] [CONTAINER_IMAGE]
```

The image name is the one that you use with the makefile, for now:

* gazebo-terminus-nvidia
* gazebo-terminus-intel

We recommend to use the same name for the container, so you should run one of these commands:

```
$ ./run_simulator gazebo-terminus-nvidia gazebo-terminus-nvidia
$ ./run_simulator gazebo-terminus-intel gazebo-terminus-intel
```

The script `run_simulator` is configured to mount 2 directories:

* Current repository folder (from docker folder, its parent directory)
* [rndf_gazebo_plugin](https://bitbucket.org/JChoclin/rndf_gazebo_plugin) repository which is supposed to be at the same level of the current repository.

In case the `rndf_gazebo_plugin` repository is not at the same level of the current repository, you should change the mount path in the `run_simulator` script (check `DOCKER_MOUNT_ARGS` variable).

We recommend working outside the container and placing the files in folder of the repositories. Be aware that the CONTAINER WILL BE DELETED EACH TIME THAT YOU EXIT IT. This is done in order to make sure that you are not modifying the image that you are working with, so all the colaborators are working with the same image.


## Gazebo 7 version

This docker compiles [Gazebo](https://bitbucket.org/osrf/gazebo) on a previusly declared commit. Please make sure that you are compiling the right commit and branch. You can always check what commit it is using by doing the following inside the image:

```
$ cd /home/gazebo/ws/gazebo
$ hg --debug id -i
```

The commit hash is set on the makefile under the argument `gazebo_commit`. Don't change it without consulting with the development team.

## Manifold version

This docker compiles [Manifold](https://bitbucket.org/osrf/manifold) on a previusly declared commit. Please make sure that you are compiling the right commit and branch. You can always check what commit it is using by doing the following inside the image:

```
$ cd /tmp/manifold
$ hg --debug id -i
```

The commit hash is set on the makefile under the argument `manifold_commit`. Don't change it without consulting with the development team.

## Other repositories

This docker compiles downloads and compiles, on the default branch, the following repositories:

* [Ignition Math](https://bitbucket.org/ignitionrobotics/ign-math)
* [SDF Format](https://bitbucket.org/osrf/sdformat)

## Special considerations regarding the graphic card usage


It is important to have the exact version of the graphics card in your computer and in the docker container. As a result we have different Dockerfiles for different drivers.

### Using NVIDIA drivers

We are using the propietary drivers from `ppa:graphics-drivers/ppa`. The default driver is `nvidia-367`. From the docker folder execute:

```
cd {REPOSITORY_PATH}/terminus/docker
make gazebo-terminus-nvidia gazebo-terminus-nvidia
```

If you are using another one you can use:

`make NVIDIA_DRIVER="nvidia-xxx" gazebo-terminus-nvidia gazebo-terminus-nvidia`

Check that your nvidia driver that is going to be downloaded is the same that the one that you have installed.

### Using Intel drivers

For intel, you need to run the following command:
```
cd {REPOSITORY_PATH}/terminus/docker
make gazebo-terminus-intel gazebo-terminus-intel
```

Make sure that your host computer has the latest version of the package `xserver-xorg-video-intel` that will be downloaded.
