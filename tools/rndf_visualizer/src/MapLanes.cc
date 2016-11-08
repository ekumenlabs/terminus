/*
 *  Copyright (C) 2007, 2010 David Li, Patrick Beeson, Jack O'Quin
 *
 *  License: Modified BSD Software License Agreement
 *
 *  $Id: 600f8f478f131ebb1027e7dcc26b1cd2bbb394ff $
 */

/**  \file

     C++ interface for operating on MapLanes polygons.

     \author David Li, Patrick Beeson, Michael Quinlan, Jack O'Quin

 */

#include <iostream>
#include <iomanip>
#include <epsilon.h>
#include <vector>

#include <rndf_visualizer/gaussian.h>
#include <rndf_visualizer/MapLanes.h>
#include <rndf_visualizer/euclidean_distance.h>

#include <rndf_visualizer/rotate_translate_transform.h>

#include <simple_svg_1.0.0.hpp>

// intial_latlong specifies whether rndf waypoints and initial
// coordinates are specified in lat/long or map_XY. The boolean
// applies to both since the RNDF itself doesn't specify. This can
// seperated if getting lat/long inital coordinates is inconvineint.

#define way_poly_size 0.5 // half of length of polygon that goes
// around waypoints
int writecounter = 0;
int aCount = 0;
int bCount = 0;
int cCount = 0;

int MapLanes::MapRNDF(Graph* _graph, float _max_poly_size)
{
	graph = _graph;

	max_poly_size = fmaxf(_max_poly_size, MIN_POLY_SIZE);

	allPolys.clear();
	//filtPolys.clear();

	//initilize poly id counter
	poly_id_counter = 0;

	std::cout << "Starting with " << graph->nodes_size << " nodes in graph" << std::endl;

	rX = 0.0;
	rY = 0.0;
	rOri = 0.0;

	cX = 0.0;
	cX = 0.0;
#ifdef DEBUGMAP
	debugFile = fopen("mapDebug.txt", "wb");
#endif

	MakePolygons();
	SetFilteredPolygons();

	printf("MapLanes constructed successfully");
	return 0;				// success
}

void MapLanes::MakePolygons()
{
	// Add Waypoints to WayPointImage
	std::vector<WayPointNode> lane;
	std::vector<Point2f> lane_pt;
	std::vector<int> lane_map;

	SmoothCurve lc, rc;

	ElementID prev_lane;             // used to determine when the edges
	// switch lanes

	// Walk along graph edges, pushing nodes (and the associated points
	// that the curve code uses) from same lane onto a list, then
	// process the list whenever a new lane is encountered (or an transition)
	// or before leaving the function if the list isn't empty.

	for (uint j = 0; j < graph->edges_size; j++)
	{
		WayPointEdge e = graph->edges[j];
		if (e.is_implicit)
			continue;
		WayPointNode w1 = graph->nodes[e.startnode_index];
		WayPointNode w2 = graph->nodes[e.endnode_index];

		if ((!e.is_exit || (w1.id.same_lane(w2.id) &&
		                    w1.id.pt + 1 == w2.id.pt))
		        && !w1.is_perimeter && !w1.is_spot &&
		        !w2.is_perimeter && !w2.is_spot)
			// if lane push next waypoint onto list
		{
			if (w1.id.seg != prev_lane.seg ||
			        w1.id.lane != prev_lane.lane ||
			        w1.id.pt != prev_lane.pt)
				//if new lane push start waypoint onto list
			{
				// If last lane info is still around, process it
				if (lane.size() > 1)
				{
					Point2f diff_pt = lane_pt[1] - lane_pt[0];
					Point2f diff_pt2 = lane_pt[lane_pt.size() - 1] -
					                   lane_pt[lane_pt.size() - 2];
					SmoothCurve c =
					    SmoothCurve(lane_pt,
					                atan2f(diff_pt[1], diff_pt[0]), 1,
					                atan2f(diff_pt2[1], diff_pt2[0]), 1);

					for (uint i = 0; i < lane.size() - 1; i++)
					{
						MakeLanePolygon(lane[i], lane[i + 1], e,
						                c.knots[lane_map[i]],
						                c.knots[lane_map[i + 1]],
						                c, true,
						                0, 0, lc,
						                0, 0, rc);
					}
				}

				// Set up new lane
				lane.clear();
				lane_pt.clear();
				lane_map.clear();

				lane.push_back(w1);
				Point2f pt1(w1.map.x, w1.map.y);
				lane_pt.push_back(pt1);
				lane_map.push_back(lane_pt.size() - 1);
			}

			// Fill in rest of lane
			lane.push_back(w2);
			Point2f pt2(w2.map.x, w2.map.y);
			lane_pt.push_back(pt2);
			lane_map.push_back(lane_pt.size() - 1);

			prev_lane = w2.id;
		}
		else if (!w1.is_spot &&
		         !w2.is_spot &&
		         (!w1.is_perimeter || !w2.is_perimeter) &&
		         (w1.id.seg != w2.id.seg ||
		          w1.id.lane == w2.id.lane))
			// Transition;
		{
			if (lane.size() > 1)
				// Process out previous lane if one exists
			{
				Point2f diff_pt = lane_pt[1] - lane_pt[0];
				Point2f diff_pt2 = lane_pt[lane_pt.size() - 1] -
				                   lane_pt[lane_pt.size() - 2];

				SmoothCurve c =
				    SmoothCurve(lane_pt,
				                atan2f(diff_pt[1], diff_pt[0]), 1,
				                atan2f(diff_pt2[1], diff_pt2[0]), 1);

				for (uint i = 0; i < lane.size() - 1; i++)
					MakeLanePolygon(lane[i], lane[i + 1], e,
					                c.knots[lane_map[i]],
					                c.knots[lane_map[i + 1]],
					                c, true,
					                0, 0, lc, 0, 0, rc);
			}

			// Make transition polygons
			lane.clear();
			lane_pt.clear();
			lane_map.clear();

			int base_ind = 0;

			// Exits have 2 waypoints, but curves need 3 or more.  Go
			// get neighboring waypoints to entrance and transition if
			// they exist.

			ElementID pre = w1.id;
			pre.pt--;

			WayPointNode* w0 = graph->get_node_by_id(pre);

			if (w0 != NULL && w0->id.lane != 0) {
				lane.push_back(*w0);
				Point2f pt(w0->map.x, w0->map.y);
				lane_pt.push_back(pt);
				lane_map.push_back(lane_pt.size() - 1);
				base_ind = 1;
			}

			// Push 2 (or 3 or 4 if found) waypoints onto list to find
			// curve.
			lane.push_back(w1);
			Point2f pt1(w1.map.x, w1.map.y);
			lane_pt.push_back(pt1);
			lane_map.push_back(lane_pt.size() - 1);

			lane.push_back(w2);
			Point2f pt2(w2.map.x, w2.map.y);
			lane_pt.push_back(pt2);
			lane_map.push_back(lane_pt.size() - 1);

			ElementID post = w2.id;
			post.pt++;

			WayPointNode* w3 = graph->get_node_by_id(post);

			if (w3 != NULL && w3->id.lane != 0)
			{
				lane.push_back(*w3);
				Point2f pt(w3->map.x, w3->map.y);
				lane_pt.push_back(pt);
				lane_map.push_back(lane_pt.size() - 1);
			}


			if (lane_pt.size() < 2)
			{
				WayPointNode w4 = w2;
				w4.map = w2.map + w2.map - w1.map;
				lane.push_back(w4);
				Point2f pt(w4.map.x, w4.map.y);
				lane_pt.push_back(pt);
				lane_map.push_back(lane_pt.size() - 1);
			}


			Point2f diff_pt = lane_pt[1] - lane_pt[0];
			Point2f diff_pt2 = lane_pt[lane_pt.size() - 1] -
			                   lane_pt[lane_pt.size() - 2];

			SmoothCurve c =
			    SmoothCurve(lane_pt,
			                atan2f(diff_pt[1], diff_pt[0]), 1,
			                atan2f(diff_pt2[1], diff_pt2[0]), 1);

			MakeTransitionPolygon(lane[base_ind], lane[base_ind + 1], e,
			                      c.knots[lane_map[base_ind]], c.knots[lane_map[base_ind + 1]], c);

			// Clear out transition
			lane.clear();
			lane_pt.clear();
			lane_map.clear();
			prev_lane = ElementID();
		}
	}

	// If last lane info is still around, process it
	if (lane.size() > 1)
	{
		// Clear out previous lane
		Point2f diff_pt = lane_pt[1] - lane_pt[0];
		Point2f diff_pt2 = lane_pt[lane_pt.size() - 1] -
		                   lane_pt[lane_pt.size() - 2];
		SmoothCurve c =
		    SmoothCurve(lane_pt,
		                atan2f(diff_pt[1], diff_pt[0]), 1,
		                atan2f(diff_pt2[1], diff_pt2[0]), 1);

		for (uint i = 0; i < lane.size() - 1; i++) {
			// Find the edge that links lane[i] and lane[i+1]
			WayPointEdge e;
			for (uint j = 0; j < graph->edges_size; j++)
			{
				e = graph->edges[j];

				if (graph->nodes[e.startnode_index].id.pt == lane[i].id.pt
				        && graph->nodes[e.startnode_index].id.lane == lane[i].id.lane
				        && graph->nodes[e.startnode_index].id.seg == lane[i].id.seg
				        && graph->nodes[e.endnode_index].id.pt == lane[i + 1].id.pt
				        && graph->nodes[e.endnode_index].id.lane == lane[i + 1].id.lane
				        && graph->nodes[e.endnode_index].id.seg == lane[i + 1].id.seg)

					break;
			}

			MakeLanePolygon(lane[i], lane[i + 1], e,
			                c.knots[lane_map[i]],
			                c.knots[lane_map[i + 1]],
			                c, true, 0, 0, lc, 0, 0, rc);
		}
	}

	// Set up new lane
	lane.clear();
	lane_pt.clear();
	lane_map.clear();
}

void MapLanes::SetFilteredPolygons()
{
	for (int i = 0; i < (int)allPolys.size(); i++)
	{
		FilteredPolygon p;
		p.SetPolygon(allPolys.at(i));
		filtPolys.push_back(p);
	}

#ifdef DEBUGMAP
	for (int i = 0; i < (int)filtPolys.size(); i++) {
		WritePolygonToDebugFile(i);
	}
#endif
}

poly MapLanes::build_waypoint_poly(const WayPointNode& w1,
                                   const WayPointEdge& e,
                                   const Point2f& _pt,
                                   float time,
                                   SmoothCurve& c)
{
	// Given a waypoint location, make a plygon 1 meter deep around the
	// waypoint.

	rotate_translate_transform trans;
	posetype origin(0, 0, 0);


	Point2f back_pt = c.evaluatePoint(time + way_poly_size);
	Point2f front_pt = c.evaluatePoint(time - way_poly_size);
	Point2f pt = _pt;

	//  static Point2f defaultpt;

	// If time <0 or > maxtime, find it and fix it.
	if (back_pt[0] == pt[0] &&
	        back_pt[1] == pt[1])
		back_pt = pt + (pt - front_pt);

	if (front_pt[0] == pt[0] &&
	        front_pt[1] == pt[1])
		front_pt = pt - (back_pt - pt);


	Point2f diff_back = back_pt - pt;
	Point2f diff_front = pt - front_pt;

	float back_angle = atan2f(diff_back[1], diff_back[0]);
	float front_angle = atan2f(diff_front[1], diff_front[0]);

	// lane
	posetype refway1(back_pt[0], back_pt[1], back_angle);
	trans.find_transform(origin, refway1);
	posetype p2 = trans.apply_transform(posetype(0, w1.lane_width / 2, 0));
	posetype p3 = trans.apply_transform(posetype(0, -w1.lane_width / 2, 0));

	posetype refway2(front_pt[0], front_pt[1], front_angle);
	trans.find_transform(origin, refway2);
	posetype p1 = trans.apply_transform(posetype(0, w1.lane_width / 2, 0));
	posetype p4 = trans.apply_transform(posetype(0, -w1.lane_width / 2, 0));

	poly newPoly;

	newPoly.p1.x = p1.x;
	newPoly.p1.y = p1.y;

	newPoly.p2.x = p2.x;
	newPoly.p2.y = p2.y;

	newPoly.p3.x = p3.x;
	newPoly.p3.y = p3.y;

	newPoly.p4.x = p4.x;
	newPoly.p4.y = p4.y;

	// Update some details
	newPoly.start_way.seg = w1.id.seg;
	newPoly.start_way.lane = w1.id.lane;
	newPoly.start_way.pt = w1.id.pt;
	newPoly.end_way.seg = w1.id.seg;
	newPoly.end_way.lane = w1.id.lane;
	newPoly.end_way.pt = w1.id.pt;
	newPoly.is_stop = w1.is_stop;
	newPoly.is_transition = false;
	newPoly.contains_way = true;
#if 0 //TODO
	newPoly.left_boundary.lane_marking = e.left_boundary.lane_marking;
	newPoly.right_boundary.lane_marking = e.right_boundary.lane_marking;
#endif

	// set initial heading based on map coordinates
	newPoly.heading = ops.PolyHeading(newPoly);
	MapXY cpt = ops.centerpoint(newPoly);
	newPoly.midpoint.x = cpt.x;
	newPoly.midpoint.y = cpt.y;
	newPoly.length = ops.getLength(newPoly);
	return newPoly;
}


void MapLanes::MakeLanePolygon(WayPointNode w1, WayPointNode w2,
                               WayPointEdge e,
                               float time1, float time2,
                               SmoothCurve& c,
                               bool new_edge,
                               float ltime1, float ltime2,
                               SmoothCurve& lc,
                               float rtime1, float rtime2,
                               SmoothCurve& rc)
{

	if (time2 <= time1)
		return;

	// Not necessary because of how this is called, but do this just in
	// case
	if (poly_id_counter == 0)
		new_edge = true;

	Point2f w1_pt = c.evaluatePoint(time1);
	Point2f w2_pt = c.evaluatePoint(time2);




	// If new edge (not called recursively)
	if (new_edge)
	{
		poly poly_w1;

		// if new lane, make polygon for start node
		if (poly_id_counter == 0 ||
		        ElementID(allPolys[poly_id_counter - 1].end_way) != w1.id)
		{
			poly_w1 = build_waypoint_poly(w1, e, w1_pt, time1, c);

			poly_w1.poly_id = poly_id_counter;

			// Add the poly to the list
			poly_id_counter++;
			allPolys.push_back(poly_w1);

		}
		else
			// If not a new lane, get lane waypoint, which should be last
			// one pushed onto list
			poly_w1 = allPolys[poly_id_counter - 1];

		// Make new polygon around second waypoint, but only add it
		// after recursive all for intermediate polygons
		poly poly_w2 = build_waypoint_poly(w2, e, w2_pt, time2, c);


		time1 = time1 + way_poly_size;
		time2 = time2 - way_poly_size;

		w1.map = ops.midpoint(poly_w1.p2, poly_w1.p3);
		w2.map = ops.midpoint(poly_w2.p1, poly_w2.p4);

		float edist =
		    Euclidean::DistanceTo(w1.map, w2.map);

		float cdist = fmax(time2 - time1, 0.0);

		// Only fill rest of lane if two waypoints are further than
		// their 1 meter polygons -- probably always true
		if (cdist > Epsilon::float_value && edist > Epsilon::float_value)
		{
			std::vector<Point2f> left_curve_pts;
			left_curve_pts.push_back(Point2f(poly_w1.p2.x, poly_w1.p2.y));
			left_curve_pts.push_back(Point2f(poly_w2.p1.x, poly_w2.p1.y));

			bool straight = false;
//     #ifdef NQE
//       if (poly_w1.start_way.seg==14 || poly_w1.start_way.seg==15 || poly_w1.start_way.seg==16 || poly_w1.start_way.seg==17) straight=true;
//     #endif
			if (straight) {
				lc =
				    SmoothCurve(left_curve_pts,
				                atan2f(poly_w1.p2.y - poly_w1.p1.y,
				                       poly_w1.p2.x - poly_w1.p1.x), 1,
				                atan2f(poly_w1.p2.y - poly_w1.p1.y,
				                       poly_w1.p2.x - poly_w1.p1.x), 1);

				ltime1 = lc.knots[0];
				ltime2 = lc.knots[1];

				std::vector<Point2f> right_curve_pts;
				right_curve_pts.push_back(Point2f(poly_w1.p3.x, poly_w1.p3.y));
				right_curve_pts.push_back(Point2f(poly_w2.p4.x, poly_w2.p4.y));

				rc =
				    SmoothCurve(right_curve_pts,
				                atan2f(poly_w1.p3.y - poly_w1.p4.y,
				                       poly_w1.p3.x - poly_w1.p4.x), 1,
				                atan2f(poly_w1.p3.y - poly_w1.p4.y,
				                       poly_w1.p3.x - poly_w1.p4.x), 1);

			} else {
				lc =
				    SmoothCurve(left_curve_pts,
				                atan2f(poly_w1.p2.y - poly_w1.p1.y,
				                       poly_w1.p2.x - poly_w1.p1.x), 1,
				                atan2f(poly_w2.p2.y - poly_w2.p1.y,
				                       poly_w2.p2.x - poly_w2.p1.x), 1);

				ltime1 = lc.knots[0];
				ltime2 = lc.knots[1];

				std::vector<Point2f> right_curve_pts;
				right_curve_pts.push_back(Point2f(poly_w1.p3.x, poly_w1.p3.y));
				right_curve_pts.push_back(Point2f(poly_w2.p4.x, poly_w2.p4.y));

				rc =
				    SmoothCurve(right_curve_pts,
				                atan2f(poly_w1.p3.y - poly_w1.p4.y,
				                       poly_w1.p3.x - poly_w1.p4.x), 1,
				                atan2f(poly_w2.p3.y - poly_w2.p4.y,
				                       poly_w2.p3.x - poly_w2.p4.x), 1);

			}
			rtime1 = rc.knots[0];
			rtime2 = rc.knots[1];

			//Make rest of lane
			WayPointNode midpoint = w2;
			midpoint.lane_width = (w1.lane_width + w2.lane_width) / 2.0;

			// Split rest of edge in half and call recursively.
			midpoint.map = ops.midpoint(w1.map, w2.map);

			float midtime = (time1 + time2) / 2;

			float lmidtime = (ltime1 + ltime2) / 2;
			float rmidtime = (rtime1 + rtime2) / 2;

			MakeLanePolygon(w1, midpoint, e, time1, midtime, c, false,
			                ltime1, lmidtime, lc, rtime1, rmidtime, rc);

			midpoint.id = w1.id;

			MakeLanePolygon(midpoint, w2, e, midtime, time2, c, false,
			                lmidtime, ltime2, lc, rmidtime, rtime2, rc);
		}

		// Now add final waypoint polygon
		poly_w2.poly_id = poly_id_counter;

		// Force last polygon before waypoint to touch waypoint.
		allPolys[poly_id_counter - 1].p2 = poly_w2.p1;
		allPolys[poly_id_counter - 1].p3 = poly_w2.p4;

		// Add the poly to the list
		poly_id_counter++;
		allPolys.push_back(poly_w2);

	}
	else
		// w1 and w2 aren't original waypoints for the edge -- this is a
		// recursive call.
	{

		//sqrtf(powf(w1_pt[0]-w2_pt[0],2) +
		//			  powf(w1_pt[1]-w2_pt[1],2));

		// After recursive calls, eventaully get two points really
		// close.  Closeness is determined by comparing Euclidean
		// distance to curve distance.

		float edist =
		    Euclidean::DistanceTo(w1.map, w2.map);

		float cdist = fmax(time2 - time1, 0.0);

		if (Epsilon::equal(cdist, 0.0) ||
		        Epsilon::equal(edist, 0.0) ||
		        cdist <= max_poly_size * edist / cdist)
		{

			poly newPoly;

			// Create the edges of the poly
			newPoly.p1 = allPolys[poly_id_counter - 1].p2;
			newPoly.p4 = allPolys[poly_id_counter - 1].p3;

			Point2f point2 = lc.evaluatePoint(ltime2);
			Point2f point3 = rc.evaluatePoint(rtime2);

			newPoly.p2.x = point2[0];
			newPoly.p2.y = point2[1];

			newPoly.p3.x = point3[0];
			newPoly.p3.y = point3[1];


			// Update some details
			newPoly.start_way.seg = w1.id.seg;
			newPoly.start_way.lane = w1.id.lane;
			newPoly.start_way.pt = w1.id.pt;
			newPoly.end_way.seg = w2.id.seg;
			newPoly.end_way.lane = w2.id.lane;
			newPoly.end_way.pt = w2.id.pt;
			newPoly.is_stop = false;
			newPoly.is_transition = false;
			newPoly.contains_way = false;
			newPoly.poly_id = poly_id_counter;
#if 0 //TODO
			newPoly.left_boundary = e.left_boundary;
			newPoly.right_boundary = e.right_boundary;
#endif

			// set initial heading based on map coordinates
			newPoly.heading = ops.PolyHeading(newPoly);
			MapXY cpt = ops.centerpoint(newPoly);
			newPoly.midpoint.x = cpt.x;
			newPoly.midpoint.y = cpt.y;
			newPoly.length = ops.getLength(newPoly);

			// Add the poly to the list
			poly_id_counter++;
			allPolys.push_back(newPoly);

		}
		else
		{
			// Make sure points are on curve, they were paased in as
			// Euclidean midpoints i nthe recursive call.
			w1.map.x = w1_pt[0];
			w1.map.y = w1_pt[1];
			w2.map.x = w2_pt[0];
			w2.map.y = w2_pt[1];

			WayPointNode midpoint = w2;
			midpoint.lane_width = (w1.lane_width + w2.lane_width) / 2.0;

			// Make midpoint for recursive call.
			midpoint.map.x = (w1.map.x + w2.map.x) / 2;
			midpoint.map.y = (w1.map.y + w2.map.y) / 2;

			float midtime = (time2 + time1) / 2;
			float lmidtime = (ltime1 + ltime2) / 2;
			float rmidtime = (rtime1 + rtime2) / 2;

			MakeLanePolygon(w1, midpoint, e, time1, midtime, c, false,
			                ltime1, lmidtime, lc, rtime1, rmidtime, rc);
			midpoint.id = w1.id;
			MakeLanePolygon(midpoint, w2, e, midtime, time2, c, false,
			                lmidtime, ltime2, lc, rmidtime, rtime2, rc);
		}
	}
}


void MapLanes::MakeTransitionPolygon(WayPointNode w1, WayPointNode w2,
                                     WayPointEdge e,
                                     float time1, float time2,
                                     SmoothCurve& c)
{
	// Assumes Transition edges come after lane edges in the edge list
	poly poly_w1, poly_w2;

	int index_w1 = -1;
	int index_w2 = -1;

	//Transitions assume that 1 meter polygons around waypoints exist.  Look
	//them up so the new polygons can be attached at the ends.

	for (uint i = 0; i < allPolys.size() && (index_w1 < 0 || index_w2 < 0); i++)
		if (allPolys[i].contains_way) {
			if (ElementID(allPolys[i].start_way) == w1.id)
			{
				poly_w1 = allPolys[i];
				index_w1 = i;
			}
			else if (ElementID(allPolys[i].start_way) == w2.id)
			{
				poly_w2 = allPolys[i];
				index_w2 = i;
			}
		}

	if (index_w1 < 0)
	{
		Point2f w1_pt = c.evaluatePoint(time1);
		poly_w1 = build_waypoint_poly(w1, e, w1_pt, time1, c);
	}

	time1 += way_poly_size;

	if (index_w2 < 0)
	{
		Point2f w2_pt = c.evaluatePoint(time2);
		poly_w2 = build_waypoint_poly(w2, e, w2_pt, time2, c);

	}

	time2 -= way_poly_size;

	float cdist = fmax(0.0, time2 - time1);

	w1.map = ops.midpoint(poly_w1.p2, poly_w1.p3);
	w2.map = ops.midpoint(poly_w2.p1, poly_w2.p4);

	float edist =
	    Euclidean::DistanceTo(w1.map, w2.map);


	// Probably always true, but is two waypoints are REALLY close
	// attach them and quit (in ELSE).
	if (cdist > Epsilon::float_value && edist > Epsilon::float_value)
	{
		// Do recursive call on transition the same way we do on and edge in a
		// lane.

		std::vector<Point2f> left_curve_pts;
		left_curve_pts.push_back(Point2f(poly_w1.p2.x, poly_w1.p2.y));
		left_curve_pts.push_back(Point2f(poly_w2.p1.x, poly_w2.p1.y));

		SmoothCurve lc =
		    SmoothCurve(left_curve_pts,
		                atan2f(poly_w1.p2.y - poly_w1.p1.y,
		                       poly_w1.p2.x - poly_w1.p1.x), 1,
		                atan2f(poly_w2.p2.y - poly_w2.p1.y,
		                       poly_w2.p2.x - poly_w2.p1.x), 1);

		float ltime1 = lc.knots[0];
		float ltime2 = lc.knots[1];

		std::vector<Point2f> right_curve_pts;
		right_curve_pts.push_back(Point2f(poly_w1.p3.x, poly_w1.p3.y));
		right_curve_pts.push_back(Point2f(poly_w2.p4.x, poly_w2.p4.y));

		SmoothCurve rc =
		    SmoothCurve(right_curve_pts,
		                atan2f(poly_w1.p3.y - poly_w1.p4.y,
		                       poly_w1.p3.x - poly_w1.p4.x), 1,
		                atan2f(poly_w2.p3.y - poly_w2.p4.y,
		                       poly_w2.p3.x - poly_w2.p4.x), 1);


		float rtime1 = rc.knots[0];
		float rtime2 = rc.knots[1];

		//Make rest of lane
		WayPointNode midpoint = w2;
		midpoint.lane_width = (w1.lane_width + w2.lane_width) / 2.0;

		// Split rest of edge in half and call recursively.
		midpoint.map = ops.midpoint(w1.map, w2.map);

		float midtime = (time1 + time2) / 2;
		float lmidtime = (ltime1 + ltime2) / 2;
		float rmidtime = (rtime1 + rtime2) / 2;

		int next_polyid = poly_id_counter;

		e.left_boundary = UNDEFINED;
		e.right_boundary = UNDEFINED;

		transition = true;
		trans_index = index_w1;

		MakeLanePolygon(w1, midpoint, e, time1, midtime, c, false,
		                ltime1, lmidtime, lc, rtime1, rmidtime, rc);

		// Ensure start of transition attaches to polygon around starting
		// waypoint.

		// Remove for end of transition polygons
		allPolys[next_polyid].p1 = poly_w1.p2;
		allPolys[next_polyid].p4 = poly_w1.p3;

		midpoint.id = w1.id;

		MakeLanePolygon(midpoint, w2, e,  midtime, time2, c, false,
		                lmidtime, ltime2, lc, rmidtime, rtime2, rc);
		// Ensure end of transition attaches to polygon around ending
		// waypoint.

		// Remove for end of transition polygons
		allPolys[poly_id_counter - 1].p2 = poly_w2.p1;
		allPolys[poly_id_counter - 1].p3 = poly_w2.p4;

		for (uint i = next_polyid; i < allPolys.size(); i++)
			allPolys[i].is_transition = true;
	}
	else if (index_w1 >= 0 && index_w2 >= 0)
	{
		allPolys[index_w1].p2 = allPolys[index_w2].p1;
		allPolys[index_w1].p3 = allPolys[index_w2].p4;
	}
}

void MapLanes::UpdatePoly(polyUpdate upPoly, float rrX, float rrY, float rrOri)
{
	if (upPoly.poly_id <= 0 || upPoly.poly_id >= (int)filtPolys.size()) {
		return;
	}
	if (upPoly.distance < 3.0) return;
	FilteredPolygon* filt = &(filtPolys.at(upPoly.poly_id));
	poly curr = filt->GetPolygon();

	// Don't break waypoints !
	if (upPoly.poly_id <= 0 || upPoly.poly_id >= (int)filtPolys.size()) {
		return;
	}
	//printf("Good %i \n",upPoly.poly_id);

	//printf("1 %i %lf %lf\n",upPoly.poly_id,upPoly.distance,upPoly.bearing);
	poly prev = (filtPolys.at(upPoly.poly_id - 1)).GetPolygon();
	poly next = (filtPolys.at(upPoly.poly_id + 1)).GetPolygon();
	// Don't update the bottom points if they touch a waypoint
	if (prev.contains_way && (upPoly.point_id == 0 || upPoly.point_id == 3)) return;
	// Don't update the top points if they touch a waypoint
	if (next.contains_way && (upPoly.point_id == 1 || upPoly.point_id == 2)) return;

	//static gaussian g1(0.0,3.0);
	//upPoly.distance=upPoly.distance+g1.get_sample_1D();
	filt->UpdatePoint(upPoly.point_id, upPoly.distance, upPoly.bearing, upPoly.confidence, rrX, rrY, Normalise_PI(rrOri + PI));

#ifdef DEBUGMAP
	WritePolygonToDebugFile(upPoly.poly_id);
#endif

	int point = 0;
	if ((upPoly.point_id == 0 || upPoly.point_id == 3) && curr.poly_id == prev.poly_id + 1 && curr.start_way.lane == prev.start_way.lane && curr.start_way.seg == prev.start_way.seg) {
		FilteredPolygon* temp = &(filtPolys.at(prev.poly_id));
		if (upPoly.point_id == 0) point = 1;
		if (upPoly.point_id == 3) point = 2;
		temp->UpdatePoint(point, upPoly.distance, upPoly.bearing, upPoly.confidence, rrX, rrY, Normalise_PI(rrOri + PI));

#ifdef DEBUGMAP
		WritePolygonToDebugFile(prev.poly_id);
#endif
	}
	if ((upPoly.point_id == 1 || upPoly.point_id == 2) && curr.poly_id == next.poly_id - 1 && curr.start_way.lane == next.start_way.lane && curr.start_way.seg == next.start_way.seg) {
		FilteredPolygon* temp = &(filtPolys.at(next.poly_id));
		if (upPoly.point_id == 1) point = 0;
		if (upPoly.point_id == 2) point = 3;
		temp->UpdatePoint(point, upPoly.distance, upPoly.bearing, upPoly.confidence, rrX, rrY, Normalise_PI(rrOri + PI));

#ifdef DEBUGMAP
		WritePolygonToDebugFile(next.poly_id);
#endif
	}
}

void MapLanes::UpdateWithCurrent(int i) {
	static gaussian g1(0.0, 1.0);
	FilteredPolygon* filt = &(filtPolys.at(i));
	poly temp2 = filtPolys.at(i).GetPolygon();
	if (temp2.is_transition || temp2.contains_way) return;

	float angle = AngleFromXY(rX, rY, rOri, temp2.p1.x, temp2.p1.y);
	float distU = DistFromXY(rX, rY, temp2.p1.x, temp2.p1.y);
	if (distU > 5 && distU < 80 && fabs(angle) < 0.2) filt->UpdatePoint(0, distU + g1.get_sample_1D(), angle, 1.0, rX, rY, rOri);

	angle = AngleFromXY(rX, rY, rOri, temp2.p2.x, temp2.p2.y);
	distU = DistFromXY(rX, rY, temp2.p2.x, temp2.p2.y);
	if (distU > 5 && distU < 80 && fabs(angle) < 0.2) filt->UpdatePoint(1, distU + g1.get_sample_1D(), angle, 1.0, rX, rY, rOri);

	angle = AngleFromXY(rX, rY, rOri, temp2.p3.x, temp2.p3.y);
	distU = DistFromXY(rX, rY, temp2.p3.x, temp2.p3.y);
	if (distU > 5 && distU < 80 && fabs(angle) < 0.2) filt->UpdatePoint(2, distU + g1.get_sample_1D(), angle, 1.0, rX, rY, rOri);

	angle = AngleFromXY(rX, rY, rOri, temp2.p4.x, temp2.p4.y);
	distU = DistFromXY(rX, rY, temp2.p4.x, temp2.p4.y);
	if (distU > 5 && distU < 80 && fabs(angle) < 0.2) filt->UpdatePoint(3, distU + g1.get_sample_1D(), angle, 1.0, rX, rY, rOri);
}


void MapLanes::testDraw(bool with_trans)
{
	ZonePerimeterList empty_zones;
	MapLanes::testDraw(with_trans, empty_zones, false);
}

//test function which outputs all polygons to a pgm image.
void MapLanes::testDraw(bool with_trans, const ZonePerimeterList &zones, bool svg_format)
{
	float max_x = -FLT_MAX;
	float min_x = FLT_MAX;
	float max_y = -FLT_MAX;
	float min_y = FLT_MAX;

	FILE* gpsFile = fopen("gps.kml", "wb");

	fprintf(gpsFile, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n <kml xmlns=\"http://earth.google.com/kml/2.2\">\n <Document>\n<name>Maplanes Polygon centres</name>\n<description>Path of the polygons</description>\n<Style id=\"yellowLineGreenPoly\">\n<LineStyle>\n<color>7f00ffff</color>\n<width>4</width>\n</LineStyle>\n<PolyStyle>\n<color>7f00ff00</color>\n</PolyStyle>\n</Style>\n<Placemark>\n<name>Absolute Extruded</name>\n<description>Transparent green wall with yellow outlines</description>\n<styleUrl>#yellowLineGreenPoly</styleUrl>\n<LineString>\n<extrude>1</extrude>\n<tessellate>1</tessellate>\n<altitudeMode>clampToGround</altitudeMode>\n<coordinates>\n");

	float yOff = 7.5;//5.17;
	float xOff = 2.9; //2.89;

	for (int i = 0; i < (int)filtPolys.size(); i++)
	{
		poly node = (filtPolys.at(i).GetPolygon());
		double lon, lat;
		UTM::UTMtoLL(cY + node.midpoint.y + yOff, cX + node.midpoint.x + xOff,
		             "11S", lon, lat);
		fprintf(gpsFile, "%lf,%lf,0\n", lat, lon);

		max_x = fmax(fmax(fmax(fmax(node.p1.x, node.p2.x),
		                       node.p3.x), node.p4.x), max_x);
		max_y = fmax(fmax(fmax(fmax(node.p1.y, node.p2.y),
		                       node.p3.y), node.p4.y), max_y);
		min_x = fmin(fmin(fmin(fmin(node.p1.x, node.p2.x),
		                       node.p3.x), node.p4.x), min_x);
		min_y = fmin(fmin(fmin(fmin(node.p1.y, node.p2.y),
		                       node.p3.y), node.p4.y), min_y);
	}
	fprintf(gpsFile,
	        "</coordinates>\n</LineString>\n</Placemark>\n</Document>\n</kml>");
	fclose(gpsFile);

	// find bounding box for coordinates of all way-points in graph
	for (uint i = 0; i < graph->nodes_size; i++)
	{
		max_x = fmax(graph->nodes[i].map.x, max_x);
		max_y = fmax(graph->nodes[i].map.y, max_y);
		min_x = fmin(graph->nodes[i].map.x, min_x);
		min_y = fmin(graph->nodes[i].map.y, min_y);
	}

	int xsize = (int)ceil(max_x - min_x);
	int ysize = (int)ceil(max_y - min_y);

	if (xsize < 240)
	{
		min_x -= (240 - xsize) / 2;
		max_x += (240 - xsize) / 2;
		xsize = 240;
	}

	if (ysize < 168)
	{
		min_y -= (168 - ysize) / 2;
		max_y += (168 - ysize) / 2;
		ysize = 168;
	}

	float ratio = 3;
	float image_size = xsize * ysize * DEFAULT_RATIO * DEFAULT_RATIO;
	if (image_size > (2048.0 * 2048))
		ratio = sqrtf((2047 * 2047.0) / (xsize * ysize));

	std::cout << "World size: " << xsize << "," << ysize << std::endl;
	std::cout << "Image size: " << xsize*ratio << "," << ysize*ratio << std::endl;

	//initialize VisualLanes
	DrawLanes* edgeImage = new DrawLanes(xsize, ysize, ratio);
	DrawLanes* polyImage = new DrawLanes(xsize, ysize, ratio);

	int imageWidth = int(ceil(xsize * ratio));
	int imageHeight = int(ceil(ysize * ratio));
	svg::Layout layout(svg::Dimensions(imageWidth, imageHeight), svg::Layout::TopLeft, 1, svg::Point(0, 0));
	svg::Document doc("sample.svg", layout);


#if 0 //TODO
	for (unsigned i = 0; i < zones.size(); i++)
	{
		polyImage->addZone(zones[i], min_x, max_y);
	}
#endif


	svg::Color blueColor = svg::Color(svg::Color::Blue);
	svg::Color redColor = svg::Color(svg::Color::Red);
	svg::Color greenColor = svg::Color(svg::Color::Green);


	svg::Stroke lineStrokeBlue = svg::Stroke(4, blueColor);
	svg::Stroke lineStrokeRed = svg::Stroke(4, redColor);
	svg::Stroke lineStrokeGreen = svg::Stroke(4, greenColor);
	
	svg::Fill greenFill = svg::Fill(svg::Color::Green);
	svg::Fill redFill = svg::Fill(svg::Color::Red);
	svg::Fill blueFill = svg::Fill(svg::Color::Blue);
	svg::Fill orangeFill = svg::Fill(svg::Color::Orange);

	//draw polygons
	for (int i = 0; i < (int)filtPolys.size(); i++)
	{
		poly temp = filtPolys.at(i).GetPolygon();

		if (!svg_format) {
			polyImage->addPoly(temp.p1.x - min_x, temp.p2.x - min_x,
			                   temp.p3.x - min_x, temp.p4.x - min_x,
			                   max_y - temp.p1.y, max_y - temp.p2.y,
			                   max_y - temp.p3.y, max_y - temp.p4.y,
			                   temp.is_stop,
			                   temp.is_transition && !with_trans);
		}
		else {
			if (!(temp.is_transition && !with_trans)) {
				doc.operator << (svg::Line(svg::Point((temp.p1.x - min_x) * ratio, (max_y - temp.p1.y) * ratio),
				                           svg::Point((temp.p2.x - min_x) * ratio, (max_y - temp.p2.y) * ratio),
				                           lineStrokeBlue));
				doc.operator << (svg::Line(svg::Point((temp.p3.x - min_x) * ratio, (max_y - temp.p3.y) * ratio),
				                           svg::Point((temp.p4.x - min_x) * ratio, (max_y - temp.p4.y) * ratio),
				                           lineStrokeBlue));
			}
			if (temp.is_stop) {
				doc.operator << (svg::Line(svg::Point((temp.p1.x - min_x) * ratio, (max_y - temp.p1.y) * ratio),
				                           svg::Point((temp.p4.x - min_x) * ratio, (max_y - temp.p4.y) * ratio),
				                           lineStrokeRed));
				doc.operator << (svg::Line(svg::Point((temp.p2.x - min_x) * ratio, (max_y - temp.p2.y) * ratio),
				                           svg::Point((temp.p3.x - min_x) * ratio, (max_y - temp.p3.y) * ratio),
				                           lineStrokeRed));
			}
		}
	}

	// Add Waypoints to WayPointImage
	for (uint i = 0; i < graph->edges_size; i++)
	{
		WayPointNode w1 = graph->nodes[graph->edges[i].startnode_index];
		WayPointNode w2 = graph->nodes[graph->edges[i].endnode_index];

		if (!svg_format) {
			edgeImage->addTrace(w1.map.x - min_x, max_y - w1.map.y,
			                    w2.map.x - min_x, max_y - w2.map.y);
		}
		else {
			doc.operator << (svg::Line(svg::Point((w1.map.x - min_x) * ratio, (max_y - w1.map.y) * ratio),
			                           svg::Point((w2.map.x - min_x) * ratio, (max_y - w2.map.y) * ratio),
			                           lineStrokeGreen));
		}
	}
	for (uint i = 0; i < graph->nodes_size; i++)
	{
		WayPointNode w1 = graph->nodes[i];

		if (!svg_format) {
			polyImage->addWay(w1.map.x - min_x, max_y - w1.map.y);
		}
		else {
			if(w1.is_exit){
				doc.operator << (svg::Circle(svg::Point((w1.map.x - min_x) * ratio, (max_y - w1.map.y) * ratio ), 5 * ratio, redFill));
			}
			else if(w1.is_entry){
				doc.operator << (svg::Circle(svg::Point((w1.map.x - min_x) * ratio, (max_y - w1.map.y) * ratio ), 5 * ratio, blueFill));
			}
			else{
				doc.operator << (svg::Circle(svg::Point((w1.map.x - min_x) * ratio, (max_y - w1.map.y) * ratio ), 5 * ratio, greenFill));
			}
		}
	}

	bool drawRobot = false;
	if (drawRobot) polyImage->addRobot(rX - min_x, max_y - rY);
	//output image

	if (!svg_format) {
		printf("Writing way-point image");
		edgeImage->savePGM("wayImage.ppm");

		char* temp = new char[255];
		sprintf(temp, "polyImage%i.ppm", writecounter);
		writecounter++;

		printf("Writing polygons image");
		polyImage->savePGM(temp);
		delete temp;
	}
	else {
		printf("Generating SVG file.\n");
		doc.save();
	}
}


#ifdef DEBUGMAP
void MapLanes::WritePolygonToDebugFile(int i) {
	poly node = (filtPolys.at(i).GetPolygon());
	fprintf(debugFile, "%i %lf %lf %lf %lf %lf %lf %lf %lf %lf %lf %lf %i %i\n",
	        i, node.p1.x, node.p1.y, node.p2.x, node.p2.y,
	        node.p3.x, node.p3.y, node.p4.x, node.p4.y,
	        node.midpoint.x, node.midpoint.y, node.length,
	        node.left_boundary, node.right_boundary);
}
#endif

bool MapLanes::WriteToFile(char* fName) {
	FILE* f = fopen(fName, "wb");
	if (f == NULL) {
		printf("MapLanes::WriteToFile Failed - Can't open file");
		return false;
	}
	int sizeAll = allPolys.size();
	int sizeFilt = filtPolys.size();

	int ret = fprintf(f, "%i %i\n", sizeAll, sizeFilt);
	if (ret < 1) {
		printf("MapLanes::SaveToFile Failed - Failed size write");
		return false;
	}

	for (int i = 0; i < sizeAll; i++)
	{
		ret = fwrite(&(allPolys.at(i)), sizeof(poly), 1, f);
		if (ret < 1) {
			printf("MapLanes::WriteToFile Failed - Failed poly write");
			return false;
		}
	}
	for (int i = 0; i < sizeFilt; i++)
	{
		ret = fwrite(&(filtPolys.at(i)), sizeof(FilteredPolygon), 1, f);
		if (ret < 1) {
			printf("MapLanes::WriteToFile Failed - Failed FilteredPoylgon write");
			return false;
		}
	}
	fclose(f);
	return true;
}

bool MapLanes::LoadFromFile(char* fName) {
	FILE* f = fopen(fName, "rb");

	if (f == NULL) {
		printf("MapLanes::LoadFromFile Failed - Can't open file");
		return false;
	}

	int sizeAll = 0;
	int sizeFilt = 0;

	int ret = fscanf(f, "%i %i\n", &sizeAll, &sizeFilt);

	if (ret < 1) {
		printf("MapLanes::LoadFromFile Failed - Failed size read");
		allPolys.clear();
		filtPolys.clear();
		return false;
	}
	if (sizeAll < 0 || sizeFilt < 0) {
		printf("MapLanes::LoadFromFile Failed - Sizes < 0");
		allPolys.clear();
		filtPolys.clear();
		return false;
	}

	// Check filesize
	fpos_t position;
	fgetpos (f, &position);
	long now = ftell(f);
	fseek (f, 0, SEEK_END);
	long size = ftell(f) - now;
	fsetpos(f, &position);
	int expected = (sizeAll * sizeof(poly)) + (sizeFilt * sizeof(FilteredPolygon));
	if (size != expected) {
		printf("MapLanes::LoadFromFile Failed - Incorred File Size");
		allPolys.clear();
		filtPolys.clear();
		return false;
	}

	allPolys.clear();
	filtPolys.clear();

	poly p;
	for (int i = 0; i < sizeAll; i++)
	{
		ret = fread(&p, sizeof(poly), 1, f);
		if (ret < 1) {
			printf("MapLanes::LoadFromFile Failed - Failed poly read");
			allPolys.clear();
			filtPolys.clear();
			return false;
		}
		allPolys.push_back(p);
	}
	FilteredPolygon fp;
	for (int i = 0; i < sizeFilt; i++)
	{
		ret = fread(&fp, sizeof(FilteredPolygon), 1, f);
		if (ret < 1) {
			printf("MapLanes::LoadFromFile Failed - Failed FilteredPolygon read");
			allPolys.clear();
			filtPolys.clear();
			return false;
		}
		filtPolys.push_back(fp);
	}
	fclose(f);
	return true;
}
