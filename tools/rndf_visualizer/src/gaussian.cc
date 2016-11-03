//////////////////////////////////////////////////////////////////////
/** \file 
Written and maintained by Patrick Beeson (pbeeson@cs.utexas.edu)
**/
//////////////////////////////////////////////////////////////////////
#include <cstdlib>
#include <math.h>
#include <rndf_visualizer/gaussian.h>

inline float real_random(float multi=1.0){
  return float(random())/RAND_MAX*multi;
}


/**
   This constructor is basically here in order to declare variables in
   other classes.

   mean = variance = 0
**/
gaussian::gaussian() {
  _mean1=_var1=_std1=0;
  _ready=false;
}

/**
   Initialize a univariate Gaussian with a mean and variance.
**/
gaussian::gaussian(float mean, float var) {
  _mean1=mean;
  _var1=var;
  _std1=sqrtf(var);
  _ready=false;
}

/**
   Returns a sample from a univariate Gaussian.  

   If the Gaussian was initialized as a multivariate, it returns a
   sample using the first dimension of the mean vector and the first
   element (0,0) of the covariance matrix as the variance.
**/
float gaussian::get_sample_1D() {
  //return a point drawn from a gaussian distribution centered at mean
  //with a given sigma^2
  
  // polar form of a gaussian distribution from
  // http://www.taygeta.com/random/gaussian.html


  float x1, x2, w, y1;
  static float y2; 
  
  
  if (_ready) {
    _ready=false;
    return y2*_std1+_mean1;
  }
  
  _ready=true;
  
  do {
    x1 = 2.0 * real_random() - 1.0;
    x2 = 2.0 * real_random() - 1.0;
    w = x1 * x1 + x2 * x2;
  } while (w>1.0 || w==0.0);
  
  w = sqrtf((-2.0 * log(w))/w );
  y1 = x1 * w;
  y2 = x2 * w;

  float tmp=y1*_std1+_mean1;
  
  return  tmp;
}  
  
