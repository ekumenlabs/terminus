#ifndef __ZONEOPS_H__
#define __ZONEOPS_H__

#include <vector>

#include <rndf_visualizer/coordinates.h>
#include <rndf_visualizer/Graph.h>
#include <rndf_visualizer/RNDF.h>
#include <rndf_visualizer/zones.h>

class ZoneManager {
public:
  ZoneManager(const ZonePerimeter &_zone,
	      float _safety_radius,
	      float _scale,
	      int _max_cells,
	      bool _write_graph,
	      ElementID _starting_id,
	      MapXY _lower_left,
	      MapXY _upper_right);

  void build_graph(const ObstacleList &obstacles,
		   const MapXY &start);

  WayPointNodeList path_through_zone(const ObstacleList &obstacles,
				     MapXY start,
				     MapXY end);
  ElementID starting_id;
private:
  bool write_graph;
  ZonePerimeter zone;
  float safety_radius;
  MapXY ll;
  MapXY ur;
  float scale;
#if 0 // skip EVG thin stuff
  grid_manager gmanager;
  evg_thin thin;
#endif // skip EVG thin stuff

  WayPointNodeList nodes;
  WayPointEdgeList edges;

  std::vector<MapXY> perimeter_points;
};

namespace ZoneOps {
  WayPointNodeList path_through_zone(const ZonePerimeter &zone,
				     float perimeter_sample,
				     float safety_radius,
				     const ObstacleList &obstacles,
				     MapXY start,
				     MapXY end,
				     bool write_graph,
				     bool write_poly,
				     bool write_obstacles,
				     float scale,
				     int max_cells);
  
  segment_id_t containing_zone(const ZonePerimeterList &zones,
			       const MapXY &point);

  bool point_in_zone(const ZonePerimeter &zone,
		     const MapXY &point);

  ZonePerimeter get_zone_by_id(const ZonePerimeterList &zones,
			       const segment_id_t &zone_id);

  bool is_a_zone_id(const ZonePerimeterList &zones,
		    const segment_id_t &zone_id);

  WayPointNode starting_node_for_zone(const ZonePerimeter &zone);

  ZonePerimeter build_fake_zone(const std::vector<MapXY> &points_to_include,
				float border_width);


  ZonePerimeterList build_zone_list_from_rndf(RNDF &rndf,
					      Graph &graph);

#if 0 // maybe later
  /* ------------ Functions primarily for internal use ------ */
  ObstacleList filter_obstacles(const ObstacleList &obstacles,
				const ZonePerimeter &zone);

  void expand_bounding_box(const std::vector<MapXY> &points_to_include,
		   MapXY &lower_left,
		   MapXY &upper_right);

  void expand_bounding_box_of_waypoints(const std::vector<WayPointNode>
					&points_to_include,
					MapXY &lower_left,
					MapXY &upper_right);
  
  void correct_edge_distances(Graph& g);

  int voronoi_from_evg_thin(WayPointNodeList &nodes,
			    WayPointEdgeList &edges,
			    const ZonePerimeter &zone,
			    float safety_radius,
			    const ObstacleList &obstacles,
			    const MapXY &start,
			    bool write_graph,
			    bool write_image,
			    float scale,
			    int max_cells);
  
  int voronoi_from_trilibrary(WayPointNodeList &nodes,
			      WayPointEdgeList &edges,
			      const ZonePerimeter &zone,
			      float perimeter_sample,
			      float safety_radius,
			      const ObstacleList &obstacles,
			      bool write_graph,
			      bool write_poly,
			      bool write_obstacles);
#endif // maybe later

  int filter_nodes_and_edges(WayPointNodeList &nodes,
			     WayPointEdgeList &edges,
			     float safety_radius);

  void print_zone_list(const ZonePerimeterList &zones);

  void print_zone(const ZonePerimeter &zone);

  void print_tio(const struct triangulateio &t);

  void print_graph_as_voronoi(Graph &graph);

  void add_densely(std::vector<MapXY> &points,
  		   const MapXY &p1,
  		   const MapXY &p2,
		   const float &max_spacing);
  
  void populate_triangulateio(struct triangulateio &t,
			      const ZonePerimeter &zone,
			      const ObstacleList &obstacles,
			      const float &max_spacing,
			      bool write_obstacles);

  void add_new_node(const struct triangulateio &t,
		    const int &i,
		    int &index,
		    std::vector<WayPointNode> &nodes,
		    std::map<int,WayPointNode> &original_node_index);

  // Must delete after calling this!
  void build_new_graph(const WayPointNodeList &nodes,
		       const WayPointEdgeList &edges,
		       Graph& g);

  ZonePerimeter build_zone_perimeter_from_zone(Graph &graph,
					       Zone &zone);

  int intersections_of_segment_and_ray_to_right(const MapXY &p1,
						const MapXY &p2,
						const MapXY &p3,
						const MapXY &r);
};

#endif /* __ZONEOPS_H__ */
