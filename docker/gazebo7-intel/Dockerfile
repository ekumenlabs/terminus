FROM gazebo7

MAINTAINER Javier Choclin, jchoclin@ekumenlabs.com

USER root

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8

# Keeps some debs from trying to open dialogs during installation
ENV DEBIAN_FRONTEND noninteractive

# Install the NVIDIA binary drivers
RUN apt-get install -y libgl1-mesa-glx libgl1-mesa-dri xserver-xorg-video-intel
