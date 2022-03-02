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



#include "multispectral.h"
#include <plantgl/scenegraph/core/pgl_messages.h>
#include <plantgl/tool/util_string.h>
#include <plantgl/tool/util_array.h>

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace std;

/* ----------------------------------------------------------------------- */


const Index3 MultiSpectral::DEFAULT_RGB_INDEX(1,1,1);


/* ----------------------------------------------------------------------- */


MultiSpectral::Builder::Builder( ) :
  Spectrum::Builder(),
  Reflectance(0),
  Transmittance(0),
  Filter(0) {
}


MultiSpectral::Builder::~Builder( ) {
}


SceneObjectPtr MultiSpectral::Builder::build( ) const {
  if (isValid())
    return SceneObjectPtr
      (new MultiSpectral(*Reflectance,
                         *Transmittance,
                         Filter ? *Filter : DEFAULT_RGB_INDEX));
  return SceneObjectPtr();
}


void MultiSpectral::Builder::destroy( ) {
  if (Reflectance) delete Reflectance;
  if (Transmittance) delete Transmittance;
  if (Filter) delete Filter;
}


bool MultiSpectral::Builder::isValid( ) const {

  // Reflectance
  if ((! Reflectance) || (! (*Reflectance))) {
    pglErrorEx(PGLWARNINGMSG(UNINITIALIZED_FIELD_ss),"MultiSpectral","Reflectance");
    return false;
  }

  uint_t _size = (*Reflectance)->size();
  if (_size < 1) {
    pglErrorEx(PGLERRORMSG(INVALID_FIELD_SIZE_sss),"MultiSpectral","Reflectance","Must have more than 0 value.");
    return false;
  };

  for (uint_t _i = 0; _i < _size; _i++) {
    const real_t& _value = (*Reflectance)->getAt(_i);
    if (_value < 0 || _value > 1) {
        string _ith = TOOLS(number)(_i + 1);
        pglErrorEx
            (PGLERRORMSG(INVALID_FIELD_ITH_VALUE_ssss),"MultiSpectral","Reflectance",_ith.c_str(),"Must be in [0,1].");
        return false;
    }
  };

  /// Transmittance
  if ((! Transmittance) || (! (*Transmittance))) {
    pglErrorEx(PGLWARNINGMSG(UNINITIALIZED_FIELD_ss),"MultiSpectral","Transmittance");
    return false;
  }

  if ((*Transmittance)->size() != _size) {
    pglErrorEx(PGLERRORMSG(INVALID_FIELD_SIZE_sss),"MultiSpectral","Transmittance","Must have the same number of values than Reflectance.");
    return false;
  };

  for (uint_t _i1 = 0; _i1 < _size; _i1++) {
    const real_t& _value = (*Transmittance)->getAt(_i1);
    if (_value < 0 || _value > 1) {
        pglErrorEx
            (PGLERRORMSG(INVALID_FIELD_ITH_VALUE_ssss),"MultiSpectral","Transmittance", TOOLS(number(_i1 + 1)).c_str(),"Must be in [0,1].");
        return false;
    }
  };

  /// Filter
  if (Filter) {
    if ((Filter->getAt(0) > _size - 1) ||
        (Filter->getAt(1) > _size - 1) ||
        (Filter->getAt(2) > _size - 1)) {
      pglErrorEx(PGLERRORMSG(INVALID_FIELD_VALUE_sss),"MultiSpectral","Filter","Must be coherent with Refectance and Transmittance numbers of values.");
    };
  };

  return true;
}


/* ----------------------------------------------------------------------- */


MultiSpectral::MultiSpectral( ) :
  Spectrum(),
  __reflectance(),
  __transmittance(),
  __filter(DEFAULT_RGB_INDEX) {
}

MultiSpectral::MultiSpectral( const RealArrayPtr& reflectance,
                              const RealArrayPtr& transmittance,
                              const Index3& rgbIndex ) :
  Spectrum(),
  __reflectance(reflectance),
  __transmittance(transmittance),
  __filter(rgbIndex) {
  GEOM_ASSERT(isValid());
}

MultiSpectral::~MultiSpectral( ) {
}


bool MultiSpectral::isValid( ) const {
  Builder _builder;
  _builder.Reflectance = const_cast<RealArrayPtr *>(&__reflectance);
  _builder.Transmittance = const_cast<RealArrayPtr *>(&__transmittance);
  _builder.Filter = const_cast<Index3 *>(&__filter);
  return _builder.isValid();
}

SceneObjectPtr MultiSpectral::copy(DeepCopier& copier) const
{
  MultiSpectral * ptr = new MultiSpectral(*this);
  copier.copy_attribute(ptr->getReflectance());
  copier.copy_attribute(ptr->getTransmittance());
  return SceneObjectPtr(ptr);
}


/* ----------------------------------------------------------------------- */

const RealArrayPtr&
MultiSpectral::getReflectance( ) const {
  return __reflectance;
}

RealArrayPtr&
MultiSpectral::getReflectance( ) {
  return __reflectance;
}

const real_t&
MultiSpectral::getReflectanceAt( uint_t i ) const {
  GEOM_ASSERT(i < __reflectance->size());
  return __reflectance->getAt(i);
}

real_t&
MultiSpectral::getReflectanceAt( uint_t i ) {
  GEOM_ASSERT(i < __reflectance->size());
  return __reflectance->getAt(i);
}

uint_t
MultiSpectral::getReflectanceSize( ) const {
  return __reflectance->size();
}

/* ----------------------------------------------------------------------- */
const RealArrayPtr&
MultiSpectral::getTransmittance( ) const {
  return __transmittance;
}

RealArrayPtr&
MultiSpectral::getTransmittance( ){
  return __transmittance;
}

const real_t&
MultiSpectral::getTransmittanceAt( uint_t i ) const {
  GEOM_ASSERT(i < __transmittance->size());
  return __transmittance->getAt(i);
}

real_t&
MultiSpectral::getTransmittanceAt( uint_t i ) {
  GEOM_ASSERT(i < __transmittance->size());
  return __transmittance->getAt(i);
}

uint_t
MultiSpectral::getTransmittanceSize( ) const {
  return __transmittance->size();
}

/* ----------------------------------------------------------------------- */

Index3&
MultiSpectral::getFilter( ) {
  return __filter;
}

bool
MultiSpectral::isFilterToDefault( ) const {
  return __filter == DEFAULT_RGB_INDEX;
}
