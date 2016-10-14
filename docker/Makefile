# If you want to rebuild all images, set this to --no-cache from the commandline
DOCKER_ARGS=
NVIDIA_DRIVER="nvidia-367"

default:
	# You need to specify a particular target

.PHONY: gazebo7
gazebo7:
	docker build ${DOCKER_ARGS} -t gazebo7 gazebo7

.PHONY: gazebo7-nvidia
gazebo7-nvidia: gazebo7
	docker build ${DOCKER_ARGS} --build-arg nvidia_driver=${NVIDIA_DRIVER} -t gazebo7-nvidia gazebo7-nvidia

.PHONY: gazebo7-intel
gazebo7-intel: gazebo7
	docker build ${DOCKER_ARGS} -t gazebo7-intel gazebo7-intel

