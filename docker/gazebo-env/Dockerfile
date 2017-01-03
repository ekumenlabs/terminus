FROM ubuntu:xenial
MAINTAINER Javier Choclin jchoclin@ekumenlabs.com

# setup environment
ENV DEBIAN_FRONTEND noninteractive
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8

# install bootstrap tools
RUN apt-get update && apt-get install --no-install-recommends -y \
    python-vcstools \
    && rm -rf /var/lib/apt/lists/*

# Install development packages
RUN apt-get update && apt-get install -y sudo git build-essential mercurial vim tmux openssh-server software-properties-common bash-completion debian-keyring debian-archive-keyring

# Add gazebo repository
RUN sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list'
RUN wget http://packages.osrfoundation.org/gazebo.key -O - | sudo apt-key add -
RUN apt-get update

# Create a user with passwordless sudo
RUN adduser --gecos "Development User" --disabled-password gazebo
RUN adduser gazebo sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN echo "export QT_X11_NO_MITSHM=1" >> /home/gazebo/.bashrc

# Install basic dependencies for Gazebo
RUN apt-get install -y build-essential cmake debhelper mesa-utils cppcheck xsltproc python-psutil python bc netcat-openbsd gnupg2 net-tools

# Install Gazebo dependencies
RUN apt-get install -y libsdformat4-dev libogre-1.9-dev libbullet-dev libqt4-dev libqtwebkit-dev libfreeimage-dev libprotoc-dev libprotobuf-dev protobuf-compiler freeglut3-dev libcurl4-openssl-dev libtinyxml-dev libtar-dev libtbb-dev libxml2-dev pkg-config libltdl-dev libgts-dev libboost-thread-dev libboost-signals-dev libboost-system-dev libboost-filesystem-dev libboost-program-options-dev libboost-regex-dev libboost-iostreams-dev libsimbody-dev libignition-math2-dev libignition-transport-dev libqwt-dev libignition-msgs-dev

# Install Gazebo aditional dependencies
RUN apt-get update && apt-get install -y libavformat-dev libavcodec-dev libgraphviz-dev libswscale-dev libavdevice-dev ruby-ronn

# Create workspace directory
RUN mkdir -p /home/gazebo/ws/