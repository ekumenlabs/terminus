#include <rndf_visualizer/DrawLanes.h>
#include <rndf_visualizer/euclidean_distance.h>

#include <iostream>

DrawLanes::DrawLanes(int x, int y, float multi) {
  MULT=multi;
  imageWidth=int(ceil(x*MULT));
  imageHeight=int(ceil(y*MULT));
  image = new RGB[imageWidth*imageHeight];
  clear();
}

DrawLanes::~DrawLanes() {

  delete[] image;
}

void DrawLanes::clear() { 
  for (int h=0; h<imageHeight; h++) {
    for (int w=0; w<imageWidth; w++) {
      int index=h*imageWidth+w;
      image[index].r=255;
      image[index].g=255;
      image[index].b=255;
    }
  } 
  // Stage crops white from around and image this fixes this by drawing a line
  // at the top and bottom of the image
  for (int w=0; w<imageWidth; w++) {
    int index=w;
    image[index].r=0;
    image[index].g=0;
    image[index].b=0;
    index=((imageHeight-1)*imageWidth)+w;
    image[index].r=0;
    image[index].g=0;
    image[index].b=0;
  }
}


void DrawLanes::line(float x0, float y0, float x1, float y1, RGB colour)
{
  x0*=MULT;
  y0*=MULT;  
  x1*=MULT;    
  y1*=MULT;

  /*
    x0+=(imageWidth/2.0);
    x1+=(imageWidth/2.0);
    y0+=(imageHeight/2.0);
    y1+=(imageHeight/2.0);
  */


  float full_dist=Euclidean::DistanceTo(x0,y0,x1,y1);

  for (float i=0.0; i<=1.0; i+=1.0/(full_dist)) {
    float newx=i*x0+(1-i)*x1;
    float newy=i*y0+(1-i)*y1;
    
    int xcell=(int)roundf(newx);
    int ycell=(int)roundf(newy);
  
    int index=imageWidth*ycell+xcell;
    
    image[index]=colour;
  }
}

void DrawLanes::savePGM(const char *filename) {
  FILE *f = fopen(filename, "w+");

  fprintf(f,"P3\n");
  fprintf(f,"#%s\n",filename);
  fprintf(f,"%i %i\n",imageWidth,imageHeight);
  fprintf(f,"%i\n",256); // Image width
  for (int h=0; h<imageHeight; h++) {
    for (int w=0; w<imageWidth; w++) {
      int index=h*imageWidth+w;
      fprintf(f,"%i %i %i ",image[index].r,image[index].g,image[index].b);
    }
    fprintf(f,"\n");
  }
  fclose(f);
}

void DrawLanes::addTrace(float w1lat, float w1long, float w2lat, float w2long){
  RGB color;
  color.r=0;
  color.g=0;
  color.b=0;
  line(w1lat,w1long,w2lat,w2long,color);
}

void DrawLanes::addWay(float w1lat, float w1long) {
  RGB color;
  color.r=0;
  color.g=0;
  color.b=0;
  line(w1lat,w1long,w1lat,w1long,color);
}

void DrawLanes::addRobot(float w1lat, float w1long) {
  RGB color;
  color.r=0;
  color.g=0;
  color.b=255;
  line(w1lat,w1long,w1lat,w1long,color);
}



void DrawLanes::addPoly(float x1, float x2, float x3, float x4, float y1,
			float y2, float y3, float y4, bool is_stop, 
			bool is_exit){
  RGB color;
  color.r=0;
  color.g=0;
  color.b=0;
  if (!is_exit)
    {
      DrawLanes::line(x1, y1, x2, y2, color);//draw left
      DrawLanes::line(x3, y3, x4, y4, color);
    }
  if (is_stop) {
    DrawLanes::line(x1, y1, x4, y4, color);
    DrawLanes::line(x2, y2, x3, y3, color);
  }
}

#if 0 //TODO
void DrawLanes::addZone(const ZonePerimeter &zone, float min_x, float max_y)
{
  RGB color;
  color.r=0;
  color.g=1;
  color.b=0;
  unsigned size = zone.perimeter_points.size();
  for(unsigned i = 0; i < size; i++)
    {
      DrawLanes::line(zone.perimeter_points[i].map.x - min_x,
		      max_y - zone.perimeter_points[i].map.y,
		      zone.perimeter_points[(i+1)%size].map.x - min_x,
		      max_y - zone.perimeter_points[(i+1)%size].map.y,
		      color);
    }
}
#endif
