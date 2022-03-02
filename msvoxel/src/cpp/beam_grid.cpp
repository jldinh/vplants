
#include "beam_grid.h"


PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE

using namespace std;

#define CODE_VIDE -99999

#define MARQUER(c,a,b) \
  if((pta[b] >= 0) && (pta[b] < int(VMax.getAt(b))))\
  {\
    int xMax,xMin;\
    if(pta[a] <0) { xMin = 0 ; xMax = -1; }\
    else if(pta[a] > int(VMax.getAt(a))-1)\
      { xMin = int(VMax.getAt(a)) ; xMax = int(VMax.getAt(a))-1; }\
    else {xMax = xMin = pta[a];}\
    tabMin[b][pta[b]] = (tabMin[b][pta[b]] == CODE_VIDE) ? \
                      tabMin[b][pta[b]] = xMin : \
                      tabMin[b][pta[b]] = min(xMin, tabMin[b][pta[b]]); \
    tabMax[b][pta[b]] = (tabMax[b][pta[b]] == CODE_VIDE) ? \
                      tabMax[b][pta[b]] = xMax : \
                      tabMax[b][pta[b]] = max(xMax, tabMax[b][pta[b]]); \
  }
#define BRESENHAM2D(c,a,b) \
  memcpy(pta,ptaMemo,12);\
  if((pta[a] == ptb[a]) && (pta[b] == ptb[b]))\
  {\
    MARQUER(c,a,b)\
  }\
  else\
  {\
    while((pta[a] != ptb[a]) || (pta[b] != ptb[b]))\
        {\
          if(H_smart.getAt(c) > 0) \
          {\
                H_smart.getAt(c) -= wid_dir.getAt(b);\
                if(pta[a] != ptb[a]) pta[a] += value[a];\
          }\
          else\
          {\
            if(H_smart.getAt(c) < 0) \
                {\
                  H_smart.getAt(c) += wid_dir.getAt(a);\
                  if(pta[b] != ptb[b]) pta[b] += value[b];\
                }\
                else \
                { \
                  H_smart.getAt(c) = wid_dir.getAt(a) - wid_dir.getAt(b);\
                  if(pta[a] != ptb[a]) pta[a] += value[a];\
                  if(pta[b] != ptb[b]) pta[b] += value[b];\
                }\
          }\
          MARQUER(c,a,b)\
    }\
  }
GeomGrid::GeomGrid(int x, int y, int z) : nx(x), ny(y), nz(z)
{
}
GeomGrid::~GeomGrid()
{
}
/*
int min(char a, char b)
{
  return (a < b) ? a : b;
}
char max(char a, char b)
{
  return (a > b) ? a : b;
}
*/
void AdaptToEpsilon(Vector3& v)
{
  if((v.x() >= - GEOM_EPSILON) && (v.x() <= GEOM_EPSILON)) v.x() = 0;
  if((v.y() >= - GEOM_EPSILON) && (v.y() <= GEOM_EPSILON)) v.y() = 0;
  if((v.z() >= - GEOM_EPSILON) && (v.z() <= GEOM_EPSILON)) v.z() = 0;
}
char sign(real_t& x)
{
        if(x < - GEOM_EPSILON) return -1;
        else
        {
                if(x > GEOM_EPSILON) return 1;
        else {x = 0; return 0;}
        }
}
real_t ceil2(real_t x)
{
        if(ceil(x) == x)
                return (x + 1);
        else return ceil(x);
}

bool GeomGrid::IsInTheGrid(int x,int y, int z)
{
        return ((x >= 0) && (x < nx) && (y >= 0) && (y < ny) && (z >= 0) && (z < nz));
}
int GeomGrid::code(int x,int y, int z)
{
    return int(x + y * nx + z * nx * ny);
}
bool GeomGrid::IsInTheGrid(const Vector3& v)
{
	return ( (floor(v.x()) >= 0) && (floor(v.x()) < nx) && 
           (floor(v.y()) >= 0) && (floor(v.y()) < ny) && 
           (floor(v.z()) >= 0) && (floor(v.z()) < nz)  );
}
int GeomGrid::code(const Vector3& v)
{
    return int(floor(v.x()) + floor(v.y()) * nx + floor(v.z()) * nx * ny);
}

void GeomGrid::intersectTriangle(list<int>& Sres, TOOLS(Vector3) cooVoxel[])
{
   // cout<<"fonction begin : "<<cooVoxel[0]<<", "<<cooVoxel[1]<<", "<<cooVoxel[2]<<endl;
    Vector3 VMax = Vector3(1,1,1) + Max(Max(cooVoxel[0],cooVoxel[1]),cooVoxel[2]);
    if((VMax.x()<=0) || (VMax.y()<=0) || (VMax.z()<=0)) return;
    VMax.set( Min( Vector3(floor(VMax.x()), floor(VMax.y()), floor(VMax.z())),
                   Vector3(real_t(nx),real_t(ny),real_t(nz))                        ));
        int i;

    Vector3 wid_dir3D[3];
        wid_dir3D[0] = cooVoxel[1] - cooVoxel[0]; AdaptToEpsilon(wid_dir3D[0]);
        wid_dir3D[1] = cooVoxel[2] - cooVoxel[1]; AdaptToEpsilon(wid_dir3D[1]);
        wid_dir3D[2] = cooVoxel[0] - cooVoxel[2]; AdaptToEpsilon(wid_dir3D[2]);
    equation EquationPlan;
    EquationPlan.ABC = direction(cross( wid_dir3D[0], -wid_dir3D[2] ));
        EquationPlan.D   = dot(cooVoxel[0] - Vector3(0.5,0.5,0.5), EquationPlan.ABC);
    real_t delta = normL1(EquationPlan.ABC)*0.5;

    int *tabMin[3];
    int *tabMax[3];
    for(i = 0; i < 3; i++)
    {
      int IMax = int(VMax.getAt(i));
      tabMin[i] = new int[ IMax ];
      tabMax[i] = new int[ IMax ];
      for(int j = 0 ; j < IMax ; j++)
        tabMin[i][j] = tabMax[i][j] = CODE_VIDE;
    }
   // cout<<"boucle beg"<<endl;
        for(i = 0 ; i < 3 ; i++)
    {

      register int value[3];
      value[0] = sign(wid_dir3D[i].x()) ;
      value[1] = sign(wid_dir3D[i].y()) ;
      value[2] = sign(wid_dir3D[i].z()) ;
      Vector3 distance(
        (value[0] ==   1 ) ? ( ceil2(cooVoxel[i].x()) - cooVoxel[i].x()) :
      ( (value[0] == - 1 ) ? (cooVoxel[i].x() - floor(cooVoxel[i].x()) ) : 0.5 ) ,
        (value[1] ==   1 ) ? ( ceil2(cooVoxel[i].y()) - cooVoxel[i].y()) :
      ( (value[1] == - 1 ) ? (cooVoxel[i].y() - floor(cooVoxel[i].y()) ) : 0.5 ) ,
        (value[2] ==   1 ) ? ( ceil2(cooVoxel[i].z()) - cooVoxel[i].z()) :
      ( (value[2] == - 1 ) ? (cooVoxel[i].z() - floor(cooVoxel[i].z()) ) : 0.5 )
        );
      register Vector3 wid_dir(abs(wid_dir3D[i]));

      Vector3 H_smart(cross(wid_dir, distance));
      int ptaMemo[3];
      ptaMemo[0] = int(floor(cooVoxel[i].x()));
      ptaMemo[1] = int(floor(cooVoxel[i].y()));
      ptaMemo[2] = int(floor(cooVoxel[i].z()));
      int ptb[3];
      ptb[0] = value[0] ? int(floor(cooVoxel[i].x() + wid_dir3D[i].x())) : ptaMemo[0] ;
      ptb[1] = value[1] ? int(floor(cooVoxel[i].y() + wid_dir3D[i].y())) : ptaMemo[1] ;
      ptb[2] = value[2] ? int(floor(cooVoxel[i].z() + wid_dir3D[i].z())) : ptaMemo[2] ;
     // cout<<"pta:"<<ptaMemo[0]<<" "<<ptaMemo[1]<<" "<<ptaMemo[2]<<endl;
     // cout<<"ptb:"<<ptb[0]<<" "<<ptb[1]<<" "<<ptb[2]<<endl;
      register int pta[3];
     // cout<<"brez1"<<endl;
      BRESENHAM2D(0,1,2)
     // cout<<"brez2"<<endl;
      BRESENHAM2D(1,2,0)
     // cout<<"brez3"<<endl;
      BRESENHAM2D(2,0,1)
     // cout<<"brezout"<<endl;
    }
    //cout<<"final algo"<<endl;
    for(int x = 0 ; x < int(VMax.getAt(0)) ; x++) if(tabMin[0][x] != CODE_VIDE)
    {
      for(int z = tabMin[0][x] ; z <= tabMax[0][x] ; z++) if(tabMin[2][z] != CODE_VIDE)
      {
        for(int y = tabMin[2][z] ; y <= tabMax[2][z] ; y++) if((tabMin[1][y] != CODE_VIDE) && ((tabMin[1][y] <= x) && (x <= tabMax[1][y])))
        {
          if(fabs( x * EquationPlan.ABC.x() +
                   y * EquationPlan.ABC.y() +
                   z * EquationPlan.ABC.z() -
                   EquationPlan.D
                 ) < delta
            )
          {
             Sres.push_back(code(x,y,z));
          }
        }
      }
    }
  //  cout<<"delete"<<endl;
    for(i = 0; i < 3; i++)
    {
      delete tabMin[i], tabMax[i];
      tabMin[i] = tabMax[i] = NULL;
    }
    //cout<<"out fct"<<endl;
}

// *********************************************
/*
void GeomGrid::intersectTriangle(list<int>& Sres, TOOLS(Vector3) cooVoxel[])
{
   int i,j;

   // CooVoxel Sort
   int sort[3][3] ;
   bool maxSort[3][3];
   sort[0][0] = sort[1][0] = sort[2][0] = sort[0][2] = sort[1][2] = sort[2][2] = -1 ;
   for( i = 0 ; i < 3 ; i++) // x,y,z
   {
      for(j = 0 ; j < 3 ; j++) // vertex
      {
        if( (sort[i][0] == -1) || (cooVoxel[j].getAt(i) <  cooVoxel[sort[i][0]].getAt(i)) ) sort[i][0] = j;
        if( (sort[i][2] == -1) || (cooVoxel[j].getAt(i) >= cooVoxel[sort[i][2]].getAt(i)) ) sort[i][2] = j;
      }
   }
   for(i = 0 ; i < 3 ; i++) sort[i][1] = 3 - sort[i][2] - sort[i][0];

   for( i = 0 ; i < 3 ; i++) // x,y,z
   {
      for( j = 0 ; j < 3 ; j++) // vertex
      { 
          if(cooVoxel[j].getAt(i) == cooVoxel[sort[i][2]].getAt(i)) ) 
            maxSort[i][j] = 1 ;
          else
            maxSort[i][j] = 0 ;
      }
   }


   // VMax (top front right point of triangle bounding box) and VMin calculus
   Vector3 VMax = Vector3( cooVoxel[sort[0][2]].x() , 
                           cooVoxel[sort[1][2]].y() , 
                           cooVoxel[sort[2][2]].z() );
   VMax.set( Min( Vector3( floor(VMax.x()), floor(VMax.y()), floor(VMax.z()) ), 
                  Vector3( real_t(nx - 1)   , real_t(ny - 1)   , real_t(nz - 1)    )
           )    );

   Vector3 VMin = Vector3( cooVoxel[sort[0][0]].x() , 
                           cooVoxel[sort[1][0]].y() , 
                           cooVoxel[sort[2][0]].z() );
   VMin.set( Max( Vector3( floor(VMin.x()), floor(VMin.y()), floor(VMin.z()) ), 
                  Vector3( 0              , 0              , 0               )
           )    );
    cout<<"cooVoxel1 : "<<cooVoxel[0]<<", cooVoxel2 : "<<cooVoxel[1]<<", cooVoxel3 : "<<cooVoxel[2]<<endl;
    cout<<"VMax : "<<VMax<<", VMin : "<<VMin<<endl;

    if( (VMax.x() <  0)        || (VMax.y() <  0)        || (VMax.z() <  0) ||
        (VMin.x() >= (real_t)nx) || (VMin.y() >= (real_t)ny) || (VMin.z() >= (real_t)nz) ) return;
    // Equation du plan du triangle
    Vector3 wid_dir3D[3];
    wid_dir3D[0] = cooVoxel[1] - cooVoxel[0];
	  wid_dir3D[1] = cooVoxel[2] - cooVoxel[1];
	  wid_dir3D[2] = cooVoxel[0] - cooVoxel[2];
    equation EquationPlan;
    EquationPlan.ABC = direction(cross( wid_dir3D[0], -wid_dir3D[2] ));
	  EquationPlan.D   = dot(cooVoxel[0] - Vector3(0.5,0.5,0.5), EquationPlan.ABC);
    real_t delta = normL1(EquationPlan.ABC)*0.5;
   
    // Creation de tabMin et tabMax
    int *tabMin[3];
    int *tabMax[3];
    for(i = 0; i < 3; i++) 
    {
      int IMax = int( VMax.getAt(i) + 1 );
      int IMin = int( VMin.getAt(i)     );
      tabMin[i] = new int[ IMax - IMin];
      tabMax[i] = new int[ IMax - IMin];
      for(int j = 0 ; j < IMax - IMin ; j++)
        tabMin[i][j] = tabMax[i][j] = CODE_VIDE;
    }
   

    algoByPlane(2, 0, cooVoxel, tabMin, tabMax, VMin, VMax, maxSort) ; // x,z
    algoByPlane(0, 1, cooVoxel, tabMin, tabMax, VMin, VMax, maxSort) ; // y,x
    algoByPlane(1, 2, cooVoxel, tabMin, tabMax, VMin, VMax, maxSort) ; // z,y
    cout<<"x :\n  tabMin [";
    for(i = 0 ; i <= int(VMax.x()) - int(VMin.x()) ; i++) cout<<" "<<tabMin[0][i];
    cout<<" ]\n  tabMax [";
    for(i = 0 ; i <= int(VMax.x()) - int(VMin.x()) ; i++) cout<<" "<<tabMax[0][i];
    cout<<" ]"<<endl;

    cout<<"y :\n  tabMin [";
    for(i = 0 ; i <= int(VMax.y()) - int(VMin.y()) ; i++) cout<<" "<<tabMin[1][i];
    cout<<" ]\n  tabMax [";
    for(i = 0 ; i <= int(VMax.y()) - int(VMin.y()) ; i++) cout<<" "<<tabMax[1][i];
    cout<<" ]"<<endl;

    cout<<"z :\n  tabMin [";
    for(i = 0 ; i <= int(VMax.z()) - int(VMin.z()) ; i++) cout<<" "<<tabMin[2][i];
    cout<<" ]\n  tabMax [";
    for(i = 0 ; i <= int(VMax.z()) - int(VMin.z()) ; i++) cout<<" "<<tabMax[2][i];
    cout<<" ]"<<endl;


     //cout<<"final algo"<<endl;
    for(int x = int(VMin.x()) ; x < int(VMax.x()) ; x++) if(tabMin[0][x - int(VMin.x())] != CODE_VIDE)
    {
      for(int z = tabMin[0][x - int(VMin.x())] ; z <= tabMax[0][x - int(VMin.x())] ; z++) if(tabMin[2][z - int(VMin.z())] != CODE_VIDE)
      {
        for(int y = tabMin[2][z - int(VMin.z())] ; y <= tabMax[2][z - int(VMin.z())] ; y++) if((tabMin[1][y - int(VMin.y())] != CODE_VIDE) && ((tabMin[1][y - int(VMin.y())] <= x) && (x <= tabMax[1][y - int(VMin.y())])))
        {
          if(fabs( x * EquationPlan.ABC.x() + 
                   y * EquationPlan.ABC.y() + 
                   z * EquationPlan.ABC.z() -
                   EquationPlan.D 
                 ) < delta
            )
          {
             Sres.push_back(code(x,y,z));
          //}
        }
      }
    }
  //  cout<<"delete"<<endl;
    for(i = 0; i < 3; i++) 
    {
      delete tabMin[i], tabMax[i];
      tabMin[i] = tabMax[i] = NULL;
    }
    //cout<<"out fct"<<endl;
}

void GeomGrid::algoByPlane( int a, int b , TOOLS(Vector3) cooVoxel[], int *tabMin[3], int *tabMax[3], const TOOLS(Vector3)& VMin, const TOOLS(Vector3)& VMax, bool maxSort[3][3])
{
   int i;
  
   Vector3 wid_dir3D[3];
   int vertexA = -1 ; //sort[b][2];
   int vertexMax = -1 ;   //sort[a][2]
   bool bStrict = ( cooVoxel[sort[b][2]].getAt(b) != cooVoxel[sort[b][1]].getAt(b) ) ;
   bool aStrict = ( cooVoxel[sort[a][2]].getAt(a) != cooVoxel[sort[a][1]].getAt(a) ) ;

   if( sort[b][2] == sort[a][2] )
   {
     if( bStrict )
       if( aStrict )
         // 1 1
       else
         // 1 0
     else
       if( aStrict )
         // 0 1
       else
         // 0 0
   }
   else
   {
   }
   if(sort[b][2] == sort[a][2]) 
     if(cooVoxel[sort[a][1]].getAt(a) == cooVoxel[sort[a][2]].getAt(a)) vertexMax = sort[a][1] ;
     else if(cooVoxel[vertexA].getAt(b) == cooVoxel[sort[b][1]].getAt(b)) {vertexMax = sort[a][2] ; vertexA = sort[b][2];}
   int vertexMin = 3 - vertexA - vertexMax;
   if( ( cooVoxel[vertexMin].getAt(a) == cooVoxel[vertexMax].getAt(a) ) && ( cooVoxel[vertexMin].getAt(b) < cooVoxel[vertexMax].getAt(b) ) )
   { int k = vertexMin ; vertexMin = vertexMax ; vertexMax = vertexMin; }
   wid_dir3D[0] = cooVoxel[vertexMin] - cooVoxel[vertexA] ;
   wid_dir3D[1] = cooVoxel[vertexMax] - cooVoxel[vertexA] ;
   wid_dir3D[2] = cooVoxel[vertexMin] - cooVoxel[vertexMax] ;
   cout<<"******** a = "<<a<<" b = "<<b<<" *************"<<endl;
   cout<<"Vertex A   = "<<cooVoxel[vertexA]<<"\n"
       <<"Vertex Min = "<<cooVoxel[vertexMin]<<"\n"
       <<"Vertex Max = "<<cooVoxel[vertexMax]<<endl;
   cout<<"WID_dir : \n\t"<<wid_dir3D[0]<<"\n\t"<<wid_dir3D[1]<<"\n\t"<<wid_dir3D[2]<<endl;
   // x = coefWd_a * y + coefWd_b

   
   
   
    
   if( cooVoxel[vertexMin].getAt(b) < cooVoxel[vertexMax].getAt(b) )
   {
      cout<<"MODE 1"<<endl;
      marquer( tabMin, VMin, VMax, a, b, cooVoxel[vertexA], wid_dir3D[0] );
      cout<<"Max:"<<endl;
      marquer( tabMax, VMin, VMax, a, b, cooVoxel[vertexA], wid_dir3D[1] );
      marquer( tabMax, VMin, VMax, a, b, cooVoxel[vertexMax], wid_dir3D[2] );

   }
   else
   { 
      cout<<"MODE 2"<<endl;
      marquer( tabMin, VMin, VMax, a, b, cooVoxel[vertexA], wid_dir3D[0] );
      marquer( tabMin, VMin, VMax, a, b, cooVoxel[vertexMin], -wid_dir3D[2] );
      cout<<"Max:"<<endl;
      marquer( tabMax, VMin, VMax, a, b, cooVoxel[vertexA], wid_dir3D[1] ); 
     
   }

   int vTmp = int(floor(cooVoxel[vertexMin].getAt(b)));
   if((VMin.getAt(b) <= vTmp) && (VMax.getAt(b) >= vTmp))
       tabMin[b][ vTmp ] = int( max( (real_t)floor(cooVoxel[vertexMin].getAt(a)), VMin.getAt(a) ) );

   vTmp = int(floor(cooVoxel[vertexMax].getAt(b)));
   if((VMin.getAt(b) <= vTmp) && (VMax.getAt(b) >= vTmp))
       tabMax[b][ vTmp ] = int( min( (real_t)floor(cooVoxel[vertexMax].getAt(a)), VMax.getAt(a) ) );
}
 
void GeomGrid::marquer( int *tab[], const Vector3& VMin, const Vector3& VMax, const int a, const int b, Vector3 vertexA , Vector3 wid_dir3D )
{
   if(wid_dir3D.getAt(b) == 0) return;
   real_t coefA = wid_dir3D.getAt(a) /  wid_dir3D.getAt(b) ;
   real_t coefB = vertexA.getAt(a) - vertexA.getAt(b) * coefA ;
   real_t x; 
   int y    = int( min( vertexA.getAt(b), VMax.getAt(b) ) );
   int yEnd = int( max( vertexA.getAt(b) + wid_dir3D.getAt(b), VMin.getAt(b) ) );
   x = coefA * y + coefB ;
   cout<<"y :"<<y<<" yEnd :"<<yEnd<<endl;

   for( int i = (y - int(VMin.getAt(b))) ; i > (yEnd - int(VMin.getAt(b))) ; i--)
   {
     cout<<"tab["<<b<<"]["<<i<<"] = "<<int(floor(x))<<endl;
     tab[b][i] = int(floor(x));
     x-=coefA;
   }
   
}
*/
