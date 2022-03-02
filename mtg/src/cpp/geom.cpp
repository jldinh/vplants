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
 *       $Id: geom.cpp 3258 2007-06-06 13:18:26Z dufourko $
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




#include <stdio.h>
#include <math.h>

#include "geom.h"

static const char rcsid[] = "$Id: geom.cpp 3258 2007-06-06 13:18:26Z dufourko $";

void vecsomme( float c1, float c2, Vect *v1, Vect *v2, Vect *v3)
{
v3->x = c1 * v1->x + c2 * v2->x;
v3->y = c1 * v1->y + c2 * v2->y;
v3->z = c1 * v1->z + c2 * v2->z;
}





void vecsomm3( float c1, float c2, float c3, Vect *v1, Vect *v2, Vect *v3)
{
v3->x = c1 * v1->x + c2 * v2->x + c3 * v3->x;
v3->y = c1 * v1->y + c2 * v2->y + c3 * v3->y;
v3->z = c1 * v1->z + c2 * v2->z + c3 * v3->z;
}





void vecaffecte( Vect *v1, Vect *v2)
{
v2->x = v1->x;
v2->y = v1->y;
v2->z = v1->z;
}




void vecmultiplie( float coef, Vect *v1, Vect *v2)
{
v2->x = coef * v1->x;
v2->y = coef * v1->y;
v2->z = coef * v1->z;
}





void norme( Vect *vin , Vect *vout)
{
float  norm;
Vect   vaux;

norm = sqrt(vin->x * vin->x + vin->y * vin->y + vin->z * vin->z);
if (norm < 0.000001)
   {
   vout->x = 0.0;
   vout->y = 0.0;
   vout->z = 0.0;
   }
  else
   {
   vaux.x = vin->x/norm;
   vaux.y = vin->y/norm;
   vaux.z = vin->z/norm;
   vout->x = vaux.x;
   vout->y = vaux.y;
   vout->z = vaux.z;
   }
}

void mtnorm( float  vin[4], float  vout[4])
{
float  norm;
float  vaux[4];

norm = sqrt(vin[0]*vin[0] + vin[1]*vin[1] + vin[2]*vin[2] + vin[3]*vin[3]);
if (norm < 0.000001)
   {
   vout[0] = 0.0;
   vout[1] = 0.0;
   vout[2] = 0.0;
   vout[3] = 0.0;
   }
  else
   {
   vaux[0] = vin[0]/norm;
   vaux[1] = vin[1]/norm;
   vaux[2] = vin[2]/norm;
   vaux[3] = vin[3]/norm;
   vout[0] = vaux[0];
   vout[1] = vaux[1];
   vout[2] = vaux[2];
   vout[3] = vaux[3];
   }
}

void vnorm( float  vin[3], float  vout[3])
{
float  norm;
float  vaux[3];

norm = sqrt(vin[0] * vin[0] + vin[1] * vin[1] + vin[2] * vin[2]);
if (norm < 0.000001)
   {
   vout[0] = 0.0;
   vout[1] = 0.0;
   vout[2] = 0.0;
   }
  else
   {
   vaux[0] = vin[0]/norm;
   vaux[1] = vin[1]/norm;
   vaux[2] = vin[2]/norm;
   vout[0] = vaux[0];
   vout[1] = vaux[1];
   vout[2] = vaux[2];
   }
}





float fnorm ( Vect  *vin, Vect  *vout)
{
float norm;
Vect  vaux;

norm = sqrt(vin->x * vin->x + vin->y * vin->y + vin->z * vin->z);
if (norm < 0.0000001)
   {
   vout->x = 0.0;
   vout->y = 0.0;
   vout->z = 0.0;
   norm = 0.0;
   }
  else
   {
   vaux.x = vin->x/norm;
   vaux.y = vin->y/norm;
   vaux.z = vin->z/norm;
   vout->x = vaux.x;
   vout->y = vaux.y;
   vout->z = vaux.z;
   }
return (norm);
}



void  vectoriel( float vin1[3], float vin2[3], float prdv[3])
{
prdv[0] =vin1[1] * vin2[2] - vin1[2] * vin2[1];
prdv[1] =vin1[2] * vin2[0] - vin1[0] * vin2[2];
prdv[2] =vin1[0] * vin2[1] - vin1[1] * vin2[0];
}



void rotation_axe( float axe[3], float vin[3], float ang, float vout[3])
{
float vaux[3],cosa,cosf,sina,ax0,ax1,ax2;
float ax00,ax01,ax02,ax11,ax12,ax22;

cosa = cos(ang);
cosf = 1. - cosa;
sina = sin(ang);

ax00 = axe[0] * axe[0] * cosf;
ax01 = axe[0] * axe[1] * cosf;
ax02 = axe[0] * axe[2] * cosf;
ax11 = axe[1] * axe[1] * cosf;
ax12 = axe[1] * axe[2] * cosf;
ax22 = axe[2] * axe[2] * cosf;
ax0  = axe[0] * sina;
ax1  = axe[1] * sina;
ax2  = axe[2] * sina;

vaux[0]=(ax00+cosa)*vin[0]+(ax01-ax2)*vin[1]+(ax02+ax1)*vin[2];
vaux[1]=(ax01+ax2)*vin[0]+(ax11+cosa)*vin[1]+(ax12-ax0)*vin[2];
vaux[2]=(ax02-ax1)*vin[0]+(ax12+ax0)*vin[1]+(ax22+cosa)*vin[2];

*vout++ = vaux[0];
*vout++ = vaux[1];
*vout   = vaux[2];
}



void  affect( float mat1[4][4], float mat2[4][4])
{
int i, j;

for(i=0; i<4; i++)
	for(j=0; j<4; j++)
		mat1[i][j] = mat2[i][j];

}

void  multmat ( float mat1[4][4], float mat2[4][4], float mat3[4][4])
{
float res[4][4];
int i, j, k;

for(i=0; i<4; i++)
	for(j=0; j<4; j++)
		res[i][j] = 0.0;

for (i=0; i<4; i++)
	for(j=0; j<4; j++)
		for(k=0; k<4; k++)
			res[i][j] += mat1[i][k] * mat2[k][j];
affect(mat3,res);
}

void mulvec( float v1[4], float mat[4][4], float v2[4])
{
int i,j;

for (i=0; i<4; i++)
   {
   v2[i] = 0;
   for (j=0; j<4; j++)
      v2[i] += v1[j] * mat[j][i];
   }
}

