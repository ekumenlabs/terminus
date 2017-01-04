FROM agalbachicar/terminus:manifold
MAINTAINER Javier Choclin jchoclin@ekumenlabs.com

# Select Gazebo commit
ARG gazebo_commit=2b49dbedff87910898d507c09135e1f078c40f59

# Download and compile Gazebo
RUN hg clone https://bitbucket.org/osrf/gazebo /home/gazebo/ws/gazebo
# Use branch visualization on demand
RUN cd /home/gazebo/ws/gazebo; hg up -r ${gazebo_commit}; mkdir build; cd build; cmake -DCMAKE_INSTALL_PREFIX=/usr -DENABLE_TESTS_COMPILATION=FALSE ../; make -j4; make install

RUN mkdir -p /home/gazebo/ws/src

WORKDIR /home/gazebo/ws
CMD ["tmux"]