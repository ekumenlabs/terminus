#include <rndf_visualizer/SmoothCurve.h>


SmoothCurve::SmoothCurve(const std::vector<Point2f>& ctrl, 
			 float starttheta, float startspeed,
			 float endtheta, float endspeed, bool use_pats)
{
  // use_pats uses Patrick's change the curves to use derivative
  // based on one neighboring waypoint instead of two.  The one
  // neighboring waypoint is chosen by looking for the one that is
  // part of the straightest path with the current waypoint.

  startspeed = fmax(1,startspeed);
  endspeed = fmax(1,endspeed);

  degree=3;
  
  dataPoints=ctrl;
  //CONTROLPOINTS
  int n =(dataPoints.size()-1)*2;
  controlPoints.resize(n);

  for (int i = 0; i < (int)controlPoints.size(); i++)
    {
      controlPoints[i] = dataPoints[(i + 1 )/ 2];
    }
    

  n = dataPoints.size();
  float speed = (startspeed+endspeed) / 2.0;
  std::vector<Point2f> M;
  M.resize(n);
  M[0] = Vec2f(cosf(starttheta),sinf(starttheta))*startspeed;
  M[n-1] = Vec2f(cosf(endtheta),sinf(endtheta))*endspeed;
  for (int i = 1; i < n-1;i++)
    {
      Vec2f a = dataPoints[i] - dataPoints[i-1];
      Vec2f b = dataPoints[i+1] - dataPoints[i];
      a.normalize();
      b.normalize();
      Vec2f top=a+b;
      if (use_pats && i >1 && i <n-2) {
	Vec2f a2 = dataPoints[i] - dataPoints[i-2];
	Vec2f b2 = dataPoints[i+2] - dataPoints[i];
	a2.normalize();
	b2.normalize();
	float adot=a.dot(a2);
	float bdot=b.dot(b2);
	float ratio=adot/bdot;
	if (Epsilon::lte(ratio,.9775))
	  top=b;
	else if (Epsilon::gte(ratio,1/.9775))
	  top=a;
	/*
	  if (Epsilon::equal(adot,bdot))
	  top = a+b;
	  else if(adot < bdot)
	  top=b;
	  else top=a;
	*/
      }
      top.normalize();
      M[i] = top*speed;
    }
  
  //Really Estimate Path Length And Calculate Knots
  knots.resize(ctrl.size());
  knots[0]=0;
  for(unsigned int i=1;i<knots.size();i++){
    Vec2f a = dataPoints[i] - dataPoints[i-1];
    float alen=a.length();

    Vec2f v1 = M[i-1]; 
    Vec2f v2 = M[i];

    a.normalize();
    v1.normalize();
    v2.normalize();
    
    float theta1 = acosf(fmax(-1.0,fmin(1.0,a.dot(v1))));
    float theta2 = acosf(fmax(-1.0,fmin(1.0,a.dot(v2))));

    float l1 = 0, l2 = 0;
    float sinth1=sinf(theta1);
    if (Epsilon::equal(sinth1,0.0)) 
      l1 = alen;
    else
      l1 = fabs(alen*theta1/sinth1);

    
    float sinth2=sinf(theta2);
    if (Epsilon::equal(sinth2,0.0)) 
      l2 = alen;
    else
      l2 = fabs(alen*theta2/sinth2);


    float r= l1 + l2;
    
    if(i==1){
      r/=(startspeed+speed);
    }
    else if(i==(knots.size()-1)){
      r/=(endspeed+speed);
    }
    else{
      r/=(2.0*speed);
    }
    
    
    knots[i]=knots[i-1]+r;
  }
  
  //for(int i=0;i<(int)knots.size();i++){
  //  printf("Knots %d %f",i,knots[i]);
  //}
  
  //Convert from Hermite to Bezier
  for(int i=0;i< (int)controlPoints.size();i++){
    Vec2f tempVec1 = M[(i+1)/2];
    float del;
    //printf("Vector for Derivative: %f, %f\n", tempVec1[0], tempVec1[1]);
    if(i%2==0){
      del = (DeltaU(i/2)/((float)degree));
      controlPoints[i]+= tempVec1 * del;
    }		
    else{
      del = (DeltaU((i-1)/2)/((float)degree));
      controlPoints[i]-= tempVec1 * del;
    }
  }
  
}
  
SmoothCurve::~SmoothCurve() {}

float SmoothCurve::DeltaU (int i) 
{ 
  if (i >= (int)knots.size()-1)
    {
      std::cerr << "Delta() - array out of bounds" << std::endl;
      exit(1);
    }
  else	
    return knots[i+1] - knots[i];
}

Point2f SmoothCurve::bezierPoint(int i)
{
  Point2f temp;
  switch(i%3){
  case 0:
    temp=dataPoints[i/3];
    break;
  case 1:
    temp=controlPoints[2*(i/3)];
    break;
  default:
    temp=controlPoints[2*(i/3)+1];    
  }
  return temp;
}
  
Vec2f SmoothCurve::Delta(int i)
{
  return bezierPoint(i+1)-bezierPoint(i);
}
  

int SmoothCurve::knotCount() const 
{
  return knots.size();
}
    
int SmoothCurve::controlPointsCount() const 
{
  return controlPoints.size();
}    
    
int SmoothCurve::dataPointsCount() const 
{
  return dataPoints.size();
}

Point2f SmoothCurve::getDataPoint(int index) const 
{
  return dataPoints[index];
}
	
Point2f SmoothCurve::getControlPoint(int index) const 
{
  return controlPoints[index];
}

float SmoothCurve::getKnot(int index) const 
{
  return knots[index];
}
    
void SmoothCurve::clear()
{
  dataPoints.clear();
  knots.clear();
  controlPoints.clear();
}
    

float SmoothCurve::curveLength() 
{
  return knots.empty() ? 0 : knots.back();
}
    
Point2f SmoothCurve::evaluatePoint(float time)
{

  if (dataPoints.empty())
    return Point2f();

  unsigned int i=0;
  
  while (i < knots.size() &&
	 knots[i] <= time)
    i++;

  if (i == 0)
    return dataPoints[0];
  if (i >= knots.size())
    return dataPoints.back();
      
  // Curves and Surfaces for Computer Aided Geometric Design 1st Edition
  // Gerald Farin 
  // Chapter 4 p 34
  Point2f sum(0,0);
  std::vector<float> b(degree+1,0);
  float u = (time-knots[i-1])/(knots[i]-knots[i-1]);
  
  b[0]=powf(1-u,3);
  b[1]=3*(u*powf(1-u,2));
  b[2]=3*(powf(u,2)*powf(1-u,1));
  b[3]=powf(u,3);
  
  i=(i-1)*3;
  for(int j=0;j<degree+1;j++)
    sum+=bezierPoint(i+j)*b[j];
  return sum;
}
