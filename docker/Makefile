# If you want to rebuild all images, set this to --no-cache from the commandline
DOCKER_ARGS?=
# Uncoment this line to rebuild without cache
# DOCKER_ARGS="--no-cache"
NVIDIA_DRIVER?="nvidia-367"
# Working branch: vis_on_demand
GAZEBO_COMMIT="2b49dbedff87910898d507c09135e1f078c40f59"

default:
	# You need to specify a particular target

.PHONY: gazebo-terminus
gazebo-terminus:
	docker build ${DOCKER_ARGS} -t gazebo-terminus gazebo-terminus

.PHONY: gazebo-terminus-nvidia
gazebo-terminus-nvidia: gazebo-terminus
	docker build ${DOCKER_ARGS} --build-arg nvidia_driver=${NVIDIA_DRIVER} -t gazebo-terminus-nvidia gazebo-terminus-nvidia

.PHONY: gazebo-terminus-intel
gazebo-terminus-intel: gazebo-terminus
	docker build ${DOCKER_ARGS} -t gazebo-terminus-intel gazebo-terminus-intel

.PHONY: ekumenlabs-terminus-intel
ekumenlabs-terminus-intel:
	docker build ${DOCKER_ARGS} -t ekumenlabs-terminus-intel ekumenlabs-terminus-intel

.PHONY: ekumenlabs-terminus-nvidia
ekumenlabs-terminus-nvidia:
	docker build ${DOCKER_ARGS} -t ekumenlabs-terminus-nvidia ekumenlabs-terminus-nvidia
