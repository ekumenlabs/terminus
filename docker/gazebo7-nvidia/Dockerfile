FROM gazebo7

MAINTAINER Javier Choclin, jchoclin@ekumenlabs.com

ARG nvidia_driver

USER root

# Keeps some debs from trying to open dialogs during installation
ENV DEBIAN_FRONTEND noninteractive

# Install the NVIDIA binary drivers
USER root
RUN apt-get -y install software-properties-common # for add-apt-repository
RUN add-apt-repository ppa:graphics-drivers/ppa
RUN apt-get update
RUN apt-get install -y mesa-utils
RUN apt-get install -y $nvidia_driver
