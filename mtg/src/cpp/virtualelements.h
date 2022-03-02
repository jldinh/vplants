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
 *       $Id: virtualelements.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _VIRTUAL_ELEMENTS_SAMIR_
#define _VIRTUAL_ELEMENTS_SAMIR_

#include "aml/fnode.h"
#include "definitions.h"
#include "branch.h"

class DressingFile;
class Plant;
class LineTree;


class VirtualSymbol
{
 public:

  VirtualSymbol();
  VirtualSymbol(IntType);
  VirtualSymbol(IntType, IntType);
  VirtualSymbol(IntType, IntType, IntType, char);
  VirtualSymbol(const VirtualSymbol&);

  const VirtualSymbol& operator=(const VirtualSymbol& );
  AmlBoolean operator==(const VirtualSymbol&) const;

  IntType _element;
  IntType _bearing_element;
  IntType _colorNumber;
  char _symbol;


};

typedef RWTValDlist<VirtualSymbol> VirtualSymbolTable;


class VirtualElements : public AMModel
{
 public:

  VirtualElements(FNode* symbol_fun,
		  FNode* verticille,
		  FNode* elements_number,
		  FNode* color,
		  FNode* top_dia,
		  FNode* bottom_dia,
		  FNode* length,
		  FNode* alpha,
		  FNode* beta);
		


  ~VirtualElements();

  void addVirtualElements(LineTree*);

  virtual std::ostream& displayOneLine(std::ostream&) const;

  void setEnvironement(LineTree*,const DressingFile*,Plant*);

 protected:

  ValType fnodeValue( FNode* function, VId vertex);

  void computeElementsCoordinates(VId support, IntType nb_elements);

  void generateElements(LineTree*, IntType, IntType, VId, 
						ValType, ValType&, 
						Branch*,ValType);
  
		  
  virtual MyVector putOnElement( const BranchElement& base, BranchElement& br, 
			    ValType alpha, ValType beta, ValType ratio);

  virtual MyVector computeElementOrigin(const BranchElement& base, BranchElement& br,ValType ratio);
  virtual MyVector computePrimerDirection(const BranchElement&, BranchElement&);
  virtual MyVector computeSecondDirection(const BranchElement&, BranchElement&);
  virtual MyVector computeThirdDirection(MyVector&,MyVector&,const BranchElement&);

  virtual void computeElementLength(BranchElement&,VId);
  virtual void computeElementTopDia(BranchElement&,VId);
  virtual void computeElementBottomDia(BranchElement&,VId);

  virtual char getDefaultSymbol()=0;

  virtual ValType getAlpha(VId);
  virtual ValType getBeta(VId);

  virtual ValType getDefaultAlpha()=0;
  virtual ValType getDefaultBeta()=0;
  virtual ValType getDefaultTopDia()=0;
  virtual ValType getDefaultBottomDia()=0;
  virtual ValType getDefaultLength()=0;

  MyVector maxVector(MyVector, MyVector);
  MyVector minVector(MyVector, MyVector);
 public:
  FNode *_symbolFun;
  FNode *_verticille;
  FNode *_elementNumber;
  FNode *_color;
  FNode *_topDia;
  FNode *_bottomDia;
  FNode *_length;
  FNode *_alpha;
  FNode *_beta;

  Plant *_plant;

  const DressingFile* _dressingFile;
  VId _maxVertex;

};


class VirtualLeaves : public VirtualElements
{
 public:

   VirtualLeaves(FNode* symbol_fun,
		 FNode* verticille,
		 FNode* elements_number,
		 FNode* color,
		 FNode* top_dia,
		 FNode* bottom_dia,
		 FNode* length,
		 FNode* alpha,
		 FNode* beta);
		
   
  ~VirtualLeaves();

   virtual std::ostream& displayOneLine(std::ostream&) const;

 protected:

   virtual MyVector computeSecondDirection(const BranchElement&, BranchElement&);

   virtual MyVector computeThirdDirection(MyVector&,MyVector&,const BranchElement&);

   virtual char getDefaultSymbol();

   virtual ValType getDefaultAlpha();
   virtual ValType getDefaultBeta();
   virtual ValType getDefaultTopDia();
   virtual ValType getDefaultBottomDia();
   virtual ValType getDefaultLength();

};

class VirtualDigitizedLeaves : public VirtualElements
{
 public:

   VirtualDigitizedLeaves(FNode* symbol_fun,
		 FNode* verticille,
		 FNode* elements_number,
		 FNode* color,
		 FNode* top_dia,
		 FNode* bottom_dia,
		 FNode* length,
		 FNode* alpha,
		 FNode* beta,
		 FNode* xx,	  
		 FNode* yy,	  
		 FNode* zz,	  
		 FNode* teta,	  
		 FNode* phi,	  
		 FNode* psi);

   ~VirtualDigitizedLeaves();

   virtual std::ostream& displayOneLine(std::ostream&) const;

 protected:

   virtual MyVector computeElementOrigin(const BranchElement& base, BranchElement& br,ValType ratio);
   virtual MyVector computePrimerDirection(const BranchElement&, BranchElement&);
   virtual MyVector computeSecondDirection(const BranchElement&, BranchElement&);
   virtual MyVector computeThirdDirection(MyVector&,MyVector&,const BranchElement&);

   MyVector computeCoords(const BranchElement&, BranchElement&);
   MyVector computeEulerAngles(const BranchElement&, BranchElement&);

   virtual char getDefaultSymbol();

   virtual ValType getDefaultAlpha();
   virtual ValType getDefaultBeta();
   virtual ValType getDefaultTopDia();
   virtual ValType getDefaultBottomDia();
   virtual ValType getDefaultLength();

   FNode* _xx;
   FNode* _yy;
   FNode* _zz;
   FNode* _teta;
   FNode* _phi;
   FNode* _psi;

};

class VirtualFruits : public VirtualElements
{
 public:

   VirtualFruits(FNode* symbol_fun,
		 FNode* verticille,
		 FNode* elements_number,
		 FNode* color,
		 FNode* top_dia,
		 FNode* bottom_dia,
		 FNode* length,
		 FNode* alpha,
		 FNode* beta);
		
  ~VirtualFruits();

   virtual MyVector computeSecondDirection(const BranchElement&, BranchElement&);
   virtual std::ostream& displayOneLine(std::ostream&) const;

 protected:

   virtual MyVector computePrimerDirection(const BranchElement&, BranchElement&);

   virtual ValType getDefaultAlpha();
   virtual ValType getDefaultBeta();
   virtual ValType getDefaultTopDia();
   virtual ValType getDefaultBottomDia();
   virtual ValType getDefaultLength();
   virtual char getDefaultSymbol();


};

class VirtualFlowers : public VirtualElements
{
 public:

   VirtualFlowers(FNode* symbol_fun,
		  FNode* verticille,
		  FNode* elements_number,
		  FNode* color,
		  FNode* top_dia,
		  FNode* bottom_dia,
		  FNode* length,
		  FNode* alpha,
		  FNode* beta);
		
  ~VirtualFlowers();

   virtual std::ostream& displayOneLine(std::ostream&) const;

 protected:

   virtual ValType getDefaultAlpha();
   virtual ValType getDefaultBeta();
   virtual ValType getDefaultTopDia();
   virtual ValType getDefaultBottomDia();
   virtual ValType getDefaultLength();
   virtual char getDefaultSymbol();

};


#endif
