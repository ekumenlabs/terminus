/* -*- mode: C++ -*- */
/*
 *  Copyright (C) 2007 Tarun Nimmagadda, Patrick Beeson
 *  Copyright (C) 2010 Jack O'Quin
 *
 *  License: Modified BSD Software License Agreement
 * 
 *  $Id: 8f4d89b09102486a7d93ae83105c6b73c39e6296 $
 */

/**  \file
 
     C++ interface for Route Network Definition File

     This defines the RNDF structure as specified by the March 14,
     2007 DARPA specification.
 */

#ifndef __RNDF_h__
#define __RNDF_h__

#include <vector>
#include <string>
#include <iterator>
#include <map>

#include <rndf_visualizer/Graph.h>

template <class T>
void print_vector (std::vector<T> vec);

//<waypoint>
class LL_Waypoint {
 public:
  int waypoint_id; //integer > 0
  LatLong ll;
  //double latitude; //6 decimal digits
  //double longitude; //6 decimal digits
  
  //METHODS
  LL_Waypoint(std::string line, int x, int y, int line_number, bool& valid,
	      bool verbose);
  bool isvalid(){return(waypoint_id > 0);};
  void clear(){ waypoint_id = -1; ll.latitude = ll.longitude = -1.0;};
  void print(){print_without_newline(); printf("\n");};
  void print_without_newline(){
    printf("Waypoint %d, Latitude: %f, Longitude: %f", 
	   waypoint_id, ll.latitude, ll.longitude);
  };
};

typedef LL_Waypoint Perimeter_Point;

//<checkpoint>
class Checkpoint {
 public:
  int checkpoint_id; //integer > 0
  int waypoint_id;   //integer > 0

  //METHODS
  Checkpoint(){};
  //Returns a parsed checkpoint from 'line' with waypoint id 'x.y.z' 
  Checkpoint (std::string line, int x, int y, int line_number, bool& valid,
	      bool verbose);
  bool isvalid(){return (waypoint_id > 0 && checkpoint_id > 0 );};
  void clear(){ waypoint_id = checkpoint_id = -1;}; 
  void print(){
    printf("Checkpoint Number %d is at Waypoint %d\n", 
	   checkpoint_id, waypoint_id);
  };
};

class Unique_id{
 public:
  int waypoint_id;
  int lane_id;
  int segment_id;
 
  //METHODS
  bool isvalid(){return (waypoint_id > 0 && lane_id >= 0 && segment_id > 0);};
  void clear();
  void print(){printf("%d.%d.%d", segment_id, lane_id, waypoint_id);};
};
//<exit>
class Exit {
 public:
  Unique_id start_point;
  Unique_id end_point;
  Exit(std::string line, int x, int y, int line_number, bool& valid, 
       bool verbose);
  bool isvalid(){    return (start_point.isvalid() && end_point.isvalid());};
  void clear(){start_point.waypoint_id = end_point.waypoint_id
      = end_point.lane_id = end_point.segment_id = -1;};
  void print();
};

/*
  typedef Exit Exit_To_Perimeter;
  typedef Exit Exit_From_Perimeter;
*/
/*
  class Exit_To_Perimeter{
  int exit_waypoint;
  int entry_perimeterpoint;
  };

  class Exit_From_Perimeter{
  int exit_perimeterpoint;
  int entry_waypoint;
  };
*/

//<stop>
class Stop{
 public:
  int waypoint_id;
  bool isvalid(){return (waypoint_id > 0);};
  void clear(){waypoint_id = -1;};
  void print(){printf("Stop at Waypoint %d\n", waypoint_id);}; 
  //Returns a parsed stop from 'line' with waypoint id 'x.y.z' 
  Stop (std::string line, int x, int y, int line_number, bool& valid, bool verbose);
};

//<lane>
class Lane{
 public:
  int lane_id; //integer > 0
  int number_of_waypoints; //integer > 0
  std::vector<LL_Waypoint> waypoints; //List of waypoints
  //<optional lane header>
  int lane_width; //integer >= 0 (OPTIONAL)
  Lane_marking left_boundary;
  Lane_marking right_boundary;
  std::vector<Checkpoint> checkpoints;
  std::vector<Stop> stops;
  std::vector<Exit> exits;
 
  //METHODS
  bool isvalid(){return (lane_id > 0 && number_of_waypoints > 0 
			 && lane_width >= 0
			 && number_of_waypoints == (int)waypoints.size());};
  void clear();
  void print();
};

//<segment>
class Segment{
 public:
  int segment_id; // integer > 0
  int number_of_lanes; // integer > 0
  //<optional segment header>
  std::string segment_name; // such as "Wisconsin_Ave"
  std::vector<Lane> lanes; // List of Lanes
 
  //METHODS
  bool isvalid(){return (segment_id > 0 && number_of_lanes > 0
			 && number_of_lanes == (int)lanes.size());};
  void clear();
  void print();
};
 
//<perimeter>
class Perimeter{
 public:
  int perimeter_id; //integer = 0 :(ALWAYS '0', because
  //there is only one perimeter per zone
  int number_of_perimeterpoints; //integer > 0
  //<optional perimeter header>
  std::vector<Exit> exits_from_perimeter;
  std::vector<Perimeter_Point> perimeterpoints;

  //METHODS
  bool isvalid(){return (perimeter_id == 0 && number_of_perimeterpoints > 0
			 && number_of_perimeterpoints == (int)perimeterpoints.size());};
  void clear();
  void print();
};

//Parking Spots
class Spot{
 public:
  int spot_id;   //integer > 0
  //<optional spot header>
  int spot_width; //integer > 0
  Checkpoint checkpoint;
  std::vector<LL_Waypoint> waypoints;

  //METHODS
  bool isvalid(){return (spot_id > 0 && spot_width >= 0);};
  void clear();
  void print();
};


//<zone>
class Zone{
 public:
  int zone_id; //integer > 0
  int number_of_parking_spots; //integer >= 0
  //<optional zone header>
  std::string zone_name; //Designate the zone, such as "North_Parking_Lot"
  //<perimeter>
  Perimeter perimeter;
  std::vector<Spot> spots;

  //METHODS
  bool isvalid(){return(zone_id > 0 && number_of_parking_spots >= 0 
			&& number_of_parking_spots == (int)spots.size());};
  void clear();
  void print();
};

//<speed_limit>
class Speed_Limit {
 public:
  int id; //either a segment or a zone id
  int min_speed; // integer >= 0 in mph
  int max_speed; // integer >= 0 in mph

  bool isvalid(){return(id > 0 && min_speed >= 0 && max_speed >= 0);};
  void clear(){id = min_speed = max_speed = -1;};
  void print(); 

  Speed_Limit(std::string line, int line_number, bool& valid, bool verbose);
  Speed_Limit(){clear();};
  //~Speed_Limit();
  bool operator==(const Speed_Limit &that)
  {
    return (this->id == that.id
	    && this->min_speed == that.min_speed
	    && this->max_speed == that.max_speed);
  }

};

class RNDF {
 public:
  //ELEMENTS
  std::string filename; //filename
  int number_of_segments; //number of segments (integer > 0)
  int number_of_zones; //number of zones (integer >= 0)

  //<optional file header>
  std::string format_version;
  std::string creation_date;

  std::vector<Segment> segments;
  std::vector<Zone> zones;

  //METHODS
  RNDF(std::string rndfname, bool verbose=false);
  ~RNDF() {};

  void populate_graph(Graph& graph);
  void print();

  bool is_valid;

 private:
  bool isvalid(){return(number_of_segments > 0 && number_of_zones >= 0
			&& number_of_segments == (int) segments.size()
			&& number_of_zones == (int) zones.size());};
  struct id_comparator {
    bool operator()(const ElementID e1, const ElementID e2) const {
      if (e1.seg != e2.seg)
	return e1.seg < e2.seg;
      else if (e1.lane != e2.lane)
	return e1.lane < e2.lane;
      else return e1.pt < e2.pt;
    }
  };
  typedef std::map<ElementID, WayPointNode, id_comparator> id_to_waypoint_map;
    
  id_to_waypoint_map id_map;

  std::vector<WayPointEdge> edges;

  void prep_graph();

  int line_number;
  Lane_marking parse_boundary(std::string line, bool& valid);
};

class MDF {
 public: 
  std::string filename; //MDF name
  std::string RNDF_name; //RNDF name

  //<optional file header>
  std::string format_version;
  std::string creation_date;

  //checkpoints
  int number_of_checkpoints; //integer > 0
  std::vector<int> checkpoint_ids;
  //speed limits
  int number_of_speedlimits; //integer > 0
  std::vector<Speed_Limit> speed_limits;

  void print();
  bool add_speed_limits(Graph& graph);
  MDF(std::string mdfname, bool verbose=false);
  ~MDF(){};

  bool is_valid;
 private:

  int line_number;
  Speed_Limit parse_speedlimits(std::string line); 
  bool isvalid(){return (number_of_checkpoints > 0 && number_of_speedlimits > 0
			 && number_of_checkpoints == (int) checkpoint_ids.size()
			 && number_of_speedlimits == (int) speed_limits.size());};
};

//Global Functions
std::string parse_string(std::string line, std::string token, 
			 int line_number, bool& valid, bool verbose);
int parse_integer(std::string line, std::string token, 
		  int line_number, bool& valid, bool verbose);
int parse_integer(std::string line, int line_number, bool& valid, bool verbose);

void checkpoint_error(int seg, int lane, int way);
void stop_error(int seg, int lane, int way);
void exit_error(Exit& exit);
void print_error_message(int line_number, std::string token);

#endif
