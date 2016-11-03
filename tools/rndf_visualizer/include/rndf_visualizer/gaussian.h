/* -*- mode: C++ -*- */
/*
 *  Copyright (C) 2007, 2010 Patrick Beeson
 *
 *  License: Modified BSD Software License Agreement
 * 
 *  $Id: 7c6a880478c297c819ae2c8dcf7f976d811dda49 $
 */

/**  \file
 
     C++ class to create a Gaussian object.  Given the parameters of a
     univariate or multivariate Gaussian, the object allows the user
     to draw samples from the Gaussian.

     \author Patrick Beeson
**/

#ifndef gaussian_hh
#define gaussian_hh

class gaussian {
public:
  gaussian();
  gaussian(float,float);
  float get_sample_1D();

private:
  bool _ready;  //<! when getting sample, two are actually computed.
		//<! this flag tells us if one is waiting.
  float _mean1, _var1, _std1;
};

#endif
