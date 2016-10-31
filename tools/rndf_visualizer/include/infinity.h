/* -*- mode: C++ -*-
 *
 *  Global ART infinity definitions
 *
 *  Copyright (C) 2009 Austin Robot Technology                    
 *  License: Modified BSD Software License Agreement
 *
 *  $Id: e97027dff95923c892f34b7e31651f89f61ce083 $
 */

#ifndef _INFINITY_H_
#define _INFINITY_H_

#include <math.h>

/**  @file
   
     @brief global ART infinity definitions.

     These constants represent effectively infinite distances, times, etc.

     @todo (if needed) make art_msgs definitions for multi-language support

     @todo make these specific to mapping and navigation components
 */

namespace Infinite
{
  const float distance = 1000000.0;	//< far off distance, in meters
  const float time = 1000000.0;		//< forever, in seconds
}

#endif // _INFINITY_H_ //
