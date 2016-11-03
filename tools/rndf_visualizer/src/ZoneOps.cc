
#include <unistd.h>
#include <float.h>
#include <vector>
#include <map>

#include <epsilon.h>

#include <rndf_visualizer/ZoneOps.h>
#include <rndf_visualizer/RNDF.h>
#include <rndf_visualizer/types.h>
#include <rndf_visualizer/RNDF.h>
#include <rndf_visualizer/coordinates.h>
#include <rndf_visualizer/euclidean_distance.h>
#include <rndf_visualizer/PolyOps.h>
#include <rndf_visualizer/Graph.h>

ZoneManager::ZoneManager(const ZonePerimeter &_zone,
			 float _safety_radius,
			 float _scale,
			 int _max_cells,
			 bool _write_graph,
			 ElementID _starting_id,
			 MapXY _lower_left,
			 MapXY _upper_right) :
  starting_id(_starting_id),
  write_graph(_write_graph),
  zone(_zone),
  safety_radius(_safety_radius),
  ll(_lower_left),
  ur(_upper_right),
  scale(fmax(_scale, sqrt((fabs(ur.x-ll.x)*fabs(ur.y-ll.y))/(_max_cells))))
{
  
  perimeter_points.clear();

  for(unsigned i = 0; i < zone.perimeter_points.size(); i++) {
    MapXY before(zone.perimeter_points.at(i).map);
    MapXY point(zone.perimeter_points.at((i+1)
					 %zone.perimeter_points.size()).map);
    ZoneOps::add_densely(perimeter_points, before, point, scale/3);
  }
}

#if 0
void ZoneManager::build_graph(const ObstacleList &obstacles,
			      const MapXY &start)
{
  //gmanager.clear_grid();

  for(unsigned i = 0; i < perimeter_points.size(); i++)
    gmanager.mark_point(perimeter_points[i]);

  for(unsigned i = 0; i < zone.perimeter_points.size(); i++) {
    if(zone.perimeter_points.at(i).is_entry ||
       zone.perimeter_points.at(i).is_exit)
      gmanager.unmark_box(zone.perimeter_points.at(i).map,
			  (int)ceil(2.0/scale));
  }
  
  for(unsigned i = 0; i < obstacles.size(); i++) {
    gmanager.mark_point(obstacles[i]);
  }

  int start_x, start_y = 0;
  gmanager.transform(start_x, start_y, start);

  evg_thin thin(gmanager.grid,
		1, FLT_MAX,
		false, true,
		start_x, start_y);
  
  thin.reset();
  thin.set_location(start_x, start_y);
  skeleton_type skel=thin.generate_skeleton();

  nodes.clear();
  edges.clear();

  for(unsigned i = 0; i < skel.size(); i++) {
    WayPointNode node;
    node.map = gmanager.reverse_transform(skel[i].x, skel[i].y);
    node.index = i;
    node.lane_width = (skel[i].radius*scale);
    node.id.seg = 0;
    node.id.lane = 0;
    node.id.pt = i + 1;
    nodes.push_back(node);
  }

  for(unsigned i = 0; i < skel.size(); i++) {
    for(unsigned j = 0; j < skel.at(i).children.size(); j++) {
      WayPointEdge edge(nodes.at(i),
			nodes.at(skel.at(i).children.at(j)),
			UNDEFINED,
			UNDEFINED,
			false);
      edge.speed_max = edge.speed_min = 0;
      // Distance to the nearest obstacle
      edge.distance = (skel.at(i).radius*scale);
      edges.push_back(edge);
      edges.push_back(edge.reverse());
    }
  }
}

WayPointNodeList ZoneManager::path_through_zone(const ObstacleList &obstacles,
						MapXY start,
						MapXY end) {
  WayPointNodeList path_nodes;

  ObstacleList filtered_obstacles = ZoneOps::filter_obstacles(obstacles, zone);

  build_graph(filtered_obstacles, start);
  ZoneOps::filter_nodes_and_edges(nodes, edges, safety_radius);
  unsigned num_nodes = nodes.size();
  unsigned num_edges = edges.size();
    
  WayPointNode c_nodes[num_nodes];
  WayPointEdge c_edges[num_edges];
  
  for(unsigned i = 0; i < num_nodes; i++)
    c_nodes[i] = nodes[i];
  
  for(unsigned i = 0; i < num_edges; i++)
    c_edges[i] = edges[i];
  
  Graph *g = new Graph(num_nodes, num_edges, c_nodes, c_edges);
  
  ZoneOps::correct_edge_distances(*g);

  if(write_graph)
    ZoneOps::print_graph_as_voronoi(*g);
  
  bool can_go_straight = false;
  for(unsigned i = 0; i < g->nodes_size; i++) {
    if((Euclidean::DistanceTo(g->nodes[i].map, start) <
	g->nodes[i].lane_width) &&
       (Euclidean::DistanceTo(g->nodes[i].map, end) <
	g->nodes[i].lane_width))
      can_go_straight = true;
  }
  
  if(!can_go_straight) {
    WayPointNode *start_node = g->get_closest_node_within_radius(start);
    WayPointNode *end_node = g->get_closest_node_within_radius(end);
    
    if(start_node == NULL)
      start_node = g->get_closest_node(start);
    
    if(end_node == NULL)
      end_node = g->get_closest_node(end);
    
    if(start_node != NULL && end_node != NULL) {
      int start_index = start_node->index;
      int end_index = end_node->index;
      
      WayPointEdgeList path = GraphSearch::astar_search(*g,
							start_index,
							end_index);
      
      path_nodes = GraphSearch::edge_list_to_node_list(*g, path);
    }
  }
  delete g;
  return path_nodes;
}

#define free_and_set_to_null(ptr) { free(ptr); (ptr) = NULL; }


int ZoneOps::filter_nodes_and_edges(WayPointNodeList &nodes,
				    WayPointEdgeList &edges,
				    float safety_radius) {
  WayPointNodeList::iterator node = nodes.begin();
  while(node < nodes.end()) {
    if(node->lane_width < safety_radius) {
      WayPointEdgeList::iterator edge = edges.begin();
      while(edge < edges.end()) {
	if(edge->distance < safety_radius ||
	   edge->startnode_index == node->index ||
	   edge->endnode_index == node->index)
	  edges.erase(edge);
	else
	  edge++;
      }
      nodes.erase(node);
    }
    else
      node++;
  }
  return 0;
}

void ZoneOps::print_graph_as_voronoi(Graph &graph) {
  std::map<int,int> index_map;
  FILE *fh = fopen("/tmp/graph.v.node","w");
  fprintf(fh, "%d 2 1 0\n", graph.nodes_size);
  for(int i = 0; i < (int) graph.nodes_size; i++) {
    fprintf(fh, "%d %.8f %.8f %.8f\n",
	    i, 
	    graph.nodes[i].map.x,
	    graph.nodes[i].map.y,
	    graph.nodes[i].lane_width);
    index_map[graph.nodes[i].index] = i;
  }
  fclose(fh);

  fh = fopen("/tmp/graph.v.edge","w");
  fprintf(fh, "%d 1\n", graph.edges_size);
  for(int i = 0; i < (int) graph.edges_size; i++) {
    fprintf(fh, "%d %d %d %.8f\n",
	    i, 
	    index_map[graph.edges[i].startnode_index],
	    index_map[graph.edges[i].endnode_index],
	    graph.edges[i].distance);
  }
  fclose(fh);
}


int ZoneOps::voronoi_from_evg_thin(WayPointNodeList &nodes,
				   WayPointEdgeList &edges,
				   const ZonePerimeter &zone,
				   float safety_radius,
				   const ObstacleList &obstacles,
				   const MapXY &start,
				   bool write_graph,
				   bool write_image,
				   float scale,
				   int max_cells) {
  if(zone.perimeter_points.size() < 3)
    return 1;
  
  MapXY ll = zone.perimeter_points[0].map;
  MapXY ur = zone.perimeter_points[0].map;
  
  std::vector<MapXY> points;

  for(unsigned i = 0; i < zone.perimeter_points.size(); i++) {
    MapXY before(zone.perimeter_points.at(i).map);
    MapXY point(zone.perimeter_points.at((i+1)%zone.perimeter_points.size()).map);
    // sampling at scale should be enough, but seeing weird stuff, so
    // divide by ten to make sure
    add_densely(points, before, point, scale/3);
  }

  expand_bounding_box(points, ll, ur);
  
  float width = fabs(ur.x-ll.x);
  float height = fabs(ur.y-ll.y);
  
  scale = fmax(scale, sqrt((width*height)/(max_cells)));
  
  grid_manager grid(scale, ll, ur);
  
  for(unsigned i = 0; i < points.size(); i++)
    grid.mark_point(points[i]);

  for(unsigned i = 0; i < zone.perimeter_points.size(); i++) {
    if(zone.perimeter_points.at(i).is_entry ||
       zone.perimeter_points.at(i).is_exit)
      grid.unmark_box(zone.perimeter_points.at(i).map, (int)ceil(2.0/scale));
  }
  
  for(unsigned i = 0; i < obstacles.size(); i++)
    grid.mark_point(obstacles[i]);
  
  int start_x, start_y = 0;
  grid.transform(start_x, start_y, start);
  
  evg_thin thin(grid.grid,
		1, // distance_min
		FLT_MAX, // distance_max
		false, // no pruning
		true, // use "robot close"
		start_x, start_y);
  
  skeleton_type skel=thin.generate_skeleton();

  /*
    if(write_image) {
    fileio IO;
    IO.save_file(skel,"/tmp/evg.pgm");  
    }
  */
  
  for(unsigned i = 0; i < skel.size(); i++) {
    WayPointNode node;
    node.map = grid.reverse_transform(skel[i].x, skel[i].y);
    node.index = i;
    node.lane_width = (skel[i].radius*scale);
    node.id.seg = 0;
    node.id.lane = 0;
    node.id.pt = i + 1;
    nodes.push_back(node);
  }

  for(unsigned i = 0; i < skel.size(); i++) {
    for(unsigned j = 0; j < skel.at(i).children.size(); j++) {
      WayPointEdge edge(nodes.at(i),
			nodes.at(skel.at(i).children.at(j)),
			UNDEFINED,
			UNDEFINED,
			false);
      edge.speed_max = edge.speed_min = 0;
      // Distance to the nearest obstacle
      edge.distance = (skel.at(i).radius*scale);
      edges.push_back(edge);
      edges.push_back(edge.reverse());
    }
  }

  return 0;
}


WayPointNodeList ZoneOps::path_through_zone(const ZonePerimeter &zone,
					    float perimeter_sample,
					    float safety_radius,
					    const ObstacleList &obstacles,
					    MapXY start,
					    MapXY end,
					    bool write_graph,
					    bool write_poly,
					    bool write_obstacles,
					    float scale,
					    int max_cells) {
  WayPointNodeList path_nodes;
  WayPointNodeList nodes;
  WayPointEdgeList edges;

  int rv = -1;

  ObstacleList filtered_obstacles = filter_obstacles(obstacles, zone);

  if(0) {
  rv = voronoi_from_trilibrary(nodes,
			       edges,
			       zone,
			       perimeter_sample,
			       safety_radius,
			       filtered_obstacles,
			       write_graph,
			       write_poly,
			       write_obstacles);
  } else {
    rv = voronoi_from_evg_thin(nodes,
			       edges,
			       zone,
			       safety_radius,
			       filtered_obstacles,
			       start,
			       write_graph,
			       write_poly,
			       scale,
			       max_cells);
  }
  if(rv == 0) {
    filter_nodes_and_edges(nodes, edges, safety_radius);
   
    unsigned num_nodes = nodes.size();
    unsigned num_edges = edges.size();
    
    WayPointNode c_nodes[num_nodes];
    WayPointEdge c_edges[num_edges];
    
    for(unsigned i = 0; i < num_nodes; i++)
      c_nodes[i] = nodes[i];
    
    for(unsigned i = 0; i < num_edges; i++)
      c_edges[i] = edges[i];
    
    Graph *g = new Graph(num_nodes, num_edges, c_nodes, c_edges);
    
    build_new_graph(nodes, edges, *g);
    
    if(write_graph)
      print_graph_as_voronoi(*g);
    
    bool can_go_straight = false;
    for(unsigned i = 0; i < g->nodes_size; i++) {
      if((Euclidean::DistanceTo(g->nodes[i].map, start) <
	  g->nodes[i].lane_width) &&
	 (Euclidean::DistanceTo(g->nodes[i].map, end) <
	  g->nodes[i].lane_width))
	can_go_straight = true;
    }
    
    if(!can_go_straight) {
      WayPointNode *start_node = g->get_closest_node_within_radius(start);
      WayPointNode *end_node = g->get_closest_node_within_radius(end);
      
      if(start_node == NULL)
	start_node = g->get_closest_node(start);

      if(end_node == NULL)
	end_node = g->get_closest_node(end);
      
      if(start_node != NULL && end_node != NULL) {
	int start_index = start_node->index;
	int end_index = end_node->index;
	
	WayPointEdgeList path = GraphSearch::astar_search(*g,
							  start_index,
							  end_index);
	
	path_nodes = GraphSearch::edge_list_to_node_list(*g, path);
      }
    }
    delete g;
  }
  return path_nodes;
}
#endif

void ZoneOps::add_densely(std::vector<MapXY> &points,
			  const MapXY &p1,
			  const MapXY &p2,
			  const float &max_spacing) {
  
  for(float i = 0; i < 1; i += max_spacing/Euclidean::DistanceTo(p1, p2)) {
    MapXY n = p1;
    n.x += i * (p2.x - p1.x);
    n.y += i * (p2.y - p1.y);
    points.push_back(n);
  }
  
  /*
  if(Euclidean::DistanceTo(p1, p2) < max_spacing)
    points.push_back(p2);
  else {
    MapXY mid((p1.x+p2.x)/2.0, (p1.y+p2.y)/2.0);
    add_densely(points, p1, mid, max_spacing);
    add_densely(points, mid, p2, max_spacing);
  }  
  */
}

#if 0 // maybe later
ObstacleList ZoneOps::filter_obstacles(const ObstacleList &obstacles,
				       const ZonePerimeter &zone)
{
  ObstacleList f;
  for(unsigned i = 0; i < obstacles.size(); i++) {
    if(point_in_zone(zone, obstacles[i]))
      f.push_back(obstacles[i]);
  }
    return f;
}
#endif

void ZoneOps::build_new_graph(const WayPointNodeList &nodes,
			      const WayPointEdgeList &edges,
			      Graph& g)
{
  
  unsigned num_edges = edges.size();

  for(uint i = 0; i < num_edges; i++) {
    WayPointNode* start=g.get_node_by_index(g.edges[i].startnode_index);
    WayPointNode* end=g.get_node_by_index(g.edges[i].endnode_index);
    
    if(start != NULL && end != NULL)      
      g.edges[i].distance=Euclidean::DistanceTo(start->map,end->map);
  }

}

#if 0 // maybe later
void ZoneOps::correct_edge_distances(Graph& g)
{
  for(uint i = 0; i < g.edges.size(); i++) {
    WayPointNode* start=g.get_node_by_index(g.edges[i].startnode_index);
    WayPointNode* end=g.get_node_by_index(g.edges[i].endnode_index);
    
    if(start != NULL && end != NULL)      
      g.edges[i].distance=Euclidean::DistanceTo(start->map,end->map);
  }
}

ZonePerimeter ZoneOps::build_fake_zone(const std::vector<MapXY>
				       &points_to_include,
				       float border_width)
{
  ZonePerimeter zone;
  zone.zone_id = 0;

  if(points_to_include.size() < 1)
    return zone;
  
  MapXY upper_right = points_to_include[0];
  MapXY lower_left = points_to_include[0];

  expand_bounding_box(points_to_include, lower_left, upper_right);

  // Expand rectangle by border_width
  lower_left.x -= border_width;
  lower_left.y -= border_width;
  upper_right.x += border_width;
  upper_right.y += border_width;

  zone.perimeter_points.push_back(WayPointNode(MapXY(upper_right.x,
						     lower_left.y)));
  zone.perimeter_points.push_back(WayPointNode(upper_right));
  zone.perimeter_points.push_back(WayPointNode(MapXY(lower_left.x,
						     upper_right.y)));
  zone.perimeter_points.push_back(WayPointNode(lower_left));

  return zone;
}

void ZoneOps::expand_bounding_box(const std::vector<MapXY>
				       &points_to_include,
				 MapXY &lower_left,
				 MapXY &upper_right)
{
  // Find bounding box
  for(unsigned i = 0; i < points_to_include.size(); i++) {
    lower_left.x = fmin(points_to_include[i].x, lower_left.x);
    lower_left.y = fmin(points_to_include[i].y, lower_left.y);
    upper_right.x = fmax(points_to_include[i].x, upper_right.x);
    upper_right.y = fmax(points_to_include[i].y, upper_right.y);
  }
}

void ZoneOps::expand_bounding_box_of_waypoints(const std::vector<WayPointNode>
					       &points_to_include,
					       MapXY &lower_left,
					       MapXY &upper_right)
{
  // Find bounding box
  for(unsigned i = 0; i < points_to_include.size(); i++) {
    lower_left.x = fmin(points_to_include[i].map.x, lower_left.x);
    lower_left.y = fmin(points_to_include[i].map.y, lower_left.y);
    upper_right.x = fmax(points_to_include[i].map.x, upper_right.x);
    upper_right.y = fmax(points_to_include[i].map.y, upper_right.y);
  }
}
#endif

WayPointNode ZoneOps::starting_node_for_zone(const ZonePerimeter &zone) 
{
  // Return the first entry we find...
  for(unsigned i = 0; i < zone.perimeter_points.size(); i++) {
    if(zone.perimeter_points[i].is_entry && !zone.perimeter_points[i].is_exit)
      return zone.perimeter_points[i];
  }

  return WayPointNode();
}

ZonePerimeter ZoneOps::get_zone_by_id(const ZonePerimeterList &zones,
                                      const segment_id_t &zone_id)
{
  for(unsigned i = 0; i < zones.size(); i++) {
    if(zones[i].zone_id == zone_id)
      return zones[i];
  }
  ZonePerimeter empty;
  return empty;
}

bool ZoneOps::is_a_zone_id(const ZonePerimeterList &zones,
                           const segment_id_t &zone_id)
{
  for(unsigned i = 0; i < zones.size(); i++) {
    if(zones[i].zone_id == zone_id)
      return true;
  }
  return false;
}

ZonePerimeterList ZoneOps::build_zone_list_from_rndf(RNDF &rndf,
						     Graph &graph)
{
  ZonePerimeterList zl;
  std::vector<Zone>::iterator zi;
  for(zi = rndf.zones.begin(); zi != rndf.zones.end(); zi++)
    {
      ZonePerimeter z=build_zone_perimeter_from_zone(graph, *zi);
      bool found=false;
      for (uint i = 0; i < graph.edges_size; i++)
	{	
	  int index1 = graph.edges[i].startnode_index;
	  int index2 = graph.edges[i].endnode_index;
	  if (graph.nodes[index1].id.seg==z.zone_id &&
	      graph.nodes[index2].id.seg==z.zone_id)
	    {
	      z.speed_limit = graph.edges[i].speed_max;
	      found=true;
	      break;
	    }
	}
      if (!found)
	z.speed_limit=DEFAULT_ZONE_SPEED;
      
      zl.push_back(z);
    }
  return zl;
}

ZonePerimeter ZoneOps::build_zone_perimeter_from_zone(Graph &graph,
						      Zone &zone)
{
  ZonePerimeter zp;
  zp.zone_id = (segment_id_t)zone.zone_id;
  std::vector<Perimeter_Point>::iterator pp;
  for(pp = zone.perimeter.perimeterpoints.begin();
      pp != zone.perimeter.perimeterpoints.end();
      pp++) {
    WayPointNode* wpn =
      graph.get_node_by_id(ElementID(zp.zone_id, 0, pp->waypoint_id));
    if(wpn != NULL) {
      zp.perimeter_points.push_back(*wpn);
    }
  }

  return zp;
}

void ZoneOps::print_zone_list(const ZonePerimeterList &zones)
{
  for(unsigned i = 0; i < zones.size(); i++)
    print_zone(zones[i]);
}

void ZoneOps::print_zone(const ZonePerimeter &zone)
{
  printf("Zone ID: %d Perimeter: ", zone.zone_id);
  for(unsigned i = 0; i < zone.perimeter_points.size(); i++) {
    printf("(%.6f, %.6f), ",
	   zone.perimeter_points[i].map.x,
	   zone.perimeter_points[i].map.y);
  }
  printf("\n");
}


segment_id_t ZoneOps::containing_zone(const ZonePerimeterList &zones,
				      const MapXY &point)
{
  for(unsigned i = 0; i < zones.size(); i++) {
    if(point_in_zone(zones[i], point))
      return zones[i].zone_id;
  }
  return -1;
}

bool ZoneOps::point_in_zone(const ZonePerimeter &zone,
			    const MapXY &point)
{
  if(zone.perimeter_points.size() < 3)
    return false;

  int intersections = 0;

  for(unsigned i = 0; i < zone.perimeter_points.size(); i++) {
    intersections += intersections_of_segment_and_ray_to_right
      (zone.perimeter_points[i].map,
       zone.perimeter_points[(i+1) % zone.perimeter_points.size()].map,
       zone.perimeter_points[(i+2) % zone.perimeter_points.size()].map,
       point);
  }

  // Returns false is intersections is even, true if odd
  return bool(intersections % 2);
}

int ZoneOps::intersections_of_segment_and_ray_to_right(const MapXY &p1,
						       const MapXY &p2,
						       const MapXY &p3,
						       const MapXY &r)
{
  if(Epsilon::equal(p2.y, r.y) && p2.x >= r.x) {
    // p2 is on the ray
    if ((p1.y > r.y && p3.y > r.y) || (p1.y < r.y && p3.y < r.y))
      return 0;
    return 1;
  }


  if((p1.x < r.x) && (p2.x < r.x)) return 0;
  if((p1.y < r.y) == (p2.y < r.y)) return 0;
  if((p1.x > r.x) && (p2.x > r.x)) return 1;
  //By this point, we know p1 and p2 are in diagonal coordinates relative to r

  if((p1.x > r.x) && (p1.y < r.y))
    return ((p2.x - r.x)*(p1.y - r.y) < (p1.x - r.x)*(p2.y - r.y));

  if((p1.x < r.x) && (p1.y < r.y))
    return ((p2.x - r.x)*(p1.y - r.y) < (p1.x - r.x)*(p2.y - r.y));
  
  return ((p2.x - r.x)*(p1.y - r.y) > (p1.x - r.x)*(p2.y - r.y));
}
