# If you want to rebuild all images, set this to --no-cache from the commandline
DOCKER_ARGS?=
# Uncoment this line to rebuild without cache
# DOCKER_ARGS="--no-cache"
NVIDIA_DRIVER?="nvidia-367"

default: gazebo-terminus
# You need to specify a particular target
#--------------------------------------------------------------------------
# Stable and local targets
.PHONY: gazebo-terminus
gazebo-terminus:
	docker build ${DOCKER_ARGS} -t gazebo-terminus:latest gazebo-terminus

.PHONY: gazebo-terminus-nvidia-local
gazebo-terminus-nvidia-local: gazebo-terminus
	docker build ${DOCKER_ARGS} --build-arg nvidia_driver=${NVIDIA_DRIVER} -t gazebo-terminus-nvidia-local:latest gazebo-terminus-nvidia-local

.PHONY: gazebo-terminus-intel-local
gazebo-terminus-intel-local: gazebo-terminus
	docker build ${DOCKER_ARGS} -t gazebo-terminus-intel-local:latest gazebo-terminus-intel-local
#--------------------------------------------------------------------------
# Stable and Docker Hub targets
.PHONY: gazebo-terminus-nvidia
gazebo-terminus-nvidia:
	docker build ${DOCKER_ARGS} --build-arg nvidia_driver=${NVIDIA_DRIVER} -t gazebo-terminus-nvidia:latest ekumenlabs-terminus-nvidia

.PHONY: gazebo-terminus-intel
gazebo-terminus-intel:
	docker build ${DOCKER_ARGS} -t gazebo-terminus-intel:latest ekumenlabs-terminus-intel
#--------------------------------------------------------------------------
# Development and local targets
.PHONY: gazebo-terminus-dev
gazebo-terminus-dev:
	docker build ${DOCKER_ARGS} -t gazebo-terminus:dev gazebo-terminus-dev

.PHONY: gazebo-terminus-intel-dev
gazebo-terminus-intel-dev: gazebo-terminus-dev
	docker build ${DOCKER_ARGS} -t gazebo-terminus-intel-local:dev gazebo-terminus-intel-dev

.PHONY: gazebo-terminus-nvidia-dev
gazebo-terminus-nvidia-dev: gazebo-terminus-dev
	docker build ${DOCKER_ARGS} --build-arg nvidia_driver=${NVIDIA_DRIVER} -t gazebo-terminus-nvidia-local:dev gazebo-terminus-nvidia-dev

