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


/*! \file appe_spectrum.h
    \brief Definition of the appearance class Spectrum.
*/

#ifndef __appe_spectrum_h__
#define __appe_spectrum_h__


#include "appearance.h"


/* ----------------------------------------------------------------------- */

PGL_BEGIN_NAMESPACE

/* ----------------------------------------------------------------------- */

/** 
    \class Spectrum
    \brief Abstract base class for all spectrum objects.
*/



class SG_API Spectrum : public Appearance
{

public:

  /// A structure which helps to build a Spectrum when parsing. 
  struct SG_API Builder : public Appearance::Builder {

    /// A constructor. It inits all the pointers to null.
    Builder( );

    /// A destructor.
    virtual ~Builder( );

  };


  /// Default constructor.
  Spectrum( );

  /// Destructor
  virtual ~Spectrum( ) ;

}; // class Spectrum

/// Spectrum Pointer
typedef RCPtr<Spectrum> SpectrumPtr;


/* ------------------------------------------------------------------------- */

// __appe_spectrum_h__
/* ----------------------------------------------------------------------- */

PGL_END_NAMESPACE

/* ----------------------------------------------------------------------- */
#endif

