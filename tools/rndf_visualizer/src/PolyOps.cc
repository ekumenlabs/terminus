/*
 *  Copyright (C) 2007, 2010 David Li, Patrick Beeson, Bartley Gillen,
 *                           Jack O'Quin
 *
 *  License: Modified BSD Software License Agreement
 * 
 *  $Id: f1795bb2ea1709cfb8af3e81ea10e011d7b089fb $
 */

/**  @file
 
     C++ class for MapLanes polygon operations.

     @todo Rewrite this mess. PolyOps need not be a class.

     @author David Li, Patrick Beeson, Bartley Gillen, Jack O'Quin

 */
#include <float.h>
#include <assert.h>
#include <limits>
#include <iostream>

#include <epsilon.h>

#include <rndf_visualizer/coordinates.h>
#include <rndf_visualizer/PolyOps.h>
#include <rndf_visualizer/euclidean_distance.h>

// for turning on extremely verbose driver logging:
//#define EXTREME_DEBUG 1

PolyOps::PolyOps()
{
  //constructor
}

PolyOps::~PolyOps()
{
  //destructor
}


bool PolyOps::pointInPoly_ratio(float x, float y, const poly& p, float ratio)
{
  
  // this is an unrolled version of the standard point-in-polygon algorithm

  float diff=(1-ratio)/2;

  MapXY p1=p.p1;
  MapXY p2=p.p2;
  MapXY p3=p.p3;
  MapXY p4=p.p4;

  poly newpoly;
	
  newpoly.p1.x=p1.x+(p4.x-p1.x)*diff;
  newpoly.p4.x=p1.x+(p4.x-p1.x)*(1-diff);
  newpoly.p1.y=p1.y+(p4.y-p1.y)*diff;
  newpoly.p4.y=p1.y+(p4.y-p1.y)*(1-diff);	

  newpoly.p2.x=p2.x+(p3.x-p2.x)*diff;
  newpoly.p3.x=p2.x+(p3.x-p2.x)*(1-diff);
  newpoly.p2.y=p2.y+(p3.y-p2.y)*diff;
  newpoly.p3.y=p2.y+(p3.y-p2.y)*(1-diff);	
	
  bool value=pointInPoly(x,y,newpoly);

#if 0
  if (value) {
    printf("Point in small poly: original poly: [%f,%f; %f,%f;%f,%f;%f,%f]"
              "   new poly: [%f,%f; %f,%f;%f,%f;%f,%f]   point: [%f,%f]",
              p.x1,p.y1,p.x2,p.y2,p.x3,p.y3,p.x4,p.y4,
              newpoly.x1,newpoly.y1,newpoly.x2,newpoly.y2,
              newpoly.x3,newpoly.y3,newpoly.x4,newpoly.y4,x,y);
  }
#endif

  return value;

}

// return index of polygon containing location (x, y)
int PolyOps::getContainingPoly(const std::vector<poly> &polys,
			       float x, float y)
{
  //assert(polys.size() > 0);
  int pindex;
  pindex= getClosestPoly(polys, x, y);
  
  if (pindex < 0)
    {
      printf("no polygon contains point (%.3f, %.3f)", x, y);
      return -1;			// no match
    }

  poly closest=polys.at(pindex);

  // make sure the polygon (nearly) contains this way-point
  if (getShortestDistToPoly(x, y, closest) < Epsilon::distance)
    {
      return pindex;
    }

  printf("no polygon contains point (%.3f, %.3f)", x, y);
  return -1;			// no match
}

/*
  int PolyOps::getContainingPoly(const std::vector<poly>& polys, 
  float x, float y)
  {

  poly p;

  for (int i = 0; (unsigned)i < polys.size(); i++)
  {
  p = polys.at(i);
  if (pointInPoly(x, y, p))
  return i;
  }
	
  return -1;
  }
*/

// if the point lies within the given polygon, the returned distance
// is 0 otherwise, the shortest distance to any edge/vertex of the
// given polygon is returned
float PolyOps::getShortestDistToPoly(float x, float y, const poly& p)
{
  float dist = 0;
  float d;

  // first check if point lies inside polygon - if so, return 0
  if (pointInPoly(x, y, p))
    return dist;

  // return minimum of distance to all vertices and of distance to
  // projections that fall on edges
	
  dist = shortestDistToLineSegment(x, y, p.p1.x, p.p1.y, p.p2.x, p.p2.y);

  if ( (d = shortestDistToLineSegment(x, y, p.p2.x, p.p2.y, p.p3.x, p.p3.y)) 
       < dist)
    dist = d;
	
  if ( (d = shortestDistToLineSegment(x, y, p.p3.x, p.p3.y, p.p4.x, p.p4.y)) 
       < dist)
    dist = d;

  if ( (d = shortestDistToLineSegment(x, y, p.p4.x, p.p4.y, p.p1.x, p.p1.y)) 
       < dist)
    dist = d;
	
  return dist;
}

// if the point lies within a polygon, that polygon is returned.
// otherwise, the nearest polygon from the list is returned index of
// winning poly within list is stored in index
int PolyOps::getClosestPoly(const std::vector<poly>& polys, float x, 
			    float y)
{
  poly p;
  float d;
  int index = -1;

  float min_dist = std::numeric_limits<float>::max();

  for (int i = 0; (unsigned)i < polys.size(); i++)
    {
      p = polys.at(i);
      d = getShortestDistToPoly(x, y, p);

      if (Epsilon::equal(d,0)) // point is inside polygon
	{
	  index = i;
	  return index;
	}

      if (i == 0) // initialize the min values
	{
	  min_dist = d;
	  index = 0;
	}
		
      if (d < min_dist) // new minimum
	{
	  min_dist = d;
	  index = i;
	}
    }

  return index;
}

// if the point lies within a non-transtion polygon, that polygon is returned.
// otherwise, the nearest non-transition polygon from the list is returned.
// index of winning non-transition poly within list is stored in index.
int PolyOps::getClosestNonTransPoly(const std::vector<poly>& polys, float x, 
			    float y)
{
  poly p;
  float d;
  int index = -1;

  float min_dist = std::numeric_limits<float>::max();

  for (int i = 0; (unsigned)i < polys.size(); i++)
    {
      p = polys.at(i);
      if (p.is_transition)
        continue;
      d = getShortestDistToPoly(x, y, p);

      if (Epsilon::equal(d,0)) // point is inside polygon
	{
	  index = i;
	  return index;
	}

      if (i == 0) // initialize the min values
	{
	  min_dist = d;
	  index = 0;
	}
		
      if (d < min_dist) // new minimum
	{
	  min_dist = d;
	  index = i;
	}
    }

  return index;
}

#if 0 //TODO
// Returns index of closest polygon if within given epsilon, -1 otherwise
int PolyOps::getClosestPolyEpsilon(const std::vector<poly>& polys,
                const player_pose2d_t& pose, const float epsilon)
{
    int index = getClosestPoly(polys, pose);
    if (index < 0)
      return -1;
    if (pointNearPoly(pose, polys.at(index), epsilon))
      return index;
    else
      return -1;
}

// Returns index of closest non-transition polygon if within given epsilon,
// -1 otherwise.
int PolyOps::getClosestNonTransPolyEpsilon(const std::vector<poly>& polys,
                const player_pose2d_t& pose, const float epsilon) 
{
    int index = getClosestNonTransPoly(polys, pose);
    if (index < 0)
      return -1;
    if (pointNearPoly(pose, polys.at(index), epsilon))
      return index;
    else
      return -1;
}
#endif

MapXY PolyOps::getPolyEdgeMidpoint(const poly& p)
{
  MapXY r;
  r.x = (p.p2.x + p.p3.x)/2;
  r.y = (p.p2.y + p.p3.y)/2;
  return r;
}

MapXY PolyOps::centerpoint(const poly& p)
{
  return midpoint(midpoint(p.p1, p.p3) , midpoint(p.p2, p.p4));
}

float PolyOps::getLength(const poly& p)
{
  MapXY back=midpoint(p.p1, p.p4);
  MapXY front=midpoint(p.p2, p.p3);
  float d1 = distance(back.x,back.y,p.midpoint.x,p.midpoint.y);
  float d2 = distance(front.x,front.y,p.midpoint.x,p.midpoint.y);
  return d1+d2;
}

std::vector<poly> 
PolyOps::getPolysBetweenPoints(const std::vector<poly>& polys,
			       float x1, float y1, 
			       float x2, float y2)
{
  std::vector<poly> retPolys;
  bool foundFirstPoint = false;

  /*	
	for (int i = 0; (unsigned)i < polys.size(); i++)
	{
	if(!foundFirstPoint)
	{
	if(pointInPoly(x1, y1, polys.at(i)))
	foundFirstPoint = true;
	}
	else
	{
	if(pointInPoly(x2, y2, polys.at(i)))
	break;
				
	retPolys.push_back(polys.at(i));
	}
	}
  */

  // find polygon corresponding to first point
  int i;
  for (i = 0; (unsigned)i < polys.size(); i++)
    {
      if(pointInPoly(x1, y1, polys.at(i)))
	{
	  foundFirstPoint = true;
	  break;
	}
    }
	
  if (!foundFirstPoint) // first point not in poly - find nearest poly
    {	
      poly p;
      i= getClosestPoly(polys, x1, y1);
      if (i<0)
	return retPolys;
      p=polys.at(i);
    }

  for ( ; (unsigned)i < polys.size(); i++)
    {
      if(pointInPoly(x2, y2, polys.at(i)))
	break;
				
      retPolys.push_back(polys.at(i));
    }
	
  return retPolys;
}

// copy from_polys polygons to to_polygons after nearest to point
void PolyOps::getRemainingPolys(const std::vector<poly> &from_polys,
				std::vector<poly> &to_polys,
				const MapXY &point)
{
  bool found_point = false;

  // find polygon corresponding to point
  unsigned i;
  for (i = 0; i < from_polys.size(); i++)
    {
      if(pointInPoly(point, from_polys.at(i)))
	{
	  found_point = true;
	  break;
	}
    }
	
  if (!found_point)
    {
      // point not in from_polys - find the nearest
      poly p;
      int closest = getClosestPoly(from_polys, point);
      if (closest < 0)
	{
	  // none found, return empty vector
	  to_polys.clear();
	  return;
	}
      i = closest;
    }

  CollectPolys(from_polys, to_polys, i);
}

std::vector<MapXY> PolyOps::getPointsFromPolys(const std::vector<poly>& polys)
{
  std::vector<MapXY> retPoints;

  for (int i = 0; (unsigned)i < polys.size(); i++)
    {
      retPoints.push_back(getPolyEdgeMidpoint(polys.at(i)));
    }

  return retPoints;
}

float PolyOps::distance(float x1, float y1, float x2, float y2)
{
  return Euclidean::DistanceTo(x1,y1,x2,y2);
}

float PolyOps::shortestDistToLineSegment(float x, float y, 
					 float line_x1, float line_y1, 
					 float line_x2, float line_y2)
{
  float dist1, dist2;
  dist1=dist2=0;

  Euclidean::DistanceFromLine(x,y,line_x1,line_y1,line_x2,line_y2,dist1,dist2);
  return dist1;

  /*
    float A = x - line_x1;
    float B = y - line_y1;
    float C = line_x2 - line_x1;
    float D = line_y2 - line_y1;

    float param = (A * C + B * D) / (C * C + D * D); // (dot product)/
    // (distance
    // squared)

    float x_on_line, y_on_line;

    if(param < 0)
    {
    x_on_line = line_x1;
    y_on_line = line_y1;
    }
    else if(param > 1)
    {
    x_on_line = line_x2;
    y_on_line = line_y2;
    }
    else
    {
    x_on_line = line_x1 + param * C;
    y_on_line = line_y1 + param * D;
    }

    return distance(x, y , x_on_line, y_on_line);
  */
}

int PolyOps::get_waypoint_index(const std::vector<poly> &polys,
				const ElementID& waypoint)
{
  
  for (unsigned i=0; i<polys.size(); i++)
    if (polys.at(i).start_way==waypoint &&
	polys.at(i).end_way==waypoint)
      return i;

  return -1;			// no match
}

int PolyOps::getPolyWayPt(const std::vector<poly> &polys,
				const ElementID& waypoint) {

  for (unsigned i=0; i<polys.size(); i++)
    if (polys.at(i).start_way==waypoint)
      return i;

  return -1;			// no match
}

// add from_polys polygons to to_polys matching from_id and to_id
//
// Adds all polygons between from_id and to_id, and also the one
// containing the to_id way-point, but not the one containing from_id.

void PolyOps::add_polys_for_waypts(const std::vector <poly> &from_polys,
				   std::vector <poly> &to_polys,
				   ElementID from_id, ElementID to_id)
{
  if (from_id != to_id)
    {
      for (unsigned i = 0; i < from_polys.size(); ++i)
	if (match_waypt_poly(from_polys.at(i), from_id, to_id))
	  {
	    to_polys.push_back(from_polys.at(i));
#define EXTREME_DEBUG 1
#ifdef EXTREME_DEBUG
	    printf("adding start, end waypoints %s, %s, poly_id = %d",
                      to_polys.back().start_way.name().str,
                      to_polys.back().end_way.name().str,
                      to_polys.back().poly_id);
#endif
	  }
    }

  for (unsigned i = 0; i < from_polys.size(); ++i)
    if (match_waypt_poly(from_polys.at(i), to_id))
      {
	to_polys.push_back(from_polys.at(i));
#ifdef EXTREME_DEBUG
	printf("adding start, end waypoints %s, %s, poly_id = %d",
                  to_polys.back().start_way.name().str,
                  to_polys.back().end_way.name().str,
                  to_polys.back().poly_id);
#endif
	break;
      }
}

// add from_polys polygons matching segment and lane to to_polys
void PolyOps::AddTransitionPolys(const std::vector <poly> &from_polys,
				 std::vector <poly> &to_polys,
				 WayPointNode way0, WayPointNode way1)
{
  for (unsigned i = 0; i < from_polys.size(); ++i)
    {
      if (MatchTransitionPoly(from_polys.at(i), way0, way1))
	{
	  to_polys.push_back(from_polys.at(i));
	}
    }
}
  
// add from_polys polygons matching segment and lane of waypt id to
// to_polys
void PolyOps::AddLanePolys(const std::vector <poly> &from_polys,
			   std::vector <poly> &to_polys, ElementID id)
{
  for (unsigned i = 0; i < from_polys.size(); ++i)
    {
      if (LanePoly(from_polys.at(i), id))
	{
	  to_polys.push_back(from_polys.at(i));
	}
    }
}

// add from_polys polygons matching segment and lane of waypt to
// to_polys
void PolyOps::AddLanePolys(const std::vector <poly> &from_polys,
			   std::vector <poly> &to_polys, WayPointNode waypt)
{
  AddLanePolys(from_polys, to_polys, waypt.id);
}

// add from_polys polygons matching segment and lane to to_polys
// in either direction (reverse if direction < 0)
void PolyOps::AddLanePolysEither(const std::vector <poly> &from_polys,
				 std::vector <poly> &to_polys, WayPointNode waypt,
				 int direction)
{
  if (direction >= 0)
    AddLanePolys(from_polys, to_polys, waypt);
  else
    AddReverseLanePolys(from_polys, to_polys, waypt);
}
  
// add from_polys polygons matching segment and lane to to_polys,
// searching the list in the reverse direction
void PolyOps::AddReverseLanePolys(const std::vector <poly> &from_polys,
				  std::vector <poly> &to_polys, ElementID id)
{
  // use int compares so the loop terminates
  int last = from_polys.size() - 1;
  printf("scanning polygons from %d back to 0", last);
  for (int i = last; i >= 0; --i)
    {
      //fprintf(stderr, "poly ID = %d\n", from_polys.at(i).poly_id);
      if (LanePoly(from_polys.at(i), id))
	{
	  to_polys.push_back(from_polys.at(i));
	}
    }
}

// add from_polys polygons matching segment and lane to to_polys,
// searching the list in the reverse direction
void PolyOps::AddReverseLanePolys(const std::vector <poly> &from_polys,
				  std::vector <poly> &to_polys, WayPointNode waypt)
{
  AddReverseLanePolys(from_polys, to_polys, waypt.id);
}
  
// Collect all polygons of from_poly from start to end from to_polys.
void PolyOps::CollectPolys(const std::vector<poly> &from_polys,
			   std::vector<poly> &to_polys,
			   unsigned start, unsigned end)
{
  to_polys.clear();
  for (unsigned i = start; i < end; ++i)
    to_polys.push_back(from_polys.at(i));
}
void PolyOps::CollectPolys(const std::vector<poly> &from_polys,
			   std::vector<poly> &to_polys,
			   unsigned start)
{
  CollectPolys(from_polys, to_polys, start, from_polys.size());
}

// true if curPoly is in the specified segment and lane
bool PolyOps::LanePoly(const poly &curPoly, WayPointNode waypt)
{
  return LanePoly(curPoly, waypt.id);
}

// true if curPoly is in the specified segment and lane
bool PolyOps::LanePoly(const poly &curPoly, ElementID id)
{
  return (curPoly.start_way.seg == id.seg
	  && curPoly.start_way.lane == id.lane
	  && curPoly.end_way.seg == id.seg
	  && curPoly.end_way.lane == id.lane
	  && !curPoly.is_transition);
}

// return true if curPoly is an transition polygon leading from way0 to way1
bool PolyOps::MatchTransitionPoly(const poly& curPoly, 
				  const WayPointNode& way0, 
				  const WayPointNode& way1)
{
  return (curPoly.start_way.same_lane(way0.id) &&
          curPoly.end_way.same_lane(way1.id) &&
          curPoly.is_transition);
}

float PolyOps::PolyHeading(const poly& curPoly)
{
  using Coordinates::bearing;
  float left_heading =  bearing(curPoly.p1,curPoly.p2);
  float right_heading = bearing(curPoly.p4, curPoly.p3);
  using Coordinates::normalize;
  return normalize(right_heading
                   + normalize(left_heading - right_heading) / 2.0f);
}

int PolyOps::getStartingPoly(const MapPose &pose,
			     const std::vector<poly>& polygons,
			     float distance,
			     float min_heading) 
{
  using Coordinates::normalize;

  // See if already in a polygon
  int index = getContainingPoly(polygons, pose.map);
  if (index >=0
      && (fabs(normalize(polygons.at(index).heading - pose.yaw))
          < min_heading))
    {
      return index;
    }
  
  // Get closest polygon 
  index = getClosestPoly(polygons, pose);
  if (index < 0)
    {
      std::cout << "none of " << polygons.size()
                      << " polygons near starting pose" << std::endl;
      return index;
    }
  else if (fabs(normalize(polygons.at(index).heading - pose.yaw))
           < min_heading)
    {
      std::cout << "closest polygon["  << index
                       << "] has suitable heading" << std::endl;
      return index;
    }
  
  // Find closest segment
  segment_id_t segment = polygons.at(index).start_way.seg;
  std::cout << "closest polygon["  << index
                  << "] in segment " << segment << std::endl;

  // Find all lanes that share same segment with closest polygons
  std::vector<lane_id_t> lanes;

  for (uint16_t i=0; i<polygons.size(); i++)
    if (polygons.at(i).start_way.seg ==
	segment) {
      bool lane_found=false;
      for (uint16_t j=0;j<lanes.size();j++)
	if (lanes.at(j)==polygons.at(i).start_way.lane) {
	  lane_found=true;
	  break;
	}
      if (!lane_found)
	lanes.push_back(polygons.at(i).start_way.lane);
    }
  

  // Find closest polygons in every lane found above and mark one with
  // heading closest to vehcile's heading
  float mindist = FLT_MAX;
  poly minpoly = polygons.at(0);
  bool foundd = false;
  for (uint16_t i=0; i<lanes.size(); i++)
    {
      ElementID point(segment,lanes.at(i),0);
      WayPointNode waypt;
      waypt.id=point;

      std::vector<poly> lane_polys;
      AddLanePolys(polygons, lane_polys, waypt);
      int newind = getClosestPoly(lane_polys, pose);
      if (newind < 0)
        continue;
      float tempdist =
        fabs(normalize(lane_polys.at(newind).heading - pose.yaw));
      if (tempdist < mindist)
        {
          mindist = tempdist;
          minpoly = lane_polys.at(newind);
          foundd=true;
        }
    }

  if (!foundd)
    {
      std::cout << "no lane within distance " << distance << std::endl;
      return -1;
    }

  // Return min polygon 
  for (uint16_t i=0; i< polygons.size(); i++)
    if (minpoly.poly_id == polygons.at(i).poly_id)
      return i;

  printf("no min polygon found");
  return -1;
}

#if 0 //TODO
ElementID
PolyOps::updateLaneLocation(const std::vector<poly>& polygons,
			    const MapPose& pose,
			    const WayPointNode& waypt1,
			    const WayPointNode& waypt2)
{
  
  std::vector<poly> lanes_polys;

  for (uint16_t i=0; i< polygons.size(); i++)
    if ((polygons.at(i).start_way.seg == waypt1.id.seg &&
	 polygons.at(i).start_way.lane == waypt1.id.lane && 
	 polygons.at(i).start_way.pt == waypt1.id.pt)
	||
	(polygons.at(i).start_way.seg == waypt2.id.seg &&
	 polygons.at(i).start_way.lane == waypt2.id.lane && 
	 polygons.at(i).start_way.pt == waypt2.id.pt))
      lanes_polys.push_back(polygons.at(i));
  
  int index=getClosestPoly(lanes_polys,pose.px,pose.py);

  if (index >= 0)
    return lanes_polys.at(index).start_way;

  return waypt1.id;

}
#endif

float PolyOps::length_between_polygons(const std::vector<poly>& polygons,
				       int index1,
				       int index2) 
{
  float length = 0;

  index1=std::max(0,index1);
  index1=std::min(int(polygons.size()),index1);
  
  index2=std::max(0,index2);
  index2=std::min(int(polygons.size()),index2);
  
  for(int i = index1+1; i < index2; i++)
    length += polygons.at(i).length;
  return length;
}

//Finds the distance between the midpoints of two polygons
//float distanceBetweenPolygons(const std::vector<poly>& polygons,
//			      poly from,
//			      poly to){
// return 
//    distanceAlongLane(polygons,
//		      from.midpoint,
//		      to.midpoint);
//}

// Requires that the polygons are in the order to follow, and all in
// the same lane
float PolyOps::distanceAlongLane(const std::vector<poly>& polygons,
				 const MapXY& from,
				 const MapXY& to)
{
  return (specialDistanceAlongLane(polygons, from, to)).first;
}

//Required by observers. 
// Returns the projection of start point on to the lane
// and the distance along the lane to the 'to' point
std::pair<float, MapXY> 
PolyOps::specialDistanceAlongLane(const std::vector<poly>& polygons,
				  const MapXY& from,
				  const MapXY& to)
{
  //Check if all Polygons are in the same lane
  int index1=getClosestPoly(polygons, from);
  int index2=getClosestPoly(polygons, to);

  if (index1 == -1 || index2 == -1) {
    std::pair<float, MapXY> return_value(0, MapXY());
    return return_value;
  }

  poly poly_start = polygons.at(index1);
  poly poly_end = polygons.at(index2);

  MapXY start_bisect1=midpoint(poly_start.p1, poly_start.p4);
  MapXY start_bisect2=midpoint(poly_start.p2, poly_start.p3);

  MapXY end_bisect1=midpoint(poly_end.p1, poly_end.p4);
  MapXY end_bisect2=midpoint(poly_end.p2, poly_end.p3);

  MapXY start_point=GetClosestPointToLine(start_bisect1,start_bisect2,
					  from, true);

  MapXY end_point=GetClosestPointToLine(end_bisect1,end_bisect2,
					to, true);

  float distance_start, distance_end, polygon_length;
  float tmp;
  if (index1 < index2)			// target is ahead?
    {
      Euclidean::DistanceFromLine(start_point, poly_start.p2, poly_start.p3,
				  distance_start, tmp);
      Euclidean::DistanceFromLine(end_point, poly_end.p1, poly_end.p4,
				  distance_end, tmp);
      polygon_length = length_between_polygons(polygons, index1, index2);
    }
  else if (index1 > index2)		// target is behind?
    {
      Euclidean::DistanceFromLine(start_point, poly_start.p1, poly_start.p4,
				  distance_start, tmp);
      Euclidean::DistanceFromLine(end_point, poly_end.p2, poly_end.p3,
				  distance_end, tmp);
      polygon_length = length_between_polygons(polygons, index2, index1);
    }
  else					// target in the same polygon
    {
      Euclidean::DistanceFromLine(start_point, poly_start.p1, poly_start.p4,
				  distance_start, tmp);
      distance_start = -distance_start;
      Euclidean::DistanceFromLine(end_point, poly_end.p1, poly_end.p4,
				  distance_end, tmp);
      polygon_length = 0;
    }

  float distance_total = distance_start + polygon_length + distance_end;
  
  if (index1 > index2)
    distance_total = -distance_total;

#ifdef EXTREME_DEBUG
  printf("distance_total to (%f, %f) %f )", to.x, to.y, distance_total);
  printf("polygon_length to (%f, %f) %f )", to.x, to.y, polygon_length);
#endif

  std::pair<float, MapXY> return_value(distance_total, start_point);
  return return_value;
}

int PolyOps::index_of_downstream_poly(const std::vector<poly>& polygons,
				      int start_index,
				      float distance) 
{
  if(start_index < 0 || start_index >= (int)polygons.size())
    return -1;

  if(distance <= 0)
    return start_index;

  int index = start_index;
  float length_so_far = polygons.at(index).length;
  while(distance > length_so_far) {
    if(index == (int)polygons.size() - 1)
      return index;
    index++;
    length_so_far += polygons.at(index).length;
  }
  return index;
}

MapXY PolyOps::midpoint(const MapXY& p1, const MapXY& p2) 
{
  MapXY mid((p1.x+p2.x)/2.0, (p1.y+p2.y)/2.0);
  return mid;
}

float PolyOps::avgLengthOfPolySides(const poly& p) 
{
  float s12 = Euclidean::DistanceTo(p.p1, p.p2);
  float s23 = Euclidean::DistanceTo(p.p2, p.p3);
  float s34 = Euclidean::DistanceTo(p.p3, p.p4);
  float s41 = Euclidean::DistanceTo(p.p4, p.p1);
  return (s12 + s23 + s34 + s41) / 4;
}

// Return a Set of unique lane IDs corresponding to the polys in the list
std::set<ElementID> PolyOps::getPolyLaneIds(const std::vector<poly>& polys) 
{
  std::set<ElementID> lane_ids;
  lane_ids.clear();   // ensure it's empty
  for (uint16_t i = 0; i < polys.size(); ++i) {
    lane_ids.insert(ElementID(polys.at(i).start_way.seg,
                              polys.at(i).start_way.lane, 0));
  }
  return lane_ids;
}

#if 0 //TODO
// Return a unique lane ID corresponding to the polys/dir given
// (uses transition polygons to determine closest lanes)
// input:  a) neighborhood polygons
//         b) relative flag (used for determining direction)
//              0 relative to lane heading
//              1 relative to pose paramater
//         c) direction (relative to relative flag)
//             +1 for getting left lane ID
//              0 for getting current lane ID
//             -1 for getting right lane ID
//         d) pose
//         e) epsilon in which our closest poly to make observations
//              from must be within
ElementID PolyOps::getPolyLaneIdDir(const std::vector<poly>& polys,
				    const int relative,
				    const int direction,
				    const player_pose2d_t& pose,
				    const float poly_epsilon) 
{
  int cur_poly_index = getClosestPolyEpsilon(polys, pose, poly_epsilon);
  if (cur_poly_index == -1) {
    printf("PolyOps::getPolyLaneIdDir: No poly found");
    return ElementID(-1,-1,-1);
  }

  int adj_poly_index[2];
  poly my_cur_poly = polys.at(cur_poly_index);

  if (direction == 0)   // if we want current lane id, return here
    return ElementID(my_cur_poly.start_way.seg, my_cur_poly.start_way.lane, 0);

  // generate adjacent lane IDs
  ElementID adj_lane[2];
  adj_lane[0] = polys.at(cur_poly_index).start_way;
  adj_lane[1] = polys.at(cur_poly_index).start_way;
  adj_lane[0].lane--;
  adj_lane[1].lane++;
  poly_list_t adj_lane_polys[2];		// adjacent lanes in segment

  // iterate through the adjacent lanes
  for (unsigned i = 0; i < 2; ++i) {
    adj_lane[i].pt = 0;		// lane ID, not way-point
    adj_lane_polys[i].clear();

    if (adj_lane[i].lane > 0) {  // lane ID in valid range?

      // get adjacent lane polys
      AddLanePolys(polys, adj_lane_polys[i], adj_lane[i]);
      if (adj_lane_polys[i].size() == 0 ) // make sure we found polys
        continue;

      // get index of closest poly in adjacent lane
      adj_poly_index[i] = getClosestPoly(adj_lane_polys[i],
                                         my_cur_poly.midpoint);
      if (adj_poly_index[i] == -1)
        continue;
      poly my_adj_poly = adj_lane_polys[i].at(adj_poly_index[i]);

      // find relative direction of poly
      MapPose poly_pose(my_cur_poly.midpoint, 0.0);
      if (relative == 0)      // relative to lane heading
        poly_pose.yaw = my_cur_poly.heading;
      else if (relative == 1) // relative to pose heading
        poly_pose.yaw = pose.pa;
      float theta = Coordinates::bearing(poly_pose, my_adj_poly.midpoint);

      if ( (theta > 0 && direction == +1) ||  // is lane left?
           (theta < 0 && direction == -1)  )   // is lane right?
        return ElementID(my_adj_poly.start_way.seg,
                         my_adj_poly.start_way.lane, 0);
      else;  // boundary case(0, +-M_PI): don't consider left/right

    } //end if valid lane
  } //end for

  printf("Error: lane must not exist this direction");
  return ElementID();                 // error: no lane this direction
}

// Return a unique lane ID corresponding to the polys/dir given
// (does NOT use transition polygons to determine closest lanes)
// input:  a) neighborhood polygons
//         b) relative flag (used for determining direction)
//              0 relative to lane heading
//              1 relative to pose paramater
//         c) direction (relative to relative flag)
//             +1 for getting left lane ID
//              0 for getting current lane ID
//             -1 for getting right lane ID
//         d) pose
//         e) epsilon in which our closest poly to make observations
//              from must be within
ElementID PolyOps::getNonTransPolyLaneIdDir(const poly_list_t& polys,
				    const int relative,
				    const int direction,
				    const player_pose2d_t& pose,
				    const float poly_epsilon) 
{
  int cur_poly_index = getClosestNonTransPolyEpsilon(polys, pose, poly_epsilon);
  if (cur_poly_index == -1) {
    printf("PolyOps::getNonTransPolyLaneIdDir: No poly found");
    return ElementID(-1,-1,-1);
  }

  int adj_poly_index[2];
  poly my_cur_poly = polys.at(cur_poly_index);

  if (direction == 0)   // if we want current lane id, return here
    return ElementID(my_cur_poly.start_way.seg, my_cur_poly.start_way.lane, 0);

  // generate adjacent lane IDs
  ElementID adj_lane[2];
  adj_lane[0] = polys.at(cur_poly_index).start_way;
  adj_lane[1] = polys.at(cur_poly_index).start_way;
  adj_lane[0].lane--;
  adj_lane[1].lane++;
  poly_list_t adj_lane_polys[2];		// adjacent lanes in segment

  // iterate through the adjacent lanes
  for (unsigned i = 0; i < 2; ++i) {
    adj_lane[i].pt = 0;		// lane ID, not way-point
    adj_lane_polys[i].clear();

    if (adj_lane[i].lane > 0) {  // lane ID in valid range?

      // get adjacent lane polys
      AddLanePolys(polys, adj_lane_polys[i], adj_lane[i]);
      if (adj_lane_polys[i].size() == 0 ) // make sure we found polys
        continue;

      // get index of closest poly in adjacent lane
      adj_poly_index[i] = getClosestNonTransPoly(adj_lane_polys[i],
                      my_cur_poly.midpoint);
      if (adj_poly_index[i] == -1)
        continue;
      poly my_adj_poly = adj_lane_polys[i].at(adj_poly_index[i]);

      // find relative direction of poly
      MapPose poly_pose(my_cur_poly.midpoint, 0.0);
      if (relative == 0)      // relative to lane heading
        poly_pose.yaw = my_cur_poly.heading;
      else if (relative == 1) // relative to pose heading
        poly_pose.yaw = pose.pa;
      float theta = Coordinates::bearing(poly_pose, my_adj_poly.midpoint);

      if ( (theta > 0 && direction == +1) ||  // is lane left?
           (theta < 0 && direction == -1)  )   // is lane right?
        return ElementID(my_adj_poly.start_way.seg,
                         my_adj_poly.start_way.lane, 0);
      else;  // boundary case(0, +-M_PI): don't consider left/right

    } //end if valid lane
  } //end for
  printf("Error: lane must not exist this direction");
  return ElementID(-1,-1,-1);  // error: no lane this direction

}
#endif

// Return the polygons in lane corresponding to the polys/dir given
// input:  a) neighborhood polygons
//         b) empty destination polygon vector
//         c) relative flag (used for determining direction)
//              0 relative to lane heading
//              1 relative to pose paramater
//         d) direction (relative to relative flag)
//             +1 for getting left lane
//              0 for getting current lane
//             -1 for getting right lane
//         e) pose
void PolyOps::getLaneDir(const std::vector<poly>& polys,
                         std::vector<poly>& to_polys,
                         const int relative,
                         const int direction,
                         const MapPose &pose) 
{
  // Clear this out here in case this function returns early.
  to_polys.clear();

  int cur_poly_index = getClosestPoly(polys, pose);
  if (cur_poly_index == -1) {
    printf("PolyOps::getLaneDir: No poly found");
    return;
  }
  int adj_poly_index[2];
  poly my_cur_poly = polys.at(cur_poly_index);

  if (direction == 0) {  // if we want current lane id, return here
    AddLanePolys(polys, to_polys, my_cur_poly.start_way);
    return;
  }

  // generate adjacent lane IDs
  ElementID adj_lane[2];
  adj_lane[0] = polys.at(cur_poly_index).start_way;
  adj_lane[1] = polys.at(cur_poly_index).start_way;
  adj_lane[0].lane--;
  adj_lane[1].lane++;
  poly_list_t adj_lane_polys[2];		// adjacent lanes in segment

  // iterate through the adjacent lanes
  for (unsigned i = 0; i < 2; ++i) {
    adj_lane[i].pt = 0;		// lane ID, not way-point
    adj_lane_polys[i].clear();

    if (adj_lane[i].lane > 0) {  // lane ID in valid range?
      
      // get adjacent lane polys
      AddLanePolys(polys, adj_lane_polys[i], adj_lane[i]);
      if (adj_lane_polys[i].size() == 0 ) // make sure we found polys
        continue;

      // get index of closest poly in adjacent lane
      adj_poly_index[i] = getClosestPoly(adj_lane_polys[i],
                                         my_cur_poly.midpoint);
      if (adj_poly_index[i] == -1)
        continue;
      poly my_adj_poly = adj_lane_polys[i].at(adj_poly_index[i]);

      // find relative direction of poly
      MapPose poly_pose(my_cur_poly.midpoint, 0.0);
      if (relative == 0)      // relative to lane heading
        poly_pose.yaw = my_cur_poly.heading;
      else if (relative == 1) // relative to pose heading
        poly_pose.yaw = pose.yaw;
      float theta = Coordinates::bearing(poly_pose, my_adj_poly.midpoint);

      if ( (theta > 0 && direction == +1) ||    // is lane left?
           (theta < 0 && direction == -1)  )   // is lane right?
        {
          CollectPolys(adj_lane_polys[i], to_polys, 0);
          return;
        }
      // else boundary case(0, +-M_PI): don't consider left/right

    } //end if valid lane
  } //end for
  printf("Error: lane must not exist this direction");
}

#if 0 //TODO
// Return the lane polys to the left up to num_lanes away.
// similar interface to getLaneDir()
void PolyOps::getNumLanesDir(const std::vector<poly>& polys,
            std::vector<poly>& to_polys,
            const int relative,
            const int direction,
            const player_pose2d_t &pose,
            const unsigned num_lanes) 
{
  int poly_index;
  player_pose2d_t my_pose = pose;
  poly_list_t dir_polys;
  to_polys.clear();
  for (unsigned i = 0; i < num_lanes; i++) {
    getLaneDir(polys, dir_polys, relative, direction, my_pose);
    poly_index = getClosestPoly(dir_polys, my_pose);
    if (poly_index < 0)
      return;
    AddLanePolys(dir_polys, to_polys, dir_polys.at(poly_index).start_way);
    my_pose.px = dir_polys.at(poly_index).midpoint.x;
    my_pose.py = dir_polys.at(poly_index).midpoint.y;
  }
  if (to_polys.size() == 0) // no lanes gotten
    printf("no lanes in given direction when expected");
}
#endif

ElementID PolyOps::getReverseLane(const std::vector<poly>& polys,
				  const MapPose &pose)
{
  poly_list_t to_polys;

  ElementID return_id;
  
  int base_index = getClosestPoly(polys, pose);
  if (base_index < 0)
    return return_id;

  float base_heading=polys.at(base_index).heading;  
  MapPose my_pose = pose;

  while (true)
    {
      getLaneDir(polys,to_polys,0,+1,my_pose);
      int poly_index = getClosestPoly(to_polys, my_pose);
      if (poly_index < 0)
	break;
      float lane_heading=to_polys.at(poly_index).heading;
      if (fabs(Coordinates::normalize(lane_heading - base_heading)) > HALFPI)
	return to_polys.at(poly_index).end_way;
      my_pose.map.x = to_polys.at(poly_index).midpoint.x;
      my_pose.map.y = to_polys.at(poly_index).midpoint.y;
    }
  return return_id;
}

// Print useful information of each polygon to ROS log
void PolyOps::printPolygons(const poly_list_t& polys) 
{
  for (uint16_t i = 0; i < polys.size(); ++i) {
    poly p = polys.at(i);
    printf("poly: %d S/T/CW: %d/%d/%d start: %d.%d.%d "
             "end: %d.%d.%d mp: %f,%f",
             p.poly_id, p.is_stop, p.is_transition, p.contains_way,
             p.start_way.seg, p.start_way.lane, p.start_way.pt,
             p.end_way.seg, p.end_way.lane, p.end_way.pt,
             p.midpoint.x, p.midpoint.y);
  }
}

// Return all the transition polys in the polys passed
poly_list_t PolyOps::getTransitionPolys(const poly_list_t& polys) {
  poly_list_t tran_polys;
  for (uint16_t i = 0; i < polys.size(); ++i)
    if (polys.at(i).is_transition)
      tran_polys.push_back(polys.at(i));
  return tran_polys;
}
  
#if 0 //TODO
// Return the closest polygon relative to pose in the seg/lane of concern
poly PolyOps::getClosestPolyInLane(const std::vector<poly>& polys,
                                   const player_pose2d_t& pose,
                                   const ElementID id) 
{
  std::vector<poly> lane_polys;
  AddLanePolys(polys, lane_polys, id);
  int poly_index = getClosestPoly(lane_polys, pose);
  if (poly_index == -1) {
    poly null_poly;
    null_poly.poly_id = -1;
    return null_poly;
  }
  else
    return lane_polys.at(poly_index);
}
#endif

// Check if polygon is valid
bool PolyOps::isValidPoly(const poly& p) 
{
  if (p.poly_id == -1)
    return false;
  else
    return true;
}

#if 0 //TODO
// Determine if the pose heading is same dirction as the polygon heading
bool PolyOps::travelingCorrectDir(const poly& p, const player_pose2d_t& pose) 
{
  float theta = Coordinates::normalize(pose.pa - p.heading);
  if (fabs(theta) < HALFPI)
    return true;
  else
    return false;
}
#endif

MapXY PolyOps::GetClosestPointToLine(MapXY A, MapXY B, 
				     MapXY P, bool segmentClamp)
//set 'segmentClamp' to true if you want the closest point on the
//segment, not just the line.
{
  MapXY AP = P - A;
  MapXY AB = B - A;
  float ab2 = AB.x*AB.x + AB.y*AB.y;
  float ap_ab = AP.x*AB.x + AP.y*AB.y;
  float t = ap_ab / ab2;
  if (segmentClamp)
    {
      if (t < 0.0f) 
	t = 0.0f;
      else if (t > 1.0f) 
	t = 1.0f;
    }
  AB.x*=t;
  AB.y*=t;
  
  MapXY Closest = A + AB;
  return Closest;
}

// get polys from from_id to to_id and store in to_polys
void PolyOps::getPolysBetweenWayPts(const std::vector<poly> &from_polys,
				   std::vector<poly> &to_polys,
				   ElementID from_id, ElementID to_id) 
{

  to_polys.clear();
  // make sure the points are valid
  if (!from_id.valid() or !to_id.valid()) {
    printf("points not valid");
    return;
  }
  // make sure the points are in the same lane
  if (!from_id.same_lane(to_id)) {
    printf("points not in same lane");
    return;
  }

  int from_index = -1;
  // find poly matching from_id
  for (uint16_t i = 0; i < from_polys.size(); ++i) {
    if (from_polys.at(i).start_way.pt == from_id.pt) {
      from_index = i;
      break;
    }
  }

  // make sure we found a poly with the eid
  if (from_index == -1)
    return;

  // collect polys between points in sequential order
  for (uint16_t i = from_index; i < from_polys.size(); ++i) {
    if (from_polys.at(i).start_way.pt < to_id.pt)
      to_polys.push_back(from_polys.at(i));
  }

}

// assumptions:
// - on a 2 lane road
// - way0 and way1 are from comm/nav plan
std::vector<MapXY> PolyOps::getRoadPerimeterPoints(
                const std::vector<poly>& polys,
                const ElementID way0, const ElementID way1) 
{

  std::vector<poly> all_polys_in_curr_lane;
  std::vector<poly> all_polys_in_left_lane;
  std::vector<poly> polys_in_curr_lane_forward;
  std::vector<poly> polys_in_left_lane_reverse;
  // perimeter points of road counter clockwise from pose
  std::vector<MapXY> perim_points;
  perim_points.clear();

  // check for invalid inputs and fail gracefully
  if (!way0.valid() or !way1.valid() or polys.empty() or (way1 < way0))
    return perim_points;

  // get poly that has way0
  int p_idx_way0 = get_waypoint_index(polys, way0);
  if (p_idx_way0 < 0)
    return perim_points;
  poly way0_poly = polys.at(p_idx_way0);
  // get pose that has way0
  MapPose way0_pose(way0_poly.midpoint, way0_poly.heading);

  // get poly that has way1
  int p_idx_way1 = get_waypoint_index(polys, way1);
  if (p_idx_way1 < 0)
    return perim_points;
  poly way1_poly = polys.at(p_idx_way1);
  // get pose that has way1
  MapPose way1_pose(way1_poly.midpoint, way1_poly.heading);

  // get all polys in current lane
  getLaneDir(polys, all_polys_in_curr_lane, 0, 0, way0_pose);
  // get polys_in_curr_lane_forward from way0 to way1
  int way0_pi = getPolyIndex(all_polys_in_curr_lane, way0_poly);
  int way1_pi = getPolyIndex(all_polys_in_curr_lane, way1_poly);
  CollectPolys(all_polys_in_curr_lane, polys_in_curr_lane_forward,
                  way0_pi, way1_pi);

  // get all polys in left lane
  getLaneDir(polys, all_polys_in_left_lane, 0, +1, way0_pose);
  int ll_way0_pi = getClosestPoly(all_polys_in_left_lane, way0_pose);
  if (ll_way0_pi < 0) {
    printf("no poly found 0");
    return perim_points;
  }
  int ll_way1_pi = getClosestPoly(all_polys_in_left_lane, way1_pose);
  if (ll_way1_pi < 0) {
    printf("no poly found 1");
    return perim_points;
  }
  poly ll_way0_poly = all_polys_in_left_lane.at(ll_way0_pi);
  poly ll_way1_poly = all_polys_in_left_lane.at(ll_way1_pi);
  // get polys_in_left_lane_reverse from way1 to way0
  ll_way0_pi = getPolyIndex(all_polys_in_left_lane, ll_way0_poly);
  ll_way1_pi = getPolyIndex(all_polys_in_left_lane, ll_way1_poly);
  CollectPolys(all_polys_in_left_lane, polys_in_left_lane_reverse,
                  ll_way1_pi, ll_way0_pi);

  // get the perimeter points on the right side of the road
  for (uint16_t i = 0; i < polys_in_curr_lane_forward.size(); ++i) {
    perim_points.push_back(polys_in_curr_lane_forward.at(i).p4);
  }
  if (polys_in_curr_lane_forward.size() > 0)
    perim_points.push_back(polys_in_curr_lane_forward.back().p3);

  // get the perimeter points on the left side of the road
  for (uint16_t i = 0; i < polys_in_left_lane_reverse.size(); ++i) {
    perim_points.push_back(polys_in_left_lane_reverse.at(i).p2);
  }
  if (polys_in_left_lane_reverse.size() > 0)
    perim_points.push_back(polys_in_left_lane_reverse.back().p1);

  return perim_points;

}

std::vector<MapXY> PolyOps::getRoadPerimeterPoints(
                const std::vector<poly>& polys,
                const ElementID way0) 
{

  ElementID way1;
  std::vector<poly> all_polys_in_curr_lane;
  std::vector<poly> all_polys_in_left_lane;
  std::vector<poly> polys_in_curr_lane_forward;
  std::vector<poly> polys_in_left_lane_reverse;
  // perimeter points of road counter clockwise from pose
  std::vector<MapXY> perim_points;
  perim_points.clear();

  // check for invalid inputs and fail gracefully
  if (!way0.valid() or polys.empty())
    return perim_points;

  // get poly that has way0
  int p_idx_way0 = get_waypoint_index(polys, way0);
  if (p_idx_way0 < 0)
    return perim_points;
  poly way0_poly = polys.at(p_idx_way0);
  // get pose that has way0
  MapPose way0_pose(way0_poly.midpoint, way0_poly.heading);

  // get all polys in current lane
  getLaneDir(polys, all_polys_in_curr_lane, 0, 0, way0_pose);
  // get first transition poly ahead in lane to be way1
  //fprintf(stderr,"all_polys_in_curr_lane.size() = %d\n",
  //        all_polys_in_curr_lane.size());
  for (uint16_t i = 0; i < all_polys_in_curr_lane.size(); ++i) {
    if (all_polys_in_curr_lane.at(i).is_stop and
        all_polys_in_curr_lane.at(i).start_way > way0) {
      way1 = all_polys_in_curr_lane.at(i).start_way;
      break;
    }
    if (i == all_polys_in_curr_lane.size()-1)
      way1 = all_polys_in_curr_lane.at(i).start_way;
  }
  //fprintf(stderr,"way1: %d.%d.%d\n",way1.seg,way1.lane,way1.pt);

  if (!way1.valid())
    return perim_points;

  // get poly that has way1
  int p_idx_way1 = get_waypoint_index(polys, way1);
  if (p_idx_way1 < 0)
    return perim_points;
  poly way1_poly = polys.at(p_idx_way1);
  // get pose that has way1
  MapPose way1_pose(way1_poly.midpoint, way1_poly.heading);

  // get polys_in_curr_lane_forward from way0 to way1
  int way0_pi = getPolyIndex(all_polys_in_curr_lane, way0_poly);
  int way1_pi = getPolyIndex(all_polys_in_curr_lane, way1_poly);
  CollectPolys(all_polys_in_curr_lane, polys_in_curr_lane_forward,
                  way0_pi, way1_pi);

  // get all polys in left lane
  getLaneDir(polys, all_polys_in_left_lane, 0, +1, way0_pose);
  int ll_way0_pi = getClosestPoly(all_polys_in_left_lane, way0_pose);
  if (ll_way0_pi < 0) {
    printf("no poly found 0");
    return perim_points;
  }
  int ll_way1_pi = getClosestPoly(all_polys_in_left_lane, way1_pose);
  if (ll_way1_pi < 0) {
    printf("no poly found 1");
    return perim_points;
  }
  poly ll_way0_poly = all_polys_in_left_lane.at(ll_way0_pi);
  poly ll_way1_poly = all_polys_in_left_lane.at(ll_way1_pi);
  // get polys_in_left_lane_reverse from way1 to way0
  ll_way0_pi = getPolyIndex(all_polys_in_left_lane, ll_way0_poly);
  ll_way1_pi = getPolyIndex(all_polys_in_left_lane, ll_way1_poly);
  CollectPolys(all_polys_in_left_lane, polys_in_left_lane_reverse,
                  ll_way1_pi, ll_way0_pi);

  // get the perimeter points on the right side of the road
  for (uint16_t i = 0; i < polys_in_curr_lane_forward.size(); ++i) {
    perim_points.push_back(polys_in_curr_lane_forward.at(i).p4);
  }
  if (polys_in_curr_lane_forward.size() > 0)
    perim_points.push_back(polys_in_curr_lane_forward.back().p3);

  // get the perimeter points on the left side of the road
  for (uint16_t i = 0; i < polys_in_left_lane_reverse.size(); ++i) {
    perim_points.push_back(polys_in_left_lane_reverse.at(i).p2);
  }
  if (polys_in_left_lane_reverse.size() > 0)
    perim_points.push_back(polys_in_left_lane_reverse.back().p1);

  return perim_points;

}
