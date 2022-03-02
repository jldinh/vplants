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
 *       $Id: coordinates.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _COORDINATES_SAMIR_DEF_
#define _COORDINATES_SAMIR_DEF_

#include "definitions.h"
#include "vector.h"
#include "refsystem.h"

#include "attributes.h"
// Contient les noms des attributs.
#include "aml/fnode.h"
#include "plant.h"
#include "measures.h"

class DressingFile;
class Plant;
class Squares;


class Coordinates : public Measures
{
 public:

  Coordinates(Plant*,
	      const DressingFile*,
	      ValType dist,
	      ValType scale);

  virtual ~Coordinates();

  virtual void computeBranchCoordinates(Branch&);
  virtual AmlBoolean areValidCoordinates() const {return _areValidCoordinates;};

  void translatePlantElements();
  void translatePlantElements(MyVector delta);
  void newTrunk(size_t);
  void lastTrunk();

  virtual void coord3D(VId ,ValType* ) const;
  virtual void coord3DOrigin(VId ,ValType* ) const;

 protected:

  ValType computeRatio(VId,VId);
  ValType lookForRatio(VId,VId);
  MyVector _origin;
  const DressingFile* _dressingFile;
  AmlBoolean _areValidCoordinates;
  Squares* _squares;

 
  MyVector minVector(MyVector ,MyVector);
  MyVector maxVector(MyVector ,MyVector);

  MyVector putOn(const BranchElement&,
		 BranchElement&,
		 const ValType,
		 const ValType,
		 const ValType);
  

  MyVector putOnAbs(const BranchElement&,
		    BranchElement&,
		    const ValType,
		    const ValType,
		    const ValType);
  
  IntType computeCategory(VId);
  MyVector computeElementCoordinates(BranchElement&,ValType);
  MyVector computeElementCoordinatesWithForm(BranchElement&);
  void translateBranch(Branch* br, ValType dx, ValType dy, ValType dz );
};


// RequiredCoords.

class RequiredCoords : public Coordinates
{

  friend class CoordLength;

 public:
  
  RequiredCoords(Plant*,
		 FNode* xxf,
		 FNode* yyf,
		 FNode* zzf,			       
		 CoordsType,
		 const DressingFile*,
		 ValType dist,
		 ValType scale);

  ~RequiredCoords();
  virtual void computeBranchCoordinates(Branch& branch);

 protected:
  
  RefSystem* _refSystem;
  IntType _DABindex,_DBCindex,_DACindex;
  Measures* _xcoord;
  Measures* _ycoord;
  Measures* _zcoord;
  AmlBoolean _isValidRefSystem;
  IntType _sysLevel;

  AmlBoolean lookForRefSystem();
  AmlBoolean lookForCoords(VId vertex,MyVector& vector);
  AmlBoolean lookUpCoords(VId vertex,MyVector& vector);
  MyVector lookForOrigin(BranchElement&);
  AmlBoolean findFeature(VId,IntType,ValType&);


};




class Troubles 
{

 public:

  Troubles(const DressingFile* ); //  FNode* nb_leaves, FNode* verticille, FNode* symbol);



  virtual void createTroubles();
  virtual void insertTroublesInPlant();
  virtual void computeTroublesCoordinates();


 protected:
  
  FNode* _nbLeaves;
  FNode* _verticille;
  FNode* _symbol;

};


class Leaves : public Troubles
{
 public:

  Leaves();

  virtual void insertTroublesInPlant();
  virtual void computeTroublesCoordinates();

};

class FruitAndFlower : public  Troubles
{
 public:
  
  FruitAndFlower();
  
  virtual void insertTroublesInPlant();
  virtual void computeTroublesCoordinates();

};

#endif




















