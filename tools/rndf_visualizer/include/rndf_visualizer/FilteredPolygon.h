/* -*- mode: C++ -*- */

// Filtered MapLanes
// Started - 1st August 2007
// Michael Quinlan
// $Id: b40172cc24267e7b1e052db5e2a2c816f2aeaf49 $

#include <rndf_visualizer/KF.h>
#include <rndf_visualizer/Matrix.h>
#include <rndf_visualizer/PolyOps.h>

#define NUM_POINTS 4

class FilteredPolygon 
{
 public:
  FilteredPolygon();
  ~FilteredPolygon() {};

  void SetPoint(int pointID, float x, float y);
  void UpdatePoint(int pointID, float visionDistance, float visionAngle,
                   float confidence,float rx, float ry, float rori);
  Matrix GetDistanceJacobian(float xb, float yb, float x, float y);
  Matrix GetAngleJacobian(float xb, float yb, float x, float y);
 
  KF point[NUM_POINTS];
  KFStruct distStruct;
  KFStruct angleStruct;

  void SetPolygon(poly p);
  poly GetPolygon();

 private:
  poly polygon_;
  PolyOps ops_;
};
