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
 *       $Id: color.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _COLOR_SAMIR_DEF_
#define _COLOR_SAMIR_DEF_

#include "definitions.h"
#include "vector.h"

#include "tool/rw_list.h"
//#include <rw/tpslist.h>


/*

   Compiled on 28 of July

   0 errors.
   0 warnings.


*/


class MyColor
{

 public:

  MyColor(const MyColor&);
  MyColor();
  MyColor(const char);
  MyColor(const MyVector&);
  MyColor(const MyVector&,
          const MyVector&,
          const MyVector&,
          const MyVector&,
          const ValType,
          const char);

  const MyVector& emissionComponent() const { return _emission; };
  const MyVector& ambientComponent() const { return _ambient; };
  const MyVector& diffuseComponent() const { return _diffuse; };
  const MyVector& specularComponent() const { return _specular; };
  ValType shininessComponent() const { return _shininess; };
  char  getSymbol() const { return _symbol; };

  // Virtuals methods for Interpoled colors.


  AmlBoolean isInterpoled() const { return _isInterpol;};
  ValType getMax() const { return _maxRange;};
  ValType getMin() const { return _minRange;};
  void putMin(ValType min);
  void putMax(ValType max);
  //Operators

  virtual const MyColor& operator=(const MyColor& );
  AmlBoolean operator==(const MyColor&) const;

 protected:

  AmlBoolean _isInterpol;
  ValType _minRange;
  ValType _maxRange;
  char _symbol;
  MyVector _emission;
  MyVector _ambient;
  MyVector _diffuse;
  MyVector _specular;
  ValType _shininess;

  void construct(const MyColor& );
};

typedef RWTValDlist<MyColor> ColorsTable;

class ColorLib
{
 public:

  // Constructor and destructor

  ColorLib();
  ~ColorLib();

  // Modifier

  void addColor(const MyColor&);
  void clear();

  // Seelctor

  MyColor getColor(IntType number) const;

 private:

  ColorsTable* _colorList;

};



#endif
