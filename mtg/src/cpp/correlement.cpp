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
 *       $Id: correlement.cpp 17611 2014-10-17 13:20:41Z pradal $
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





#include "correlement.h"

CorrElement::CorrElement(VId vertex,
			 SymbType symbol,
			 ValType range)
{
  _vertex=vertex;
  _symbol=symbol;
  _range=range;
}

CorrElement::CorrElement(VId vertex)
{
  _vertex=vertex;
  _symbol=-1;
  _range=1;
}

CorrElement::CorrElement(const CorrElement& corr_element)
{
  _vertex=corr_element._vertex;
  _symbol=corr_element._symbol;
  _range=corr_element._range;
}


CorrElement::CorrElement()
{
  _vertex=UNDEF;
  _symbol=-1;
  _range=1;
}


void CorrElement::translateRange(ValType delta)
{
  _range+=delta;
 
  // After the translation the range must be obligatory positive.
  assert(_range>=0);
}

AmlBoolean CorrElement::operator==(const CorrElement& corr_element) const
{
  if (_vertex==corr_element._vertex)
  {
    return TRUE;
  }
  else
  {
    return FALSE;
  }
}

AmlBoolean CorrElement::operator<(const CorrElement& corr_element) const
{
  if (_vertex<corr_element._vertex)
  {
    return TRUE;
  }
  else
  {
    return FALSE;
  }
}

const CorrElement& CorrElement::operator=(const CorrElement& corr_element)
{
  if (this!=&corr_element)
  {
    _vertex=corr_element._vertex;
    _symbol=corr_element._symbol;
    _range=corr_element._range;
  } 
  
  return *this;
}

