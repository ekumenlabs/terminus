FROM agalbachicar/terminus:env
MAINTAINER Javier Choclin jchoclin@ekumenlabs.com

# Install DART dependencies
RUN apt-get install -y libflann-dev libgtest-dev libeigen3-dev libassimp-dev freeglut3-dev libxi-dev libxmu-dev libtinyxml-dev libtinyxml2-dev libfcl-dev liburdfdom-dev libboost-system-dev libboost-filesystem-dev

# Install SDF format dependencies
RUN apt-get install -y libboost-system-dev libboost-filesystem-dev libboost-program-options-dev libboost-regex-dev libboost-iostreams-dev libtinyxml-dev libxml2-utils ruby2.3 ruby2.3-dev

# Install ignition dependencies
RUN apt-get install -y libprotoc-dev libprotobuf-dev protobuf-compiler uuid-dev libzmq3-dev libczmq-dev uuid-dev libignition-math2-dev libfreeimage-dev libgts-dev libavformat-dev libavcodec-dev libswscale-dev libavutil-dev libavdevice-dev uuid-dev

# Download and compile Ignition package
RUN hg clone https://bitbucket.org/ignitionrobotics/ign-math /home/gazebo/ws/ign-math
RUN cd /home/gazebo/ws/ign-math; mkdir build; cd build; cmake .. -DCMAKE_INSTALL_PREFIX=/usr; make -j4; make install

# Download and compile SDFormat package
RUN hg clone https://bitbucket.org/osrf/sdformat /home/gazebo/ws/sdformat
RUN cd /home/gazebo/ws/sdformat; mkdir build; cd build; cmake .. -DCMAKE_INSTALL_PREFIX=/usr; make -j4; make install