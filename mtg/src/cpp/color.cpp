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
 *       $Id: color.cpp 17611 2014-10-17 13:20:41Z pradal $
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





#include "color.h"

MyColor::MyColor(const MyVector& emission,
		 const MyVector& ambient,
		 const MyVector& diffuse,
		 const MyVector& specular,
		 const ValType shininess,
		 const char a_symb )
{

  _emission=emission;
  _ambient=ambient;
  _diffuse=diffuse;
  _specular=specular;
  _shininess=shininess;
  _symbol=a_symb;
  _isInterpol=FALSE;
  _minRange=+99999999;
  _maxRange=-99999999;
}

MyColor::MyColor(const MyColor& color)
{
  construct(color);
}

MyColor::MyColor(const MyVector& c)
{
  _symbol=UNDEF;
  _ambient=c;// (0.071,0.050,0.011);
  _emission=MyVector (0.000,0.000,0.000);
  _diffuse=MyVector (0.42,0.42,0.17);
  _specular=MyVector (0.,0.,0.);// (0.221,0.207,0.125);
  _shininess=1;
  _isInterpol=FALSE;
  _minRange=+99999999;
  _maxRange=-99999999;
}

MyColor::MyColor(const char a_symb)
{
  _symbol=a_symb;
  _emission=MyVector (0.000,0.000,0.000);
  _ambient=MyVector (0.168,0.168,0.068);// (0.071,0.050,0.011);
  _diffuse=MyVector (0.42,0.42,0.17);
  _specular=MyVector (0.,0.,0.);// (0.221,0.207,0.125);
  _shininess=1;
  _isInterpol=FALSE;
  _minRange=+99999999;
  _maxRange=-99999999;
}
  

MyColor::MyColor()
{
  _symbol=UNDEF; 
  _isInterpol=FALSE;
  _minRange=+99999999;
  _maxRange=-99999999;
}

void MyColor::construct(const MyColor& color)
{
  _emission=color.emissionComponent();
  _ambient=color.ambientComponent();
  _diffuse=color.diffuseComponent();
  _specular=color.specularComponent();
  _shininess=color.shininessComponent();
  _symbol=color.getSymbol(); 
  _minRange=color._minRange;
  _maxRange=color._maxRange;
  _isInterpol=color._isInterpol;
}


const MyColor& MyColor::operator=(const MyColor& color)
{
  if (this!=&color)
  {
    construct(color);
  }
  
  return *this;
}

void MyColor::putMin(ValType min)
{
  _minRange=min;
  _isInterpol=TRUE;
}

void MyColor::putMax(ValType max)
{
  _maxRange=max;
  _isInterpol=TRUE;
}



AmlBoolean MyColor::operator==(const MyColor& color) const
{
  AmlBoolean result=FALSE;

  if ((_symbol==color.getSymbol())
      && (_emission==color._emission)
      && (_ambient==color._ambient)
      && (_diffuse==color._diffuse)
      && (_specular==color._specular)
      && (_shininess==color._shininess))     
  {
    result=TRUE;
  }

  return result;
}


// Definition de la classe ColorLib.


const MyVector COLORZERO (0,0,0);
const MyVector COLORONE (1,1,1);
const MyVector COLORTWO (0,1,0);
const MyVector COLORTHREE (1,0,0);
const MyVector COLORFOUR (0,0,1);
const MyVector COLORFIVE (1,1,0);
const MyVector COLORSIX (1,0,1);
const MyVector COLORSEVEN (0,1,1);
const MyVector COLORDEFAULT (0.5,0.5,0.5);

ColorLib::ColorLib()
{
  _colorList=new ColorsTable;
/*  MyColor color(COLORZERO,COLORZERO,COLORZERO,COLORZERO,1,-1);
  _colorList->insert(color);
  color = MyColor(COLORONE,COLORONE,COLORONE,COLORONE,1,-1);
  _colorList->insert(color);
  color = MyColor(COLORTWO,COLORTWO,COLORTWO,COLORTWO,1,-1);
  _colorList->insert(color);
  color = MyColor(COLORTHREE,COLORTHREE,COLORTHREE,COLORTHREE,1,-1); 
  _colorList->insert(color);
  color = MyColor(COLORFOUR,COLORFOUR,COLORFOUR,COLORFOUR,1,-1);
  _colorList->insert(color);
  color = MyColor(COLORFIVE,COLORFIVE,COLORFIVE,COLORFIVE,1,-1);
  _colorList->insert(color);
  color = MyColor(COLORSIX,COLORSIX,COLORSIX,COLORSIX,1,-1);
  _colorList->insert(color);
  color = MyColor(COLORSEVEN,COLORSEVEN,COLORSEVEN,COLORSEVEN,1,-1);
  _colorList->insert(color);
  color = MyColor(COLORDEFAULT,COLORDEFAULT,COLORDEFAULT,COLORDEFAULT,1,-1);
  _colorList->insert(color);*/

  MyColor color(COLORZERO,COLORZERO,COLORZERO,COLORZERO,1,-1); // black
  _colorList->insert(color); 
  color = MyColor(COLORONE,COLORONE,COLORONE,COLORONE,1,-1);  // white
  _colorList->insert(color);
  color = MyColor(COLORZERO,COLORTWO,COLORTWO,COLORZERO,1,-1); // green
  _colorList->insert(color);
  color = MyColor(COLORZERO,COLORTHREE,COLORTHREE,COLORZERO,1,-1); 
  _colorList->insert(color);
  color = MyColor(COLORZERO,COLORFOUR,COLORFOUR,COLORZERO,1,-1);
  _colorList->insert(color);
  color = MyColor(COLORZERO,COLORFIVE,COLORFIVE,COLORZERO,1,-1);
  _colorList->insert(color);
  color = MyColor(COLORZERO,COLORSIX,COLORSIX,COLORZERO,1,-1);
  _colorList->insert(color);
  color = MyColor(COLORZERO,COLORSEVEN,COLORSEVEN,COLORZERO,1,-1);
  _colorList->insert(color);
  color = MyColor(COLORZERO,COLORDEFAULT,COLORDEFAULT,COLORZERO,1,-1);
  _colorList->insert(color);
}

ColorLib::~ColorLib()
{
  delete _colorList;
}


void ColorLib::addColor(const MyColor& color)
{
  if (!_colorList->contains(color))
  {
    _colorList->insert(color);
  }
}

MyColor ColorLib::getColor(IntType number) const
{
  if (_colorList->entries()>0)
  {
    MyColor result (_colorList->at(_colorList->entries()-1));
    
    if (number<0)
    {
      //cout << "COLOR LIB L17: Warning :  Negative color number. " << endl;
    }
    else
    {
      if (number>=int(_colorList->entries()))
      {
	//cout << "COLOR LIB L23: Default color. " << endl;
      }
      else
      {
	result=_colorList->at(number);
      }
    }

    return result;
  }
  else 
  {
    return MyColor(COLORDEFAULT,COLORDEFAULT,COLORDEFAULT,COLORDEFAULT,1,-1);
  }
}


void ColorLib::clear()
{
  _colorList->clear();
}







