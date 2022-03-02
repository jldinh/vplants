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
 *       $Id: correlement.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _CORR_ELEMENT_SAMIR_DEF_
#define _CORR_ELEMENT_SAMIR_DEF_


#include "tool/rw_vector.h"
//#include <rw/tvsrtvec.h>
#include "definitions.h"

class CorrElement
{
 public:

  CorrElement(VId vertex,
              SymbType symbol,
              ValType range);

  CorrElement(const CorrElement&);
  CorrElement(VId vertex);
  CorrElement();

  AmlBoolean operator==(const CorrElement&) const;
  AmlBoolean operator<(const CorrElement&) const;
  const CorrElement& operator=(const CorrElement&);

  SymbType getSymbol() const { return _symbol;};
  ValType getRange() const { return _range;};
  VId getVertex() const { return _vertex;};

  void translateRange(ValType delta);

 private:

  ValType _range;
  SymbType _symbol;
  VId _vertex;
};

typedef RWTValSortedVector<CorrElement> CorrTable;

#endif

