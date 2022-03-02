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
 *       $Id: plantframe.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _PLANTFRAME_SAMIR_DEF_
#define _PLANTFRAME_SAMIR_DEF_

#include "aml/fnode.h"

#include "plant.h"
#include "definitions.h"

class GeomComputer;
class DressingFile;

struct GP_window;

class PlantFrame : public AMModel


//class PlantFrame

{
 public:

  PlantFrame(VId,
             MTG* mtg,
             IntType,
             FNode*,
             FNode*,
             FNode*,
             FNode*,
             FNode*,
             FNode*,
             FNode*,
             FNode*,
             FNode*,
             FNode*,
             FNode*,
             FNode*,
             FNode*,
             RWCString opt,
             RWCString length_algo,
             ValType dist=0,
             const DressingFile* drf=NULL,
             ValType* translation = 0,
             ValType* origin = 0,
             FNode* digitizedf = 0
             );

PlantFrame(const VIdList*,
           MTG* mtg,
           IntType,
           FNode*,
           FNode*,
           FNode*,
           FNode*,
           FNode*,
           FNode*,
           FNode*,
           FNode*,
           FNode*,
           FNode*,
           FNode*,
           FNode*,
           FNode*,
           RWCString opt,
           RWCString length_algo,
           ValType dist=0,
           const DressingFile* drf=NULL,
           ValType* origin = 0,
           FNode* digitizedf = 0
           );

  ~PlantFrame();

  AmlBoolean isValid()const { return _plant->isAValidPlant();};


  void coord3D(VId vertex, ValType* v) const;
  void coord3DOrigin(VId vertex, ValType* v) const;
  void pdir(VId vertex, ValType* v) const;
  void sdir(VId vertex, ValType* v) const;
  void tdir(VId vertex, ValType* v) const;
  ValType length(VId vertex) const;
  ValType topDia(VId vertex) const;
  ValType botDia(VId vertex) const;
  ValType alpha(VId vertex) const;
  ValType beta(VId vertex) const;

  virtual AMObj plot(GP_window&, const AMObjVector& args) const;
  virtual std::ostream& displayOneLine(std::ostream&) const;

  const DressingFile * getDressingFile() const{
      return _dressingFile;
  }

  //  void plot(char* );

  void report();

  GeomComputer* _geomComputer;
  Plant* _plant;

 private:

  const DressingFile* _dressingFile;
  AmlBoolean _isMyDressingFile;
  RWCString* _displayMessage;
  AmlBoolean mtgType(MTG*);
  AmlBoolean verifyCartesianRef(MTG*);
  AmlBoolean verifyTriangRef(MTG*);

};


#endif






