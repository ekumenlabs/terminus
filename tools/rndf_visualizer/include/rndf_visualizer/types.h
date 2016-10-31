/* -*- mode: C++ -*- */
/*
 *  Description:  global ART type definitions
 *
 *  Copyright (C) 2009 Austin Robot Technology                    
 *
 *  License: Modified BSD Software License Agreement
 *
 *  $Id: 6f6ba58e3f7fa505a22b3cc96274938018fcd054 $
 */

#ifndef _TYPES_HH_
#define _TYPES_HH_

/** @file
    
    @brief global ART vehicle type definitions
 */

 #include <stdint.h>
#include <stdio.h>
#include <epsilon.h>
#include <rndf_visualizer/coordinates.h>

/** @brief global ART types definitions. */

#define WAYPT_NAME_SIZE 20
typedef struct {char str[WAYPT_NAME_SIZE];} waypt_name_t;

// some fixed-size types passed in messages
typedef int32_t poly_id_t;		//< polygon ID
typedef int16_t segment_id_t;		//< RNDF segment ID
typedef int16_t lane_id_t;		//< RNDF lane ID
typedef int16_t point_id_t;		//< RNDF way-point ID
typedef uint16_t waypt_index_t;		//< parser way-point index

enum Lane_marking
  {DOUBLE_YELLOW, SOLID_YELLOW, SOLID_WHITE, BROKEN_WHITE, UNDEFINED};

/** RNDF element identifier for segments, lanes and way-points */
class ElementID
{
public:
  segment_id_t seg;
  lane_id_t lane;
  point_id_t pt;

  // constructors
  ElementID()
  {
    seg = lane = pt = -1;
  };
  ElementID(segment_id_t _seg, lane_id_t _lane, point_id_t _pt)
  {
    seg = _seg;
    lane = _lane;
    pt = _pt;
  };

  /** Convert ElementID to MapID message. */
  waypt_name_t lane_name(void) const
  {
    waypt_name_t lanename;
    snprintf(lanename.str, sizeof(lanename.str), "%d.%d", seg, lane);
    return lanename;
  };

  waypt_name_t name(void) const
  {
    waypt_name_t wayname;
    snprintf(wayname.str, sizeof(wayname.str), "%d.%d.%d", seg, lane, pt);
    return wayname;
  };

  bool operator==(const ElementID &that) const
  {
    return (this->seg == that.seg
	    && this->lane == that.lane
	    && this->pt == that.pt);
  }

  bool operator!=(const ElementID &that) const
  {
    return (this->seg != that.seg
	    || this->lane != that.lane
	    || this->pt != that.pt);
  }

  bool operator<(const ElementID &that) const
  {
    if (this->seg != that.seg)
      return this->seg < that.seg;
    else if (this->lane != that.lane)
      return this->lane < that.lane;
    else return this->pt < that.pt;
  }

  bool operator>(const ElementID &that) const
  {
    if (this->seg != that.seg)
      return this->seg > that.seg;
    else if (this->lane != that.lane)
      return this->lane > that.lane;
    else return this->pt > that.pt;
  }
  bool valid() const
  {
    return (seg >= 0 && lane >= 0 && pt >= 0);
  }
  bool same_lane(segment_id_t segid, lane_id_t laneid) const
  {
    return (seg == segid && lane == laneid);
  };

  bool same_lane(ElementID wayid) const
  {
    return (seg == wayid.seg && lane == wayid.lane);
  };

  waypt_name_t seg_name(void) const
  {
    waypt_name_t segname;
    snprintf(segname.str, sizeof(segname.str), "%d", seg);
    return segname;
  };
};

typedef ElementID LaneID;

class WayPointNode			//< way-point graph node
{
public:
  LatLong ll;				//< latitude and longitude
  MapXY map;				//< MapXY position
  ElementID id;				//< way-point ID
  waypt_index_t index;			//< parser index of waypoint

  // way-point flags
  bool is_entry;			//< lane or zone exit point
  bool is_exit;				//< lane or zone entry point
  bool is_goal;				//< this is a goal checkpoint
  bool is_lane_change;			//< change lanes after here
  bool is_spot;				//< parking spot
  bool is_stop;				//< stop line here
  bool is_perimeter;			//< zone perimeter point
  int checkpoint_id;			//< checkpoint ID or zero
  float lane_width;
  
  // constructors
  WayPointNode(){ clear();};
  WayPointNode(const MapXY &point) : map(point) { clear();};

  // public methods
  void clear()
  {
    is_entry = is_exit = is_goal = is_spot = is_stop = false;
    is_perimeter = is_lane_change = false;
    checkpoint_id = index = 0;
    lane_width=0;
    id = ElementID();
  };

  bool operator<(const WayPointNode &that)
  {
    return (this->id < that.id);
  };

  bool operator==(const WayPointNode &that)
  {
    return (this->ll == that.ll &&
            this->map == that.map &&
            this->id == that.id &&
            this->index == that.index &&
            this->lane_width == that.lane_width &&
            this->is_entry == that.is_entry &&
            this->is_exit == that.is_exit &&
            this->is_goal == that.is_goal &&
            this->is_spot == that.is_spot &&
            this->is_perimeter == that.is_perimeter &&
            this->checkpoint_id == that.checkpoint_id);
  };
  
};

class WayPointEdge			//< graph edge
{
public:
  waypt_index_t startnode_index;
  waypt_index_t endnode_index;
  float distance;
  float speed_max;
  float speed_min;
	
  bool is_exit;
  bool blocked;
  bool is_implicit;

  Lane_marking	left_boundary;
  Lane_marking	right_boundary;
		
  //constructor
  WayPointEdge() { clear(); };
  WayPointEdge(WayPointNode& node1, WayPointNode& node2,  
	       Lane_marking lb, Lane_marking rb, bool _is_exit)
  {
    startnode_index = node1.index;
    endnode_index = node2.index;
    left_boundary = lb;
    right_boundary = rb;
    is_exit = _is_exit;
    distance = -1.0;
    blocked = false;
    speed_max = speed_min = 0;
    is_implicit=false;
  };
  bool operator==(const WayPointEdge &that)
  {
  	return (this->startnode_index == that.startnode_index &&
		this->endnode_index == that.endnode_index &&
		this->distance == that.distance &&
		Epsilon::equal(this->speed_max,that.speed_max) &&
		Epsilon::equal(this->speed_min,that.speed_min) &&
		this->is_exit == that.is_exit &&
		this->left_boundary == that.left_boundary &&
		this->right_boundary == that.right_boundary
		);
  };
  void clear(){
    blocked = false;
    startnode_index = 0;
    endnode_index = 0;
    distance  = -1.0;		
    speed_max = speed_min = 0;
    is_exit = false;
    left_boundary = right_boundary = UNDEFINED;	  
    is_implicit=false;
  };

  WayPointEdge reverse() {
    WayPointEdge reverse(*this);

    reverse.startnode_index = endnode_index;
    reverse.endnode_index = startnode_index;
    reverse.left_boundary = right_boundary;
    reverse.right_boundary = left_boundary;
    
    return reverse;
  };
};

#endif // _TYPES_HH_ //
