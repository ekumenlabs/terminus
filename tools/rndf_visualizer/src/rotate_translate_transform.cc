//////////////////////////////////////////////////////////////////////
/** \file 
    Written and maintained by Patrick Beeson (pbeeson@cs.utexas.edu)
**/
//////////////////////////////////////////////////////////////////////

#include <rndf_visualizer/rotate_translate_transform.h>
#include <math.h>

/**
   This should figure out the rotation and translation to move x,y,theta
   coordinate frame C1 to match coordinate frame C2.
**/
void rotate_translate_transform::find_transform(const posetype& c1, 
						const posetype& c2) {
  // ROTATION*(C1x,C1y)+(OffsetX,OffsetY)=(C2_X,C2_Y) 
  // ROTATION=C2_TH-C1_TH

  actual_transform.theta=c2.theta-c1.theta;
  
  actual_cs=cosf(actual_transform.theta);
  actual_sn=sinf(actual_transform.theta);
  
  float rotated_x=c1.x*actual_cs+c1.y*-actual_sn;
  float rotated_y=c1.x*actual_sn+c1.y*actual_cs;

  float offset_x=c2.x-rotated_x;
  float offset_y=c2.y-rotated_y;

  actual_transform.x=offset_x;
  actual_transform.y=offset_y;
}

/**
   Constructor that sets transform to (0,0,0)
**/
rotate_translate_transform::rotate_translate_transform() {
  actual_transform.x=actual_transform.y=actual_transform.theta=0;
  actual_cs=1;
  actual_sn=0;
}

/**
   Transform a coordinate (in C1) into another frame of reference (C2)
   using info found after calling find_transform()
**/
posetype rotate_translate_transform::apply_transform(const posetype& c1) const {

  float rotated_x=c1.x*actual_cs+c1.y*-actual_sn;
  float rotated_y=c1.x*actual_sn+c1.y*actual_cs;

  posetype c2;

  c2.x=rotated_x+actual_transform.x;
  c2.y=rotated_y+actual_transform.y;
  c2.theta=c1.theta+actual_transform.theta;

  return c2;
}

/**
   Uses a pre-calculated transform from find_transform() to apply the
   inverse transform to a coordinate (from C2 to C1).
**/
posetype rotate_translate_transform::apply_inverse_transform(const posetype& c2) const{

  posetype c1;

  float rotated_x=c2.x-actual_transform.x;
  float rotated_y=c2.y-actual_transform.y;

  c1.theta=c2.theta-actual_transform.theta;

  c1.x=rotated_x*actual_cs+rotated_y*actual_sn;
  c1.y=rotated_x*-actual_sn+rotated_y*actual_cs;

  return c1;
}
