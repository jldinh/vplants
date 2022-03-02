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
 *       $Id: measures.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _MEASURES_SAMIR_DEF
#define _MEASURES_SAMIR_DEF


#include "aml/fnode.h"

// Classe Category.


class DressingFile;

class Measures
{
 public:


  Measures(Plant* the_plant,
	   const FNode*,
	   const ValType scale);
  ~Measures();

  virtual void computeBranchCoordinates(Branch&){assert(1==0);};
  virtual void computeBranchLengths(Branch&, Measures*){assert(1==0);};
  virtual void computeAzimut(){assert(1==0);};
  virtual void computeDiameters(Branch&){assert(1==0);};
  virtual void computeBranchAlpha(Branch&) {assert(1==0);}; 
  virtual void computeBranchTeta(Branch&) {assert(1==0);}; 
  virtual void computeBranchPhi(Branch&) {assert(1==0);}; 
  virtual void computeBranchPsi(Branch&) {assert(1==0);}; 
  virtual void computeBranchCategory(Branch&) {assert(1==0);};
  virtual AmlBoolean areValidCoordinates() const  {assert(1==0); return 1;};
  virtual AmlBoolean areValidLengths() const {assert(1==0); return 1; };

  virtual void translatePlantElements() {assert(1==0);};
  virtual void translatePlantElements(MyVector) {assert(1==0);};
  virtual void newTrunk(size_t){assert(1==0);};
  virtual void lastTrunk(){assert(1==0);};

  virtual void coord3D( VId, ValType* ) const {assert(1==0);};
  virtual void coord3DOrigin( VId, ValType* ) const {assert(1==0);};

  IntType getLevel() const {return _level;};

  IntType _level;
  IntType _index;
  ValType _scale;
  Plant* _plant;
  MTG* _mtg;
  const FNode* _function;

  ValType fnodeValue(VId vertex) const;
  ValType lookForFeature(VId vertex, Date = (unsigned long)LUNDEF) const;
  IntType lookForLevel(VId vertex);

};

class Category : public Measures
{
 public:

  // Must have a constructor with a FNODE

  Category(Plant*,
	   const FNode*,
	   const DressingFile*);

  virtual void computeBranchCategory(Branch&);

 protected:

  const DressingFile* _dressingFile;

  ValType lookUpForCategory(VId) const;
  ValType lookDownForCategory(VId) const;
  IntType lookForCategory(VId) const;
  IntType ramOrder(const Branch&);

};

// Classe length

class Length : public Measures
{
 public:

  Length(Plant* plant,
	 const DressingFile*,
	 const FNode*,
	 const ValType scale);

  virtual void computeBranchLengths( Branch&, Measures*);
  virtual AmlBoolean areValidLengths() const { return _areValidLengths;};

  ValType lookDown(const VId) const;

 protected:
  
  AmlBoolean _areValidLengths;
  const DressingFile* _dressingFile;

  ValType lookUp(const VId) const;

  void computeElementLength( BranchElement& );
};

// Classe coordLength

struct IndexSegment{
  
  IntType topIndex;
  IntType botIndex; 

  IndexSegment();
  IndexSegment(IntType top, IntType bot);

  const IndexSegment& operator=(IndexSegment& ind_s);

  // Modification du segment

  void modif(IntType i);
};

class CoordLength : public Measures
{
 public:
  
  CoordLength(Plant*,
	      RWCString length_algo,
	      const FNode*,
	      const DressingFile*,
	      ValType);

  ~CoordLength();
  ValType getMinLength(VId vertex) const ;
  virtual void computeBranchLengths(Branch& branch, Measures*);
  
 private:
  
  AmlBoolean _isValid;
  const FNode* _function;
  const DressingFile* _dressingFile;
  Measures* _length;

  RWCString _length_algo;

  AmlBoolean isThereCoords(Branch&, Measures*);
  ValType computeElementLength(VId,
			       IntType,
			       IntType,
			       IndexSegment);

  VId nextIndex(Branch&,size_t, Measures*);
  
};

class Azimut : public Measures
{
 public:

  Azimut(Plant*,
	 const FNode*,
	 ValType base,
	 ValType scale);

  Azimut(Plant*,
	 const FNode*,
	 ValType nb_tours,
	 ValType nb_leaves,
	 ValType scale);
	    
  virtual void computeAzimut();
  
 private: 

  AmlBoolean _isPosition;
  AmlBoolean _isAzimut;
  ValType _base;
  ValType _nbTours;

  ValType lookForAzimut(VId) const;
  ValType lookUpForAzimut(VId) const;
  ValType lookDownForAzimut(VId) const;

};


class DressingFile;

class Alpha : public Measures
{
 public:

  Alpha(Plant* plant,
	const FNode*,
	const DressingFile*,
	ValType scale);

  ~Alpha();


  virtual void computeBranchAlpha(Branch& br);

  
 protected:

  ValType _defaultAlpha;
 
  ValType lookUpForAlpha(VId) const;
  ValType lookDownForAlpha(VId) const;
  ValType computeElementAngle(VId) const;

};

class Teta : public Measures
{
 public:

  Teta(Plant* plant,
	const FNode*,
	const DressingFile*,
	ValType scale);

  ~Teta();

  ValType computeTeta(VId) const;

 protected:

  ValType _default;
 
  ValType lookUp(VId) const;
  ValType lookDown(VId) const;

};

class Phi : public Measures
{
 public:

  Phi(Plant* plant,
	const FNode*,
	const DressingFile*,
	ValType scale);

  ~Phi();

  ValType computePhi(VId) const;

 protected:

  ValType _default;
 
  ValType lookUp(VId) const;
  ValType lookDown(VId) const;

};

class Psi : public Measures
{
 public:

  Psi(Plant* plant,
	const FNode*,
	const DressingFile*,
	ValType scale);

  ~Psi();

  ValType computePsi(VId) const;

 protected:

  ValType _default;
 
  ValType lookUp(VId) const;
  ValType lookDown(VId) const;

};

// Classe lcoords

class L1Coord : public Measures
{
 public:
  
  L1Coord(Plant*,
	  const FNode*,
	  ValType scale=1);
 
};

class L2Coord : public Measures
{
 public:
  
  L2Coord(Plant*,
	 const FNode*,
	  ValType scale=1);

};

class L3Coord : public Measures
{
 public:
  
  L3Coord(Plant*,
	 const FNode*,
	  ValType scale=1);

};
class XCoord : public Measures
{
 public:
  
  XCoord(Plant*,
	 const FNode*,
	 ValType scale=1);
 
};

class YCoord : public Measures
{
 public:
  
  YCoord(Plant*,
	 const FNode*,
	 ValType scale=1);

};

class ZCoord : public Measures
{
 public:
  
  ZCoord(Plant*,
	 const FNode*,
	 ValType scale=1);

};

#endif






