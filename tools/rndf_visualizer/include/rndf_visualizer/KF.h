/* -*- mode: C++ -*- */

// $Id: 376dd95228773b5c530140f71722e39a63799d58 $

#ifndef _KF_h_DEFINED
#define _KF_h_DEFINED

//#define DEBUGFILTER

#include <stdio.h>
#include <rndf_visualizer/Matrix.h>
#include <rndf_visualizer/MQMath.h>

#define KF_CRASH 0 // Matrix dimensions error, check your code!
#define KF_NUMERICS 1 // Bad error matrix, reset
#define KF_OUTLIER 2 // Outlier rejected
#define KF_SUCCESS 3 // Success!

#define S_D_RANGE_REJECT 2

struct KFStruct {
  //Matrix &C;
  float R;
  float Y;
  float Ybar;
  bool rejectOutliers;
  float outlierSD;
  bool mainFilterAngleUpdate;
  bool ingoreLongRangeUpdate;
  float deadzoneSize;
  float dist;
  bool ambigObject;
  bool changeAlpha;
};

class KF 
{
  public:
    KF();
    ~KF() {};
        
    bool Start(short numStates, Matrix& uncert, Matrix& intStates);
    bool Restart();
    bool TimeUpdate(Matrix& A, Matrix& B, Matrix& U, Matrix& Q,
                    bool mainFilterUpdate);
    bool TimeUpdateExtended(Matrix& A, Matrix& Xbar, Matrix& Q);
    int MeasurementUpdate(Matrix& C, float R, float Y, bool rejectOutliers,
                          float outlierError, bool mainFilterAngleUpdate);
    int MeasurementUpdateExtended(Matrix& C, float R, float Y, float Ybar,
                                  bool rejectOutliers, float outlierError,
                                  bool mainFilterAngleUpdate,
                                  bool ignoreLongRangeUpdate,
                                  float deadzoneSize, float dist,
                                  bool ambigObject, bool changeAlpha);

    int MeasurementUpdateExtended(Matrix &C,KFStruct s);

    void Reset();
    Matrix GetStates();
    void SetStates(Matrix Xbar);
    float GetState(short n);
    void SetState(short n, float x);
    void NormaliseState(short n);
    Matrix GetErrorMatrix();
    void SetErrorMatrix(Matrix Pbar);
    float GetCovariance(short m, short n);
    float GetVariance(short n);
    Matrix GetXchanges();
    float GetXchange(short n);
    void CompilerError(const char* str);
    
    void Deadzone(float* R, float* innovation, float CPC, float eps);

    short numStates;
    Matrix I;
    Matrix initX;
    Matrix initP;
    Matrix X;
    Matrix P;
    Matrix Xchange;
  
    // ------ New Stuff for multiple models

    // Control and model Evaluation
    bool active;    // Is the model currrently in use ?
    bool activate; 
    float alpha;   // The probability that the model is correct (0->1)
};

#endif // _KF_h_DEFINED
