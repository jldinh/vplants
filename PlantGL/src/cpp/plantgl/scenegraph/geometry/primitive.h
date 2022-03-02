/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture 
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): C. Nouguier & F. Boudon (frederic.boudon@cirad.fr) nouguier 
 *
 *       $Source$
 *       $Id: primitive.h 2562 2007-01-30 14:37:43Z boudon $
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


/*! \file geom_primitive.h
    \brief Definition of the geometry class Primitive.
*/


#ifndef __geom_primitive_h__
#define __geom_primitive_h__

/* ----------------------------------------------------------------------- */

#include "geometry.h"

/* ----------------------------------------------------------------------- */

PGL_BEGIN_NAMESPACE

/* ----------------------------------------------------------------------- */

/** 
    \class Primitive
    \brief Abstract base class for all predefined primitives. 
*/

/* ----------------------------------------------------------------------- */

class SG_API Primitive : public virtual Geometry
{
 
public:

  /// A structure which helps to build a Primitive when parsing. 
  struct SG_API Builder : public Geometry::Builder {
    
    /// Constructor.
    Builder( );

    /// Destructor.
    virtual ~Builder( );

  };


  /// Default constructor.
  Primitive( );

  /// Destructor.
  virtual ~Primitive( );

};

/// Primitive Pointer
typedef RCPtr<Primitive> PrimitivePtr;


/* ----------------------------------------------------------------------- */

// __geom_primitive_h__
/* ----------------------------------------------------------------------- */

PGL_END_NAMESPACE

/* ----------------------------------------------------------------------- */
#endif

