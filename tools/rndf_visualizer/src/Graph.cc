//Tarun Nimmagadda
//The University of Texas, Austin

//Defines methods on the Graph Data Structure

#include <iostream>
#include <sstream>
#include <string>
#include <stdexcept>
#include <float.h>

#include <UTM.h>
#include <rndf_visualizer/euclidean_distance.h>
#include <rndf_visualizer/Graph.h>

WayPointEdgeList Graph::edges_from(const waypt_index_t index) const {
  WayPointEdgeList new_edges;
  for(uint i=0; i<edges_size; i++) {
    if(edges[i].startnode_index == index)
      new_edges.push_back(edges[i]);
  }
  return new_edges;
};

WayPointEdgeList Graph::edges_leaving_segment(const segment_id_t seg) const {
  WayPointEdgeList new_edges;
  for(uint i=0; i<edges_size; i++) {
    if(get_node_by_index(edges[i].startnode_index)->id.seg == seg)
      new_edges.push_back(edges[i]);
  }
  return new_edges;
};

WayPointNode* Graph::get_node_by_index(const waypt_index_t index) const {
  for(uint i=0; i<nodes_size; i++) 
    if(nodes[i].index == index)
      return &nodes[i];
  return NULL;
};

WayPointNode* Graph::get_node_by_id(const ElementID id) const {
  for(uint i=0; i<nodes_size; i++) {
    if(nodes[i].id == id)
      return &nodes[i];
  }
  return NULL;
};

WayPointNode* Graph::get_closest_node(const MapXY &p) const {
  WayPointNode* closest = NULL;
  float distance = 0;
  float new_distance = 0;
  for(uint i=0; i<nodes_size; i++) {
    new_distance = Euclidean::DistanceTo(p, nodes[i].map);
    if(closest == NULL || new_distance < distance) {
      closest = &nodes[i];
      distance = new_distance;
    }
  }
  return closest;
};

WayPointNode* Graph::get_closest_node_within_radius(const MapXY &p) const {
  WayPointNode* closest = NULL;
  float distance = 0;
  float new_distance = 0;
  for(uint i=0; i<nodes_size; i++) {
    new_distance = Euclidean::DistanceTo(p, nodes[i].map);
    if((closest == NULL || new_distance < distance)
       && (new_distance < nodes[i].lane_width)) {
      closest = &nodes[i];
      distance = new_distance;
    }
  }
  return closest;
};


/*
ZoneList get_zones(const Graph& graph) {
  //	int number_of_zones = get_number_of_zones(graph);
  std::pair<int, int> zone_min_max = get_number_of_zones(graph);
  int min_zone = zone_min_max.first;
  int max_zone = zone_min_max.second;	
  ZoneList zonelist;
  WayPointNodeList nodelist;
  for (int i = min_zone; i <= max_zone; i++){
    for(int j=0; j<nodes_size; j++) {
      if(nodes[j].id.seg == i && nodes[j].is_perimeter)
	nodelist.push_back(nodes[j]);
    }
    //	    std::sort(nodelist.begin(), nodelist.end());
    printf("num_points %d\n", nodelist.size());
    zonelist.push_back(nodelist);
  }
  return zonelist;
};


std::pair<int, int> get_number_of_zones(const Graph& graph){
  int min_zone = INT_MAX;
  int max_zone = INT_MIN;
  for(int i=0; i<nodes_size; i++) {
    if (nodes[i].is_perimeter){
      min_zone = std::min(min_zone, (int)nodes[i].id.seg);
      max_zone = std::max(max_zone, (int)nodes[i].id.seg);
    }
  }
  //	int number_of_zones = max_zone - min_zone;
  //	if (min_zone != 1) printf("Min Zone ID is not 0\n");
  //	if (number_of_zones > 0) return number_of_zones;
  //	else return 0;
  printf("Zones start:%d -> end:%d\n", min_zone, max_zone);
  return std::pair<int, int>(min_zone, max_zone);
};
*/


void Graph::save(const char* fName){
  WayPointNode node;
  WayPointEdge edge;
  FILE* f = fopen(fName,"wb");
  fprintf(f, "GRAPH-STATE\n");
  fprintf(f, "Node_Number %d\n", nodes_size);
  fprintf(f, "Edge_Number %d\n", edges_size);
  for (uint i = 0; i < nodes_size; i++){
    node = nodes[i];
    fprintf(f, "Node ");
    //LatLong
    fprintf(f, "%.10lf, %.10lf; ", node.ll.latitude, node.ll.longitude);
    //MapXY
    fprintf(f, "%f, %f; ", node.map.x, node.map.y);
    //ElementID
    fprintf(f, "%d, %d, %d; ", node.id.seg, node.id.lane, node.id.pt);
    //Waypoint Index
    fprintf(f, "%d; ", node.index);
    //FLAGS
    fprintf(f, "%d, %d, %d, %d, %d, %d; ", node.is_entry, node.is_exit, node.is_goal, node.is_spot, node.is_stop, node.is_perimeter);
    //Checkpoint ID
    fprintf(f, "%d; ", node.checkpoint_id);
    //Lane Width
    fprintf(f, "%f; ", node.lane_width);
    //END NODE
    fprintf(f, "\n");
    
  }
  for (uint i = 0; i < edges_size; i++){
    edge = edges[i];
    fprintf(f, "Edge ");
    //Start, End Nodes
    fprintf(f, "%d, %d; ", edge.startnode_index, edge.endnode_index);
    //Distance
    fprintf(f, "%f; ", edge.distance);
    //Speeds
    fprintf(f, "%f, %f; ", edge.speed_max, edge.speed_min);
    //FLAGS
    fprintf(f, "%d; ", edge.is_exit);
    //Lane Markings
    fprintf(f, "%d, %d; ", edge.left_boundary, edge.right_boundary);
    //END EDGE
    fprintf(f, "\n");
  }
  fclose (f);
}

bool Graph::load(const char* fName){
  WayPointNode node;
  WayPointEdge edge;
  clear();
  
  std::ifstream graph_file;
  graph_file.open(fName);
  if (!graph_file){
    printf("Error in opening Graph Log file\n");
    return false;
  }
  

  int number_of_nodes = 0, number_of_edges = 0;
  int line_number = 0, current_node = 0, current_edge = 0;
  bool valid = true;
  std::string lineread;
  while(getline(graph_file, lineread) ) // Read line by line
    {
      line_number++;
      std::string token;
      char token_char [lineread.size()+1];
      //Read in one line
      sscanf(lineread.c_str(), "%s", token_char);
      token.assign(token_char);

      //      printf("Token: |%s|\n", token.c_str());
      
      if (line_number == 1){
	if (!(token.compare("GRAPH-STATE") == 0)) return false;
      }
      
      else if (line_number == 2){
	if (!(token.compare("Node_Number") == 0)) {return false;}
	else {
	  number_of_nodes = parse_integer(lineread, std::string("Node_Number"), valid);
	}
	if (!valid) return false;
	else {
	  nodes_size = number_of_nodes;
	  nodes = new WayPointNode[nodes_size];
	}
      }
      else if (line_number == 3){
	if (!(token.compare("Edge_Number") == 0)) {return false;}
	else {
	  number_of_edges = parse_integer(lineread, std::string("Edge_Number"), valid);
	}
	if (!valid) return false;
	else {
	  edges_size = number_of_edges;
	  edges.resize(edges_size);
	}
      }
      else if (token.compare("Node") == 0){
	current_node++;
	node = parse_node(lineread, valid);
	if (!valid) return false;
	else nodes[current_node-1] = node;
      }
      else if (token.compare("Edge") == 0){
	current_edge++;
	edge = parse_edge(lineread, valid);
	if (!valid) return false;
	else edges[current_edge-1] = edge;
      }
      else return false;
    }
  if (line_number < 3)return false;
  else if (current_node != number_of_nodes) return false;
  else if (current_edge != number_of_edges) return false;
  //ONE MORE CONDITION: CHECK CURRENT_EDGE, CURRENT_NODE
  else return true;
}

void Graph::clear(){
  for(uint i = 0; i < nodes_size; i++)
    nodes[i].clear();
  nodes_size = 0;
  for(uint i = 0; i < edges_size; i++)
    edges[i].clear();
  edges_size = 0;
  
}

void Graph::printNodes(){
  printf("\nNodes: \n");
  for(uint i = 0; i < nodes_size; i++){
    printf("%2d: ", nodes[i].index);
    printf("%2d.%2d.%2d ", nodes[i].id.seg, nodes[i].id.lane, nodes[i].id.pt);
    // printf("Lat: %4.4f, Long: %4.2f ", 
    //	nodes[i].ll.latitude, nodes[i].ll.longitude);
    printf(",Width: %2.3f ", nodes[i].lane_width);
    printf("CKPT: %s, STOP: %s", nodes[i].is_goal?"true ":"false", 
	   nodes[i].is_stop?"true ":"false");
    printf(", ENTRY: %s, EXIT: %s", nodes[i].is_entry?"true ":"false", 
	   nodes[i].is_exit?"true ":"false");
    printf(", SPOT: %s\n", nodes[i].is_spot?"true ":"false");
  }
};

void Graph::printEdges(){
  printf("\nEdges: \n");
  for(uint i = 0; i < edges_size; i++){
    printf("%3d: ", i);
    printf("%3d to %3d ", edges[i].startnode_index, edges[i].endnode_index);
    printf("Boundary- Left:%2d, Right:%2d, ", 
	   edges[i].left_boundary, edges[i].right_boundary);
    printf("Speed- Min:%f, Max:%f, ", 
	   edges[i].speed_min, edges[i].speed_max);
    printf(",EXIT: %s\n", edges[i].is_exit?"true ":"false");
  }
};

void Graph::printNodesFile(const char* fName){
  FILE* f = fopen(fName,"wb");
  fprintf(f,"Nodes: \n");
  for(uint i = 0; i < nodes_size; i++){
    fprintf(f,"%2d: ", nodes[i].index);
    fprintf(f,"%2d.%2d.%2d ", nodes[i].id.seg, 
	    nodes[i].id.lane, nodes[i].id.pt);
    // printf("Lat: %4.4f, Long: %4.2f ", 
    //  nodes[i].ll.latitude, nodes[i].ll.longitude);
    fprintf(f,",Width: %2.3f ", nodes[i].lane_width);
    fprintf(f,"CKPT: %s, STOP: %s", nodes[i].is_goal?"true ":"false", 
	    nodes[i].is_stop?"true ":"false");
    fprintf(f,", ENTRY: %s, EXIT: %s", nodes[i].is_entry?"true ":"false", 
	    nodes[i].is_exit?"true ":"false");
    fprintf(f,", SPOT: %s\n", nodes[i].is_spot?"true ":"false");
  }
  fclose(f);
};

void Graph::printEdgesFile(const char* fName){
  FILE* f = fopen(fName,"wb");
  fprintf(f,"Edges: \n");
  for(uint i = 0; i < edges_size; i++){
    fprintf(f,"%3d: ", i);
    fprintf(f,"%3d to %3d ", edges[i].startnode_index, edges[i].endnode_index);
    fprintf(f,"Boundary- Left:%2d, Right:%2d, ", 
	    edges[i].left_boundary, edges[i].right_boundary);
    fprintf(f,",EXIT: %s\n", edges[i].is_exit?"true ":"false");
  }
  fclose(f);
}; 

bool Graph::rndf_is_gps() {
  double minlat=INFINITY;
  double minlong=INFINITY;
  double maxlat=-INFINITY;
  double maxlong=-INFINITY;

  for(uint i = 0; i < nodes_size; i++){
    minlat = std::min(minlat,nodes[i].ll.latitude);
    minlong = std::min(minlong,nodes[i].ll.longitude);
    maxlat = std::max(maxlat,nodes[i].ll.latitude);
    maxlong = std::max(maxlong,nodes[i].ll.longitude);
  }

  if (minlat == INFINITY ||
      maxlat == INFINITY ||
      minlong == INFINITY ||
      maxlong == INFINITY)
    return false;

  if (maxlat-minlat <= 2 && // 138 miles
      maxlong-minlong <= 2) //84 miles
    return true;

  return false;

}

void Graph::xy_rndf() {
  for(uint i = 0; i < nodes_size; i++){
    nodes[i].map.x = nodes[i].ll.latitude;
    nodes[i].map.y = nodes[i].ll.longitude;
  }

  for(uint i = 0; i < edges_size; i++){
    WayPointNode* start=get_node_by_index(edges[i].startnode_index);
    if(start == NULL) {
      std::cerr << "Error getting start edge. Start Edge node index: " << edges[i].startnode_index << std::endl;
      throw std::exception();
    }
    WayPointNode* end=get_node_by_index(edges[i].endnode_index);
    if(end == NULL) {
      std::cerr << "Error getting end edge. End Edge node index: " << edges[i].startnode_index << std::endl;
      throw std::exception();
    }
    edges[i].distance=Euclidean::DistanceTo(start->map,end->map);
  }
}

/** Fill in MapXY coordinates for map graph.
 *
 * This method uses the latitude and longitude of the first way-point
 * in the graph, generating its corresponding MapXY coordinates
 * relative to the 10km UTM grid.  Then, all the other way-points are
 * relocated relative to that same grid origin.
 */
void Graph::find_mapxy(void)
{
  if (nodes_size < 1)
    {
      printf("No graph nodes available for conversion to MapXY");
      return;
    }

  // Compute the MapXY value corresponding to the first way-point in
  // the graph.  Use temporaries because MapXY is defined in floats,
  // while the UTM function returns doubles.
  double tX;
  double tY;  
  UTM::UTM(nodes[0].ll.latitude, nodes[0].ll.longitude, &tX, &tY);

  // Round UTM origin of map to nearest UTM grid intersection.  All
  // odometry is reported relative to that location.
  double grid_x = (rint(tX/UTM::grid_size) * UTM::grid_size);
  double grid_y = (rint(tY/UTM::grid_size) * UTM::grid_size);
  nodes[0].map = MapXY(tX - grid_x, tY - grid_y);
  printf("UTM grid of first way-point: (%.f, %.f)", grid_x, grid_y);

  // Relocate all other way-points relative to (grid_x, grid_y),
  // instead of individually relocating each way-point.  This may
  // avoid some discontinuities if the map happens to span a grid
  // boundary.
  for(uint i = 1; i < nodes_size; i++)
    {
      UTM::UTM(nodes[i].ll.latitude, nodes[i].ll.longitude, &tX, &tY);
      nodes[i].map = MapXY(tX - grid_x, tY - grid_y);
    }

  for(uint i = 0; i < edges_size; i++){
    WayPointNode* start=get_node_by_index(edges[i].startnode_index);
    WayPointNode* end=get_node_by_index(edges[i].endnode_index);
    
    edges[i].distance=Euclidean::DistanceTo(start->map,end->map);
    //    std::cerr << "Edge "<<i<<" "<<start->id.name().str<<" "<<
    //      end->id.name().str<<" "<<edges[i].distance<<std::endl;
  }
}

bool Graph::passing_allowed(int index, int index2, bool left) {
  if (index < 0 || index >= (int)nodes_size)
    return false;
  
  WayPointNode node1=nodes[index];
  WayPointNode node2=nodes[index2];
  
  ElementID ahead=ElementID(node1.id.seg,node1.id.lane,node1.id.pt+1);
  
  bool found_ahead=false;

  for (uint i=0; i<nodes_size; i++)
    if (nodes[i].id==ahead)
      {
	found_ahead=true;
	break;
      }

  if (!found_ahead)
    return true;
	
			       

  for (uint i=0; i<edges.size(); i++)
    {
      if (edges.at(i).startnode_index==node1.index)
	{
	  ElementID neighbor_id=nodes[edges.at(i).endnode_index].id;
	  if (neighbor_id.seg==node1.id.seg &&
	      neighbor_id.lane==node1.id.lane &&
	      neighbor_id.pt==node1.id.pt+1) {
	    if (left)
	      {
		if (edges.at(i).left_boundary==DOUBLE_YELLOW ||
		    edges.at(i).left_boundary==SOLID_YELLOW ||
		    edges.at(i).left_boundary==SOLID_WHITE)
		  return false;
	      }
	    else
	      {
		if (edges.at(i).right_boundary==DOUBLE_YELLOW ||
		    edges.at(i).right_boundary==SOLID_YELLOW ||
		    edges.at(i).right_boundary==SOLID_WHITE)
		  return false;
	      }
	  }
	}
      if (edges.at(i).startnode_index==node2.index)
	{
	  ElementID neighbor_id= nodes[edges.at(i).endnode_index].id;
	  if (neighbor_id.seg==node2.id.seg &&
	      neighbor_id.lane==node2.id.lane &&
	      neighbor_id.pt==node2.id.pt+1) {
	    if (!left)
	      {
		if (edges.at(i).left_boundary==DOUBLE_YELLOW ||
		    edges.at(i).left_boundary==SOLID_YELLOW ||
		    edges.at(i).left_boundary==SOLID_WHITE)
		  return false;
	      }
	    else
	      {
		if (edges.at(i).right_boundary==DOUBLE_YELLOW ||
		    edges.at(i).right_boundary==SOLID_YELLOW ||
		    edges.at(i).right_boundary==SOLID_WHITE)
		  return false;
	      }
	  }
	}
    }
  
  return true;

}

bool Graph::lanes_in_same_direction(int index1,int index2, bool& left_lane) {
  if (index1<0 || index2<0 ||
      index1>=(int)nodes_size ||
      index2>=(int)nodes_size)
    return false;

  ElementID el1=ElementID(nodes[index1].id);
  el1.pt+=1;

  ElementID el2=ElementID(nodes[index2].id);
  el2.pt+=1;

  int ind1=-1;
  int ind2=-1;

  for (uint i=0; i<nodes_size; i++)
    {
      if (nodes[i].id==el1)
	ind1=i;
      if (nodes[i].id==el2)
	ind2=i;
    }
  
  float head1;
  float head2;

  if (ind1>=0 && ind2>=0)
    {
      head1=atan2f(nodes[ind1].map.y-nodes[index1].map.y,
		   nodes[ind1].map.x-nodes[index1].map.x);
      head2=atan2f(nodes[ind2].map.y-nodes[index2].map.y,
		   nodes[ind2].map.x-nodes[index2].map.x);

      MapPose p1(nodes[index1].map,head1);
      
      if (Coordinates::bearing(p1,nodes[index2].map) > 0)
	left_lane=true;
      else left_lane=false;

    }
  else
    {
      el1.pt-=2;
      el2.pt-=2;
      ind1=-1;
      ind2=-1;

      for (uint i=0; i<nodes_size; i++)
	{
	  if (nodes[i].id==el1)
	    ind1=i;
	  if (nodes[i].id==el2)
	    ind2=i;
	}

      if (ind1>=0 && ind2>=0)
	{
	  head1=atan2(nodes[ind1].map.y-nodes[index1].map.y,
		      nodes[ind1].map.x-nodes[index1].map.x);
	  head2=atan2(nodes[ind2].map.y-nodes[index2].map.y,
		      nodes[ind2].map.x-nodes[index2].map.x);

	  MapPose p1(nodes[index1].map,head1);
	  
	  if (Coordinates::bearing(p1,nodes[index2].map) < 0)
	    left_lane=true;
	  else left_lane=false;
	}
      else return false;
    }

  if (fabsf(Coordinates::normalize(head1-head2)) < HALFPI)
    return true;
  else return false;

}

void Graph::find_implicit_edges() {
  
  for (unsigned i=0; i< nodes_size; i++)
    {
      WayPointNode node1=nodes[i];
      if (node1.is_stop || node1.is_perimeter ||
	  node1.is_spot)
	continue;
      {// left case
	float min_dist=FLT_MAX;
	int min_index=-1;
	for (unsigned j=0; j< nodes_size; j++)
	  if (i!=j)
	    {
	      WayPointNode node2=nodes[j];
	      if (node1.id.seg==node2.id.seg &&
		  node1.id.lane-1==node2.id.lane)
		{
		  float curr_dist=Euclidean::DistanceTo(node1.map,node2.map);
		  if (curr_dist < min_dist)
		    {
		      min_dist=curr_dist;
		      min_index=j;
		    }
		}
	    }
	if (min_index<0)
	  continue;
	if (nodes[min_index].is_stop || nodes[min_index].is_perimeter ||
	    nodes[min_index].is_spot)
	  continue;
	bool left_lane;
	if (lanes_in_same_direction(i,min_index, left_lane))
	  {
	    if (passing_allowed(i,min_index,left_lane))
	      {
		WayPointEdge new_edge;
		new_edge.startnode_index=i;
		new_edge.endnode_index=min_index;
		//HACK
		new_edge.distance=30;
		new_edge.speed_max=6.0;	// TODO: Something nicer
		new_edge.blocked=false;
		new_edge.is_implicit=true;
		edges.push_back(new_edge);
		edges_size++;
	      }
	  }
      }
      
      {// right case
	float min_dist=FLT_MAX;
	int min_index=-1;
	for (unsigned j=0; j< nodes_size; j++)
	  if (i!=j)
	    {
	      WayPointNode node2=nodes[j];
	      if (node1.id.seg==node2.id.seg &&
		  node1.id.lane+1==node2.id.lane)
		{
		  float curr_dist=Euclidean::DistanceTo(node1.map,node2.map) < min_dist;
		  if (curr_dist < min_dist)
		    {
		      min_dist=curr_dist;
		      min_index=j;
		    }
		}
	    }
	if (min_index<0)
	  continue;
	bool left_lane;
	if (lanes_in_same_direction(i,min_index, left_lane))
	  {
	    if (passing_allowed(i,min_index,left_lane))
	      {
		WayPointEdge new_edge;
		new_edge.startnode_index=i;
		new_edge.endnode_index=min_index;
		//HACK
		new_edge.distance=25;
		new_edge.speed_max=6.0;	// TODO: something smarter
		new_edge.blocked=false;
		new_edge.is_implicit=true;
		edges.push_back(new_edge);
		edges_size++;
	      }
	  }
      }
    }
}

      
int parse_integer(std::string line, std::string token, 
		  bool& valid){
  int integer;
  if (!sscanf(line.c_str(), "%*s %d", &integer)){
    valid=false;
  }
  return integer; 
};

WayPointNode parse_node(std::string line, bool& valid){
  WayPointNode node;
  double f1, f2;
  float f3, f4, f5;
  int d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11;
  if (sscanf(line.c_str(), 
	     "Node %lf, %lf; %f, %f; %d, %d, %d; %d; %d, %d, %d, %d, %d, %d; %d; %f;", 
	     &f1, &f2, &f3, &f4, &d1, &d2, &d3, &d4, &d5, &d6, &d7, &d8, &d9, &d10, &d11, &f5) 
      == 16){
    valid = true;
    node.ll.latitude = f1;
    node.ll.longitude = f2;
    node.map.x = f3;
    node.map.y = f4;
    node.id.seg = d1;
    node.id.lane = d2;
    node.id.pt = d3;
    node.index = d4;
    node.is_entry = d5;
    node.is_exit = d6;
    node.is_goal = d7;
    node.is_spot = d8;
    node.is_stop = d9;
    node.is_perimeter = d10;
    node.checkpoint_id = d11;
    node.lane_width = f5;
  }
  else
    valid=false;
  //printf("--> %s\n", line.c_str());
  return node;


};

WayPointEdge parse_edge(std::string line, bool& valid){

  WayPointEdge edge;
  float f1,f2,f3;
  int d1, d2, d6, d7, d8;
  if (sscanf(line.c_str(), 
	     "Edge %d, %d; %f; %f, %f; %d; %d, %d; ",
	     &d1, &d2, &f1, &f2, &f3, &d6, &d7, &d8) 
      == 8){
    valid = true;
    edge.startnode_index = d1;
    edge.endnode_index = d2;
    edge.distance = f1;
    edge.speed_max = f2;
    edge.speed_min = f3;
    edge.is_exit = d6;
    edge.left_boundary = static_cast<Lane_marking>(d7);
    edge.right_boundary = static_cast<Lane_marking>(d8);
  }
  else
    valid=false;
  //printf("--> %s\n", line.c_str());
  return edge;

};
