# Gazebo compilation image

In order to guarantee that we are all using the same gazebo configuration we have created a docker image that downloads and compiles Gazebo 8.

## Usage

To start the container just execute the script `run_simulator`:

```
cd {REPOSITORY_PATH}/terminus/docker
$ ./run_simulator [CONTAINER_NAME:TAG] [IMAGE_NAME]
```

The available image names are the following:

| Name                         | Tag    | Function                                                                                                                                  |
|------------------------------|--------|-------------------------------------------------------------------------------------------------------------------------------------------|
| gazebo-terminus              | latest | It has the base Gazebo image with all the resources including Manifold. It is the latest stable container.                                |
| gazebo-terminus              | dev    | It has the base Gazebo image with all the resources including Manifold. It is headed for development purposes so it may vary from latest. |
| gazebo-terminus-intel-local  | latest | It is based on gazebo-terminus:latest and includes Intel graphic card drivers.                                                            |
| gazebo-terminus-intel-local  | dev    | It is the same as gazebo-terminus-intel-local:latest but based on gazebo-terminus:dev.                                                    |
| gazebo-terminus-nvidia-local | latest | It is based on gazebo-terminus:latest and includes NVidia graphic card drivers.                                                           |
| gazebo-terminus-nvidia-local | dev    | It is based on gazebo-terminus:dev and includes NVidia graphic card drivers.                                                              |
| gazebo-terminus-intel        | latest | It is based on the ekumenlabs/gazebo-terminus:latest and includes Intel graphic card drivers.                                             |
| gazebo-terminus-nvidia       | latest | It is based on the ekumenlabs/gazebo-terminus:latest and includes Intel graphic card drivers.                                             |

We recommend to use the same name for the container, so you should run one of these commands for example:

```
$ ./run_simulator gazebo-terminus-nvidia gazebo-terminus-nvidia
$ ./run_simulator gazebo-terminus-intel gazebo-terminus-intel
$ ./run_simulator gazebo-terminus-intel-local:latest gazebo-terminus-intel-local
$ ./run_simulator gazebo-terminus-nvidia-local:dev gazebo-terminus-nvidia-local
```

The script `run_simulator` is configured to mount 2 directories:

* Current repository folder (from docker folder, its parent directory)
* [rndf_gazebo_plugin](https://bitbucket.org/JChoclin/rndf_gazebo_plugin) repository which is supposed to be at the same level of the current repository.

In case the `rndf_gazebo_plugin` repository is not at the same level of the current repository, you should change the mount path in the `run_simulator` script (check `DOCKER_MOUNT_ARGS` variable).

We recommend working outside the container and placing the files in folder of the repositories. BEWARE THAT THE CONTAINER WILL BE DELETED EACH TIME THAT YOU EXIT IT. This is done in order to make sure that you are not modifying the image that you are working with, so all the colaborators are working with the same image.

## Dependencies

### Current repositories commits

In the following table you can check the current repositories commits used for tag.

| Repository    | latest                                   | dev                                      |
|---------------|------------------------------------------|------------------------------------------|
| Gazebo        | [2b49dbedff87910898d507c09135e1f078c40f59](https://bitbucket.org/osrf/gazebo/src/2b49dbedff87910898d507c09135e1f078c40f59) | [2b49dbedff87910898d507c09135e1f078c40f59](https://bitbucket.org/osrf/gazebo/src/2b49dbedff87910898d507c09135e1f078c40f59) |
| Manifold      | [d17f711f060559033426b560c23bbe3ba2334fd3](https://bitbucket.org/osrf/manifold/src/d17f711f060559033426b560c23bbe3ba2334fd3) | [d17f711f060559033426b560c23bbe3ba2334fd3](https://bitbucket.org/osrf/manifold/src/d17f711f060559033426b560c23bbe3ba2334fd3) |
| SDFormat      | [a3fa3d1163cc](https://bitbucket.org/osrf/sdformat/src/a3fa3d1163cc)                             | [a3fa3d1163cc](https://bitbucket.org/osrf/sdformat/src/a3fa3d1163cc)                             |
| Ignition Math | [05e4ffaab536566ae5b55ed2cd2e62b94fdc1e23](https://bitbucket.org/ignitionrobotics/ign-math/src/05e4ffaab536566ae5b55ed2cd2e62b94fdc1e23) | [05e4ffaab536566ae5b55ed2cd2e62b94fdc1e23](https://bitbucket.org/ignitionrobotics/ign-math/src/05e4ffaab536566ae5b55ed2cd2e62b94fdc1e23) |


### Checking Gazebo version

This docker compiles [Gazebo](https://bitbucket.org/osrf/gazebo) on a previusly declared commit. Please make sure that you are compiling the right commit and branch. You can always check what commit it is using by doing the following inside the image:

```
$ cd /home/gazebo/ws/gazebo
$ hg --debug id -i
```

The commit hash is set on the makefile under the argument `gazebo_commit`. **Don't change it without consulting with the development team.**

## Checking Manifold version

This docker compiles [Manifold](https://bitbucket.org/osrf/manifold) on a previusly declared commit. Please make sure that you are compiling the right commit and branch. You can always check what commit it is using by doing the following inside the image:

```
$ cd /tmp/manifold
$ hg --debug id -i
```

The commit hash is set on the makefile under the argument `manifold_commit`. Don't change it without consulting with the development team.

## Checking Ignition Math version

This docker compiles [Ignition Math](https://bitbucket.org/ignitionrobotics/ign-math) on a previusly declared commit. Please make sure that you are compiling the right commit and branch. You can always check what commit it is using by doing the following inside the image:

```
$ cd /home/gazebo/ws/ign-math
$ hg --debug id -i
```

The commit hash is set on the makefile under the argument `ign_math_commit`. Don't change it without consulting with the development team.

## Checking SDFormat version

This docker compiles [SDFormat](https://bitbucket.org/osrf/sdformat) on a previusly declared commit. Please make sure that you are compiling the right commit and branch. You can always check what commit it is using by doing the following inside the image:

```
$ cd /home/gazebo/ws/sdformat
$ hg --debug id -i
```

The commit hash is set on the makefile under the argument `sdformat_commit`. Don't change it without consulting with the development team.

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
