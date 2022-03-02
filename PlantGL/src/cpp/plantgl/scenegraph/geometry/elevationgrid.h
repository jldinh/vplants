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

/*! \file geom_elevationgrid.h
    \brief Definition of the geometry class ElevationGrid.
*/


#ifndef __geom_elevationgrid_h__
#define __geom_elevationgrid_h__

/* ----------------------------------------------------------------------- */

#include "patch.h"
#include <plantgl/math/util_vector.h>

/* ----------------------------------------------------------------------- */

TOOLS_BEGIN_NAMESPACE
class RealArray2;
typedef RCPtr<RealArray2> RealArray2Ptr;
TOOLS_END_NAMESPACE

/* ----------------------------------------------------------------------- */

PGL_BEGIN_NAMESPACE

/* ----------------------------------------------------------------------- */

/**
   \class ElevationGrid
   \brief A mesh represented by an array of points.
*/


class SG_API ElevationGrid : public Patch
{

public:

  /// The default XSpacing field value.
  static const real_t DEFAULT_X_SPACING;

  /// The default YSpacing field value.
  static const real_t DEFAULT_Y_SPACING;


  /// A structure which helps to build a ElevationGrid when parsing. 
  struct SG_API Builder : public Patch::Builder {


    /// A pointer to the HeightList field.
    TOOLS(RealArray2Ptr) * HeightList;

    /// A pointer to the XSpacing field.
    real_t * XSpacing;

    /// A pointer to the YSpacing field.
    real_t * YSpacing;

    /// Constructor.
    Builder( );

    /// Detructor.
    virtual ~Builder( );

    virtual SceneObjectPtr build( ) const;

    virtual void destroy( );

    virtual bool isValid( ) const;

  };

  /// Default Constructor. Build object is invalid.
  ElevationGrid();

  /// Complete constructor.
  ElevationGrid( const TOOLS(RealArray2Ptr)& heights,
		 real_t xSpacing = DEFAULT_X_SPACING,
		 real_t ySpacing = DEFAULT_Y_SPACING,
		 bool ccw = DEFAULT_CCW);
  
  /// Destructor
  virtual ~ElevationGrid( );

  PGL_OBJECT(ElevationGrid)

  /** Returns the value of \b HeightList at the i-th row and the j-th column.
      \warning
      - \e i must belong to the range [0,XDim[;
      - \e j must belong to the range [0,YDim[. */
  const real_t& getHeightAt( const uint_t i, const uint_t j ) const;

  /** Returns the field of \b HeightList at the i-th row and the j-th column.
      \warning
      - \e i must belong to the range [0,XDim[;
      - \e j must belong to the range [0,YDim[. */
  real_t& getHeightAt( const uint_t i, const uint_t j );

  /// Returns \b HeightList values.
  const TOOLS(RealArray2Ptr)& getHeightList( ) const;

  /// Returns \b HeightList field.
  TOOLS(RealArray2Ptr)& getHeightList( );

  /// Returns \e CrtlPoints value.
  virtual Point4MatrixPtr getCtrlPoints( ) const;


  /// Returns \b XDim value.
  const uint_t getXDim( ) const;

  /// Returns the extent of \e self along the \c x-axis.
  const real_t getXSize( ) const;
  
  /// Returns \b XSpacing value.
  const real_t& getXSpacing( ) const;

  /// Returns \b XSpacing field.
  real_t& getXSpacing( ) ;

  /// Returns \b YDim value.
  const uint_t getYDim( ) const;

  /// Returns the extent of \e self along the \c y-axis.
  const real_t getYSize( ) const;

  /// Returns YSpacing value.
  const real_t& getYSpacing( ) const;

  /// Returns YSpacing field.
  real_t& getYSpacing( );

  /// Returns the (i,j)th point of the grid
  TOOLS(Vector3) getPointAt(uint_t i, uint_t j) const;

  ///  Returns the field of \b HeightList at the position pos. If pos is outside grid, return 0
  real_t getHeightAt(const TOOLS(Vector2) pos) const;

  /// Returns whether \b XSpacing is set to its default value.
  bool isXSpacingToDefault( ) const;

  /// Returns whether \b YSpacing is set to its default value.
  bool isYSpacingToDefault( ) const;

  virtual bool isValid( ) const;

protected:

  /// The HeightList field.
  TOOLS(RealArray2Ptr) __heightList;

  /// The XSpacing field.
  real_t __xSpacing; 

  /// The YSpacing field.
  real_t __ySpacing; 
   
}; // ElevationGrid

/// ElevationGrid Pointer
typedef RCPtr<ElevationGrid> ElevationGridPtr;


/* ----------------------------------------------------------------------- */

// __geom_elevationgrid_h__
/* ----------------------------------------------------------------------- */

PGL_END_NAMESPACE

/* ----------------------------------------------------------------------- */
#endif

