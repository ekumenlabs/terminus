/* -*- mode: C++ -*-
 *
 *  Units conversion aids.
 *
 *  Copyright (C) 2007, 2009 Austin Robot Technology                    
 *  License: Modified BSD Software License Agreement
 *
 *  $Id: 8b85d8eee695030560adbf478dadcedbd5d9287a $
 */

#ifndef _CONVERSIONS_H
#define _CONVERSIONS_H

/**  @file
   
     @brief Units conversion constants and functions.

     @todo use art_msgs/Conversions definitions for multi-language support
 */

#include <math.h>
#include <sys/time.h>
#include <time.h>


/** Unit conversion constants: */
const double INCHES_PER_FOOT = 12.0;
const double CM_PER_INCH = 2.54;
const double CM_PER_METER = 100.0;
const double METERS_PER_FOOT = INCHES_PER_FOOT * CM_PER_INCH / CM_PER_METER; // = 0.3048
const double MMETERS_PER_KM =	1000000.0;
const double MMETERS_PER_MILE =	1609344.0;
const double METERS_PER_MILE =	MMETERS_PER_MILE / 1000.0;
const long   SECONDS_PER_MINUTE = 60;
const long   MINUTES_PER_HOUR =	60;
const long   SECONDS_PER_HOUR =	SECONDS_PER_MINUTE * MINUTES_PER_HOUR;
const double RADIANS_PER_DEGREE = M_PI/180.0;
const double DEGREES_PER_RADIAN = 180.0/M_PI;

/** Useful constants **/
const double TWOPI = 2.0 * M_PI;
const double HALFPI = M_PI / 2.0;


/** convert between millimeters per second and miles per hour */
static inline double mmps2mph(double mm)
{
  return mm * SECONDS_PER_HOUR / MMETERS_PER_MILE;
}

static inline double kmph2mmps(double kmph)
{
  return kmph * MMETERS_PER_KM / SECONDS_PER_HOUR;
}

static inline double mph2mmps(double mph)
{
  return mph * MMETERS_PER_MILE / SECONDS_PER_HOUR;
}

/** convert between meters per second and miles per hour */
static inline double mph2mps(double mph)
{
  return mph * METERS_PER_MILE / SECONDS_PER_HOUR;
}

/** convert from meters per second to miles per hour  */
static inline double mps2mph(double mps)
{
  return mps * SECONDS_PER_HOUR / METERS_PER_MILE;
}

/** convert from feet to meters */
static inline double feet2meters(double feet)
{
  return feet * METERS_PER_FOOT;
}

/** convert from meters to feet */
static inline double meters2feet(double meters)
{
  return meters / METERS_PER_FOOT;
}

/** convert timeval to seconds */
static inline double tv2secs(struct timeval *tv)
{
  return tv->tv_sec + (tv->tv_usec / 1000000.0);
}

/** convert analog input data to corresponding voltage */
static inline double analog_volts(int data, double maxvolts, int nbits)
{
  // clamp value to specified bit range
  int limit = (1<<nbits);
  data &= (limit - 1);
  return (maxvolts * data) / limit;
}

/** convert analog voltage corresponding digital encoding */
static inline int analog_to_digital(double voltage,
                                    double maxvolts, int nbits)
{
  return (int) rintf((voltage / maxvolts) * (1<<nbits));
}

#endif // _CONVERSIONS_H
