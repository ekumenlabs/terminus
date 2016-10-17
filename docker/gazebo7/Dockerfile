FROM ubuntu:xenial
MAINTAINER Javier Choclin jchoclin@ekumenlabs.com

# Select Gazeo 7 commit
ARG gazebo_commit

# setup environment
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8

# install bootstrap tools
RUN apt-get update && apt-get install --no-install-recommends -y \
    python-vcstools \
    && rm -rf /var/lib/apt/lists/*

# Install development packages
RUN apt-get update && apt-get install -y sudo git build-essential mercurial vim tmux openssh-server software-properties-common bash-completion

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

# Install SDF format dependencies
RUN apt-get install -y libboost-system-dev libboost-filesystem-dev libboost-program-options-dev libboost-regex-dev libboost-iostreams-dev libtinyxml-dev libxml2-utils ruby2.3 ruby2.3-dev

# Install Gazebo dependencies
RUN apt-get install -y libsdformat4-dev libogre-1.9-dev libbullet-dev libqt4-dev libqtwebkit-dev libfreeimage-dev libprotoc-dev libprotobuf-dev protobuf-compiler freeglut3-dev libcurl4-openssl-dev libtinyxml-dev libtar-dev libtbb-dev libxml2-dev pkg-config libltdl-dev libgts-dev libboost-thread-dev libboost-signals-dev libboost-system-dev libboost-filesystem-dev libboost-program-options-dev libboost-regex-dev libboost-iostreams-dev libsimbody-dev libignition-math2-dev libignition-transport-dev libqwt-dev libignition-msgs-dev

# Install Gazebo aditional dependencies
RUN apt-get install -y libavformat-dev libavcodec-dev libgraphviz-dev libswscale-dev libavdevice-dev ruby-ronn

# Install ignition dependencies
RUN apt-get install -y libprotoc-dev libprotobuf-dev protobuf-compiler uuid-dev libzmq3-dev libczmq-dev uuid-dev libignition-math2-dev libfreeimage-dev libgts-dev libavformat-dev libavcodec-dev libswscale-dev libavutil-dev libavdevice-dev uuid-dev

# Install DART dependencies
RUN apt-get install -y libflann-dev libgtest-dev libeigen3-dev libassimp-dev freeglut3-dev libxi-dev libxmu-dev libtinyxml-dev libtinyxml2-dev libfcl-dev liburdfdom-dev libboost-system-dev libboost-filesystem-dev

# Create workspace directory
RUN mkdir -p /home/gazebo/ws/

# Download and compile Ignition package
RUN hg clone https://bitbucket.org/ignitionrobotics/ign-math /home/gazebo/ws/ign-math
RUN cd /home/gazebo/ws/ign-math; mkdir build; cd build; cmake .. -DCMAKE_INSTALL_PREFIX=/usr; make -j4; make install

# Download and compile SDFormat package
RUN hg clone https://bitbucket.org/osrf/sdformat /home/gazebo/ws/sdformat
RUN cd /home/gazebo/ws/sdformat; mkdir build; cd build; cmake .. -DCMAKE_INSTALL_PREFIX=/usr; make -j4; make install

# Download and compile Gazebo
RUN hg clone https://bitbucket.org/osrf/gazebo /home/gazebo/ws/gazebo
# Use branch visualization on demand
RUN cd /home/gazebo/ws/gazebo; hg up -r $gazebo_commit; mkdir build; cd build; cmake .. -DCMAKE_INSTALL_PREFIX=/usr; make -j4; make install

USER gazebo

WORKDIR /home/gazebo/ws
CMD ["tmux"]
