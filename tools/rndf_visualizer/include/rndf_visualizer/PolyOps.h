/* -*- mode: C++ -*- */
/*
 *  Copyright (C) 2007, 2010 David Li, Patrick Beeson, Bartley Gillen,
 *                           Jack O'Quin
 *
 *  License: Modified BSD Software License Agreement
 * 
 *  $Id: 5cee49767c51531b787172e229aa195b69f6e4aa $
 */

/**  \file
 
     C++ interface for MapLanes polygon operations.

     \author David Li, Patrick Beeson, Bartley Gillen, Jack O'Quin

 */

#ifndef __POLYOPS_H__
#define __POLYOPS_H__


#include <utility>
#include <math.h>
#include <vector>
#include <set>
#include <map>
#include <stdint.h>
#include <rndf_visualizer/coordinates.h>
#include <rndf_visualizer/types.h>

/** Polygon class used internally.
 *
 *  These polygons are always quadrilaterals.
 *  @todo change the class name to something like Quad
 */
class poly
{
public:

  // Each polygon is a quadrilateral.  The four vertex points are
  // ordered relative to the heading of the lane containing it.
  MapXY p1;    // bottom left
  MapXY p2;    // top left
  MapXY p3;    // top right
  MapXY p4;    // bottom right

  // average of right and left boundary headings
  float heading;

  // Middle of the polygon
  MapXY midpoint;

  // Length of the polygon
  float length;

  poly_id_t poly_id;			// unique MapLanes ID

  bool is_stop;				// this poly has a stop waypoint
  bool is_transition;			// not a lane polygon, no waypoint

  // if true, both start_way and end_way are the contained waypoint
  bool contains_way;

  ElementID start_way;
  ElementID end_way;

  Lane_marking	left_boundary;
  Lane_marking	right_boundary;

  /** empty copy constructor */
  poly() {};
};

typedef std::vector<poly> poly_list_t;  // polygon vector type

// Stuff returned from vision..
typedef struct polyUpdate
{
  poly_id_t poly_id;			// unique MapLanes ID
  int point_id;
  float distance;
  float bearing;
  float confidence;
} lanes_poly_vision_t;


/** Polygon operations.
 *
 *  @todo This class has no state.  It should be replaced by a
 *        collection of functions in an appropriate namespace.
 */
class PolyOps
{
 public:
  PolyOps();
  ~PolyOps();

  int get_waypoint_index(const std::vector<poly> &polys,
			 const ElementID& waypoint);

  int getPolyWayPt(const std::vector<poly> &polys,
				const ElementID& waypoint);
    
  // add from_polys polygons to to_polys matching from_id and to_id
  void add_polys_for_waypts(const std::vector <poly> &from_polys,
			    std::vector <poly> &to_polys,
			    ElementID from_id, ElementID to_id);

  // add from_polys polygons matching segment and lane to to_polys
  void AddTransitionPolys(const std::vector <poly> &from_polys,
			  std::vector <poly> &to_polys,
			  WayPointNode way0, WayPointNode way1);
  
  // add from_polys polygons matching segment and lane of waypt id to
  // to_polys
  void AddLanePolys(const std::vector <poly> &from_polys,
		    std::vector <poly> &to_polys, ElementID id);

  void AddLanePolys(const std::vector <poly> &from_polys,
		    std::vector <poly> &to_polys, WayPointNode waypt);

  // add from_polys polygons matching segment and lane to to_polys
  // in either direction (reverse if direction < 0)
  void AddLanePolysEither(const std::vector <poly> &from_polys,
			  std::vector <poly> &to_polys, WayPointNode waypt,
			  int direction);
  
  // add from_polys polygons matching segment and lane of waypt id to to_polys,
  // searching the list in the reverse direction
  void AddReverseLanePolys(const std::vector <poly> &from_polys,
			   std::vector <poly> &to_polys, ElementID id);

  void AddReverseLanePolys(const std::vector <poly> &from_polys,
			   std::vector <poly> &to_polys, WayPointNode waypt);
  
  // Collect all polygons of from_poly from start to end from to_polys.
  void CollectPolys(const std::vector<poly> &from_polys,
		    std::vector<poly> &to_polys,
		    unsigned start, unsigned end);

  void CollectPolys(const std::vector<poly> &from_polys,
		    std::vector<poly> &to_polys,
		    unsigned start);

  // true if curPoly is in the specified segment and lane
  // Note: this ignores stop line polygons, we don't want to use them
  // for steering.  Why do they interfere?
  bool LanePoly(const poly &curPoly, ElementID id);

  bool LanePoly(const poly &curPoly, WayPointNode waypt);

  // true if curPoly connects way0 and way1
  bool match_waypt_poly(const poly& curPoly, ElementID way0, ElementID way1)
  {
    return (ElementID(curPoly.start_way) == way0
            && ElementID(curPoly.end_way) == way1);
  }

  // true if curPoly contains way0
  bool match_waypt_poly(const poly& curPoly, ElementID way)
  {
    return (ElementID(curPoly.start_way) == way
            && ElementID(curPoly.end_way) == way);
  }

  // return true if curPoly is an transition polygon leading from way0 to way1
  bool MatchTransitionPoly(const poly& curPoly, 
			   const WayPointNode& way0, 
			   const WayPointNode& way1);

  float PolyHeading(const poly& curPoly);

  // determines if point lies in interior of given polygon points on
  // edge segments are considered interior points
  bool pointInHull(float x, float y, const poly& p)
  {
    float minx=p.p1.x;
    float maxx=p.p1.x;
    float miny=p.p1.y;
    float maxy=p.p1.y;
    
    minx=fminf(fminf(fminf(minx,p.p2.x),p.p3.x),p.p4.x);
    miny=fminf(fminf(fminf(miny,p.p2.y),p.p3.y),p.p4.y);
    maxx=fmaxf(fmaxf(fmaxf(maxx,p.p2.x),p.p3.x),p.p4.x);
    maxy=fmaxf(fmaxf(fmaxf(maxy,p.p2.y),p.p3.y),p.p4.y);

    return (Epsilon::gte(x,minx) && Epsilon::lte(x,maxx) &&
	    Epsilon::gte(y,miny) && Epsilon::lte(y,maxy));
  }
  
  bool pointOnSegment(float x, float y, MapXY p1, MapXY p2)
  {
    float minx=fminf(p1.x,p2.x);
    float miny=fminf(p1.y,p2.y);
    float maxx=fmaxf(p1.x,p2.x);
    float maxy=fmaxf(p1.y,p2.y);

    if (Epsilon::gte(x,minx) && Epsilon::lte(x,maxx) &&
	Epsilon::gte(y,miny) && Epsilon::lte(y,maxy))
      {
	float diffy=p2.y-p1.y;
	float diffx=p2.x-p1.x;
	
	float diff2y=y-p1.y;
	float diff2x=x-p1.x;
	
	if (Epsilon::equal(diffx,0.0))
	  return (Epsilon::equal(diff2x,0.0) &&
		  ((diff2y<0) == (diffy<0)));
	
	if (Epsilon::equal(diff2x,0.0))
	  return false;
	
	return (Epsilon::equal(diffy/diffx,diff2y/diff2x));
      }
    return false;
    
  }
  
  bool pointOnEdges(float x, float y, const poly& p)
  {
    return (pointOnSegment(x, y, MapXY(p.p1), MapXY(p.p2)) ||
	    pointOnSegment(x, y, MapXY(p.p3), MapXY(p.p2)) ||
	    pointOnSegment(x, y, MapXY(p.p4), MapXY(p.p3)) ||
	    pointOnSegment(x, y, MapXY(p.p1), MapXY(p.p4)));
  }

  bool pointInPoly(float x, float y, const poly& p)
  {
    if (!pointInHull(x,y,p))
      return false;

    bool odd = false;

    // this is an unrolled version of the standard point-in-polygon algorithm

    if ((p.p1.y < y && p.p2.y >= y) || (p.p2.y < y && p.p1.y >= y))
      if (p.p1.x + (y-p.p1.y)/(p.p2.y-p.p1.y)*(p.p2.x-p.p1.x) < x)
	odd = !odd;

    if ((p.p2.y < y && p.p3.y >= y) || (p.p3.y < y && p.p2.y >= y))
      if (p.p2.x + (y-p.p2.y)/(p.p3.y-p.p2.y)*(p.p3.x-p.p2.x) < x)
	odd = !odd;

    if ((p.p3.y < y && p.p4.y >= y) || (p.p4.y < y && p.p3.y >= y))
      if (p.p3.x + (y-p.p3.y)/(p.p4.y-p.p3.y)*(p.p4.x-p.p3.x) < x)
	odd = !odd;

    if ((p.p4.y < y && p.p1.y >= y) || (p.p1.y < y && p.p4.y >= y))
      if (p.p4.x + (y-p.p4.y)/(p.p1.y-p.p4.y)*(p.p1.x-p.p4.x) < x)
	odd = !odd;

    if (odd)
      return true;

    return pointOnEdges(x, y, p);
  
  }

  bool pointInPoly(const MapXY& pt, const poly& p)
  {
    return pointInPoly(pt.x, pt.y, p);
  };

  bool pointInPoly(const Polar& polar, const MapPose &origin,
        	   const poly &p)
  {
    return pointInPoly(Coordinates::Polar_to_MapXY(polar, origin), p);
  };

  //bool pointInPoly(const player_pose2d_t &pose, const poly& p)
  //{
  //  return pointInPoly(pose.px, pose.py, p);
  //};
  bool pointInPoly_ratio(float x, float y, const poly& p, float ratio);
  bool pointInPoly_ratio(const MapXY& pt, const poly& p, float ratio)
  {
    return pointInPoly_ratio(pt.x, pt.y, p, ratio);
  };
  //bool pointInPoly_ratio(const player_pose2d_t &pose,
  //                       const poly& p, float ratio)
  //{
  //  return pointInPoly_ratio(pose.px, pose.py, p, ratio);
  //};

  // returns true if point is within epsilon of poly
  bool pointNearPoly(double x, double y, const poly& poly, double epsilon)
  {
    return (getShortestDistToPoly(x, y, poly) < epsilon);
  }
  bool pointNearPoly(const MapXY& pt, const poly& poly, double epsilon)
  {
    return (getShortestDistToPoly(pt.x, pt.y, poly) < epsilon);
  }
  //bool pointNearPoly(const player_pose2d_t &pose, const poly& poly, 
  //      	     double epsilon)
  //{
  //  return (getShortestDistToPoly(pose.px, pose.py, poly) < epsilon);
  //}

  /** Get containing polygon
   *
   * @param polys vector of polygons to consider
   * @param x, y MapXY coordinates of desired point
   * @return index of polygon containing location (x, y) in @a polys
   *         -1 if no such polygon is found
  */
  int getContainingPoly(const std::vector<poly> &polys, float x, float y);
  int getContainingPoly(const std::vector<poly>& polys, const MapXY& pt)
  {
    return getContainingPoly(polys, pt.x, pt.y);
  };

  int getContainingPoly(const std::vector<poly>& polys,
                        const MapPose &pose)
  {
    return getContainingPoly(polys, pose.map.x, pose.map.y);
  };

  // return containing POLYGON ID, -1 if none in list
  poly_id_t getContainingPolyID(const std::vector<poly> &polys,
                                float x, float y)
  {
    int index = getContainingPoly(polys, x, y);
    if (index < 0)
      return -1;
    else
      return polys[index].poly_id;
  };
  poly_id_t getContainingPolyID(const std::vector<poly>& polys,
                                const MapXY& pt)
  {
    int index = getContainingPoly(polys, pt);
    if (index < 0)
      return -1;
    else
      return polys[index].poly_id;
  };
  //poly_id_t getContainingPolyID(const std::vector<poly>& polys,
  //      			const player_pose2d_t &pose)
  //{
  //  int index = getContainingPoly(polys, pose);
  //  if (index < 0)
  //    return -1;
  //  else
  //    return polys[index].poly_id;
  //};
  
  // return index of curPoly in polys vector, -1 if missing
  int getPolyIndex(const std::vector<poly>& polys, const poly& curPoly)
  {
    int i;
    for (i = 0; i < (int) polys.size(); ++i)
      {
	if (polys.at(i).poly_id == curPoly.poly_id)
	  return i;
      }
    return -1;
  }

  // copy from_polys polygons to to_polygons after nearest to point
  void getRemainingPolys(const std::vector<poly> &from_polys,
			 std::vector<poly> &to_polys,
			 const MapXY &point);
  //void getRemainingPolys(const std::vector<poly> &from_polys,
  //      		 std::vector<poly> &to_polys,
  //      		 const player_pose2d_t &pose)
  //{
  //  getRemainingPolys(from_polys, to_polys, MapXY(pose));
  //}

  // if the point lies within the given polygon, the returned distance
  // is 0 otherwise, the shortest distance to any edge/vertex of the
  // given polygon is returned
  float getShortestDistToPoly(float x, float y, const poly& p);
  float getShortestDistToPoly(MapXY pt, const poly& p)
  {
    return getShortestDistToPoly(pt.x, pt.y, p);
  }
  //float getShortestDistToPoly(const player_pose2d_t &pose, const poly& p)
  //{
  //  return getShortestDistToPoly(pose.px, pose.py, p);
  //}

  // if the point lies within a polygon, that polygon is returned.
  // otherwise, the nearest polygon from the list is returned index of
  // winning poly within list is stored in index
  int getClosestPoly(const std::vector<poly>& polys, float x, float y);
  int getClosestPoly(const std::vector<poly>& polys, MapXY pt)
  {
    return getClosestPoly(polys, pt.x, pt.y);
  }
  int getClosestPoly(const std::vector<poly>& polys,
                     const MapPose &pose)
  {
    return getClosestPoly(polys, pose.map.x, pose.map.y);
  }
  //int getClosestPoly(const std::vector<poly>& polys, const Polar& pt, 
  //      	     player_pose2d_t pose)
  //{
  //  MapXY mapxy = Coordinates::Polar_to_MapXY(pt, pose);
  //  return getClosestPoly(polys, mapxy);
  //}

  // Returns index of closest polygon if within given epsilon, -1 otherwise
  //int getClosestPolyEpsilon(const std::vector<poly>& polys,
  //                          const player_pose2d_t& pose, const float epsilon);

  // if the point lies within a non-transtion polygon, that polygon is returned.
  // otherwise, the nearest non-transition polygon from the list is returned.
  // index of winning non-transition poly within list is stored in index.
  int getClosestNonTransPoly(const std::vector<poly>& polys, float x, float y);
  int getClosestNonTransPoly(const std::vector<poly>& polys, MapXY pt)
  {
    return getClosestNonTransPoly(polys, pt.x, pt.y);
  }
  //int getClosestNonTransPoly(const std::vector<poly>& polys,
  //                           const player_pose2d_t &pose)
  //{
  //  return getClosestNonTransPoly(polys, pose.px, pose.py);
  //}
  //int getClosestNonTransPoly(const std::vector<poly>& polys, const Polar& pt, 
  //      	     player_pose2d_t pose)
  //{
  //  MapXY mapxy = Coordinates::Polar_to_MapXY(pt, pose);
  //  return getClosestNonTransPoly(polys, mapxy);
  //}

  // Returns index of closest non-transition polygon if within given epsilon,
  // -1 otherwise.
  //int getClosestNonTransPolyEpsilon(const std::vector<poly>& polys,
  //                                  const player_pose2d_t& pose,
  //                                  const float epsilon);
			   
  // returns an x-y pair representing the midpoint of the 2-3 (top)
  // edge of input polygon
  MapXY getPolyEdgeMidpoint(const poly& p);

  // Returns the center of the polygon
  MapXY centerpoint(const poly& p);

  // Return the length of a polygon
  float getLength(const poly& p);

  // returns list of polygons between the polygons containing the two
  // given points. assumes polygon list is sorted and that second
  // point follows first (e.g. waypoints from navigator Order).
  // returned list starts with polygon containing or closest to the
  // first point. if second point is not inside a polygon, new list
  // will extend to end of the old one
  std::vector<poly> getPolysBetweenPoints(const std::vector<poly>& polys, 
					  float x1, float y1, 
					  float x2, float y2);
		
  // returns list polygon edge midpoints - ideally these can be used
  // by navigator as waypoints
  std::vector<MapXY> getPointsFromPolys(const std::vector<poly>& polys);

  /** Get closest polygon in front of robot's current pose
   *
   * Useful when starting off road.  
   *
   * @param pose current vehicle pose (2D map coordinates)
   * @param polygons list of polygons
   * @param distance looks ahead a certain amount so that we don't turn
   *                 sharply to reach a nearby waypoint.
   * @param min_heading angle to accept polygon as valid
   * @return index in @a polygons of closest polygon within
   *                 @a min_heading and @a distance.
   */
  int getStartingPoly(const MapPose &pose,
                      const std::vector<poly>& polygons,
                      float distance,
                      float min_heading);
  
  //ElementID updateLaneLocation(const std::vector<poly>& polygons,
  //                             const player_pose2d_t& pose,
  //                             const WayPointNode& waypt1,
  //                             const WayPointNode& waypt2);


  // Finds the closest polygons to two points, then finds the length
  // in the ordered list of polygons between them.
  float distanceAlongLane(const std::vector<poly>& polygons,
                          const MapXY& from,
                          const MapXY& to);

  std::pair<float, MapXY>
  specialDistanceAlongLane(const std::vector<poly>& polygons,
                           const MapXY& from,
                           const MapXY& to);
    
  //Finds the distance between the midpoints of two polygons
  //float distanceBetweenPolygons(const std::vector<poly>& polygons,
  //                            poly from,
  //                            poly to);
  
  // Returns the index of the polygon that is distance downstream
  // from the trailing edge of polygons[start_index]. If distance
  // is less than the length of polygons[start_index], start_index is returned.
  int index_of_downstream_poly(const std::vector<poly>& polygons,
                               int start_index,
                               float distance);


  // returns shortest distance from a point to a line segment
  float shortestDistToLineSegment(float x, float y, float line_x1, 
                                  float line_y1, float line_x2, 
                                  float line_y2);

  // returns the average length of the 4 sides of a polygon
  float avgLengthOfPolySides(const poly& p);

  // Return a Set of unique lane IDs corresponding to the polys in the list
  std::set<ElementID> getPolyLaneIds(const std::vector<poly>& polys);

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
  //ElementID getPolyLaneIdDir(const poly_list_t& polys,
  //                           const int relative,
  //                           const int direction,
  //                           const player_pose2d_t &pose,
  //                           const float poly_epsilon);

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
  //ElementID getNonTransPolyLaneIdDir(const poly_list_t& polys,
  //                           const int relative,
  //                           const int direction,
  //                           const player_pose2d_t &pose,
  //                           const float poly_epsilon);

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

  void getLaneDir(const std::vector<poly>& polys,
                  std::vector<poly>& to_polys,
                  const int relative,
                  const int direction,
                  const MapPose &pose);

  // Return the lane polys to the left up to num_lanes away.
  // similar interface to getLaneDir()
  //void getNumLanesDir(const std::vector<poly>& polys,
  //                    std::vector<poly>& to_polys,
  //                    const int relative,
  //                    const int direction,
  //                    const player_pose2d_t &pose,
  //                    const unsigned num_lanes);

  // Print useful information of each polygon
  void printPolygons(const poly_list_t& polys);

  // Return all the transition polys in the polys passed
  poly_list_t getTransitionPolys(const poly_list_t& polys);

  // Return the closest polygon relative to pose in the seg/lane of concern
  //poly getClosestPolyInLane(const std::vector<poly>& polys,
  //                          const player_pose2d_t& pose,
  //                          const ElementID id);

  // Check if polygon is valid
  bool isValidPoly(const poly& p);

  // Determine if the pose heading is same dirction as the polygon heading
  //bool travelingCorrectDir(const poly& p, const player_pose2d_t& pose);

  MapXY GetClosestPointToLine(MapXY A, MapXY B, 
                              MapXY P, bool segmentClamp);

  MapXY midpoint(const MapXY& p1, const MapXY& p2);

  ElementID getReverseLane(const std::vector<poly>& polys,
                           const MapPose &pose);

  // true if this_poly is to the left of cur_poly.
  bool left_of_poly(const poly &this_poly, const poly &cur_poly)
  {
    // pose of cur_poly
    MapPose cur_pose(cur_poly.midpoint, cur_poly.heading);

    // normalized bearing of this_poly from cur_poly
    float theta = Coordinates::bearing(cur_pose, this_poly.midpoint);
    return (theta > 0.0);
  }

  // true if p1 and p2 are within angle of the same heading
  bool same_direction(const poly &p1, const poly &p2, float angle)
  {
    return (fabs(Coordinates::normalize(p1.heading - p2.heading)) < angle);
  }

  // get polys from from_id to to_id and store in to_polys
  void getPolysBetweenWayPts(
           const std::vector<poly> &from_polys,
                                   std::vector<poly> &to_polys,
                                   ElementID from_id, ElementID to_id);

  // assumptions:
  // - on a 2 lane road
  // - way0 and way1 are from comm/nav plan
  std::vector<MapXY> getRoadPerimeterPoints(const std::vector<poly>& polys,
                                            const ElementID way0,
                                            const ElementID way1);

  std::vector<MapXY> getRoadPerimeterPoints(const std::vector<poly>& polys,
                                            const ElementID way0);


 private:

  // TODO: (after Urban Challenge) use Euclidean::DistanceTo()...
  // simple distance between two points
  float distance(float x1, float y1, float x2, float y2);

  // Total length of midlines of polygons
  float length_between_polygons(const std::vector<poly>& polygons,
                                int index1=-1,
                                int index2=-1);


};

#endif
