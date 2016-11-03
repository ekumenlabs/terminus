/* -*- mode: C++ -*-
 *
 *  ART epsilon definitions
 *
 *  Copyright (C) 2009 Austin Robot Technology                    
 *  License: Modified BSD Software License Agreement
 *
 *  $Id: 3096350e0e09657fc7a1574427dee1d454032db5 $
 */

#ifndef _EPSILON_H_
#define _EPSILON_H_

#include <math.h>

/**  @file
   
     @brief global ART Epsilon definitions.

     These constants represent trivial differences in distance, speed,
     angle, etc.

     @todo use art_msgs/Epsilon definitions for multi-language support

     @todo make these specific to mapping and navigation components
 */

namespace Epsilon
{
  const float float_value = 1e-5;	//< minimal float value
  const float distance = 0.01;		//< one centimeter
  const float speed = 0.01;		//< in meters/second
  const float yaw = 3.1416/180; //< in radians


  // Slightly better AlmostEqual function – still not recommended
  
  inline bool AlmostEqualRelativeOrAbsolute(float A, float B,
				     float maxRelativeError, 
				     float maxAbsoluteError)
  {
    if (fabs(A - B) < maxAbsoluteError)
        return true;

    float relativeError;

    if (fabs(B) > fabs(A))
        relativeError = fabs((A - B) / B);
    else
        relativeError = fabs((A - B) / A);

    if (relativeError <= maxRelativeError)
        return true;

    return false;
}

  inline bool equal(float a, float b) {
    return AlmostEqualRelativeOrAbsolute(a,b,float_value,float_value);
  }

  inline bool lte(float a, float b) {
    return ((a<b) || (equal(a,b)));
  }

  inline bool gte(float a, float b) {
    return ((a>b) || (equal(a,b)));
  }

}

#endif // _EPSILON_H_ //
