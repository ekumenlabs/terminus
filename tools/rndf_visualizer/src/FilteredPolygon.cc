#include <stdio.h>
#include <rndf_visualizer/Matrix.h>
#include <rndf_visualizer/FilteredPolygon.h>

FilteredPolygon::FilteredPolygon() 
{
  // Set up the initial KF matrix entries for each point
  int numStates=2;
  
  Matrix initStates = Matrix(numStates,1,false);
  initStates[0][0] = -0.001; // Initially place robot at basically 0,0
  initStates[1][0] = -0.001;

  Matrix uncert = Matrix(numStates,numStates,false);
  uncert[0][0] = 6.25;  // Standard deviation is 5.0 metres
  uncert[1][1] = 6.25;
  
  // Start the KF for each point
  for (int i=0; i<NUM_POINTS; i++) {
    point[i].Start(numStates,uncert,initStates);
    point[i].active=true; // Turn the KF on .. supports multiple models which we don't need here
  }

  // Set the KF update parameters that don't change between vision frames
  distStruct.rejectOutliers = false;
  distStruct.outlierSD = 10.0;
  distStruct.mainFilterAngleUpdate = false;
  distStruct.ingoreLongRangeUpdate = false;
  distStruct.deadzoneSize = 0.25; // 25cm
  distStruct.ambigObject = false;
  distStruct.changeAlpha = true;

  angleStruct.rejectOutliers = true;
  angleStruct.outlierSD = DEG_T_RAD*10.0;
  angleStruct.mainFilterAngleUpdate = true;
  angleStruct.ingoreLongRangeUpdate = false;
  angleStruct.deadzoneSize = DEG_T_RAD*2;
  angleStruct.ambigObject = false;
  angleStruct.changeAlpha = true;
  //------------

  #ifdef DEBUGFILTER
  printf("Constructed FilteredPolygon\n");
  #endif
}

// Sets the location of the filtered point ... 
//
// I would suggest only using this to set the original location
// because it changes the X matrix directly and therefore changing it
// other times could corrupt the relationship between X and P
void FilteredPolygon::SetPoint(int pointID, float x, float y) {
  Matrix X=point[pointID].GetStates();
  X[0][0]=x;
  X[1][0]=y;
  point[pointID].SetStates(X);

  #ifdef DEBUGFILTER
  printf("Point %i set to (%f,%f)\n",pointID,x,y);
  #endif
}

// Do an update on a point given vision input (distance and angle)
// *TODO* -> rX,rY,rOri are the location of the robot ... this needs to be fixed
// Also tune !
void FilteredPolygon::UpdatePoint(int pointID, float visionDistance,
                                  float visionBearing, float confidence,
                                  float rX, float rY, float rOri) 
{
  #ifdef DEBUGFILTER	
  Matrix X2=point[pointID].GetStates();
  printf("(%f,%f)->",X2[0][0],X2[1][0]);
  #endif

// The current state of the Kalman Filter	
  Matrix X = point[pointID].GetStates();

  float visionElevation=0;
  float dist = visionDistance*cos(visionElevation);
  float angle = visionBearing;

  // ---- Distance Update
  float Rdist = dist*dist/50 ; // modified .. *TODO* Tune this number
  Matrix Cdist = GetDistanceJacobian(rX, rY, X[0][0], X[1][0]);
  float estDist = sqrt(SQUARE(rX - X[0][0]) + SQUARE(rY - X[1][0]));

  distStruct.R=Rdist;
  distStruct.Y=ABS(dist);
  distStruct.Ybar=estDist;
  distStruct.dist=dist;
  int updateSuccessD = point[pointID].MeasurementUpdateExtended(Cdist,distStruct);
  // ----

  // ---- Angle Update
  float Rangle = 0.002*10;
  Matrix Cangle = GetAngleJacobian(rX, rY, X[0][0], X[1][0]);
  float estAngle = Normalise_PI(atan2(rY-X[1][0],rX-X[0][0]) - rOri);
 // printf("%lf %lf\n",estAngle,visionBearing);
  angleStruct.R=Rangle;
  angleStruct.Y=angle;
  angleStruct.Ybar=estAngle;
  angleStruct.dist=dist;
  int updateSuccessA =
    point[pointID].MeasurementUpdateExtended(Cangle,angleStruct);
  // ----
  if (updateSuccessD!=KF_SUCCESS) {
#ifdef DEBUGFILTER
  printf("updateSuccessD %i",updateSuccessD);
#endif  
  }
  if (updateSuccessA!=KF_SUCCESS) {
#ifdef DEBUGFILTER
  printf("updateSuccessA failed %i",updateSuccessA);
#endif  
  }
  
  #ifdef DEBUGFILTER	
  X2=point[pointID].GetStates();
  printf("(%f,%f)",X2[0][0],X2[1][0]);
  Matrix P2=point[pointID].GetErrorMatrix();
  printf("(%f,%f)\n",P2[0][0],P2[1][0]);
  #endif
}


// Jacobian for Distance and Angle, pass in the location of the robot
// and then the current x,y of the point. Returns a matrix ..
Matrix FilteredPolygon::GetDistanceJacobian(float xb, float yb,
                                            float x, float y)
{
  float dist = sqrt((x-xb)*(x-xb) + (y-yb)*(y-yb));
  if (dist == 0) dist = 0.00001;
  Matrix C = Matrix(1,2,false);
  C[0][0] = (x-xb)/dist;
  C[0][1] = (y-yb)/dist;
  return C;
}

Matrix FilteredPolygon::GetAngleJacobian(float xb, float yb, float x, float y)
{
  float distSqrd = (x-xb)*(x-xb) + (y-yb)*(y-yb);
  if (distSqrd == 0) distSqrd = 0.00001;
  Matrix C = Matrix(1,2,false);
  C[0][0] = (yb-y)/distSqrd;
  C[0][1] = (x-xb)/distSqrd;
  return C;
}

void FilteredPolygon::SetPolygon(poly p)
{
  polygon_ = p;
  SetPoint(0,p.p1.x,p.p1.y);
  SetPoint(1,p.p2.x,p.p2.y);
  SetPoint(2,p.p3.x,p.p3.y);
  SetPoint(3,p.p4.x,p.p4.y);
}

poly FilteredPolygon::GetPolygon()
{
  Matrix X=point[0].GetStates();
  polygon_.p1 = MapXY(X[0][0],X[1][0]);  
  X=point[1].GetStates();
  polygon_.p2 = MapXY(X[0][0],X[1][0]);  
  X=point[2].GetStates();
  polygon_.p3 = MapXY(X[0][0],X[1][0]);
  X=point[3].GetStates();
  polygon_.p4 = MapXY(X[0][0],X[1][0]);
  
  polygon_.heading = ops_.PolyHeading(polygon_);
  polygon_.midpoint = ops_.centerpoint(polygon_);
  polygon_.length = ops_.getLength(polygon_);

  return polygon_;
}

