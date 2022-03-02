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
 *       $Id: header.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef MTGHEADER_HEADER
#define MTGHEADER_HEADER

#include <assert.h>

#include "tool/rw_list.h"
#include "tool/rw_cstring.h"
#include "tool/rw_vector.h"
#include "tool/rw_bitvec.h"

//#include <rw/cstring.h>
//#include <rw/tvordvec.h>
//#include <rw/tvslist.h>
//#include <rw/bitvec.h>

#include "aml/defs.h"
#include "utils.h"
#include "utils_template.h"

typedef RWTValOrderedVector<char> CharArray;
typedef RWTValOrderedVector<int> IntArray;
typedef RWTValDlist<VClass> VClassList;

typedef RWTValOrderedVector<String> StringArray;
typedef RWTValOrderedVector<FType> FTypeArray;
typedef RWTValOrderedVector<void*> FeatureSmbTableArray;

// Definition d'enum pour parler des attributs predefinis comme "Date", "State", ...
// UNDEF_f should not be used as a valid FFLAG. Rather it is used to
// know the number of FFlag and as an undefined return value.

typedef enum {ALIAS_F = 0, DATE_F, STATE_F, NBEL_F, LENGTH_F, DIAM_F, UNDEF_F} FFlag;


class ClassDef {

  int _class_nb;

  CharArray _class_symbol; //correspondance class/symbol(nom)

  IntArray _scale;     // correspondance class/scale

  IntArray _vdecomp;   // FREE, LINEAR or CONNECTED
  IntArray _vindexing; // FREE, CONSECUTIVE
  IntArray _vdef;      // IMPLICIT or EXPLICIT

  TwoDimArray<Intervalle>* _less; // definition precise des classes
  TwoDimArray<Intervalle>* _plus;

public:

  ClassDef(int class_nb,
           const CharArray class_symbol,
           const IntArray scale,
           const IntArray vdecomp,
           const IntArray vindexing,
           const IntArray vdef);
  ~ClassDef();

  ClassDef& operator=(const ClassDef&);

  AmlBoolean isValid(char i) const;
  AmlBoolean isValid(VClass i) const {return (i>=0 && i<_class_nb);}

  VClass vClass(char c) const;

  char symbol(VClass c) const {assert(isValid(c)); return _class_symbol[c];}

  int classNb() const {return _class_nb;}

  // Alloue une zone dynammique
  VClassList* classesAtScale(int scale) const;

  int scale(VClass c) const {if (isValid(c)) return _scale[c];
                             else return UNDEF;}

  int vdecomp(VClass c) const {if (isValid(c)) return _vdecomp[c];
                               else return UNDEF;}

  int vindexing(VClass c) const {if (isValid(c)) return _vindexing[c];
                               else return UNDEF;}

  int vdef(VClass c) const {if (isValid(c)) return _vdef[c];
                            else return UNDEF;}

  Intervalle& less(VClass i, VClass j) const;
  Intervalle& plus(VClass i, VClass j) const;

};



// the Feature of index 0 is used to store the line nb of
// the feature-set definition

class FSetDef {

  int _fnb; // nombre de features associees a un vertex + 1 (line nb)

  StringArray _name;
  const FTypeArray _type;
  const FeatureSmbTableArray _smbtable;

  RWBitVec _fflags; // ensemble de flags positionnes une fois pour toute d'apres l'entete
  RWTValOrderedVector<FFlag> _findexflag; // each index stores the FFLAG type of the coresponding feature

public:

  static FFlag nameFFlag(const String& name);
  static int checkPredefinedFeature(RWCString nameval, FType typeval);
  static int checkOrderIfPredefined(const StringArray* featname, String newfeatname);

  FSetDef(int fnb, StringArray name, FTypeArray type, FeatureSmbTableArray smbtable);
  ~FSetDef() {}

  int fNb() {return _fnb;}
  int findex(FFlag f) const;
  FFlag fFlag(int index) const;
  AmlBoolean isFFlagSet(FFlag i) const {return _fflags.testBit((int) i);}

  AmlBoolean existsType(FType type) const;
  AmlBoolean existsName(const String& name) const;
  AmlBoolean existsIndex(int index) const {return index < FSetDef::_fnb && index >=0 ? TRUE : FALSE;}

  int typeIndex(FType type) const;
  int nameIndex(const String& name) const;

  String name(int i) const {assert(existsIndex(i)); return _name[i];}
  FType type(int i) const {assert(existsIndex(i)); return _type[i];}
  void* smbTable(int i) const {assert(existsIndex(i)); return _smbtable[i];}

};

class MTG;

// Classe de l'objet associe a la description de l'entete
// generale d'un fichier de codage. Cette entete n'est
// creer qu'une seule fois pour un fichier donne et est
// referencee par tous les GTM imbriques d'une hierarchie
// de gtm

class MTGHeader {

  MTG* _the_mtg;        // mtg GLOBAL considere

  int _scale_nb;        // nb total de niveaux definis dans ce fichier de codage

  ClassDef* _cldef;     // Contient la definition de l'ensemble de classes

  FSetDef* _fsetdef;    // Contient la definition des attributs

public:

  MTGHeader(int scale_nb,
            ClassDef* cldef,
            FSetDef* fsetdef,
            MTG* mtg);

  ~MTGHeader() {delete _cldef; delete _fsetdef;}

  int scaleNb() const {return _scale_nb;}

  VClass vClass(char c) const {return _cldef->vClass(c);}
  AmlBoolean isValidClass(char i) const{return _cldef->isValid(i);}
  AmlBoolean isValidClass(VClass i) const {return _cldef->isValid(i);}

  char symbol(VClass c) const {return _cldef->symbol(c);}

  int classNb() const {return _cldef->classNb();}

  // Alloue une liste dynamique
  VClassList* classesAtScale(int scale) const {return _cldef->classesAtScale(scale);}

  int scale(VClass c) const {return _cldef->scale(c);}
  int vdecomp(VClass c) const {return _cldef->vdecomp(c);}
  int vindexing(VClass c) const {return _cldef->vindexing(c);}
  int vdef(VClass c) const {return _cldef->vdef(c);}

  Intervalle& less(VClass i, VClass j) const {return _cldef->less(i,j);}
  Intervalle& plus(VClass i, VClass j) const {return _cldef->plus(i,j);}


  int fNb() const {return _fsetdef->fNb();}

  AmlBoolean existsFType(FType type) const {return _fsetdef->existsType(type);}
  AmlBoolean existsFName(const String& name) const {return _fsetdef->existsName(name);}
  AmlBoolean existsFIndex(int index) const {return _fsetdef->existsIndex(index);}

  int fTypeIndex(FType type) const {return _fsetdef->typeIndex(type);}
  int fNameIndex(const String& name) const {return _fsetdef->nameIndex(name);}

  int fIndex(FFlag f) const {return _fsetdef->findex(f);}
  FFlag fFlag(int index) const {return _fsetdef->fFlag(index);}
  AmlBoolean isFFlagSet(FFlag i)const {return _fsetdef->isFFlagSet(i);}

  String fName(int i) const {return _fsetdef->name(i);}
  FType fType(int i) const {return _fsetdef->type(i);}
  void* fSmbTable(int i) const {return _fsetdef->smbTable(i);}

  std::ostream& print(std::ostream&) const;

};


#endif
