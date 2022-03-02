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
 *       $Id: diameters.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _DIAMETERS_SAMIR_DEF_
#define _DIAMETERS_SAMIR_DEF_


#include "measures.h"
#include "definitions.h"

class DressingFile;

#include "aml/fnode.h"

const ValType DEFAULTTOP=100;
const ValType DEFAULTBOT=100;

class TopDia : public Measures
{

 public:

  TopDia(Plant*,
	 const FNode*,
	 const ValType scale=1);
  
 protected:

  ValType lookForTopDia(const VId) const;
  ValType lookUpTopDia(const VId) const;
  ValType lookDownTopDia(const VId) const;
  
};


class BottomDia : public Measures
{

 public:

  BottomDia(Plant*,
	    const FNode*,
	    const ValType scale=1);

 protected:  

  ValType lookForBottomDia(const VId) const;  
  ValType lookUpBottomDia(const VId) const;
  ValType lookDownBottomDia(const VId) const;

};

class Diameters : public TopDia, public BottomDia 
{

 public:

  
  Diameters(Plant*,
	    const FNode* topf,
	    const FNode* botf,
	    const DressingFile*,
	    const ValType scale);

  virtual void computeDiameters(Branch&);
  AmlBoolean areValidDiameters() const { return _areValidDiameters;};


 private:
  
  const DressingFile* _dressingFile;
  AmlBoolean _areValidDiameters;
 
  ValType computeDiamsRatio(IntType, ValType, ValType);
  BranchElement nextDefinedTopDia(const Branch&, const BranchElement );
  BranchElement nextDefinedBottomDia(const Branch&, const BranchElement );
  void passOne(Branch&);


};

#endif

