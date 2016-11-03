/*
 *  Copyright (C) 2007 Patrick Beeson
 *  Copyright (C) 2010 Jack O'Quin
 *
 *  License: Modified BSD Software License Agreement
 * 
 *  $Id: 2af9529a5e2abbaad142244d236da9e93de62212 $
 */

/**  \file
 
     C++ interface for smooth curves.

 */

#ifndef __SMOOTHCURVE_H__
#define __SMOOTHCURVE_H__

#include <vector>

#include <rndf_visualizer/vec.h>                // TODO: eliminate this
#include <epsilon.h>

typedef Vec2f Point2f;

class SmoothCurve 
{

public:
  SmoothCurve(){}

  SmoothCurve(const std::vector<Point2f>& ctrl, 
	      float starttheta, float startspeed,
	      float endtheta, float endspeed, bool use_pats=true);
  ~SmoothCurve();

  void clear();

  float curveLength();
    
  Point2f evaluatePoint(float time);

  int knotCount() const;

  std::vector<float> knots;

private:
    
  int controlPointsCount() const;
    
  int dataPointsCount() const;
  
  std::vector<Point2f> dataPoints;
  std::vector<Point2f> controlPoints; 

  int degree;
  
  float DeltaU (int i);

  Point2f bezierPoint(int i);
  
  Point2f Delta(int i);


  Point2f getDataPoint(int index) const;
	
  Point2f getControlPoint(int index) const;

  float getKnot(int index) const;
    
    
};


#endif
