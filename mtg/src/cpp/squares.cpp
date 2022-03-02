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
 *       $Id: squares.cpp 17611 2014-10-17 13:20:41Z pradal $
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





#include "squares.h"

using namespace std;

// Class Voxel

size_t Voxel::_voxelsNumber=0;

Voxel::Voxel(size_t index,MyVector min, MyVector max)
{
  _index=index;
  _minVector=min;
  _maxVector=max;
  _voxelsNumber++;
  _deltaX=_deltaY=_deltaZ=0;
}

Voxel::Voxel(size_t index)
{
  _index=index;
  _voxelsNumber++;
  _deltaX=_deltaY=_deltaZ=0;
}

Voxel::Voxel(const Voxel& v)
{
  _index=v._index;
  _minVector=v._minVector;
  _maxVector=v._maxVector;
  _voxelsNumber++;
  _deltaX=_deltaY=_deltaZ=0;
}

Voxel::~Voxel()
{
  _voxelsNumber--;
}

void Voxel::putMin(MyVector min)
{
  _minVector=min;
}

void Voxel::putMax(MyVector max)
{
  _maxVector=max;
}

AmlBoolean Voxel::operator==(const Voxel& v) const
{
  if (_index==v._index)
  {
    return TRUE;
  }
  else
  {
    return FALSE;
  }
}


const Voxel& Voxel::operator=(const Voxel& v)
{
  if (this!=&v)
  {
    _index=v._index;
    _minVector=v._minVector;
    _maxVector=v._maxVector;
  }

  return *this;
}


void Voxel::translate()
{
  MyVector delta(_deltaX,_deltaY,_deltaZ);

  _minVector=_minVector+delta;
  _maxVector=_maxVector+delta;
}

void Voxel::report()
{

  cout << "-------------------------------------------------------------" << endl;
  cout << "Voxel for index : " << _index << endl;
  cout << "Min : (" << _minVector[0] << "," <<  _minVector[1] << "," << _minVector[2] << ")" << endl;
  cout << "Max : (" << _maxVector[0] << "," <<  _maxVector[1] << "," << _maxVector[2] << ")" << endl;
  cout << "Delta X : " << _deltaX << " Delta Y : " << _deltaY << " Delta Z : " << _deltaZ << endl;
  cout << "-------------------------------------------------------------" << endl;
}

// Class Squares


Squares::Squares(ValType delta_plant)
{
  _voxels=new ListOfVoxels;
  _deltaPlant=delta_plant;
}

Squares::~Squares()
{
  delete _voxels;
}

MyVector Squares::getMin(size_t index) const
{
  assert(index<=_voxels->entries());

  return _voxels->at(index).getMin();
}

MyVector Squares::getMax(size_t index) const
{
  assert(index<=_voxels->entries());

  return _voxels->at(index).getMax();
}

void Squares::addVoxel(Voxel v)
{
  assert(!_voxels->contains(v));

  _voxels->insert(v);
}

void Squares::computePositions(size_t n)
{
  // N est le nombre de plantes par ligne

  // cerr << "nombre de plantes par ligne = " << n << endl;

  size_t nb_voxels=_voxels->entries();
  size_t index=0;

  AmlBoolean end_of_loop=!(index<nb_voxels);

  ValType ddy=0;
  ValType ddx=_deltaPlant;


  while(!end_of_loop)
  {
    if ((index % n) != 0)
    {
      // Translation en Y

      MyVector min=_voxels->at(index).getMin();
      MyVector max=_voxels->at(index-1).getMax();

      ValType y1=min[1];
      ValType y2=max[1];

      // Rajoute le 15/11/95

      if (_deltaPlant>0)
      {
        _voxels->at(index).putDeltaY(y2+_deltaPlant-y1);
      }
      else
      {
        _voxels->at(index).putDeltaY(-_deltaPlant+ddy); // Dans ce cas _deltaPlant est negatif.
        ddy+=(-_deltaPlant);
      }

    }
    else
    {
      ddy=0;
      ddx+=(-_deltaPlant);
    }

    if (index>=n)
    {
      // Translation en X

      MyVector min=_voxels->at(index).getMin();
      MyVector max=_voxels->at(index-n).getMax();

      ValType x1=min[0];
      ValType x2=max[0];

      if (_deltaPlant>0)
      {
        _voxels->at(index).putDeltaX(x2+_deltaPlant-x1);
      }
      else
      {
        _voxels->at(index).putDeltaX(ddx); // _deltaPlant);
      }
    }


    _voxels->at(index).translate();

    index++;

    end_of_loop=!(index<nb_voxels);
  }
}

void Squares::report()
{

  size_t nb_v=_voxels->entries();
  cout << "Voxels number : " << nb_v << endl;
  for (size_t i=0;i<nb_v;i++)
  {
    _voxels->at(i).report();
  }

}

