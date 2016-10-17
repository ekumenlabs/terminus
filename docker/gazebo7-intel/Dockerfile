FROM gazebo7

MAINTAINER Javier Choclin, jchoclin@ekumenlabs.com

USER root

# Keeps some debs from trying to open dialogs during installation
ENV DEBIAN_FRONTEND noninteractive

# Install the NVIDIA binary drivers
USER root
sudo apt-get install -y libgl1-mesa-glx libgl1-mesa-dri xserver-xorg-video-intel
