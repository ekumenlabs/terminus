/* -*- mode: C++ -*- */

// $Id: 21de9ed4599e87501796133171d01240d0554cec $

#include <math.h>
#define PI 3.141592
#define PI_L 3141592L

#define DEG_TO_RAD(x)           ((double)((x)*PI)/180.0)
#define RAD_TO_MICRO(x)		((long)((x)*1000000))
#define DEG_TO_MICRO(x)		(RAD_TO_MICRO((DEG_TO_RAD((x)))))
#define RAD_TO_DEG(x)           ((double)((x)*180.0)/PI)
#define MICRO_TO_RAD(x)		((double)(x)/1000000.0)
#define MICRO_TO_DEG(x)		(RAD_TO_DEG((MICRO_TO_RAD((x)))))

#define DEG_T_RAD PI/180.0
#define RAD_T_DEG 180.0/PI

#define SQUARE(x)         ((x) * (x))
#define ABS(x)            (((x)>0)?(x):-1*(x))

//#define MAX(x,y) ((x) > (y) ? (x) : (y))
//#define MIN(x,y) ((x) > (y) ? (y) : (x))

inline double Normalise_PI(double angle)
{
  while (angle>PI) {
    angle -= 2.0*PI;
  }
  while (angle<=-PI) {
    angle += 2.0*PI;
  }
  return angle;
}

inline double DistFromXY(double x, double y, double x2,double y2)
{
  return sqrt(SQUARE(x2-x)+SQUARE(y2-y));
}

inline double AngleFromXY(double x,double y, double ori, double x2, double y2)
{
  return Normalise_PI(atan2(y2-y,x2-x) - ori);
}

inline double AngleFromXY2(double x,double y, double ori, double x2, double y2)
{
  return Normalise_PI(atan2(x2-x,y2-y) - ori);
}
