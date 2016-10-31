#ifndef __VECTOR_HEADER__
#define __VECTOR_HEADER__

#include <algorithm>
#include <iostream>
#include <float.h>
#include <epsilon.h>

//==========[ Forward References ]=========================

template <class T> class Vec;
template <class T> class Vec3;
template <class T> class Vec4;
template <class T> class Mat3;
template <class T> class Mat4;

//==========[ Exception Classes ]==========================

class VectorSizeMismatch {};

//==========[ class Vec2 ]=================================

template <class T>
class Vec2 {

  //---[ Private Variable Declarations ]-------

  // x, y
  T n[2];

 public:

  //---[ Constructors ]------------------------

  Vec2() { n[0] = FLT_MAX; n[1] = FLT_MAX; }
  Vec2( const T x, const T y )
    { n[0] = x; n[1] = y; }
  Vec2( const Vec2<T>& v )
    { n[0] = v.n[0]; n[1] = v.n[1]; }

  //---[ Equal Operators ]---------------------

  Vec2<T>& operator=( const Vec2<T>& v )
    { n[0] = v.n[0]; n[1] = v.n[1]; return *this; }
  Vec2<T>& operator +=( const Vec2<T>& v )
    { n[0] += v.n[0]; n[1] += v.n[1]; return *this; }
  Vec2<T>& operator -= ( const Vec2<T>& v )
    { n[0] -= v.n[0]; n[1] -= v.n[1]; return *this; }
  float operator * ( const Vec2<T>& v )
  { return (n[0] * v.n[0] + n[1] * v.n[1]);}
  Vec2<T>& operator *= ( const T d )
    { n[0] *= d; n[1] *= d; return *this; }
  Vec2<T>& operator /= ( const T d )
    { n[0] /= d; n[1] /= d; return *this; }

  //---[ Access Operators ]--------------------

  T& operator []( int i )
    { return n[i]; }
  T operator []( int i ) const 
  { return n[i]; }

  //---[ Arithmetic Operators ]----------------

  Vec2<T> operator-( const Vec2<T>& a ) { 
    return Vec2<T>(n[0]-a.n[0],n[1]-a.n[1]); }
  Vec2<T> operator+( const Vec2<T>& a ) { 
    return Vec2<T>(a.n[0]+n[0],a.n[1]+n[1]); }
  Vec2<T> operator*( const T d) {
    return Vec2<T>(d*n[0],d*n[1] );}
  //---[ Conversion Operators ]----------------

  const T* getPointer() const { return n; }

  //---[ Length Methods ]----------------------

  float length2() const
  { return n[0]*n[0] + n[1]*n[1]; }
  float length() const
  { return sqrtf( length2() ); }

  //---[ Normalization ]-----------------------

  void normalize() { 
    float len = length();
    if (!Epsilon::equal(len,0)) {
      n[0] /= len; 
      n[1] /= len;
    }
  }
  //---[Dot Product]--------------------------
	
  float dot(const Vec2<T>& a){
    return n[0]*a.n[0]+n[1]*a.n[1];
  }

  //---[ Zero Test ]---------------------------

  bool iszero() { return ( (n[0]==0 && n[1]==0) ? true : false); };
  void zeroElements() { memset(n,0,sizeof(T)*2); }

  //---[ Friend Methods ]----------------------
  /* not implemented
     template <class U> friend T operator *( const Vec3<T>& a, const Vec4<T>& b );
     template <class U> friend T operator *( const Vec4<T>& b, const Vec3<T>& a );
     template <class U> friend Vec3<T> operator -( const Vec3<T>& v );
     template <class U> friend Vec3<T> operator *( const Vec3<T>& a, const double d );
     template <class U> friend Vec3<T> operator *( const double d, const Vec3<T>& a );
     template <class U> friend Vec3<T> operator *( const Vec3<T>& v, Mat4<T>& a );
     template <class U> friend T operator *( const Vec3<T>& a, const Vec3<T>& b );
     template <class U> friend Vec3<T> operator *( const Mat3<T>& a, const Vec3<T>& v );
     template <class U> friend Vec3<T> operator *( const Vec3<T>& v, const Mat3<T>& a );
     template <class U> friend Vec3<T> operator *( const Mat4<T>& a, const Vec3<T>& v );
     template <class U> friend Vec3<T> operator /( const Vec3<T>& a, const double d );
     template <class U> friend Vec3<T> operator ^( const Vec3<T>& a, const Vec3<T>& b );
     template <class U> friend bool operator ==( const Vec3<T>& a, const Vec3<T>& b );
     template <class U> friend bool operator !=( const Vec3<T>& a, const Vec3<T>& b );
     template <class U> friend ostream& operator <<( ostream& os, const Vec3<T>& v );
     template <class U> friend istream& operator >>( istream& is, Vec3<T>& v );
     template <class U> friend Vec3<T> minimum( const Vec3<T>& a, const Vec3<T>& b );
     template <class U> friend Vec3<T> maximum( const Vec3<T>& a, const Vec3<T>& b );
     template <class U> friend Vec3<T> prod( const Vec3<T>& a, const Vec3<T>& b );
  */
};

typedef Vec2<int> Vec2i;
typedef Vec2<float> Vec2f;

#endif
