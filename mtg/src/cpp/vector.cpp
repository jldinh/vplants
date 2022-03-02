/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): Ch. Godin (christophe.godin@cirad.fr)
 *
 *       $Source$
 *       $Id: vector.cpp 17611 2014-10-17 13:20:41Z pradal $
 *
 *       Forum for AMAPmod developers    : amldevlp@cirad.fr
 *
 *  ----------------------------------------------------------------------------
 *
 *                      GNU General Public Licence
 *
 *       This program is free software; you can redistribute it and/or
 *       modify it under the terms of the GNU General Public License as
 *       published by the Free Software Foundation; either version 2 of
 *       the License, or (at your option) any later version.
 *
 *       This program is distributed in the hope that it will be useful,
 *       but WITHOUT ANY WARRANTY; without even the implied warranty of
 *       MERCHANTABILITY or FITNESS For A PARTICULAR PURPOSE. See the
 *       GNU General Public License for more details.
 *
 *       You should have received a copy of the GNU General Public
 *       License along with this program; see the file COPYING. If not,
 *       write to the Free Software Foundation, Inc., 59
 *       Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 *  ----------------------------------------------------------------------------
 */





#include "vector.h"
#include "tool/util_math.h"

using namespace std;

MyVector::MyVector(const ValType xx,
               const ValType yy,
               const ValType zz )
{
  _x=xx;
  _y=yy;
  _z=zz;
}

MyVector::MyVector(const MyVector& v )
{
  _x=v[0];
  _y=v[1];
  _z=v[2];
}

MyVector::MyVector(const ValType alpha,
               const ValType beta)
{
  ValType al=alpha;
  ValType be=beta;

  _x=MyCos(be)*MyCos(al);
  _y=MySin(be)*MyCos(al);
  _z=MySin(al);

  Test();
}

void MyVector::trafic(ValType alpha)
{
  ValType zz=_z*MySin(alpha);
  ValType xx=_x*MyCos(alpha);

  _x=xx;_z=zz;

  Test();
}

void MyVector::Test()
{
  if (MyAbs(_x)<pow((double)10,(double)-4))
  {
    _x=0;
  }
  if (MyAbs(_y)<pow((double)10,(double)-4))
  {
    _y=0;
  }
  if (MyAbs(_z)<pow((double)10,(double)-4))
  {
    _z=0;
  }
}


MyVector::MyVector()
{
  _x=_y=_z=0;
}

const MyVector& MyVector::operator=(const MyVector& v)
{
  if (this!=&v)
  {
    _x=v[0];
    _y=v[1];
    _z=v[2];
  }

  return *this;
}

AmlBoolean MyVector::operator==(const MyVector& v) const
{
  AmlBoolean result=FALSE;

  if ((_x==v[0]) && (_y==v[1]) && (_z==v[2]))
  {
    result=TRUE;
  }

  return result;
}

MyVector MyVector::operator+(const MyVector& v) const
{
  ValType xx,yy,zz;

  xx=_x+v[0];
  yy=_y+v[1];
  zz=_z+v[2];

  MyVector result(xx,yy,zz);

  return result;
}

MyVector MyVector::operator-(const MyVector& v) const
{
  ValType xx,yy,zz;

  xx=_x-v[0];
  yy=_y-v[1];
  zz=_z-v[2];

  MyVector result(xx,yy,zz);

  return result;
}

MyVector MyVector::operator*(const MyVector& v) const
{
  ValType xx,yy,zz;
  float v1[3];
  float v2[3];

  v1[0]=_x;v1[1]=_y;v1[2]=_z;
  v2[0]=v[0];v2[1]=v[1];v2[2]=v[2];

  xx =v1[1] * v2[2] - v1[2] * v2[1];
  yy =v1[2] * v2[0] - v1[0] * v2[2];
  zz =v1[0] * v2[1] - v1[1] * v2[0];

  MyVector result(xx,yy,zz);

  return result;

}

ValType MyVector::operator^(const MyVector& v) const
{
  ValType result;

  result=_x*v[0]+_y*v[1]+_z*v[2];

  return result;
}


const ValType& MyVector::operator[](const IntType index ) const
{
  switch (index)
  {
  case 0:
    {
      return _x;
      break;
    }
  case 1:
    {
      return _y;
      break;
    }
  case 2:
    {
      return _z;
      break;
    }
  }
}

ValType& MyVector::operator[](const IntType index )
{
  switch (index)
  {
  case 0:
    {
      return _x;
      break;
    }
  case 1:
    {
      return _y;
      break;
    }
  case 2:
    {
      return _z;
      break;
    }
  }
}

void MyVector::multiply(const ValType n)
{
  _x*=n;
  _y*=n;
  _z*=n;
}

/* MyVector& MyVector::rotateX( ValType alpha )
{

} */

const MyVector& MyVector::rotateY( const ValType alpha )
{
  ValType xx,yy,zz;

  xx=_x*MyCos(alpha)+_z*MySin(alpha);
  zz=-MySin(alpha)*_x+MyCos(alpha)*_z;
  yy=_y;

  // MyVector result( xx,yy,zz );

  _x=xx;
  _y=yy;
  _z=zz;

  Test();

  return *this;
}


const MyVector& MyVector::rotateZ( const ValType alpha )
{
  ValType xx,yy,zz;

  xx=_x*MyCos(alpha)-_y*MySin(alpha);
  yy=_x*MySin(alpha)+_y*MyCos(alpha);
  zz=_z;

  _x=xx;
  _y=yy;
  _z=zz;

  Test();

  return *this;
}


ValType MyVector::computeAlpha() const
{

  ValType l=computeLength();
  ValType sinA=(l > 0 ?_z/l: 0);
  ValType result;

  if (sinA!=0)
  {
    if (sinA>1)
    {
      cout << "SinA : " << sinA << endl;
      sinA=1;
    }
    if (sinA<-1)
    {
      cout << "SinA : " << sinA << endl;
      sinA=-1;
    }

    result=MyAsin(sinA);
  }
  else
  {
    result=0;
  }

  if ((MyAbs(result)<pow((double)10,(double)-4)))
  {
    result=0;
  }

  return result;
}

ValType MyVector::computeBeta() const
{
  ValType l=computeLength();
  ValType xx= (l>0 ?_x/l:0);
  ValType result;

  ValType alpha=computeAlpha();
  ValType cosA=MyCos(alpha);

  if (cosA!=0)
  {
    ValType cosB=xx/cosA;

    if (cosB>1)
    {

      cosB=1;
    }

    if (cosB<-1)
    {

      cosB=-1;
    }

    result=MyAcos(cosB);

    if (_y<0)
    {
      result=2*M_PI-result;;
    }

    if (_y==0)
    {
      // 2 cas se presentent:

      // Cas 1: _x>=0

      if (_x>=0)
      {
        result=0;
      }
      else // Cas 2 : _x<0
      {
        result=M_PI;
      }
    }
  }
  else
  {
    // Cas ou cos(alpha)==0 ==> alpha=-+Pi/2 donc Beta=0
    result=0;
  }


  if ((MyAbs(result)<pow((double)10,(double)-4)))
  {
    result=0;
  }

  return result;

}

ValType MyVector::computeLength() const
{
  ValType result=sqrt(_x*_x+_y*_y+_z*_z);

  return result;
}

void  MyVector::norm()
{
  ValType l=computeLength();

  if (l!=0)
  {
    _x=_x/l;
    _y=_y/l;
    _z=_z/l;
  }

}

// On part d'un vecteur V exprime dans une base B' donnee.
// cette base B' est elle meme definie par les vecteurs (u,v,w)dans une base initiale B.
// Soit P la matrice dont les colonnes sont constituees des vecteurs colonne
// u, v et w, exprimes dans B alors
// les coordonnees de V exprimees dans la base initiale sont :
// V/B = P V/B'
//
//

void MyVector::changeRepere(const MyVector& u, const MyVector& v,const MyVector& w)
{
  ValType X=_x;
  ValType Y=_y;
  ValType Z=_z;

  _x=X*u[0]+Y*v[0]+Z*w[0];
  _y=X*u[1]+Y*v[1]+Z*w[1];
  _z=X*u[2]+Y*v[2]+Z*w[2];

}


void MyVector::report()
{
  cout << "( " << _x << " , " << _y << " , " << _z << " )" << " Alpha : " << computeAlpha()*180/M_PI << "  Beta : " <<  computeBeta()*180/M_PI << " Longueur : " << computeLength() << endl;
}


