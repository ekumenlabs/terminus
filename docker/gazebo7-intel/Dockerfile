FROM gazebo7

MAINTAINER Javier Choclin, jchoclin@ekumenlabs.com

USER root

# Keeps some debs from trying to open dialogs during installation
ENV DEBIAN_FRONTEND noninteractive

# Install the NVIDIA binary drivers
USER root
sudo apt-get install xserver-xorg-video-intel
