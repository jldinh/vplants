/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: The Plant Graphic Library
 *
 *       Copyright 1995-2007 UMR CIRAD/INRIA/INRA DAP 
 *
 *       File author(s): F. Boudon et al.
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



/*! \file geom_lineicmodel.h
    \brief Definition of the geometry class LineicModel.
*/

#ifndef __geom_lineicmodel_h__
#define __geom_lineicmodel_h__

/* ----------------------------------------------------------------------- */

#include "primitive.h"
#include <plantgl/math/util_vector.h>

/* ----------------------------------------------------------------------- */

PGL_BEGIN_NAMESPACE

class QuantisedFunction;
typedef RCPtr<QuantisedFunction> QuantisedFunctionPtr;

/* ----------------------------------------------------------------------- */

/**
   \class LineicModel
   \brief Abstract Base Classe for all Lineic Model.
*/

/* ----------------------------------------------------------------------- */


class SG_API LineicModel :  public virtual Primitive {

public:

  static const uchar_t DEFAULT_WIDTH;

  /// constructor
  LineicModel(uchar_t width = DEFAULT_WIDTH);

  /// Destructor
  virtual ~LineicModel();

  virtual bool isACurve( ) const ;
  
  virtual bool isASurface( ) const ;
  
  virtual bool isAVolume( ) const ;
  
  /// Returns the \e fist knots value.
  virtual const real_t getFirstKnot() const = 0;
  
  /// Returns the \e last  knots value.
  virtual const real_t getLastKnot() const = 0;
  
  /// Returns \e Stride value.
  virtual const uint_t getStride( ) const = 0;
  
  
  /*! Returns the \e Point for u = \e u.
    \pre 
    - \e u must be in [FirstKnot,LastKnot];*/
  virtual TOOLS(Vector3) getPointAt(real_t u) const = 0;
  
  /*! Returns the \e Tangent for u = \e u.
    \pre 
    - \e u must be in [FirstKnot,LastKnot];*/
  virtual TOOLS(Vector3) getTangentAt(real_t u) const = 0;
  
  
  /*! Returns the principal \e Normal for u = \e u.
    \pre 
    - \e u must be in [FirstKnot,LastKnot];*/
    virtual TOOLS(Vector3) getNormalAt(real_t u) const = 0;
  
  /// Return the length of the lineic model.
  inline real_t getLength() const { return getLength(getFirstKnot(),getLastKnot()); }

  /// Return the length of the lineic model starting from u = begin.
  inline real_t getLength(real_t begin) const { return getLength(begin,getLastKnot()); }

  /// Return the length of the lineic model from u = begin to u = end.
  virtual real_t getLength(real_t begin, real_t end) const ;

  virtual TOOLS(Vector3) findClosest(const TOOLS(Vector3)& pt, real_t* u = NULL) const;
  
  QuantisedFunctionPtr getArcLengthToUMapping() const;
  QuantisedFunctionPtr getUToArcLengthMapping() const;

  // Get the width value of the curve
  inline const uchar_t getWidth() const { return __width; }
  inline uchar_t& getWidth() { return __width; }
  inline bool isWidthToDefault( ) const { return __width == DEFAULT_WIDTH; }


protected:
  uchar_t __width;

};

/* ----------------------------------------------------------------------- */

/// LineicModel Pointer
typedef RCPtr<LineicModel> LineicModelPtr;
 
/* ----------------------------------------------------------------------- */

SG_API real_t closestPointToSegment(TOOLS(Vector3)& p, 
						   const TOOLS(Vector3)& segA,
						   const TOOLS(Vector3)& segB,
                           real_t* u = NULL);

/* ----------------------------------------------------------------------- */

PGL_END_NAMESPACE

/* ----------------------------------------------------------------------- */
#endif

