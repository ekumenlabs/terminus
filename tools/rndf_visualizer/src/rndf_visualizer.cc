/*
 *  utility to print RNDF lane information
 *
 *  Copyright (C) 2005, 2010, Austin Robot Technology
 *
 *  License: Modified BSD Software License Agreement
 *
 *  $Id: b36bb9911e50d99a0f0558355914f0636cc3a687 $
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>			// for sleep
#include <getopt.h>
#include <signal.h>
#include <string.h>

#include <iostream>
#include <fstream>
#include <iomanip>

#include <rndf_visualizer/euclidean_distance.h>
#include <rndf_visualizer/MapLanes.h>
#include <rndf_visualizer/zones.h>
#include <rndf_visualizer/ZoneOps.h>

/** @file

 @brief utility to print RNDF lane information.

 @author Jack O'Quin, Patrick Beeson

*/


// default parameters
char *pname;				// program name
bool print_polys = false;
bool output_polys = false;
bool make_image = false;
bool svg_format = false;
bool with_trans = false;
int verbose = 0;
char *rndf_name;
float poly_size=-1;

double gps_latitude = 0.0;
double gps_longitude = 0.0;

RNDF *rndf = NULL;
Graph* graph = NULL;

float centerx,centery;
#define CMD "rndf_lanes: "		// message prefix

/** build road map graph from Road Network Definition File */
bool build_RNDF()
{
  rndf = new RNDF(rndf_name);

  if (!rndf->is_valid) {
    std::cerr << "RNDF not valid\n";
    return false;;
  }

  graph = new Graph();

  rndf->populate_graph(*graph);

  // pos.gps_latitude=graph.nodes[0].ll.latitude;
  // pos.gps_longitude=graph.nodes[0].ll.longitude;

  if (graph->rndf_is_gps())
    {

      std::cout << "RNDF uses GPS waypoints\n";

      if (gps_latitude == 0 &&
	  gps_longitude == 0)
	{
	  gps_latitude = graph->nodes[0].ll.latitude;
	  gps_longitude = graph->nodes[0].ll.longitude;
	  graph->find_mapxy();

	  float min_x=FLT_MAX;
	  float min_y=FLT_MAX;
	  float max_x=-FLT_MAX;
	  float max_y=-FLT_MAX;
	  double initial_UTM_x;
	  double initial_UTM_y;
	  char zone[255];

          UTM::LLtoUTM(graph->nodes[0].ll.latitude,
                       graph->nodes[0].ll.longitude,
                       initial_UTM_y,
                       initial_UTM_x,
                       zone);

	  ZonePerimeterList zones =
            ZoneOps::build_zone_list_from_rndf(*rndf, *graph);

	  for(unsigned j = 0; j < zones.size(); j++) {
	    ZonePerimeter zzone = zones[j];
	    for(unsigned i = 0; i < zzone.perimeter_points.size(); i++) {
	      if (zzone.perimeter_points[i].map.x < min_x)
		min_x=zzone.perimeter_points[i].map.x;
	      if (zzone.perimeter_points[i].map.y < min_y)
		min_y=zzone.perimeter_points[i].map.y;
	      if (zzone.perimeter_points[i].map.x > max_x)
		max_x=zzone.perimeter_points[i].map.x;
	      if (zzone.perimeter_points[i].map.y > max_y)
		max_y=zzone.perimeter_points[i].map.y;
	    }
	  }

	  for (uint i=0;i<graph->nodes_size;i++)
	    {
	      if (graph->nodes[i].map.x < min_x)
		min_x=graph->nodes[i].map.x;
	      if (graph->nodes[i].map.y < min_y)
		min_y=graph->nodes[i].map.y;
	      if (graph->nodes[i].map.x > max_x)
		max_x=graph->nodes[i].map.x;
	      if (graph->nodes[i].map.y > max_y)
		max_y=graph->nodes[i].map.y;
	    }

	  centerx=(max_x+min_x)/2 - graph->nodes[0].map.x + initial_UTM_x;
	  centery=(max_y+min_y)/2 - graph->nodes[0].map.y + initial_UTM_y;

	  double centerlat, centerlong;

          UTM::UTMtoLL(centery,centerx,zone,
                       centerlat,centerlong);

	  std::cout << "Center for RNDF is at lat/long: "<<
	    std::setprecision(8)<<
	    centerlat<<", "<<centerlong<<" "<<zone<<std::endl;

    std::cout << "X,Y coordiantes for map: \n"
              << std::setprecision(8)<< "  min=(" << min_x << "," << max_x << ")\n  max=(" << max_x << "," << max_y << ")\n  centre=(" << (max_x+min_x)/2  << "," << (max_y+min_y)/2  << ")\n";
    std::cout << std::setprecision(8) << "  Width=" << max_x-min_x << " m\n  Height=" << max_y-min_y << " m\n";


	  gps_latitude = centerlat;
	  gps_longitude = centerlong;

	}
      graph->find_mapxy();

    }
  else
    {
      std::cout << "RNDF does not use GPS waypoints\n";
      graph->xy_rndf();
    }


  return true;
}

/** parse command line arguments */
void parse_args(int argc, char *argv[])
{
  bool print_usage = false;
  const char *options = "higops:tx:y:v";
  int opt = 0;
  int option_index = 0;
  struct option long_options[] =
    {
      { "help", 0, 0, 'h' },
      { "image", 0, 0, 'i' },
      { "svg", 0, 0, 'g' },
      { "latitude", 1, 0, 'x' },
      { "longitude", 1, 0, 'y' },
      { "size", 1, 0, 's' },
      { "print", 0, 0, 'p' },
      { "output-points", 0, 0, 'o' },
      { "trans", 0, 0, 't' },
      { "verbose", 0, 0, 'v' },
      { 0, 0, 0, 0 }
    };

  /* basename $0 */
  pname = strrchr(argv[0], '/');
  if (pname == 0)
    pname = argv[0];
  else
    pname++;

  opterr = 0;
  while ((opt = getopt_long(argc, argv, options,
			    long_options, &option_index)) != EOF)
    {
      switch (opt)
	{
	case 'i':
	  make_image = true;
	  break;

	case 'g':
	  make_image = true;
    svg_format = true;

	case 'v':
	  ++verbose;
	  break;

	case 'x':
	  gps_latitude = atof(optarg);
	  break;

	case 'y':
	  gps_longitude = atof(optarg);
	  break;

	case 's':
	  poly_size = atof(optarg);
	  break;

	case 't':
	  with_trans = true;
	  break;

	default:
	  fprintf(stderr, "unknown option character %c\n",
		  optopt);
	  /*fallthru*/
	case 'h':
	  print_usage = true;
	}
    }

  if (print_usage || optind >= argc)
    {
      fprintf(stderr,
	      "usage: %s [options] RNDF_name\n\n"
	      "    Display RNDF lane information.  Possible options:\n"
	      "\t-h, --help\tprint this message\n"
	      "\t-i, --image\tmake .pgm image of polygons\n"
	      "\t-g, --svg\tmake SVG image from file\n"
	      "\t-y, --latitude\tinitial pose latitude\n"
	      "\t-x, --longitude\tinitial pose longitude\n"
	      "\t-s, --size\tmax polygon size\n"
	      "\t-v, --verbose\tprint verbose messages\n",
	      pname);
      exit(9);
    }

  rndf_name = argv[optind];
}


/** main program */
int main(int argc, char *argv[]) {
  int rc;

  parse_args(argc, argv);

  if (!build_RNDF()) {
      std::cerr << "RNDF not valid\n";
      return 1;
  }

  MapLanes *mapl = new MapLanes(verbose);

  rc = mapl->MapRNDF(graph,poly_size);
  if (rc != 0) {
      std::cout << "cannot process RNDF! (error code " << rc <<")\n";
      return 1;
  }

  if (make_image) {
    ZonePerimeterList zones = ZoneOps::build_zone_list_from_rndf(*rndf, *graph);
    mapl-> SetGPS(centerx,centery);
	  mapl-> testDraw(with_trans, zones, svg_format);
  }
  return rc;
}
