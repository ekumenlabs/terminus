/* -*- mode: C++ -*- */
/*
 *  Copyright (C) 2007, 2010 David Li, Patrick Beeson, Jack O'Quin
 *
 *  License: Modified BSD Software License Agreement
 * 
 *  $Id: 2b19de2f6211075d2eda2a54be9a389a4ce2ed22 $
 */

/**  \file
 
     C++ interface for drawing MapLanes polygons.

     \author David Li, Patrick Beeson, Jack O'Quin

 */

#ifndef __DRAW_LANES_H__
#define __DRAW_LANES_H__

#include <vector>
#include <math.h>
#include <errno.h>
#include <stdint.h>
//#include <rndf_visualizer/zones.h>

/*struct poly{
		double x1;
		double x2;
		double x3;
		double x4;
		double y1;
		double y2;
		double y3;
		double y4;
	};*/

struct RGB {
  int r;
  int g;
  int b;
};

#define DEFAULT_RATIO 3.0f

class DrawLanes {
public:
  DrawLanes(int x,int y, float multi=DEFAULT_RATIO);
  ~DrawLanes();
  
  void clear();
  
  void savePGM(const char *filename);
  void saveBMP(const char *filename);

  void addPoly(float x1, float x2, float x3, float x4,
               float y1, float y2,float y3, float y4,
               bool is_stop, bool is_exit);

  //void addZone(const ZonePerimeter &zone, float min_x, float max_y);

  void addWay(float w1lat, float w1long);
  void addRobot(float w1lat, float w1long);
  void addTrace(float w1lat, float w1long, float w2lat, float w2long);

private:
  float MULT;

  RGB* image;
  int imageWidth;
  int imageHeight;

  void line(float x0, float y0, float x1, float y1,RGB colour);
};

#endif
