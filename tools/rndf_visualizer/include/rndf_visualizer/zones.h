/* -*- mode: C++ -*- */
/*
 *  Copyright (C) 2007, 2010 David Li, Patrick Beeson, Jack O'Quin
 *
 *  License: Modified BSD Software License Agreement
 * 
 *  $Id: 2975b8c1a2be758dca10d50876975c4bb16315ea $
 */

/**  \file
 
     C++ interface for Road Network Definition File zones.

     \author David Li, Patrick Beeson, Jack O'Quin

 */

#ifndef __ZONES_H__
#define __ZONES_H__

#define PLAYER_OPAQUE_MAX_SIZE            1048576

#include <vector>

#include <rndf_visualizer/coordinates.h>
#include <rndf_visualizer/types.h>

#define DEFAULT_ZONE_SPEED 3.0f


typedef std::vector<MapXY> ObstacleList;

// MGR: Currently, these two have to be typedefs of the same thing
typedef WayPointNode PerimeterPoint;
typedef WayPointNode zone_pp_type;

typedef std::vector<PerimeterPoint> PerimeterPointList;

// This class is not called Zone to avoid confusion with the RNDF Zone
// class, which has more information
class ZonePerimeter 
{
public:
  ZonePerimeter():
    speed_limit(0.0),
    zone_id(-1)
  {}
  float speed_limit;
  segment_id_t zone_id;
  PerimeterPointList perimeter_points;
};

typedef std::vector<ZonePerimeter> ZonePerimeterList;

typedef struct zone_pp_count {
  segment_id_t zone_id;
  uint32_t perimeter_points_count;
} zone_pp_count_t;

#if 0

// MGR: How do we pick this value?
#define MAX_ZONE_COUNT 100

#define MAX_TOTAL_PERIMETER_POINTS (PLAYER_OPAQUE_MAX_SIZE - \
			   sizeof(art_message_header_t) - \
			   sizeof(uint32_t) - \
			   sizeof(uint32_t) - \
				 (MAX_ZONE_COUNT * sizeof(zone_pp_count_t)) \
         ) / sizeof(zone_pp_type)

typedef struct zones_msg {
  uint32_t zone_count;
  uint32_t total_perimeter_points;
  zone_pp_count_t zones[MAX_ZONE_COUNT];
  zone_pp_type perimeter_points[MAX_TOTAL_PERIMETER_POINTS];
} zones_msg_t;

#endif

#endif /* __ZONES_H__ */
