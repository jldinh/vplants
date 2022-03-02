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
 *       $Id: geom.h 3258 2007-06-06 13:18:26Z dufourko $
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




#ifndef GEOM_HEADER
#define GEOM_HEADER


#ifdef __cplusplus
extern "C" {
#endif

  typedef struct {
    float x;
    float y;
    float z;
  } Vect;


  typedef struct {
    Vect vx;
    Vect vy;
    Vect vz;
    Vect tr;
  } Matr;


  typedef struct {
    int symb;
    int detail;
    int bouf1;
    int bouf2;
    float mat[3][4];
    float diamb;
    float diamh;
    int bouf3;
  } LtreeRecord;

  void vecsomme( float c1, float c2, Vect *v1, Vect *v2, Vect *v3);
  void vecsomm3( float c1, float c2, float c3, Vect *v1, Vect *v2, Vect *v3);
  void vecaffecte( Vect *v1, Vect *v2);
  void vecmultiplie( float coef, Vect *v1, Vect *v2);
  void norme( Vect *vin , Vect *vout);
  void mtnorm( float  vin[4], float  vout[4]);
  void vnorm( float  vin[3], float  vout[3]);
  float fnorm ( Vect  *vin, Vect  *vout);
  void vectoriel( float vin1[3], float vin2[3], float prdv[3]);
  void rotation_axe( float axe[3], float vin[3], float ang, float vout[3]);
  void affect( float mat1[4][4], float mat2[4][4]);
  void multmat ( float mat1[4][4], float mat2[4][4], float mat3[4][4]);
  void mulvec( float v1[4], float mat[4][4], float v2[4]);
  int write_info (char *ligne, float age, int nbb, int graine, int simplification, float *max, float *min);

#ifdef __cplusplus
}
#endif



#endif

