cmake_minimum_required(VERSION 2.8.8)
project(sample_svgpp)

include_directories( 
	include
)

link_directories(
)

add_executable( sample-svg src/main.cpp )

target_link_libraries(sample-svg)