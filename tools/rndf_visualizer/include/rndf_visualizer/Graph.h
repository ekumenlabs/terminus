/* -*- mode: C++ -*- */
/*
 *  Copyright (C) 2007 Tarun Nimmagadda, Mickey Ristroph, Patrick Beeson
 *  Copyright (C) 2010 Jack O'Quin
 *
 *  License: Modified BSD Software License Agreement
 * 
 *  $Id: cf39ddab209e1c980cfc798f822945825ac9d172 $
 */

/**  \file
 
     C++ interface for the Graph data structure

 */


#ifndef __GRAPH_h__
#define __GRAPH_h__

#include <vector>
#include <algorithm>
#include <fstream>
#include <cstdlib>

#include <rndf_visualizer/coordinates.h>
#include <rndf_visualizer/types.h>

typedef std::vector<WayPointEdge> WayPointEdgeList;
typedef std::vector<WayPointNode> WayPointNodeList;
typedef std::vector<WayPointNodeList> ZoneList;
typedef std::vector<int> intList;



class Graph{
 public:	
  Graph(){
    nodes_size = 0;
    edges_size = 0;
    nodes=NULL;
    edges.clear();
  };

  Graph(uint num_nodes, uint num_edges, 
	const WayPointNode nnodes[],
	const WayPointEdge nedges[]) {
    nodes_size=num_nodes;
    nodes = new WayPointNode[nodes_size];
    for (uint i=0; i< num_nodes; i++)
      nodes[i]=nnodes[i];

    edges_size=num_edges;
    edges.clear();
   for (uint i=0; i< num_edges; i++)
     edges.push_back(nedges[i]);
  };
  
  Graph(Graph& that){
    this->nodes_size=that.nodes_size;
    this->nodes = new WayPointNode[this->nodes_size];
    for (uint i=0; i< (uint)this->nodes_size; i++)
      this->nodes[i] = that.nodes[i];
    
    this->edges_size=that.edges_size;
    this->edges=that.edges;
  };


  ~Graph(){
    if (this->nodes !=NULL)
      delete[] this->nodes;
    edges.clear();
  };

  //Operators
  //bool operator==(const Graph &that);
  bool compare(const Graph &that)
  {
    bool size_check = (this->nodes_size == that.nodes_size
      && this->edges_size == that.edges_size);
    bool node_check = true, edge_check = true;
    //REVERSE THIS BOOLEAN CHECK
    for (uint i=0; i< (uint)this->nodes_size; i++){
      node_check = (this->nodes[i] == that.nodes[i]) && node_check;
      if (!node_check) printf("Node Number %d\n", i);
    }
    //REVERSE THIS BOOLEAN CHECK
    for (uint i=0; i< (uint)this->edges_size; i++)
      edge_check = (this->edges[i] == that.edges[i]) && edge_check;
    
    if (!size_check) printf("Graph Sizes don't match\n");
    if (!node_check) printf("Graph Nodes don't match\n");
    if (!edge_check) printf("Graph Edges don't match\n");    
    return (size_check && node_check && edge_check);
  }

  WayPointEdgeList edges_from(const waypt_index_t index) const;
  WayPointEdgeList edges_leaving_segment(const segment_id_t seg) const;


  // Hooks to save, reload Graph state
  void save(const char* fName);
  bool load(const char* fName);  

  void clear();
  void find_mapxy(void);
  void find_implicit_edges();
  void xy_rndf();
  bool rndf_is_gps();

  void printNodes();
  void printEdges();

  // Print to a file (MQ 8/15/07)
  void printNodesFile(const char* fName);
  void printEdgesFile(const char* fName);

  // get node by ElementID (JOQ 8/25/07)
  WayPointNode *get_node_by_id(const ElementID id) const;
  WayPointNode* get_node_by_index(const waypt_index_t index) const;

  WayPointNode* get_closest_node(const MapXY &p) const;
  WayPointNode* get_closest_node_within_radius(const MapXY &p) const;

  WayPointNode* nodes;
  std::vector<WayPointEdge> edges;
  uint32_t nodes_size;
  uint32_t edges_size;
  bool passing_allowed(int index, int index2, bool left);

  bool lanes_in_same_direction(int index1,int index2, bool& left_lane);
};
	
int parse_integer(std::string line, std::string token, 
		  bool& valid);

WayPointNode parse_node(std::string line, bool& valid);
WayPointEdge parse_edge(std::string line, bool& valid);

#endif
