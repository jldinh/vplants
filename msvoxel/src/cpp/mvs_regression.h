/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): O. Puech (puech.olivier@orange.fr)
 *
 *       $Source$
 *       $Id: mvs_regression.h 3268 2007-06-06 16:44:27Z dufourko $
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

#ifndef __reg_h__
#define __reg_h__

#include "plantgl/pgl_namespace.h"
#include "tool/rcobject.h"
#include "plantgl/scenegraph/container/indexarray.h"
#include <math.h>

PGL_BEGIN_NAMESPACE
/* ----------------------------------------------------------------------- */

/**
    regression
*/

/* ----------------------------------------------------------------------- */
;

class MsvRegression
{
  private :
    int nb_vector, nb_variable ;
    double *mean;
    int **vector;
    double **covariance;
    double *point;
    double *residual;
    double max_value, min_value;
    double a,b,r2;

  protected :
    void mean_computation(int variable);
    void covariance_computation();
    void computation();
    void residual_computation();
    double residual_mean_computation() const;
    void variance_computation(int variable);
    double residual_square_sum_computation() const;
    void parameters_computation();
    double getVector(int i, int j){return log( (double) vector[j][i]);};

  public:
    MsvRegression(int inb_vector, int **ivector);
    ~MsvRegression();

    double& getA() { return a;  };
    double& getB() { return b;  };
    double& getR2(){ return r2; };
};

PGL_END_NAMESPACE

/* ----------------------------------------------------------------------- */
#endif

