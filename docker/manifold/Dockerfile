FROM gazebo-subprojects
MAINTAINER Javier Choclin jchoclin@ekumenlabs.com

#Install Manifold dependencies
RUN apt-get update && apt-get install -y cmake pkg-config python ruby-ronn

# Select Manifold commit
ARG manifold_commit=5a095e0

#Clone and install Manifold
RUN hg clone https://bitbucket.org/osrf/manifold /tmp/manifold
RUN cd /tmp/manifold; hg up -r ${manifold_commit}; mkdir build; cd build; cmake -DCMAKE_INSTALL_PREFIX=/home/gazebo/manifold ../; cmake -DCMAKE_BUILD_TYPE=Debug ../; make -j4; make install