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
 *       $Id: squares.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _SQUARES_SAMIR_DEF_
#define _SQUARES_SAMIR_DEF_

#include "definitions.h"
#include "vector.h"
#include <iostream>
#include "tool/rw_list.h"
//#include <rw/tvslist.h>

class Voxel
{
 public:

  Voxel(size_t index);
  Voxel(size_t, MyVector, MyVector);
  Voxel(const Voxel&);
  ~Voxel();

  void putMin(MyVector min);
  void putMax(MyVector max);

  void putDeltaX(ValType delta) { _deltaX=delta;};
  void putDeltaY(ValType delta) { _deltaY=delta;};
  void putDeltaZ(ValType delta) { _deltaZ=delta;};

  ValType getDeltaX() const { return _deltaX;};
  ValType getDeltaY() const { return _deltaY;};
  ValType getDeltaZ() const { return _deltaZ;};

  MyVector getMin() const {return _minVector;};
  MyVector getMax() const {return _maxVector;};

  AmlBoolean operator==(const Voxel&) const;
  const Voxel& operator=(const Voxel&);

  void translate();

  size_t getVoxelsNumber() const {return _voxelsNumber;};

  void report();

 private:

  size_t _index;
  MyVector _minVector;
  MyVector _maxVector;
  ValType _deltaX;
  ValType _deltaY;
  ValType _deltaZ;
  static size_t _voxelsNumber;

};


typedef RWTValDlist<Voxel> ListOfVoxels;

class Squares
{
 public:

  Squares(ValType);
  ~Squares();

  MyVector getMin(size_t index) const;
  MyVector getMax(size_t index) const;

  void addVoxel(Voxel);

  void computePositions(size_t number_per_line);
  size_t getNbVoxels() const { return _voxels->entries();};
  void report();

  ListOfVoxels* _voxels;
  ValType _deltaPlant;

};


#endif



