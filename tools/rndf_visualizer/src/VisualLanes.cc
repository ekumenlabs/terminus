#include <rndf_visualizer/coordinates.h>
#include <rndf_visualizer/euclidean_distance.h>
#include <rndf_visualizer/VisualLanes.h>

#define ONE_GRID 0.9
#define TWO_GRID 1.8

VisualLanes::VisualLanes(double physical_size,
			     int resolution) :
  _m(NULL),
  _physical_size(physical_size),
  _resolution(resolution),
  _x(0),
  _y(0),
  _theta(0),
  _x_offset(0),
  _y_offset(0),
  _shift(0),
  scan_off_right_side(false),
  scan_off_left_side(false),
  scan_off_bottom_side(false),
  scan_off_top_side(false),
  count(0) {
  int r;
  _m = new cell*[_resolution];
  for(r = 0; r < _resolution; r++) {
    _m[r] = NULL;
    _m[r] = new cell[_resolution];
  }
}

VisualLanes::~VisualLanes() {
  int r;
  for(r = 0; r < _resolution; r++) {
    delete[] _m[r];
  }
  delete[] _m;
}

void VisualLanes::clear() {
  int r, c;
  for(r = 0; r < _resolution; r++) {
    for(c = 0; c < _resolution; c++) {
      _m[r][c] = OCCUPANCY_UNKNOWN;
    }
  }
}

void VisualLanes::initialize(double x, double y, double theta) {
  _theta = theta;
  _x = x;
  _y = y;
  _x_offset = 0;
  _y_offset = 0;
  clear();
}

/*
 * Note, that all of these fuctions require that _resolution/2 -
 * (laser_range/_physical_size) >= 0); Also, make sure that if a scan
 * range goes off... of a side that executing these searches on the
 * map don't overlap with the robot's position. This can be arranged
 * by using an appropriate size.
 */

void VisualLanes::clearBottom()
{
  for(int num = _resolution/2; num < _resolution; num++)
    for(int num2 = 0; num2 < _resolution; num2++)	
      _m[num][num2] = 0;
  
}

void VisualLanes::clearTop()
{
  for(int num = 0; num < _resolution/2; num++)
    for(int num2 = 0; num2 < _resolution; num2++)
      _m[num][num2] = 0;
}

void VisualLanes::clearRight()
{
  for(int num = 0; num < _resolution; num++)
    for(int num2 = _resolution/2; num2 < _resolution; num2++)
      _m[num][num2] = 0;
}

void VisualLanes::clearLeft()
{
  for(int num = 0; num < _resolution; num++)
    for(int num2 = 0; num2 < _resolution/2; num2++)
      _m[num][num2] = 0;
}

void VisualLanes::setPosition(double x, double y, double theta) {
  _theta = theta;
  rX = x;
  rY = y;
  if(fabs(_x - x) >= _physical_size) {
    double _x_offset_temp = _x_offset + ((x - _x) / _physical_size);
    _x_offset = (int)_x_offset_temp;
    //printf("_x_offset %i\n", _x_offset);
    _x = x - fmod(x, _physical_size);
  }
  
  if(fabs(_y - y) >= _physical_size) {
    double _y_offset_temp = _y_offset + ((y - _y) / _physical_size);
    _y_offset = (int)_y_offset_temp;
    //printf("_y_offset %i\n", _y_offset);
    _y = y - fmod(y, _physical_size);
  }
  
  
  
  double cellX = _resolution / 2 + _x_offset;
  double cellY = _resolution / 2 + _y_offset;
  
  int cellXtemp = (int)(cellX) % _resolution;
  int cellYtemp = (int)(cellY) % _resolution;
  
  if(cellXtemp < 0)
    {
      printf("The value of cellX %f\n", cellX);
    }
  if(cellYtemp < 0)
    printf("The value of cellY %f\n", cellY);
  
  if( (_resolution/2 + _x_offset) > _resolution
      && (_resolution/2 + _y_offset)  < _resolution
      && (_resolution/2 + _y_offset)  >= 0)
    {
      clearBottom();
      _x_offset = -_resolution/2;
      printf("The bottom was cleared by position\n");
      scan_off_right_side = false;
      scan_off_bottom_side = false;
      scan_off_left_side = false;
      scan_off_top_side = false;
    }
  else if( (_resolution/2 + _x_offset) < 0
           && (_resolution/2 + _y_offset)  >= 0
           && (_resolution/2 + _y_offset)  < _resolution)
    {
      clearTop();
      _x_offset = (_resolution - 1) -  _resolution / 2;
      scan_off_top_side = false;
      scan_off_bottom_side = false;
      scan_off_left_side = false;
      scan_off_right_side = false;
    }
  else if( (_resolution/2 + _y_offset) < 0
           && (_resolution/2 + _x_offset) >= 0
           && (_resolution/2 + _x_offset) < _resolution)
    {
      clearLeft();
      _y_offset = (_resolution - 1) - _resolution / 2;
      printf("The _y_offset %i\n", _y_offset);
      scan_off_top_side = false;
      scan_off_bottom_side = false;
      scan_off_left_side = false;
      scan_off_right_side = false;
    }
  else if( (_resolution/2 + _x_offset) < _resolution
           && (_resolution/2 + _y_offset) > _resolution
           && (_resolution/2 + _x_offset) >= 0)
    {
      clearRight();
      printf("The right was cleared by position: %i\n", count);
      _y_offset = -_resolution/2;
      printf("value: %i \n", _resolution/2 + _y_offset);
      scan_off_right_side = false;
      scan_off_bottom_side = false;
      scan_off_left_side = false;
      scan_off_top_side = false;
      count++;
    }
  
}

std::vector<float>* VisualLanes::getPose()
{
  std::vector<float>* temp = new std::vector<float>();
  temp->push_back(rX);
  temp->push_back(_x_offset);
  temp->push_back(rY);
  temp->push_back(_y_offset);
  temp->push_back(_theta);
  return temp;
}

void VisualLanes::addSickScan(std::vector<double> ranges) {
  int l;
  double temp_theta = _theta - 90 * M_PI/180;
  for (l = 0; l < 180; l++) {
    
    double tempTheta = temp_theta + l * M_PI/180;
    //if(l == 0)
    //printf("temp theta %f\n", temp_theta);
    Coordinates::normalize(temp_theta);
    
    /*double t = M_PI * (1.0 - l/180.0) + _theta;
      double x = (ranges[l] * sin(t)) / _physical_size;
      double y = (ranges[l] * cos(t)) / _physical_size;*/
    
    /*if(l == 90)
      {
      printf("Theta %f tempTheta %f\n", _theta, tempTheta);
      printf("Theta %f super Theta %f\n", _theta,
             (_theta - angles::from_degrees(90)) + angles::from_degrees(90));
      }*/
    //if(ranges[l] != 0)
    //{
    double x = (ranges[l] * cos(tempTheta)) / _physical_size;
    double y = (ranges[l] * sin(tempTheta)) / _physical_size;
    
    //lighten(x, y);
    if( ( x + ( _resolution/2 + _x_offset)%_resolution) > _resolution
        && y < _resolution && y >= 0 && !scan_off_bottom_side)
      {
	clearTop();
	scan_off_bottom_side = true;
      }
    if( (x < _resolution
         && (y + (_resolution/2 + _y_offset)%_resolution) > _resolution
         && x >= 0 && !scan_off_right_side))
      { 
	clearLeft();
	scan_off_right_side = true;
      }
    if( x < _resolution
        && (y + (_resolution/2 + _y_offset)%_resolution ) < 0
        && x >= 0 && !scan_off_left_side)
      {
	clearRight();
	scan_off_left_side = true;
      }
    if( (x + (_resolution/2 + _x_offset)%_resolution ) < 0
        && y >= 0
        && y < _resolution && !scan_off_top_side)
      {
	clearBottom();
	scan_off_top_side = true;
      }
    
    
    //fp = VisualLanes::cellLighten;
    
    
    VisualLanes::line( 0, 0, (int)x, (int)y, (&VisualLanes::cellLighten));
    
    //lighten(x, y);
    double distance = Euclidean::DistanceTo(x,y,0,0);
if ( ( distance < (laser_range / _physical_size - EPSILON)) && ranges[l] != 0)
      {
	cell* c = at((int)x, (int)y);
	if(c != NULL)
	  {
	    if((*c) < 0)
	      (*c) = 3.5;
	    else
	      {
		//(*c) = std::min(LOGODDS_MAX_OCCUPANCY, (*c) +
		//	 LOGODDS_OCCUPANCY_INCREMENT);
		//printf("moo\n");
		(*c) = LOGODDS_MAX_OCCUPANCY;
	      }
	  }	
      }
    //}
  }
}


// This should be deleted but I am leaving it in so that everyone can
// see the old way to do ligthen/line trace

/*void VisualLanes::lighten(int x, int y) {
  int step_count = floor(sqrt(x * x + y * y)) + 2;
  double dx = x / (step_count - 1.0);
  double dy = y / (step_count - 1.0);
  int j;
  
  for (j = 0; j < step_count; j++) {
  int nx = dx * j;
  int ny = dy * j;
  
  cell* c = at(nx, ny);
  if(c != NULL) {
  //cellLighten(nx, ny);
  (*c) = std::max((*c)-LOGODDS_OCCUPANCY_DECREMENT, LOGODDS_MIN_OCCUPANCY);
  //if((*c - OCCUPANCY_DECREMENT) > MIN_OCCUPANCY)
  //	(*c) -= OCCUPANCY_DECREMENT;
  }
  }
  } */


void VisualLanes::setThreshold(int threshold)
{ _threshold = threshold; }

/**
 * This is one of many private functions that are intended to be feed
 * into the generic line trace function, if you need to use it, the
 * arguements are..  number of args, followed by x and y. don't really
 * need number of args... but its there so I can get to the parameters
 * I want.
 */
std::pair<int,int>* VisualLanes::cellLighten(int x, int y)
{
  cell* c = at(x,y);
  if(c != NULL)
    {
      (*c) = std::max((*c)-LOGODDS_OCCUPANCY_DECREMENT, LOGODDS_MIN_OCCUPANCY);
      //(*c) = LOGODDS_MIN_OCCUPANCY;
    } 
  return NULL;	
}

/**
 * If the cell is occupied then return the std::pair<int,int>
 * containing the x and y that refer to the occupancy grid point.
 * 
 * Note, don't forget that the pair will be casted to void* before
 * return!!
 */
std::pair<int,int>* VisualLanes::cellOccupied(int x, int y)
{
  cell* c = atgoal(x,y);
  if(c != NULL)
    {
      //cellLightenDebug(x,y);
      if( *c >= _threshold )
	{
	  //printf("x: %i, y: %i 's value: %i\n", x, y, *c);
	  //printf("_threshold: %i: \n", _threshold);
	  std::pair<int,int>* result = new std::pair<int,int>();
	  result->first = x;
	  result->second = y;
	  return result;
	}
    }
  return NULL;
}

std::pair<int,int>* VisualLanes::cellOccupiedDebug(int x, int y)
{
  cell* c = atgoal(x,y);
  if(c != NULL)
    {
      //printf("x: %i, y: %i 's value: %i\n", x, y, *c);
      cellLightenDebug(x,y);
      if( *c >= _threshold )
	{
	  std::pair<int,int>* result = new std::pair<int,int>();
	  result->first = x;
	  result->second = y;
	  return result;
	}
    }
  return NULL;
}

std::pair<int,int>* VisualLanes::cellLightenDebug(int x, int y)
{
  cell* c = atgoal(x,y);
  if(c != NULL)
    {
      //(*c) = std::max((*c)-LOGODDS_OCCUPANCY_DECREMENT, LOGODDS_MIN_OCCUPANCY);
      (*c) = LOGODDS_MIN_OCCUPANCY;
    } 
  return NULL;	
}

/**
 * Takes in a function pointer to a function that opperates
 * on x and y cell. The x and y are cells that must be reached by
 * by a line trace.
 */
std::pair<int,int>* VisualLanes::line(int x0, int y0, int x1, int y1,
                                      std::pair<int,int>*
                                      (VisualLanes::*_fp) (int,int))
{
  //This is how you invoke a pointer to a memeber function!!!
  //(this->*_fp)(1,1);
  
  
  int dy = y1 - y0;
  int dx = x1 - x0;
  int stepx, stepy;
  
  std::pair<int,int> *result = NULL;
  
  if (dy < 0) { dy = -dy;  stepy = -1; } else { stepy = 1; }
  if (dx < 0) { dx = -dx;  stepx = -1; } else { stepx = 1; }
  dy <<= 1;                                                  // dy is now 2*dy
  dx <<= 1;                                                  // dx is now 2*dx
  
  (this->*_fp)(x0, y0); //never check for a return value on this
			//cell... until its changed to where the car
			//is not there, at this point in time.
  if (dx > dy) {
    int fraction = dy - (dx >> 1);      // same as 2*dy - dx
    while (x0 != x1) {
      if (fraction >= 0) {
	y0 += stepy;
	fraction -= dx;                 // same as fraction -= 2*dx
      }
      x0 += stepx;
      fraction += dy;                   // same as fraction -= 2*dy
      if( (result = (this->*(_fp))(x0, y0)) != NULL  )
	return result;
    }
  } else {
    int fraction = dx - (dy >> 1);
    while (y0 != y1) {
      if (fraction >= 0) {
	x0 += stepx;
	fraction -= dy;
      }
      y0 += stepy;
      fraction += dx;
      if( (result = (this->*(_fp))(x0, y0)) != NULL  )
	return result;
    }
  }
  return result;     
}

cell VisualLanes::value(int x, int y) {
  if(valid(x, y)) {
    return *(at(x,y));
  }
  else return OCCUPANCY_UNKNOWN;
}

bool VisualLanes::valid(int x, int y) {
  return (x < _resolution / 2 &&
	  y < _resolution / 2 &&
	  x > -_resolution / 2 &&
	  y > -_resolution / 2);
}

void VisualLanes::savePGM(const char *filename) {
  int i, j;
  cell c;
  unsigned char d;
  FILE *file;
  
  file = fopen(filename, "w+");
  if (file == NULL) {
    //fprintf(stderr, "error writing %s : %s", filename, strerror(errno));
    return;
  }
  
  fprintf(file, "P5 %d %d 255\n", _resolution, _resolution);
  for (j = _resolution - 1; j >= 0; j--) {
    for (i = 0; i < _resolution; i++) {
      c = _m[i][j];
      
      d = (unsigned char)((unsigned int)(((20 - c)*255/40)));
      
      fwrite(&d, 1, 1,  file);
    }
  }
  fclose(file);
}



void VisualLanes::padObstacles()
{
  
}

std::pair<int,int>* VisualLanes::cellOccupiedRelative(int x, int y)
{
  cell* c = at(x,y);
  if(c != NULL)
    {
      if( *c >= _threshold )
	{
	  std::pair<int,int>* result = new std::pair<int,int>();
	  result->first = x;
	  result->second = y;
	  return result;
	}
      //else
      //   printf("c value %f\n", *c);
    }
  return NULL;
}

std::pair<double,double>* VisualLanes::laserScan(double x, double y)
{
  std::pair<double,double>* result = new std::pair<double,double>();
  
  result->first = 0;
  result->second = 0;
  
  std::pair<int,int>* temp;
  //uses a different occupied that looks locally to the robot rather than
  //some global point in the map!!
  temp = VisualLanes::line(0, 0, (int)x, (int)y,
                           (&VisualLanes::cellOccupiedRelative));
  if(temp != NULL)
    {
      //double x_offsetObstacle = (2 * temp->first - _resolution)
      //                           /(_physical_size + 2);
      //double y_offsetObstacle = (2 * temp->second - _resolution)
      //                           /(_physical_size + 2);
      
      result->first = temp->first;
      result->second = temp->second;
      //printf("result offset x: %f, offset y: %f\n",
      //       x_offsetObstacle, y_offsetObstacle);
    }
  else
    return NULL;
  
  return result;    
}

std::pair<double,double>* VisualLanes::isPathClear(double x, double y)
{   
  std::pair<double,double>* result = new std::pair<double,double>();
  
  result->first = 0;
  result->second = 0;
  
  double x_offset = 0;
  double y_offset = 0;
  
  
  //printf("y value passed in %f\n", y);   
  if(fabs(0 - x) >= _physical_size) {
    x_offset = (x - 0) / _physical_size;
    x = x - fmod(x, _physical_size);
  }
  if(fabs(0 - y) >= _physical_size) {
    y_offset = (y - 0) / _physical_size;
    y = y - fmod(y, _physical_size);
  }
  
  //printf("y_offset %f should be 0:\n", y_offset);
  //printf("y value after modifications %f\n", y);
  
  //printf(" x cell without mod %i\n",
  //       (((int)x) + _resolution) / 2 + ((int)x_offset) );
  
  double xGoalLocalTemp = 0;
  xGoalLocalTemp = ( (0 + _resolution / 2 ) + x_offset );  //% _resolution;
  double yGoalLocalTemp = 0;
  yGoalLocalTemp = ( (0 + _resolution / 2 ) + y_offset );
  int xGoalLocal = (int)(xGoalLocalTemp);
  int yGoalLocal = (int)(yGoalLocalTemp);
  
  double tempXRobotLocal = ( (0 + _resolution / 2) + _x_offset );
  double tempYRobotLocal = ( (0 + _resolution / 2) + _y_offset );
  int xRobotLocal = (int)tempXRobotLocal;
  int yRobotLocal = (int)tempYRobotLocal;
  
  //printf("xGoalLocal: %i yGoalLocal: %i xRobotLocal: %i yRobotLocal: %i\n",
  //       xGoalLocal, yGoalLocal, xRobotLocal, yRobotLocal);
  std::pair<int,int>* center_collision;
  double offset_right = _theta-HALFPI;
  offset_right=Coordinates::normalize(offset_right);
  double offset_left = _theta+HALFPI;
  offset_left=Coordinates::normalize(offset_left);
  
  center_collision = (VisualLanes::line(xRobotLocal, yRobotLocal,
                                        xGoalLocal, yGoalLocal,
                                        (&VisualLanes::cellOccupied)));
  std::pair<int,int>* right_collision =
    (VisualLanes::line((int)(cos(offset_right) * ONE_GRID + xRobotLocal),
                       (int)(sin(offset_right) * ONE_GRID + yRobotLocal),
                       (int)(cos(offset_right) * ONE_GRID + xGoalLocal),
                       (int)(sin(offset_right) * ONE_GRID + yGoalLocal),
                       (&VisualLanes::cellOccupied)));
  std::pair<int,int>* right_collision2 =
    (VisualLanes::line((int)(cos(offset_right) * TWO_GRID + xRobotLocal),
                       (int)(sin(offset_right) * TWO_GRID + yRobotLocal),
                       (int)(cos(offset_right) * TWO_GRID + xGoalLocal),
                       (int)(sin(offset_right) * TWO_GRID + yGoalLocal),
                       (&VisualLanes::cellOccupied)));
  std::pair<int,int>* left_collision =
    (VisualLanes::line((int)(cos(offset_left) * ONE_GRID + xRobotLocal),
                       (int)(sin(offset_left) * ONE_GRID + yRobotLocal),
                       (int)(cos(offset_left) * ONE_GRID + xGoalLocal),
                       (int)(sin(offset_left) * ONE_GRID + yGoalLocal),
                       (&VisualLanes::cellOccupied)));
  std::pair<int,int>* left_collision2 =
    (VisualLanes::line((int)(cos(offset_left) * TWO_GRID + xRobotLocal),
                       (int)(sin(offset_left) * TWO_GRID + yRobotLocal),
                       (int)(cos(offset_left) * TWO_GRID + xGoalLocal),
                       (int)(sin(offset_left) * TWO_GRID + yGoalLocal),
                       (&VisualLanes::cellOccupied)));
  
  std::pair<int,int>* collision = center_collision;
  
  //FORGIVE US JACK!
  collision = (center_collision != NULL) ? center_collision : 
    (right_collision != NULL) ? right_collision :
    (right_collision2 != NULL) ? right_collision2 :
    (left_collision != NULL) ? left_collision :
    (left_collision2 != NULL) ? left_collision2 : NULL;
  
  if(collision != NULL)
    {
      //This conversion code should also be placed in a function!
      double x_offsetObstacle =
        (2 * collision->first - _resolution)/(_physical_size + 2);
      double y_offsetObstacle =
        (2 * collision->second -_resolution)/(_physical_size + 2);
      
      result->first =  (_physical_size * x_offsetObstacle);
      result->second = (_physical_size * y_offsetObstacle);
      
      //result->first = temp->first;
      //result->second = temp->second;
    }
  else
    result = NULL;
  
  return result;
}

//Note, this is the amout to shift on the perpendicular line from
//an obstacle. (static only!)
void VisualLanes::setCellShift(int shift)
{ _shift = shift;}


//There is lots of room for expansion in how this class returns a point
//This function is currently not working as intended; I will try my best
//to debug it quickly, but it is possible to do some basic behaviors in
//assignment 2 without it.
std::pair<double,double>
VisualLanes::nearestClearPath(std::pair<double,double> obstacle,
                              std::pair<double,double> original)
{
  std::pair<int,int>* temp;
  
  double slop = 0;
  
  double localXobstacle = 0;
  double localYobstacle = 0;
  
  double localXGoal = 0;
  double localYGoal = 0;
  
  double xTempOffset = 0;
  double yTempOffset = 0;
  
  double xTemp = 0;
  double yTemp = 0;
  
  //This conversion code should really be placed in a function!
  if(fabs(0 - obstacle.first) >= _physical_size) {
    xTempOffset = (obstacle.first - 0) / _physical_size;
    xTemp = obstacle.first - fmod(obstacle.first, _physical_size);
  }
  if(fabs(0 - obstacle.second) >= _physical_size) {
    yTempOffset = (obstacle.second - 0) / _physical_size;
    yTemp = obstacle.second - fmod(obstacle.second, _physical_size);
  }
  
  localXobstacle = ( (((int)xTemp) + _resolution) / 2 + ((int)xTempOffset) );
  localYobstacle = ( (((int)yTemp) + _resolution) / 2 + ((int)yTempOffset) );
  
  xTempOffset = 0;
  yTempOffset = 0;    
  
  xTemp = 0;
  yTemp = 0;
  
  if(fabs(0 - original.first) >= _physical_size) {
    xTempOffset = (original.first - 0) / _physical_size;
    xTemp = original.first - fmod(original.first, _physical_size);
  }
  if(fabs(0 - original.second) >= _physical_size) {
    yTempOffset = (original.second - 0) / _physical_size;
    yTemp = original.second - fmod(original.second, _physical_size);
  }
  
  localXGoal = ( (((int)xTemp) + _resolution) / 2 + ((int)xTempOffset) );
  localYGoal = ( (((int)yTemp) + _resolution) / 2 + ((int)yTempOffset) );
  
  //The perpendicular slop -1/m
  
  //printf("LocalYGoal: %f LocalYobstacle: %f\n", localYGoal, localYobstacle);
  //printf("localXGoal: %f LocalXobstacle: %f\n", localXGoal, localXobstacle);
  
  
  if((localYGoal - localYobstacle) == 0)
    slop = -((localXGoal - localXobstacle)/(localYGoal+1 - localYobstacle));
  else
    slop = -((localXGoal - localXobstacle)/(localYGoal - localYobstacle));
  
  //printf("slop: %f\n", slop);
  
  bool validPointFound = false;
  int shiftScaler = 1;
  
  int localXshiftedUp = 0;
  int localYshiftedUp = 0;
  
  int localXshiftedDown = 0;
  int localYshiftedDown = 0;
  
  while(!validPointFound)
    {
      localXshiftedUp =
        (int)(((_shift * shiftScaler) + slop * localXobstacle)/slop);
      localYshiftedUp =
        (int)(_shift * shiftScaler + localYobstacle);
      
      localXshiftedDown =
        (int)((( -1 * _shift * shiftScaler) + slop * localXobstacle)/slop);
      localYshiftedDown =
        (int)(-1 * _shift * shiftScaler + localYobstacle);
      
      //Logic Flaw here to fix... at a later date
      temp = (VisualLanes::line(localXshiftedUp, localYshiftedUp,
                                (int)localXGoal, (int)localYGoal,
                                (&VisualLanes::cellOccupied)));
      if(temp == NULL)
	{
	  temp = new std::pair<int,int>( (int)localXshiftedUp,
                                         (int)localYshiftedUp);
	  break;
	}
      temp = (VisualLanes::line(localXshiftedDown, localYshiftedDown,
                                (int)localXGoal, (int)localYGoal,
                                (&VisualLanes::cellOccupied)));
      if(temp != NULL)
	{
	  temp = new std::pair<int,int>( (int)localXshiftedDown,
                                         (int)localYshiftedDown);
	  break;
	}
      
      shiftScaler++;
    }
  
  double x_offsetSubPoint = (2 * temp->first - _resolution)/(_physical_size + 2);
  double y_offsetSubPoint = (2 * temp->second -_resolution)/(_physical_size + 2);
  
  std::pair<double,double>* result =
    new std::pair<double,double>(_physical_size * x_offsetSubPoint,
                                 _physical_size * y_offsetSubPoint);
  
  return *result;
}


cell *VisualLanes::atgoal(int x, int y)
{
  //printf(" cell x index %i\n",
  //       ((x + _resolution)/2 + x_offsetCurrentGoal) % _resolution);
  return &(_m[x % _resolution][y % _resolution]);
}


cell *VisualLanes::at(int x, int y) {
  if(valid(x,y)) {
    
    int cellX = (x + _resolution / 2 + _x_offset) % _resolution;
    int cellY = (y + _resolution / 2 + _y_offset) % _resolution;
    //return &(_m[(x + _resolution / 2 + _x_offset) % _resolution]
    //	 [(y + _resolution / 2 + _y_offset) % _resolution]);
    
    //if(cellY == 0)
    //{
    //	printf("The Y offset: %i\n", _y_offset);
    //	printf("The Y value: %i\n", y);
    //	printf("Cell Value: %i\n",
    //         (y + _resolution/2 + _y_offset) % _resolution);
    //}
    if( cellX >= 0 && cellY >= 0 )
      return &_m[cellX][cellY];
    else if(cellY < 0 && cellX < 0)
      return &_m[_resolution+cellX][_resolution+cellY];
    else if(cellX < 0)
      return &_m[_resolution+cellX][cellY];
    else
      return &_m[cellX][_resolution+cellY];
    
    
  }
  return NULL;
}

//map lanes stuff
//takes a couple of waypoints and makes a sick scan of the lane
void VisualLanes::addMapLane(double w1lat, double w1long, double w2lat,
    double w2long, double w3lat, double w3long, double laneWidth){
	//store car's current position
	//double carX = _x;
	//double carY = _y;
	//double carTheta = _theta;

  double distance1 = Euclidean::DistanceTo(w1lat, w1long, w2lat, w2long);
  double distance2 = Euclidean::DistanceTo(w3lat, w3long, w2lat, w2long);
  double theta1 = atan2(w2long-w1long, w2lat-w1lat);
  double theta2 = atan2(w3long-w2long, w3lat-w2lat);
	
  if(distance1 > 5 && distance2 > 5){
    //calc first bisec
    double angle = theta1 - (theta2 - theta1)/4;
    double newDist = (distance1/2) * cos((theta2-theta1)/4);
    double mid1lat = w1lat + newDist*cos(angle);
    double mid1long = w1long + newDist*sin(angle);
    //calc second bisec
    angle = theta2 - (theta2 - theta1)/4;
    newDist = (distance2/2) * cos((theta2-theta1)/4);
    double mid2lat = w2lat + newDist*cos(angle);
    double mid2long = w2long + newDist*sin(angle);
    addMapLane(w1lat, w1long, mid1lat, mid1long, w2lat, w2long, laneWidth);
    addMapLane(mid1lat, mid1long, w2lat, w2long, mid2lat, mid2long, laneWidth);
    addMapLane(w2lat, w2long, mid2lat, mid2long, w3lat, w3long, laneWidth);
  }
  else{
    //add first segment
    double theta = theta1;
    double laneMarkOffset = laneWidth/2;
    
    //create laser array
    std::vector<double> ranges(180);
    for (int i = 0; i < 90; i++){
      if(laneMarkOffset*tan(i * M_PI/180) <= distance1)
	ranges[i] = laneMarkOffset/cos(i * M_PI/180);
      else
	ranges[i] = -distance1/sin(i * M_PI/180);
    }
    for (int i = 90; i < 180; i++){
      ranges[i] = ranges[179-i];
    }
    
    //add lane to ogrid
    setPosition(w1lat, w1long, theta);
    addMapLane(ranges);
    setPosition(w2lat, w2long, (theta < 0 ? theta+M_PI : theta-M_PI));
    addMapLane(ranges);
    
    //add second segment
    theta = theta2;
    
    //create laser array
    for (int i = 0; i < 90; i++){
      if(laneMarkOffset*tan(i * M_PI/180) <= distance2)
	ranges[i] = laneMarkOffset/cos(i * M_PI/180);
      else
	ranges[i] = -distance2/sin(i * M_PI/180);
    }
    for (int i = 90; i < 180; i++){
      ranges[i] = ranges[179-i];
    }
    
    //add lane to ogrid
    setPosition(w2lat, w2long, theta);
    addMapLane(ranges);
    setPosition(w3lat, w3long, (theta < 0 ? theta+M_PI : theta-M_PI));
    addMapLane(ranges);
  }
  
  //reset location to car
  //setPosition(carX, carY, carTheta);
}

//adds a lane segment to the ogrid
void VisualLanes::addMapLane(std::vector<double> ranges)
{
  int l;
  double temp_theta = _theta - 90 * M_PI/180;
  bool laneMark = true;
  for (l = 0; l < 180; l++) {
	
    double tempTheta = temp_theta + l  * M_PI/180;
    //if(l == 0)
    //printf("temp theta %f\n", temp_theta);
    temp_theta=Coordinates::normalize(temp_theta);

    /*double t = M_PI * (1.0 - l/180.0) + _theta;
      double x = (ranges[l] * sin(t)) / _physical_size;
      double y = (ranges[l] * cos(t)) / _physical_size;*/

    /*if(l == 90)
      {
      printf("Theta %f tempTheta %f\n", _theta, tempTheta);
      printf("Theta %f super Theta %f\n", _theta,
      (_theta - angles::from_degrees(90))
      + angles::from_degrees(90));
      }*/
    //if(ranges[l] != 0)
    //{
    laneMark = ranges[l] > 0;
    if(!laneMark)
      ranges[l] = -ranges[l];
    double x = (ranges[l] * cos(tempTheta)) / _physical_size;
    double y = (ranges[l] * sin(tempTheta)) / _physical_size;

    //lighten(x, y);
    if(( x + ( _resolution/2 + _x_offset)%_resolution) > _resolution
       && y < _resolution && y >= 0 && !scan_off_bottom_side)
      {
        clearTop();
        scan_off_bottom_side = true;
      }
    if( (x < _resolution
         && (y + (_resolution/2 + _y_offset)%_resolution) > _resolution
         && x >= 0
         && !scan_off_right_side))
      { 
        clearLeft();
        scan_off_right_side = true;
      }
    if( x < _resolution
        && (y + (_resolution/2 + _y_offset)%_resolution ) < 0
        && x >= 0 && !scan_off_left_side)
      {
        clearRight();
        scan_off_left_side = true;
      }
    if( (x + (_resolution/2 + _x_offset)%_resolution ) < 0
        && y >= 0 && y < _resolution && !scan_off_top_side)
      {
        clearBottom();
        scan_off_top_side = true;
      }

    VisualLanes::line( 0, 0, (int)x, (int)y,
                       (&VisualLanes::drawPointW));

    if(laneMark){
      drawPointB((int)x, (int)y);
    }
  }
}

void VisualLanes::addPoly(double x1, double x2, double x3, double x4,
                          double y1, double y2, double y3, double y4,
                          bool is_stop)
{
  x1 = x1 / _physical_size;
  x2 = x2 / _physical_size;
  x3 = x3 / _physical_size;
  x4 = x4 / _physical_size;
  y1 = y1 / _physical_size;
  y2 = y2 / _physical_size;
  y3 = y3 / _physical_size;
  y4 = y4 / _physical_size;
  
  if(is_stop)
    {
      //draw front
      VisualLanes::line((int)x2, (int)y2, (int)x3, (int)y3,
                        (&VisualLanes::drawPointW));
      //draw back
      VisualLanes::line((int)x4, (int)y4, (int)x1, (int)y1,
                        (&VisualLanes::drawPointW));
    }
  //draw left
  VisualLanes::line( (int)x1, (int)y1, (int)x2, (int)y2,
                     (&VisualLanes::drawPointB));
  //draw right
  VisualLanes::line((int)x3, (int)y3, (int)x4, (int)y4,
                    (&VisualLanes::drawPointB));
}

void VisualLanes::addTrace(double w1lat, double w1long,
                           double w2lat, double w2long)
{
  double x1 = w1lat / _physical_size;
  double y1 = w1long / _physical_size;
  double x2 = w2lat / _physical_size;
  double y2 = w2long / _physical_size;
  VisualLanes::line( (int)x1, (int)y1, (int)x2, (int)y2,
                     (&VisualLanes::drawPointW));
}

//for map lanes: only makes cell black if not already white to avoid overdraw
std::pair<int,int>* VisualLanes::drawPointB(int x, int y)
{
  cell* c = at(x,y);
  if(c != NULL)
    {
      (*c) = LOGODDS_MAX_OCCUPANCY;;
    } 
  return NULL;	
}

//for map lanes
std::pair<int,int>* VisualLanes::drawPointW(int x, int y)
{
  cell* c = at(x,y);
  if(c != NULL)
    {
      (*c) = LOGODDS_MIN_OCCUPANCY;;
    } 
  return NULL;	
}
//end map lane stuff
