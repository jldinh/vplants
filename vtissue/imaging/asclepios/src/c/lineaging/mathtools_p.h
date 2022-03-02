#ifndef __MATHTOOLS_P_H__
#define __MATHTOOLS_P_H__

#include <vector>
#include <cmath>
#include <algorithm>


inline float norm(float x1,float y1, float z1,float x2,float y2, float z2){
  return std::sqrt( (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2) + (z1-z2)*(z1-z2) );
}

inline int max(int a,int b,int c){
  return std::max(a,std::max(b,c));
}

inline int sign(int a){return a<0 ? -1 : 1;}

inline void bresenham_line3d(std::vector < int> * init,std::vector < int> * fin,std::vector < std::vector < int > > * tabCoords){
  int nbPoints = max(abs((*fin)[0]-(*init)[0])+1,
		     abs((*fin)[1]-(*init)[1])+1,
		     abs((*fin)[2]-(*init)[2])+1);

  int X[nbPoints];
  int Y[nbPoints];
  int Z[nbPoints];
  int x1 = (*init)[0],y1 = (*init)[1],z1 = (*init)[2];
  int x2 = (*fin)[0],y2 = (*fin)[1],z2 = (*fin)[2];
  int dx = x2 - x1,dy = y2 - y1,dz = z2 - z1;
  int ax = abs(dx)*2,ay = abs(dy)*2,az = abs(dz)*2;
  int sx = sign(dx),sy = sign(dy),sz = sign(dz);
  int x = x1,y = y1,z = z1,idx = 0,xd,yd,zd;
  bool dedans=true;

  if(ax>=std::max(ay,az)){
    yd = ay - ax/2;
    zd = az - ax/2;
    while(dedans){
      X[idx] = x;
      Y[idx] = y;
      Z[idx] = z;
      idx = idx + 1;
      if(x == x2) dedans=false;
      if(dedans){
	if(yd >= 0){
	  y = y + sy;
	  yd = yd - ax;
	}
	if(zd >= 0){
	  z = z + sz;
	  zd = zd - ax;
	}
	x  = x  + sx;
	yd = yd + ay;
	zd = zd + az;
      }
    }
  }
  else if(ay >= std::max(ax,az)){
    xd = ax - ay/2;
    zd = az - ay/2;

    while(dedans){
      X[idx] = x;
      Y[idx] = y;
      Z[idx] = z;
      idx = idx + 1;
      if(y == y2)dedans=false;
      if(dedans){
	if(xd >= 0){
	  x = x + sx;
	  xd = xd - ay;
	}
	if(zd >= 0){
	  z = z + sz;
	  zd = zd - ay;
	}
	y  = y  + sy;
	xd = xd + ax;
	zd = zd + az;
      }
    }
  }
  else if(az >= std::max(ax,ay)){
    xd = ax - az/2;
    yd = ay - az/2;

    while(dedans){
      X[idx] = x;
      Y[idx] = y;
      Z[idx] = z;
      idx = idx + 1;
      if(z == z2)dedans=false;
      if(dedans){
	if(xd >= 0){
	  x = x + sx;
	  xd = xd - az;
	}
	if(yd >= 0){
	  y = y + sy;
	  yd = yd - az;
	}
	z  = z  + sz;
	xd = xd + ax;
	yd = yd + ay;
      }
    }
  }
  for(int i =0 ; i <nbPoints ; i++){
    (*tabCoords)[i][0]=X[i];
    (*tabCoords)[i][1]=Y[i];
    (*tabCoords)[i][2]=Z[i];
    (*tabCoords)[i][3]=nbPoints;
  }
}


#endif//__MATHTOOLS_P_H__
