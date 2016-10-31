cmake_minimum_required(VERSION 2.8.8)
project(nrdf_visualizer)


include_directories(
  include
)

file(GLOB rndf_visualizer_SRC "src/*.cc")

add_executable(rndf_visualizer ${rndf_visualizer_SRC})


