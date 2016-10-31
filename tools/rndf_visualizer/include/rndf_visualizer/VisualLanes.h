// $Id: ad7698127797bd05f15536732c45b0cfcf98d4e4 $

#ifndef __VISUAL_LANES_H__
#define __VISUAL_LANES_H__

#include <vector>
#include <math.h>
#include <errno.h>
#include <stdint.h>

#define OCCUPANCY_UNKNOWN 0.0
#define MAX_OCCUPANCY 127
#define MIN_OCCUPANCY -128
#define OCCUPANCY_INCREMENT 10
#define OCCUPANCY_DECREMENT 5
#define LOGODDS_OCCUPANCY_INCREMENT 3.5
#define LOGODDS_OCCUPANCY_DECREMENT 2.0
#define LOGODDS_MAX_OCCUPANCY 20.0
#define LOGODDS_MIN_OCCUPANCY -20.0
#define EPSILON 0.5
#define MAX_RANGE 160.0


typedef double cell;

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

class VisualLanes {
public:
  VisualLanes(double physical_size, int resolution);
  ~VisualLanes();
  
  /**
   **/
  void gpsEnabled(bool onOff)
  { gpsOnOff = onOff; }
  
  /**
   * Standard initialization function that sets up the robots initial
   * position.
   *
   * Recommended use, is at start up.
   **/
  void initialize(double x, double y, double theta);
  
  /**
   * The function clears the occupancy grid and resets all values in
   * the grid back to the default occupancy.
   **/   
  void clear();
  
  /**
   * This function updates the robot's position in the occupancy grid,
   * I do not know how this will behave if given a GPS coordinate.
   *
   * The function is generally used with respect to the imu, but it is
   * very possible to use it with the GPS player position info as
   * well.
   **/
  void setPosition(double x, double y, double theta);
  
  /**
   * The function takes a 180 degree sick laser scan and updates the
   * occupancy grid.
   **/
  void addSickScan(std::vector<double> ranges);
  
  /**
   * Since the robot behaves in local coordinates, if you pass in an x
   * and y with respect to the robot, it should return the value of
   * that cell. (Note only with respect to the robot)
   *
   * If you need to check a cell for occupancy, its better to use is
   * path clear, Since it will check all sells in between and return
   * the point it believes to have a collision based on the set
   * threshold.
   **/
  cell value(int x, int y);
  
  void setThreshold(int threshold);
  void setCellShift(int shift);
  
  /**
   * This function saves the current occupancy grid to a specified
   * .pgm file.
   **/
  void savePGM(const char *filename);
  
  /**
   * If path is clear, then the function returns an empty cell else
   * the function returns the first cell in which it hits an obstacle
   *
   * Note, this function's input is a point relative to the odometry
   * of the car, I need to write a function for converting GPS to
   * local odometry.
   *
   * Before using this function, you must use setThreshold(int
   * threshold) to set the specified threshold for a cell to be
   * occupied.
   **/
  std::pair<double,double>* isPathClear(double x , double y); 
  
  /**
   * Beware the function is still experimental and definitely needs
   * some work!!
   *
   * The function should return a intermediate point to a goal point,
   * note before using this function, you must set the cell shift
   * size, by using setCellShift(int shift) first.
   **/
  std::pair<double,double> nearestClearPath(std::pair<double,double> obstacle, 
					    std::pair<double,double> original);
  std::pair<double,double>* laserScan(double x, double y);
  
  std::vector<float>* getPose();
  
  void setLaserRange(float range){ laser_range = range; };
  
  double getPhysicalSize(){
    return _physical_size;}

  //map lane fuction that takes waypoints
  void addMapLane(double w1lat, double w1long, double w2lat, double w2long,
      double w3lat, double w3long, double laneWidth);

  //map lane function that takes a sick scan
  void addMapLane(std::vector<double> ranges);

  //add polygon
  //void addPoly(poly &polygon);
  void addPoly(double x1, double x2, double x3, double x4, double y1, double y2,
      double y3, double y4, bool is_stop);

  void addTrace(double w1lat, double w1long, double w2lat, double w2long);
  
private:
  bool valid(int x, int y);
  void lighten(int x, int y);
  cell* at(int x, int y);
  cell *atgoal(int x, int y);
  
  cell **_m;
  double _physical_size;
  int _resolution;
  double _x;
  double _y;
  double _theta;
  int _x_offset;
  int _y_offset;
  
  int _threshold;
  int _shift;
  
  bool scan_off_right_side;
  bool scan_off_left_side;
  bool scan_off_bottom_side;
  bool scan_off_top_side;
  
  int count;
  
  double rX;
  double rY;
  
  float laser_range;
  
  
  bool gpsOnOff;
  
  // implement later 
  // may not need to implement
  void padObstacles(); 
  
  void clearBottom();
  void clearTop();
  void clearRight();
  void clearLeft();
  
  // General Bresenham Function that traverses from (xo, y1) to (x1,
  // y1) and applies 'function' std::pair<int,int>*
  // (VisualLanes::*_fp)(int,int)
  std::pair<int,int>* line(int x0, int y0, int x1, int y1, 
			   std::pair<int,int>* (VisualLanes::*_fp)(int,int));
  
  // Follows the list of functions that should only be used as
  // parameters to line!!  In no way shape or form should there ever
  // be a way to pass a public function pointer to line nor an
  // external function pointer.
  std::pair<int,int>* cellLighten(int x, int y);
  std::pair<int,int>* cellOccupied(int x, int y);
  std::pair<int,int>* cellOccupiedRelative(int x, int y);
  std::pair<int,int>* drawPointB(int x, int y); //for map lanes
  std::pair<int,int>* drawPointW(int x, int y); //for map lanes
  
  // Debug functions, not yet fully implemented; expect them to be
  // explained in the next update.
  std::pair<int,int>* cellOccupiedDebug(int x, int y);
  std::pair<int,int>* cellLightenDebug(int x, int y);
};

#endif
