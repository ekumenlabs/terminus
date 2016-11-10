//Tarun Nimmagadda
//The University of Texas, Austin

//This file defines the RNDF structure as specified by the DARPA
//specification.  It parses the RNDF file into the RNDF data structure

#include <cstdio>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string.h>
#include <cstdlib>
#include <conversions.h>
#include <epsilon.h>
#include <rndf_visualizer/RNDF.h>

#include <limits.h>
#include <stdio.h>

#define DEFAULT_LANE_WIDTH 3
#define DEFAULT_SPOT_WIDTH 3
#define DEFAULT_LANE_SPEED mph2mps(30)

enum RNDF_PARSE_STATE {COMMENT, GENERAL, SEGMENTS, LANES,
		       ZONES, PERIMETER, PARKING_SPOT, UNKNOWN};

enum MDF_PARSE_STATE {MDF_COMMENT, MDF_GENERAL, MDF_CHECKPOINTS,
		      MDF_SPEEDLIMITS, MDF_UNKNOWN};

template <class T>
void change_state(T& previous_state, T& current_state, const T new_state){
  previous_state = current_state;
  current_state = new_state;
};


RNDF::RNDF(std::string rndfname, bool verbose)
{
  number_of_segments = number_of_zones = -1;
  is_valid=true;
  
  std::ifstream rndf_file;
  rndf_file.open(rndfname.c_str());
  if (!rndf_file)
    {
      std::cout << "Error opening RNDF \"" << rndfname << "\"";
      is_valid = false;
      return;
    }
  
  //Parser State
  line_number = 0;
  RNDF_PARSE_STATE state = UNKNOWN, previous_state = UNKNOWN;

  Segment temp_segment;
  Lane temp_lane;
  Zone temp_zone;
  Perimeter temp_perimeter;
  Spot temp_spot;
  //Clear temp variables
  temp_segment.clear();
  temp_lane.clear();
  temp_zone.clear();
  temp_perimeter.clear();
  temp_spot.clear();



  std::string lineread;
  while(getline(rndf_file, lineread)) // Read line by line
    {
      line_number++;
      uint real_characters=0;

      for (uint ind=0; ind < lineread.length(); ind++)
	if (lineread[ind] != '\r' &&
	    lineread[ind] != '\t' &&
	    lineread[ind] != ' ')
	  real_characters++;
      
      //Blank lines
      if (real_characters == 0) {
	if (verbose)
	  printf("%d: Blank Line\n",line_number);
	continue;
      }
      
      std::string token;
      char token_char [lineread.size()+1];
      char temp_char [lineread.size()+1];

      //Read in one line
      sscanf(lineread.c_str(), "%s", token_char);
      token.assign(token_char);

      //      printf("Token: |%s|\n", token.c_str());

      if (state != COMMENT){
	if (token.compare("RNDF_name") == 0)
	  change_state(previous_state, state, GENERAL);
	else if (token.compare("segment") == 0)
	  change_state(previous_state, state, SEGMENTS);
	else if (token.compare("lane") == 0)
	  change_state(previous_state, state, LANES);
	else if (token.compare("zone") == 0)
	  change_state(previous_state, state, ZONES);
	else if (token.compare("perimeter") == 0)
	  change_state(previous_state, state, PERIMETER);
	else if (token.compare("spot") == 0)
	  change_state(previous_state, state, PARKING_SPOT);
	else if (token.find("/*") != std::string::npos)
	  change_state(previous_state, state, COMMENT);
      }

      bool valid=true;
      switch (state){
      case COMMENT:
	if (verbose)
	  printf("%d: COMMENT: %s\n", line_number, lineread.c_str());
	if (lineread.find("*/") != std::string::npos)
	  state = previous_state;
	break;
      case GENERAL:
	//RNDF_NAME
	if (token.compare("RNDF_name") == 0)
	  filename =
	    parse_string(lineread, std::string("RNDF_name"),
			 line_number, valid, verbose);
	//NUM_SEGMENTS
	else if (token.compare("num_segments") == 0){
	  number_of_segments =
	    parse_integer(lineread, std::string("num_segments"),
			  line_number, valid, verbose);
	  if (number_of_segments <= 0) valid = false;
	}
	//NUM_ZONES
	else if (token.compare("num_zones") == 0){
	  number_of_zones =
	    parse_integer(lineread, std::string("num_zones"),
			  line_number, valid, verbose);
	  if (number_of_zones < 0) valid = false;
	}
	//FORMAT_VERSION
	else if (token.compare("format_version") == 0)
	  format_version =
	    parse_string(lineread, std::string("format_version"),
			 line_number, valid, verbose);
	//CREATION_DATE
	else if (token.compare("creation_date") == 0)
	  creation_date =
	    parse_string(lineread, std::string("creation_date"),
			 line_number, valid, verbose);
	//END_FILE
	else if (token.compare("end_file") == 0){
	  if (!isvalid())
	    valid = false;
	  else if (verbose)
	    printf("%d: RNDF file has finished parsing\n", line_number);
	}
	//printf("Token: |%s|\n", token.c_str());
	else {
	  printf("%d: Unexpected token\n", line_number);
	  valid=false;
	}
	break;
      case SEGMENTS:
	//SEGMENT
	if(token.compare("segment") == 0){
	  temp_segment.segment_id =
	    parse_integer(lineread, std::string("segment"),
			  line_number, valid, verbose);
	  if (temp_segment.segment_id <= 0) valid = false;
	}
	//NUM_LANES
	else if(token.compare("num_lanes") == 0){
	  temp_segment.number_of_lanes =
	    parse_integer(lineread, std::string("num_lanes"),
			  line_number, valid, verbose);
	  if (temp_segment.number_of_lanes <= 0) valid = false;
	}
	//SEGMENT_NAME
	else if(token.compare("segment_name") == 0)
	  temp_segment.segment_name =
	    parse_string(lineread, std::string("segment_name"),
			 line_number, valid, verbose);
	//END_SEGMENT
	else if(token.compare("end_segment") == 0){
	  if (!temp_segment.isvalid())
	    valid = false;
	  else{
	    segments.push_back(temp_segment);
	    if (verbose)
	      printf("%d: segment has ended\n", line_number);
	    change_state(previous_state, state, GENERAL);
	    temp_segment.clear();
	  }
	}
	else{
	  printf("%d: Unexpected token\n", line_number);
	  valid=false;
	}
	break;
      case LANES:
	//LANE
	if(token.compare("lane") == 0){
	  sprintf(temp_char, "lane %d.%%d", temp_segment.segment_id);
	  if (sscanf(lineread.c_str(), temp_char, &temp_lane.lane_id) == 1){
	    if (verbose)
	      printf("%d: Lane number is %d\n",
		     line_number, temp_lane.lane_id);
	  }
	  else valid=false;
	  if (temp_lane.lane_id <= 0) valid = false;
	}
	//NUM_WAYPOINTS
	else if(token.compare("num_waypoints") == 0){
	  temp_lane.number_of_waypoints =
	    parse_integer(lineread, std::string("num_waypoints"),
			  line_number, valid, verbose);
	  if (temp_lane.number_of_waypoints <= 0) valid = false;
	}
	//LANE_WIDTH
	else if(token.compare("lane_width") == 0){
	  temp_lane.lane_width =
	    parse_integer(lineread, std::string("lane_width"),
			  line_number, valid, verbose);
	  if (temp_lane.lane_width <= 0) valid = false;
	}
	//LEFT_BOUNDARY
	else if(token.compare("left_boundary") == 0){
	  temp_lane.left_boundary =
	    parse_boundary(lineread, valid);
	  if (verbose)
	    printf("%d: left boundary type is %d\n",
		   line_number, temp_lane.left_boundary);
	}
	//RIGHT_BOUNDARY
	else if(token.compare("right_boundary") == 0){
	  temp_lane.right_boundary =
	    parse_boundary(lineread, valid);
	  if (verbose)
	    printf("%d: right boundary type is %d\n",
		   line_number, temp_lane.right_boundary);
	}
	//CHECKPOINT
	else if(token.compare("checkpoint") == 0){
	  Checkpoint checkpoint(lineread, temp_segment.segment_id,
				temp_lane.lane_id, line_number, valid, verbose);
	  temp_lane.checkpoints.push_back(checkpoint);
	}
	//STOP
	else if(token.compare("stop") == 0){
	  Stop stop(lineread, temp_segment.segment_id,
		    temp_lane.lane_id, line_number, valid, verbose);
	  temp_lane.stops.push_back(stop);
	}
	//EXIT
	else if(token.compare("exit") == 0){
	  Exit exit(lineread, temp_segment.segment_id,
		    temp_lane.lane_id, line_number, valid, verbose);
	  temp_lane.exits.push_back(exit);
	}
	//END_LANE
	else if(token.compare("end_lane") == 0){
	  if(temp_lane.number_of_waypoints != (int)temp_lane.waypoints.size())
	    printf("Number of waypoints in lane does not match num_waypoints\n");
	  if (!temp_lane.isvalid())
	    valid = false;
	  else{
	    temp_segment.lanes.push_back(temp_lane);
	    if (verbose)
	      printf("%d: lane has ended\n", line_number);
	    change_state(previous_state, state, SEGMENTS);
	    temp_lane.clear();
	  }
	}
	
	//NO TOKEN
	else{
	  //WAYPOINT
	  sprintf(temp_char, "%d.%d.", temp_segment.segment_id,
		  temp_lane.lane_id);
	  if(token.find(temp_char) != std::string::npos ){
	    LL_Waypoint wp(lineread, temp_segment.segment_id,
			   temp_lane.lane_id, line_number, valid, verbose);
	    temp_lane.waypoints.push_back(wp);
	  }
	  else{
	    printf("%d: Unexpected token\n", line_number);
	    valid=false;
	  }
	}
	break;
      case ZONES:
	//ZONE
	if(token.compare("zone") == 0){
	  temp_zone.zone_id =
	    parse_integer(lineread, std::string("zone"),
			  line_number, valid, verbose);
	  if (temp_zone.zone_id <= 0) valid = false;
	
	}
	//NUM_SPOTS
	else if(token.compare("num_spots") == 0){
	  temp_zone.number_of_parking_spots =
	    parse_integer(lineread, std::string("num_spots"),
			  line_number, valid, verbose);
	  if (temp_zone.number_of_parking_spots < 0) valid = false;	
	}
	//ZONE_NAME
	else if(token.compare("zone_name") == 0)
	  temp_zone.zone_name =
	    parse_string(lineread, std::string("zone_name"),
			 line_number, valid, verbose);
	//END_ZONE
	else if(token.compare("end_zone") == 0){
	  if(!temp_zone.isvalid())
	    valid = false;
	  else{
	    zones.push_back(temp_zone);
	    if (verbose)
	      printf("%d: zone has ended\n", line_number);
	    change_state(previous_state, state, GENERAL);
	    temp_zone.clear();
	  }
	}
	else {
	  printf("%d: Unexpected token\n", line_number);
	  valid=false;
	}	
	break;
      case PERIMETER:
	//PERIMETER
	if(token.compare("perimeter") == 0){
	  sprintf(temp_char,"perimeter %d.%%d" , temp_zone.zone_id);
	  if (sscanf(lineread.c_str(), temp_char,
		     &temp_perimeter.perimeter_id) == 1){
	    if (verbose)
	      printf("%d: Perimeter id is %d\n",
		     line_number, temp_perimeter.perimeter_id);
	  }
	  else valid=false;
	  if (temp_perimeter.perimeter_id != 0)
	    valid = false;
	}
	//NUM_PERIMETER_POINTS
	else if(token.compare("num_perimeterpoints") == 0){
	  temp_perimeter.number_of_perimeterpoints =
	    parse_integer(lineread, std::string("num_perimeterpoints"),
			  line_number, valid, verbose);
	  if (temp_perimeter.number_of_perimeterpoints <= 0)
	    valid = false;
	}
	//EXIT
	else if(token.compare("exit") == 0){
	  Exit exit(lineread, temp_zone.zone_id, 0, line_number, valid,
		    verbose);
	  temp_perimeter.exits_from_perimeter.push_back(exit);
	}
	//END_PERIMETER
	else if(token.compare("end_perimeter") == 0){
	  if(!temp_perimeter.isvalid())
	    valid = false;
	  else{
	    temp_zone.perimeter = temp_perimeter;
	    if (verbose)
	      printf("%d: perimeter has ended\n", line_number);
	    change_state(previous_state, state, ZONES);
	    temp_perimeter.clear();
	  }
	}
	else{
	  //WAYPOINT
	  sprintf(temp_char, "%d.%d.", temp_zone.zone_id, 0);
	  if(token.find(temp_char) != std::string::npos ){
	    LL_Waypoint wp(lineread, temp_zone.zone_id, 0, line_number,
			   valid, verbose);
	    temp_perimeter.perimeterpoints.push_back(wp);
	  }
	  else valid=false;
	}
	break;
      case PARKING_SPOT:
	//SPOT
	if(token.compare("spot") == 0){
	  sprintf(temp_char,"spot %d.%%d" , temp_zone.zone_id);
	  if (sscanf(lineread.c_str(), temp_char, &temp_spot.spot_id) == 1){
	    if (verbose)
	      printf("%d: Spot id is %d\n", line_number, temp_spot.spot_id);
	  }
	  else valid=false;
	  if (temp_spot.spot_id <= 0) valid = false;
	}
	//SPOT_WIDTH
	else if(token.compare("spot_width") == 0){
	  temp_spot.spot_width =
	    parse_integer(lineread, std::string("spot_width"),
			  line_number, valid, verbose);
	  if (temp_spot.spot_width <= 0) valid = false;	
	}
	//CHECKPOINT
	else if(token.compare("checkpoint") == 0)
	  temp_spot.checkpoint = Checkpoint(lineread, temp_zone.zone_id,
					    temp_spot.spot_id,
					    line_number, valid, verbose);
	//END_SPOT
	else if(token.compare("end_spot") == 0){
	  if(!temp_spot.isvalid())
	    valid = false;
	  else{
	    temp_zone.spots.push_back(temp_spot);
	    if (verbose)
	      printf("%d: spot has ended\n", line_number);
	    change_state(previous_state, state, ZONES);
	    temp_spot.clear();
	  }
	}
	else{
	  //WAYPOINT
	  sprintf(temp_char, "%d.%d.", temp_zone.zone_id, temp_spot.spot_id);
	  if(token.find(temp_char) != std::string::npos ){
	    LL_Waypoint wp(lineread, temp_zone.zone_id,
			   temp_spot.spot_id, line_number, valid, verbose);
	    temp_spot.waypoints.push_back(wp);
	  }
	  else{
	    printf("%d: Unexpected token\n", line_number);
	    valid=false;
	  }
	}
	break;
      case UNKNOWN:
	printf("%d: Unexpected token\n", line_number);
	valid=false;
      }
      if (!valid) {
	is_valid=false;
	print_error_message(line_number, token);
	return;
      }
    }
  prep_graph();
  if (verbose) printf("Parser Finishes\n");
}

MDF::MDF(std::string mdfname, bool verbose)
{
  verbose=verbose;

  is_valid=true;

  if (verbose) printf("MDF Parser Begins\n");

  std::ifstream mdf_file;
  mdf_file.open(mdfname.c_str());
  if (!mdf_file){
    printf("Error in opening MDF file\n");
    is_valid=false;
    return;
  }

  //Parser State
  line_number = 0;
  MDF_PARSE_STATE state = MDF_UNKNOWN, previous_state = MDF_UNKNOWN;

  std::string lineread;
  while(getline(mdf_file, lineread) ) // Read line by line
    {

      line_number++;

      uint real_characters=0;

      for (uint ind=0; ind < lineread.length(); ind++)
	if (lineread[ind] != '\r' &&
	    lineread[ind] != '\t' &&
	    lineread[ind] != ' ')
	  real_characters++;
 

      //Blank lines
      if (real_characters == 0) {
	if (verbose)
	  printf("%d: Blank Line\n",line_number);
	continue;
      }

      std::string token;
      char token_char [lineread.size()+1];
      // char temp_char [lineread.size()+1];

      //Read in one line
      sscanf(lineread.c_str(), "%s", token_char);
      token.assign(token_char);


      if (state != MDF_COMMENT){
	if (token.compare("MDF_name") == 0)
	  change_state(previous_state, state, MDF_GENERAL);
	else if (token.compare(0, 11, "checkpoints") == 0)
	  change_state(previous_state, state, MDF_CHECKPOINTS);
	else if (token.compare(0, 12, "speed_limits") == 0)
	  change_state(previous_state, state, MDF_SPEEDLIMITS);
	else if (token.find("/*") != std::string::npos)
	  change_state(previous_state, state, MDF_COMMENT);
      }

      bool valid=true;
      switch (state){
      case MDF_COMMENT:
	if (verbose)
	  printf("%d: COMMENT: %s\n", line_number, lineread.c_str());
	if (lineread.find("*/") != std::string::npos)
	  state = previous_state;
	break;
      case MDF_GENERAL:
	if (token.compare("MDF_name") == 0)
	  filename =
	    parse_string(lineread, std::string("MDF_name"),
			 line_number, valid, verbose);
	else if (token.compare("RNDF") == 0)
	  RNDF_name =
	    parse_string(lineread, std::string("RNDF"),
			 line_number, valid, verbose);
	else if (token.compare("format_version") == 0)
	  format_version =
	    parse_string(lineread, std::string("format_version"),
			 line_number, valid, verbose);
	else if (token.compare("creation_date") == 0)
	  creation_date =
	    parse_string(lineread, std::string("creation_date"),
			 line_number, valid, verbose);
	else if (token.compare("end_file") == 0){
	  if (!isvalid()){
	    printf("%d: MDF Properties are not valid\n", line_number);	
	    valid = false;
	  }
	  if (verbose)
	    printf("%d: MDF file has finished parsing\n", line_number);
	}
	else{
	  printf("%d: Unexpected token\n", line_number);
	  valid=false;
	}
	break;
      case MDF_SPEEDLIMITS:
	if(token.compare(0, 12, "speed_limits") == 0){
	  if (verbose)
	    printf("%d: Speed Limits\n", line_number);
	}
	else if(token.compare(0, 16, "num_speed_limits") == 0){
	  number_of_speedlimits =
	    parse_integer(lineread, std::string("num_speed_limits"),
			  line_number, valid, verbose);
	  if (number_of_speedlimits <= 0) valid = false;
	}
	else if(token.compare("end_speed_limits") == 0){
	  if (number_of_speedlimits != (int) speed_limits.size())
	    printf("Number of Speed Limits do not match num_speedlimits\n");
	  else if (verbose)
	    printf("%d: End of Speed Limits\n", line_number);
	  change_state(previous_state, state, MDF_GENERAL);
	}
	else{
	  Speed_Limit speedlimit(lineread, line_number, valid, verbose);
	  if (valid) speed_limits.push_back(speedlimit);
	  else {
	    printf("%d: Unexpected token\n", line_number);
	    valid = false;
	  }
	}
	break;
      case MDF_CHECKPOINTS:
	if(token.compare(0, 11, "checkpoints") == 0){
	  if (verbose)
	    printf("%d: Checkpoints\n", line_number);
	}
	else if(token.compare("num_checkpoints") == 0){
	  number_of_checkpoints =
	    parse_integer(lineread, std::string("num_checkpoints"),
			  line_number, valid, verbose);
	  if (number_of_checkpoints <= 0) valid = false;
	}
	else if(token.compare("end_checkpoints") == 0){
	  if (number_of_checkpoints != (int) checkpoint_ids.size())
	    printf("Number of Checkpoints do not match num_checkpoints\n");
	  else if (verbose)
	    printf("%d: Checkpoints have ended\n", line_number);
	  change_state(previous_state, state, MDF_GENERAL);
	}
	//NO TOKEN
	else{
	  //CHECKPOINT
	  int checkpoint_id =
	    parse_integer(lineread, line_number, valid, verbose);
	  if (valid) checkpoint_ids.push_back(checkpoint_id);
	  else {
	    printf("%d: Unexpected token\n", line_number);
	    valid = false;
	  }
	  if (checkpoint_id <= 0) valid = false;	
	}
	break;
      case MDF_UNKNOWN:
	printf("%d: COULD NOT PARSE: %s\n", line_number, lineread.c_str());
	valid = false;
      }
      if (!valid) {
	is_valid=false;
	print_error_message(line_number, token);
	return;
      }
    }

  if (verbose) printf("MDF Parser Finishes\n");

}

Lane_marking RNDF::parse_boundary(std::string line, bool& valid){
  Lane_marking boundary_type = UNDEFINED;
  char temp_char [line.size()+1];
  if (!sscanf(line.c_str(), "%*s %s", temp_char) == 1)
    valid = false;
  if (strcmp(temp_char, "double_yellow") == 0)
    boundary_type = DOUBLE_YELLOW;
  else if (strcmp(temp_char, "solid_yellow") == 0)
    boundary_type = SOLID_YELLOW;
  else if (strcmp(temp_char, "solid_white") == 0)
    boundary_type = SOLID_WHITE;
  else if (strcmp(temp_char, "broken_white") == 0)
    boundary_type = BROKEN_WHITE;
  else
    valid=false;
  return boundary_type;

};

Checkpoint::Checkpoint(std::string line, int x, int y,
		       int line_number, bool& valid, bool verbose) {
  char temp_char [line.size()+1];
  sprintf(temp_char,"checkpoint %d.%d.%%d %%d" ,x, y);
  if (sscanf(line.c_str(), temp_char, &waypoint_id, &checkpoint_id) == 2 &&
      isvalid()){
    if (verbose){ 
      printf("%d: ", line_number);
      print();
    }
  }
  else{
    //    clear();
    valid=false;
  }
};

LL_Waypoint::LL_Waypoint(std::string line, int x, int y,
			 int line_number, bool& valid, bool verbose) {

  char temp_char [line.size()+1];
  sprintf(temp_char, "%d.%d.%%d %%lf %%lf", x, y);
  if(sscanf(line.c_str(), temp_char, &waypoint_id, &ll.latitude, &ll.longitude) == 3 && isvalid()){
    if (verbose) {
      printf("%d: ", line_number);
      print();
    }
  }
  else{
    //    clear();
    valid=false;
  }
};



Exit::Exit(std::string line, int x, int y, int line_number, bool& valid,
	   bool verbose) {

  char temp_char [line.size()+1];
  sprintf(temp_char,"exit %d.%d.%%d %%d.%%d.%%d", x, y);
  start_point.segment_id = x;
  start_point.lane_id = y;
  if (sscanf(line.c_str(), temp_char, &start_point.waypoint_id,
	     &end_point.segment_id, &end_point.lane_id,
	     &end_point.waypoint_id) == 4  && isvalid()){
    if (verbose){
      printf("%d: ", line_number);
      print();
    }
  }
  else{
    //    clear();
    //    start_point.segment_id = x;
    //    start_point.lane_id = y;
    valid=false;
  }
};

Speed_Limit::Speed_Limit(std::string line, int line_number, bool& valid,
			 bool verbose){
  if (sscanf(line.c_str(), "%d %d %d", &id, &min_speed, &max_speed) == 3 && isvalid()){
    if (verbose){
      printf("%d: ", line_number);
      print();
    }
  }
  else{
    //    clear();
    valid=false;
  }
};

Stop::Stop(std::string line, int x, int y,
	   int line_number, bool& valid, bool verbose){
  //  clear()
  char temp_char [line.size()+1];
  sprintf(temp_char,"stop %d.%d.%%d" , x, y);
  if (sscanf(line.c_str(), temp_char, &waypoint_id) == 1 && isvalid()){
    if (verbose)
      printf("%d: Stop at Waypoint %d\n",
	     line_number, waypoint_id);
  }
  else{
    //    clear();
    valid=false;
  }
};


std::string parse_string(std::string line, std::string token,
			 int line_number, bool& valid, bool verbose){
  char temp_char [line.size()+1];
  temp_char[0]='\0';
  if (sscanf(line.c_str(), "%*s %s", temp_char)){
    if (verbose)
      printf("%d: %s is %s\n", line_number, token.c_str(), temp_char);
  }
  else
    valid=false;

  return std::string(temp_char);
};

//WITH STRING TOKEN
int parse_integer(std::string line, std::string token,
		  int line_number, bool& valid, bool verbose){
  int integer = INT_MIN;
  if (sscanf(line.c_str(), "%*s %d", &integer) == 1){
    if (verbose)
      printf("%d: %s is %d\n", line_number, token.c_str(), integer);
  }
  else
    valid=false;

  if (integer == INT_MIN) valid = false;
  return integer;
};

//WITHOUT TOKEN
int parse_integer(std::string line, int line_number, bool& valid,
		  bool verbose){
  int integer = INT_MIN;
  if (sscanf(line.c_str(), "%d", &integer) == 1){
    if (verbose)
      printf("%d: %d\n", line_number, integer);
  }
  else
    valid=false;
  if (integer == INT_MIN) valid = false;
  return integer;
};

void Lane::clear(){
  waypoints.clear();
  checkpoints.clear();
  stops.clear();
  exits.clear();
  left_boundary = right_boundary = UNDEFINED;
  lane_id = number_of_waypoints = INT_MIN;
  lane_width = 0;
};

void Segment::clear(){
  lanes.clear();
  segment_name = std::string("default");
  segment_id = number_of_lanes = INT_MIN;
};

void Zone::clear(){
  zone_id = number_of_parking_spots = INT_MIN;
  zone_name = std::string("default");
  perimeter.clear();
  spots.clear();
};

void Spot::clear(){
  spot_id = INT_MIN;
  spot_width = 0;
  checkpoint.clear();
  waypoints.clear();
};

void Perimeter::clear(){
  perimeter_id = number_of_perimeterpoints = INT_MIN;
  exits_from_perimeter.clear();
  perimeterpoints.clear();

};

void RNDF::print(){

  if (!is_valid) {
    printf("RNDF not valid\n");
    return;
  }

  printf("RNDF name is %s\n", filename.c_str());
  printf("Number of segments is %d\n", number_of_segments);
  printf("Number of zones is %d\n", number_of_zones);
  printf("format version is %s\n", format_version.c_str());
  printf("creation date is %s\n", creation_date.c_str());
  print_vector(segments);
  print_vector(zones);
};

void MDF::print(){

  if (!is_valid) {
    printf("MDF not valid\n");
    return;
  }

  printf("MDF name is %s\n", filename.c_str());
  printf("RNDF name is %s\n", RNDF_name.c_str());
  printf("format version is %s\n", format_version.c_str());
  printf("creation date is %s\n", creation_date.c_str());
  printf("Number of checkpoints is %d\n", number_of_checkpoints);
  std::vector<int>::iterator i;
  for(i = checkpoint_ids.begin(); i != checkpoint_ids.end(); i++)
    printf("Checkpoint id: %d\n", *i);

  printf("Number of speedlimits is %d\n", number_of_speedlimits);
  print_vector(speed_limits);
};

void Segment::print(){

  printf("Segment number is %d\n", segment_id);
  printf("Number of Lanes in Segment %d\n", number_of_lanes);
  printf("segment name is %s\n", segment_name.c_str());
  print_vector(lanes);
};

void Lane::print(){

  printf("Lane number is %d\n", lane_id);
  printf("Number of Waypoints in lane %d\n", number_of_waypoints);
  printf("Width of lane %d\n", lane_width);
  printf("left boundary type is %d\n", left_boundary);
  printf("right boundary type is %d\n", right_boundary);
  print_vector(checkpoints);
  print_vector(stops);
  print_vector(exits);
  print_vector(waypoints);
};

void Exit::print(){

  printf("Exit from ");
  start_point.print();

  printf(" to ");
  end_point.print();

  printf("\n");
};

void Spot::print(){

  printf("Spot id is %d\n", spot_id);
  printf("Spot width is %d\n", spot_width);
  printf("Spot Checkpoint is: ");
  checkpoint.print();
  printf("Spot - First waypoint: ");
  waypoints[0].print_without_newline();
  printf(",Second waypoint: ");
  waypoints[1].print_without_newline();
  printf("\n");
};

void Zone::print(){

  printf("Zone number is %d\n", zone_id);
  printf("Number of parking spots is %d\n",
	 number_of_parking_spots); //integer >= 0
  printf("Zone name is %s\n", zone_name.c_str()); //Designate the
  //zone, such as
  //"North_Parking_Lot"
  perimeter.print();
  print_vector(spots);
};

void Perimeter::print(){

  printf("Perimeter id is %d\n", perimeter_id); //integer ALWAYS 0

  printf("Number of perimeter points is %d\n", number_of_perimeterpoints);
  print_vector(exits_from_perimeter);
  print_vector(perimeterpoints);
};

void Speed_Limit::print(){

  printf("Speed Limit id: %d", id); //integer > 0
  printf(", min_speed is %d", min_speed); //integer >= 0
  printf(", max_speed is %d\n", max_speed); //integer >= 0
}

template <class T>
void print_vector (std::vector<T> vec) {
  typename std::vector<T>::iterator i;
  for(i = vec.begin(); i != vec.end(); i++)
    i->print();
};


void RNDF::prep_graph(){

  int index = 0;
  std::vector<Segment>::iterator si;
  std::vector<Lane>::iterator li;
  std::vector<LL_Waypoint>::iterator wi;
  std::vector<Checkpoint>::iterator ci;
  std::vector<Stop>::iterator stops_i;
  std::vector<Exit>::iterator exits_i;
  std::vector<Zone>::iterator zones_i;
  std::vector<Spot>::iterator spots_i;
  std::vector<Perimeter_Point>::iterator peri_i;
  std::vector<WayPointNode>::iterator wpni;
  std::vector<ElementID>::iterator eid_i;

  //-----VERTICES-------
  for(si = segments.begin(); si != segments.end(); si++){
    for(li = si->lanes.begin(); li != si->lanes.end(); li++){
      for(wi = li->waypoints.begin(); wi != li->waypoints.end(); wi++){
	WayPointNode wpn;
	wpn.ll = wi->ll;
	if (li->lane_width == 0)
	  wpn.lane_width = DEFAULT_LANE_WIDTH;
	else wpn.lane_width = feet2meters(li->lane_width);
	wpn.id = ElementID(si->segment_id, li->lane_id, wi->waypoint_id);
	wpn.index = index;
	index++;
	id_map[wpn.id] = (wpn);
      }
    }
  }
  
  //Goal waypoints, no orientation required
  for(zones_i = zones.begin(); zones_i != zones.end(); zones_i++){
    for(spots_i = zones_i->spots.begin();
	spots_i != zones_i->spots.end(); spots_i++){
      for(wi = spots_i->waypoints.begin();
	  wi != spots_i->waypoints.end(); wi++){
	WayPointNode wpn;
	wpn.ll = wi->ll;
	wpn.id = ElementID(zones_i->zone_id, spots_i->spot_id,
			   wi->waypoint_id);
	if (spots_i->checkpoint.waypoint_id == wi->waypoint_id){
	  wpn.is_goal = true;
	  wpn.checkpoint_id = spots_i->checkpoint.checkpoint_id;
	}
	else wpn.is_goal = false;
	wpn.is_spot = true;
	if (spots_i->spot_width == 0)
	  wpn.lane_width = DEFAULT_SPOT_WIDTH;
	else wpn.lane_width = feet2meters(spots_i->spot_width);
	wpn.is_stop = wpn.is_exit = wpn.is_entry = false;
	wpn.index = index;
	index++;
	id_map[wpn.id] = (wpn);
      }
    }
  }
  
  //Perimeter waypoints, no orientation required
  for(zones_i = zones.begin(); zones_i != zones.end(); zones_i++){
    for(peri_i = zones_i->perimeter.perimeterpoints.begin();
	peri_i != zones_i->perimeter.perimeterpoints.end(); peri_i++){
      WayPointNode wpn;
      wpn.ll = peri_i->ll;
      wpn.id = ElementID(zones_i->zone_id, zones_i->perimeter.perimeter_id,
			 peri_i->waypoint_id);
      wpn.is_perimeter = true;
      wpn.lane_width = DEFAULT_LANE_WIDTH;
      wpn.is_stop = wpn.is_exit = wpn.is_entry = false;
      wpn.index = index;
      index++;
      id_map[wpn.id] = (wpn);
    }
  }

  //Entry and exit waypoints, no orientation required
  for(zones_i = zones.begin(); zones_i != zones.end(); zones_i++){
    for(exits_i = zones_i->perimeter.exits_from_perimeter.begin();
	exits_i != zones_i->perimeter.exits_from_perimeter.end(); exits_i++){
      ElementID id_start (exits_i->start_point.segment_id,
			  exits_i->start_point.lane_id,
			  exits_i->start_point.waypoint_id);
      ElementID id_end (exits_i->end_point.segment_id,
			exits_i->end_point.lane_id,
			exits_i->end_point.waypoint_id);
      if (id_map.find(id_start) == id_map.end() ||
	  id_map.find(id_end) == id_map.end()) {
	exit_error(*exits_i);
	is_valid=false;
	return;
      }
      id_map[id_start].is_exit = true;
      id_map[id_end].is_entry = true;
    }
  }

  for(si = segments.begin(); si != segments.end(); si++){
    for(li = si->lanes.begin(); li != si->lanes.end(); li++){
      for(ci = li->checkpoints.begin(); ci != li->checkpoints.end(); ci++){
	ElementID id (si->segment_id, li->lane_id, ci->waypoint_id);
	if (id_map.find(id) == id_map.end()) {
	  checkpoint_error(si->segment_id, li->lane_id, ci->waypoint_id);
	  is_valid=false;
	  return;
	}
	id_map[id].checkpoint_id = ci->checkpoint_id;
	id_map[id].is_goal = false;
      }
      for(stops_i = li->stops.begin(); stops_i != li->stops.end(); stops_i++){
	ElementID id (si->segment_id, li->lane_id, stops_i->waypoint_id);
	if (id_map.find(id) == id_map.end()) {
	  stop_error(si->segment_id, li->lane_id, stops_i->waypoint_id);
	  is_valid=false;
	  return;
	}
	id_map[id].is_stop = true;
      }
      for(exits_i = li->exits.begin(); exits_i != li->exits.end(); exits_i++){
	ElementID id_start (exits_i->start_point.segment_id,
			    exits_i->start_point.lane_id,
			    exits_i->start_point.waypoint_id);
	ElementID id_end (exits_i->end_point.segment_id,
			  exits_i->end_point.lane_id,
			  exits_i->end_point.waypoint_id);
	if (id_map.find(id_start) == id_map.end() || id_map.find(id_end) ==
	    id_map.end()) {
	  exit_error(*exits_i);
	  is_valid=false;
	  return;
	}
	id_map[id_start].is_exit = true;
	id_map[id_end].is_entry = true;
      }
    }
  }

  //-----EDGES-------
  //-----LANES
  for(si = segments.begin(); si != segments.end(); si++){
    for(li = si->lanes.begin(); li != si->lanes.end(); li++){
      for(wi = li->waypoints.begin(); wi != li->waypoints.end() -1; wi++){
	ElementID id_start (si->segment_id, li->lane_id, wi->waypoint_id);
	ElementID id_end (si->segment_id, li->lane_id, (wi+1)->waypoint_id);
	if (id_map.find(id_start) == id_map.end() ||
	    id_map.find(id_end) == id_map.end()) {
	  exit_error(*exits_i);
	  is_valid=false;
	  return;
	}
	edges.push_back( WayPointEdge(id_map[id_start], id_map[id_end],
				      li->left_boundary,
				      li->right_boundary, false));
      }
    }
  }
  //-----EXITS
  for(si = segments.begin(); si != segments.end(); si++){
    for(li = si->lanes.begin(); li != si->lanes.end(); li++){
      for(exits_i = li->exits.begin(); exits_i != li->exits.end(); exits_i++){
	ElementID id_start (exits_i->start_point.segment_id,
			    exits_i->start_point.lane_id,
			    exits_i->start_point.waypoint_id);
	ElementID id_end (exits_i->end_point.segment_id,
			  exits_i->end_point.lane_id,
			  exits_i->end_point.waypoint_id);
	if (id_map.find(id_start) == id_map.end() ||
	    id_map.find(id_end) == id_map.end()) {
	  exit_error(*exits_i);
	  is_valid=false;
	  return;
	}
	if (id_start.seg==id_end.seg &&
	    id_start.lane==id_end.lane &&
	    id_start.pt+1==id_end.pt)
	  for (uint i=0; i<edges.size(); i++)
	    {
	      if (edges.at(i).startnode_index==id_map[id_start].index &&
		  edges.at(i).endnode_index==id_map[id_end].index)
		{
		  edges.at(i).is_exit=true;
		  break;
		}
	    }
	else
	  edges.push_back(WayPointEdge(id_map[id_start], id_map[id_end],
				       li->left_boundary,
				       li->right_boundary, true));
      }
    }
  }
  
  //-----ZONES
  std::vector<ElementID> zone_exits;
  for(zones_i = zones.begin(); zones_i != zones.end(); zones_i++){
    for(exits_i = zones_i->perimeter.exits_from_perimeter.begin();
	exits_i != zones_i->perimeter.exits_from_perimeter.end(); exits_i++){
      ElementID id_start (exits_i->start_point.segment_id,
			  exits_i->start_point.lane_id,
			  exits_i->start_point.waypoint_id);
      ElementID id_end (exits_i->end_point.segment_id,
			exits_i->end_point.lane_id,
			exits_i->end_point.waypoint_id);
      if (id_map.find(id_start) == id_map.end() ||
	  id_map.find(id_end) == id_map.end()) {
	exit_error(*exits_i);
	is_valid=false;
	return;
      }
      edges.push_back( WayPointEdge(id_map[id_start], id_map[id_end],
				    UNDEFINED, UNDEFINED, true));
      zone_exits.push_back(id_map[id_start].id);
    }
  }
  
  
  //HANDLING EDGES FROM ZONE START TO ZONE END
  id_to_waypoint_map::iterator node_itr, node_itr2;
  for(node_itr = id_map.begin(); node_itr != id_map.end(); node_itr++){
    //If the node is an entry
    if (node_itr->second.is_entry && node_itr->second.is_perimeter) {
      for(node_itr2 = id_map.begin(); node_itr2 != id_map.end(); node_itr2++){
	if (node_itr2->second.id!=node_itr->second.id && node_itr2->second.is_perimeter &&
	    node_itr2->second.is_exit)
	  //Check if they are in the same zone
	  if(node_itr2->second.id.seg == node_itr->second.id.seg &&
	     node_itr2->second.id.pt != node_itr->second.id.pt) {
	    edges.push_back(WayPointEdge(node_itr->second, node_itr2->second,
					 UNDEFINED, UNDEFINED, false));
	  }
      }
    }
  }
  for(node_itr = id_map.begin(); node_itr != id_map.end(); node_itr++){
    if (node_itr->second.is_exit || node_itr->second.is_entry)
      for(node_itr2 = id_map.begin(); node_itr2 != id_map.end(); node_itr2++){
	if (node_itr2->second.id != node_itr->second.id)
	  if (node_itr2->second.is_spot)
	    if ((node_itr->second.id.seg == 
		 node_itr2->second.id.seg) &&
		(node_itr2->second.id.pt==1))
	      {
		if (node_itr->second.is_exit)
		  edges.push_back( WayPointEdge(node_itr2->second, node_itr->second,
						UNDEFINED, UNDEFINED, false));
		if (node_itr->second.is_entry)
		  edges.push_back
		    (WayPointEdge(node_itr->second, node_itr2->second,
				  UNDEFINED, UNDEFINED, false));
	      }
      } 
  }
  
  for(node_itr = id_map.begin(); node_itr != id_map.end(); node_itr++){
    //If the node is an entry
    if (node_itr->second.is_spot)
      for(node_itr2 = id_map.begin(); node_itr2 != id_map.end(); node_itr2++){
	if (node_itr2->second.id != node_itr->second.id)
	  if (node_itr2->second.is_spot) {
	    if ((node_itr->second.id.seg==
		 node_itr2->second.id.seg) &&
		(node_itr->second.id.lane==
		 node_itr2->second.id.lane) &&
		(node_itr->second.id.pt==1) &&
		(node_itr2->second.id.pt==2))
	      {
		edges.push_back( WayPointEdge(node_itr->second, node_itr2->second,
					      UNDEFINED, UNDEFINED, false));
		edges.push_back( WayPointEdge(node_itr2->second, node_itr->second,
					      UNDEFINED, UNDEFINED, false));
	      }
	    if ((node_itr->second.id.seg==
		 node_itr2->second.id.seg) &&
		(node_itr->second.id.lane!=
		 node_itr2->second.id.lane) &&
		(node_itr->second.id.pt==1) &&
		(node_itr2->second.id.pt==1))
	      {
		edges.push_back( WayPointEdge(node_itr->second, node_itr2->second,
					      UNDEFINED, UNDEFINED, false));
		edges.push_back( WayPointEdge(node_itr2->second, node_itr->second,
					      UNDEFINED, UNDEFINED, false));
	      }
	  }
      }
  }
}

/** Populate graph from RNDF parser data.
 *
 * Copies all nodes from the way-point map to an array in the
 * graph. Includes edges via a pointer copy.
 */
void RNDF::populate_graph(Graph& graph)
{
  graph.nodes_size = id_map.size();
  graph.nodes = new WayPointNode[graph.nodes_size];
  id_to_waypoint_map::iterator node_itr;
  for(node_itr = id_map.begin(); node_itr != id_map.end(); node_itr++){
    graph.nodes[(node_itr->second).index] = (node_itr->second);
  }

  graph.edges_size = edges.size();
  graph.edges = edges;
  /*
    std::vector<WayPointEdge>::iterator edge_itr;
  int edge_index = 0;
  for(edge_itr = edges.begin(); edge_itr != edges.end(); edge_itr++){
    graph.edges[edge_index] = (*edge_itr);
    edge_index++;
  }
  */
}


//ISSUE: What should the SpeedLimits of Exits be
bool MDF::add_speed_limits(Graph& graph){
  std::vector<Speed_Limit>::iterator itr;
  int num_speed_limits = (int)speed_limits.size();
  int matches = 0;
  Speed_Limit matched, current;

  for (uint i = 0; i < graph.edges_size; i++){
    graph.edges[i].speed_min = 0.0;
    graph.edges[i].speed_max = DEFAULT_LANE_SPEED;
  }
  
  for(itr = speed_limits.begin(); itr != speed_limits.end(); itr++){
    current = *itr;
    for (uint i = 0; i < graph.edges_size; i++){
      int index = graph.edges[i].startnode_index;
      //      assert(index < graph.nodes_size);

      if(graph.nodes[index].id.seg == itr->id){
	if (itr->min_speed < Epsilon::speed)
	  graph.edges[i].speed_min = 0.0;
	else
	  graph.edges[i].speed_min = mph2mps(itr->min_speed);

	if (itr->max_speed < Epsilon::speed)
	  graph.edges[i].speed_max = fmax(graph.edges[i].speed_min,
					  DEFAULT_LANE_SPEED);
	else
	  graph.edges[i].speed_max = fmax(graph.edges[i].speed_min,
					  mph2mps(itr->max_speed));
	
	if (!(matched == current)){
	  matches++;
	  matched = current;
	}
      }
    }
  }

#if 0
  for (uint i = 0; i < graph.edges_size; i++){
    std::cerr << graph.nodes[graph.edges[i].startnode_index].id.seg
	      <<" "<<graph.edges[i].speed_min<<" "
	      <<graph.edges[i].speed_max<<std::endl;
  }
#endif

  if (matches == num_speed_limits)
    return true;
  else{
    //printf("[%d] != [%d]\n", matches, num_speed_limits);
    return false;
  }
}

void exit_error(Exit& ex){

  printf("ERROR: In Exit from %d.%d.%d to %d.%d.%d.",
	 ex.start_point.segment_id, ex.start_point.lane_id,
	 ex.start_point.waypoint_id,
	 ex.end_point.segment_id, ex.end_point.lane_id,
	 ex.end_point.waypoint_id);
  printf("  One of the WayPoints is not defined.\n");
}

void stop_error(int seg, int lane, int way){

  printf("ERROR: In Stop %d.%d.%d - The WayPoint is not defined\n",
	 seg, lane, way);
}

void checkpoint_error(int seg, int lane, int way){

  printf("ERROR: In Checkpoint %d.%d.%d - The WayPoint is not defined\n",
	 seg, lane, way);
}

void print_error_message(int line_number, std::string token){
  printf("%d: Invalid %s\n", line_number, token.c_str());
}

