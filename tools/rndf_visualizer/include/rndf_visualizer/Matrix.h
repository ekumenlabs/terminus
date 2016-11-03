/* -*- mode: C++ -*- */

// $Id: 511499d31810733a500dfcdc20f02f7c7b8508ee $

#ifndef _Matrix_h_DEFINED
#define _Matrix_h_DEFINED

class Matrix
{
public:
  int		M;			// number of rows
  int		N;			// number of columns
  float*	X;			// matrix pointer

  int		getm()	const;		// return number  of rows
  int		getn()	const;		// return number  of columns
  float*	getx()	const;		// return pointer to array	 

  // Constructors
  Matrix();
  Matrix(int m, int n, bool I=false);
  Matrix(const Matrix& a);
  ~Matrix();
	
  Matrix transp(); // Matrix Transpose
  Matrix&	operator =  (const Matrix& a); // Overloaded Operator
  float*	operator [] (int i)	const; // Overloaded Operator
	
};

// Overloaded Operators
Matrix	operator +  (const Matrix& a, const Matrix& b);
Matrix	operator -  (const Matrix& a, const Matrix& b);
Matrix	operator *  (const Matrix& a, const Matrix& b);
Matrix	operator *  (const float& a, const Matrix& b);
Matrix	operator *  (const Matrix& a, const float& b);
Matrix	operator /  (const Matrix& a, const float& b);


// 2x2 Matrix Inversion
Matrix Invert22(const Matrix& a);

inline float convDble(const Matrix& a) { return a[0][0]; } // Convert 1x1 matrix to Double
inline	 int		Matrix::getm() const { return M; }
inline	 int		Matrix::getn() const { return N; }
inline	 float*	Matrix::getx() const { return X; }

#endif
