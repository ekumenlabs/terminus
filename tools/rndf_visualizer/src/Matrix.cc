/* $Id: 477b7d1f78f5e8300dbb57da7fb985b10f7101f3 $ */

#include <rndf_visualizer/Matrix.h>
#include <string.h>

// Constructors
Matrix::Matrix()
{
	M = 0;
	N = 0;
	X = 0;
}

Matrix::Matrix(int m, int n, bool I/*= false*/)  
{	
	M=m;
	N=n;
	X=new float [m*n];
	//Initialise matrix to zero
	for (int i = 0; i < m; i++)
	{
		for (int j = 0; j < n; j++)
		{
			(*this)[i][j] = 0;
		}
	}
	//Identity Matrix Initialisation
	if (I)
	{
		if (m != n)
			return;
			
		for (int i = 0; i < m; i++)
		{
			for (int j = 0; j < n; j++)
			{
				(*this)[i][j] = (i == j) ? 1 : 0;
			}
		}
	}
}

// Copy Constructor
Matrix::Matrix(const Matrix& a)
{
	M=a.M;
	N=a.N;
	X=new float [M*N];
	memcpy(X,a.X,sizeof(float)*M*N);
}

// Destructor
Matrix::~Matrix()
{ 
	delete [] X; X = 0; 
}

// Matrix Index Operator
// Returns a pointer to the ith row in the matrix
float*	Matrix::operator []	(int i)	const
{ return &X[i*N]; }

// Matrix Addition
Matrix operator + (const Matrix& a, const Matrix& b)
{
	Matrix addAns(a.getm(),a.getn());
	int i=0,j=0;
	if ((a.getn()==b.getn())&&(a.getm()==b.getm()))
	{
		for (i=0; i<a.getm(); i++)
		{
			for (j=0; j<a.getn();j++)
			{
				addAns[i][j]=a[i][j]+b[i][j];
			}
		}
	}
	return addAns;
	//This return calls the copy constructor which copies the matrix into another block of memory
	//and then returns the pointer to this new memory.
	//Otherwise the array addAns is deleted by the destructor here and the pointer returned from the addition
	//is a pointer to deleted memory. This causes problems when the function calling this tries to delete this memory again.	
}

// Matrix Subtraction
Matrix	operator -  (const Matrix& a, const Matrix& b)
{
	Matrix subAns(a.getm(),a.getn());
	int i=0,j=0;
	if ((a.getn()==b.getn())&&(a.getm()==b.getm()))
	{
		for (i=0; i<a.getm(); i++)
		{
			for (j=0; j<a.getn();j++)
			{
				subAns[i][j]=a[i][j]-b[i][j];
			}
		}
	}
	return subAns;
}

//Matrix Multiplication
Matrix	operator * (const Matrix& a, const Matrix& b)
{	
	Matrix multAns(a.getm(),b.getn());
	int i=0,j=0,k=0;
	if (a.getn()==b.getm())
	{
		for (i=0; i<a.getm(); i++)
		{
			for (j=0; j<b.getn();j++)
			{
				float temp=0;				
				for (k=0; k<a.getn(); k++)
				{
                    temp+=a[i][k]*b[k][j];
				}	
				multAns[i][j]=temp;
			}
		}					
	}
	return multAns;
}

// Matrix Multiplication by a Scalar
Matrix	operator * (const float& a, const Matrix& b)
{	
	Matrix multAns(b.getm(),b.getn());
	int i=0,j=0;
	for (i=0; i<b.getm(); i++)
	{
		for (j=0; j<b.getn();j++)
		{				
			multAns[i][j]=b[i][j]*a;
		}
	}	
	return multAns;
}

// Matrix Multiplication by a Scalar
Matrix	operator * (const Matrix& a, const float& b)
{	
	Matrix multAns(a.getm(),a.getn());
	int i=0,j=0;
	for (i=0; i<a.getm(); i++)
	{
		for (j=0; j<a.getn();j++)
		{				
			multAns[i][j]=a[i][j]*b;
		}
	}	
	return multAns;
}

// Matrix Division by a Scalar
Matrix	operator / (const Matrix& a, const float& b)
{	
	Matrix divAns(a.getm(),a.getn());
	int i=0,j=0;
	for (i=0; i<a.getm(); i++)
	{
		for (j=0; j<a.getn();j++)
		{				
			divAns[i][j]=a[i][j]/b;
		}
	}	
	return divAns;
}

// Matrix Equality
Matrix& Matrix::operator =  (const Matrix& a)
{
	if (X!=0)
		delete [] X;
	M=a.M;
	N=a.N;
	X=new float [M*N];
	memcpy(X,a.X,sizeof(float)*M*N);
	return *this;
}

// Matrix Transpose
Matrix	Matrix::transp()
{ 
	Matrix transpAns(getn(),getm());
	int i=0,j=0;
	for (i=0; i<getm(); i++)
	{
		for (j=0; j<getn();j++)
		{				
			transpAns[j][i]=(*this)[i][j];
		}
	}	
	return transpAns; 
}

// 2x2 Matrix Inversion
Matrix Invert22(const Matrix& a)
{
	Matrix invertAns(a.getm(),a.getn());	
	invertAns[0][0]=a[1][1];
	invertAns[0][1]=-a[0][1];
	invertAns[1][0]=-a[1][0];
	invertAns[1][1]=a[0][0];
	float divisor=a[0][0]*a[1][1]-a[0][1]*a[1][0];
	invertAns=invertAns/divisor;
	return invertAns;
}
