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
 *       $Id: header.cpp 17611 2014-10-17 13:20:41Z pradal $
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




#include <assert.h>
#include <iostream>

#include "header.h"
#include "error.h"
#include "errormsgs.h"
#include "parser_dec.h"

using namespace std;

//static const char rcsid[] = "$Id: header.cpp 17611 2014-10-17 13:20:41Z pradal $";

ClassDef::ClassDef(int class_nb,
                   const CharArray class_symbol,
                   const IntArray scale,
                   const IntArray vdecomp,
                   const IntArray vindexing,
                   const IntArray vdef
                   ):
_class_nb(class_nb),
_class_symbol(class_symbol),
_scale(scale),
_vdecomp(vdecomp),
_vindexing(vindexing),
_vdef(vdef)
{

/*
  cerr << "classnb      = " << class_nb << endl;
  cerr << "class_symbol = " << class_symbol.entries() << endl;
  cerr << "scale_entr   = " << scale.entries() << endl;
*/
  assert(class_nb == class_symbol.entries() && class_nb == scale.entries());

  _less = new TwoDimArray<Intervalle>(class_nb, class_nb);
  _plus = new TwoDimArray<Intervalle>(class_nb, class_nb);

  assert(_less);
  assert(_plus);

}

ClassDef::~ClassDef() {

  delete _less;
  delete _plus;

}

ClassDef& ClassDef::operator=(const ClassDef& cd) {

  if (this != &cd) {

    _class_nb = cd._class_nb;
    _class_symbol = cd._class_symbol;
    _scale = cd._scale;

    delete _less;
    delete _plus;

    _less = new TwoDimArray<Intervalle>(_class_nb, _class_nb);
    _plus = new TwoDimArray<Intervalle>(_class_nb, _class_nb);

    assert(_less);
    assert(_plus);

    *_less = *cd._less;
    *_plus = *cd._plus;

  }

  return *this;

}

VClass ClassDef::vClass(char c) const {

  assert(isValid(c));

  int id = (int) _class_symbol.index(c);

  return id;

}

AmlBoolean ClassDef::isValid(char c) const {

  if (_class_symbol.index(c) != RW_NPOS) return TRUE;
  else return FALSE;

}

VClassList* ClassDef::classesAtScale(int scale) const {

  VClassList* list = new VClassList; // construit une liste vide
  assert(list);

  for(int i=0; i<_class_nb; i++) {

    if (scale == _scale[i]) list->insert(i);

  }

  return list;

}

Intervalle& ClassDef::less(VClass i, VClass j) const {

  assert(isValid(i) && isValid(j) && _less != 0);

  return (*_less)(i,j);

}

Intervalle& ClassDef::plus(VClass i, VClass j) const {

  assert(isValid(i) && isValid(j) && _plus != 0);
  return (*_plus)(i,j);

}


//------------- FSetDef --------------

FSetDef::FSetDef(int fnb, StringArray name, FTypeArray type, FeatureSmbTableArray smbtable):
  _name(name),
  _type(type),
  _smbtable(smbtable),
  _fflags(RWBitVec(UNDEF_F, FALSE))
{

  _fnb = fnb; // line_nb is stored as a feature of index 0

  _findexflag.resize(_fnb);

  for(int i1=0; i1<_fnb; i1++) _findexflag.insertAt(i1,UNDEF_F);

  for(int i=0; i<_fnb; i++) {

    if (name(i) == "Alias") {
      _fflags.setBit(ALIAS_F);
      _findexflag[i] = ALIAS_F;
    }
    else if (name(i) == "Date") {
      _fflags.setBit(DATE_F);
      _findexflag[i] =  DATE_F;
    }
    else if (name(i) == "State") {
      _fflags.setBit(STATE_F);
      _findexflag[i] = STATE_F;
    }
    else if (name(i) == "NbEl") {
      _fflags.setBit(NBEL_F);
      _findexflag[i] = NBEL_F;
    }
    else if (name(i) == "Length") {
      _fflags.setBit(LENGTH_F);
      _findexflag[i] = LENGTH_F;
    }
    else if (name(i) == "Diam") {
      _fflags.setBit(DIAM_F);
      _findexflag[i] = DIAM_F;
    }

  }

}

int FSetDef::findex(FFlag ff) const {

  if (ff == UNDEF_F) return UNDEF;

  for (int i=0; i < _fnb; i++) {

    if (_findexflag[i] == ff) return i;

  }

  return UNDEF;

}

FFlag FSetDef::fFlag(int index) const {

  return _findexflag[index];

}


AmlBoolean FSetDef::existsType(FType type) const {

  for (int i=0; i<_fnb; i++) {

    if (_type[i] == type) return TRUE;
  }

  return FALSE;
}

AmlBoolean FSetDef::existsName(const String& name) const {

  for (int i=0; i<FSetDef::_fnb; i++) {

    if (_name[i] == name) return TRUE;
  }

  return FALSE;

}

int FSetDef::typeIndex(FType type) const {

  for (int i=0; i<_fnb; i++) {

    if (_type[i] == type) return i;
  }

  return UNDEF;
}

int FSetDef::nameIndex(const String& name) const {

  for (int i=0; i<_fnb; i++) {

    if (_name[i] == name) return i;
  }

  return UNDEF;

}

FFlag FSetDef::nameFFlag(const String& name) {

  FFlag nameval = UNDEF_F;

  if (name == "Alias") nameval = ALIAS_F;
  else if (name == "Date") nameval = DATE_F;
  else if (name == "State") nameval = STATE_F;
  else if (name == "NbEl") nameval = NBEL_F;
  else if (name == "Length") nameval = LENGTH_F;
  else if (name == "Diam") nameval = DIAM_F;
  else nameval = UNDEF_F;

  return nameval;

}


int FSetDef::checkPredefinedFeature(RWCString nameval, FType typeval) {

  if (nameval == "Alias") {

    if (ISFALSE(typeval == ALPHA)) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(NOTYPEFORPREDFEAT_0);

      return CHECKERROR;
    }
  }
  else if (nameval == "Date") {

    if (ISFALSE(typeval == DDMM ||
                typeval == DDMMYY ||
                typeval == MMYY ||
                typeval == DDMMTIME ||
                typeval == DDMMYYTIME)) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(NOTYPEFORPREDFEAT_0);

      return CHECKERROR;
    }

  }
  else if (nameval == "State") {

    if (ISFALSE(typeval == ALPHA)) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(NOTYPEFORPREDFEAT_0);

      return CHECKERROR;
    }

  }
  else if (nameval == "Diam") {

    if (ISFALSE(typeval == INTEGER)) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(NOTYPEFORPREDFEAT_0);

      return CHECKERROR;
    }

  }
  else if (nameval == "Length") {

    if (ISFALSE(typeval == INTEGER)) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(NOTYPEFORPREDFEAT_0);

      return CHECKERROR;
    }

  }
  else if (nameval == "NbEl") {

    if (ISFALSE(typeval == INTEGER)) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(NOTYPEFORPREDFEAT_0);

      return CHECKERROR;
    }

  }

  return TRUE;

}

int FSetDef::checkOrderIfPredefined(const StringArray* featname, String newfeatname) {


  FFlag nameval = FSetDef::nameFFlag(newfeatname);

  // get last non UNDEF_F FFLAG in array name

  if (nameval != UNDEF_F) {

    if (nameval == ALIAS_F && featname->entries() != 0) {

      yyerror(LOGICALERR);
      COMPLETEERRORITEM(ALIASDEFINEDFIRST_0);

      return CHECKERROR;

    }

    for(int i=featname->entries()-1; i>=0; i--) {

      if ((*featname)(i) == "Alias") {

        if (ISFALSE(ALIAS_F < nameval)) {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(PREDFEATORDERING_0);

          return CHECKERROR;

        }

      }
      else if ((*featname)(i) == "Date") {

        if (ISFALSE(DATE_F < nameval)) {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(PREDFEATORDERING_0);

          return CHECKERROR;

        }

      }
      else if ((*featname)(i) == "State") {

        if (ISFALSE(STATE_F < nameval)) {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(PREDFEATORDERING_0);

          return CHECKERROR;

        }

      }
      else if ((*featname)(i) == "NbEl") {

        if (ISFALSE(NBEL_F < nameval)) {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(PREDFEATORDERING_0);

          return CHECKERROR;

        }

      }
      else if ((*featname)(i) == "Length") {

        if (ISFALSE(LENGTH_F < nameval)) {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(PREDFEATORDERING_0);

          return CHECKERROR;

        }

      }
      else if ((*featname)(i) == "Diam") {

        if (ISFALSE(DIAM_F < nameval)) {

          yyerror(LOGICALERR);
          COMPLETEERRORITEM(PREDFEATORDERING_0);

          return CHECKERROR;

        }

      }

    } // end of for

  }
  else return TRUE; // a none predefined feature is always correctly placed

  return TRUE;

}



// --------------- MTGHeader -----------------

MTGHeader::MTGHeader(int scale_nb,
                     ClassDef* cldef,
                     FSetDef* fsetdef,
                     MTG* mtg)
{

  _scale_nb = scale_nb;

  _cldef = cldef;

  _fsetdef = fsetdef;

  _the_mtg = mtg;

}

ostream& MTGHeader::print(ostream& o) const {

  o << "\nCLASS DEFINITION :" << endl;

  int clnb = classNb();

  for(int i=0; i<clnb; i++) {

    o << "class " << i << ": scale=" << scale(i)
    << ", symbol= " << symbol(i) << endl;

    for (int j=0; j<clnb; j++) {

      if (less(i,j).Max()!=0 || plus(i,j).Max()!= 0) {
        o << "\t" << symbol(i) << "->" << symbol(j) << endl;
        if (less(i,j).Max()!=0) {
          o << "\t< : (" << less(i,j).Min() << "," << less(i,j).Max() << ")" << endl;
        }
        if (plus(i,j).Max()!= 0) {
          o << "\t+ : (" << plus(i,j).Min() << "," << plus(i,j).Max() << ")" << endl;
        }
      }
    }

  }

  o << endl;

  o << "FEATURE DEFINITION :" << endl;

  int fnb = fNb();

  for(int i2=0; i2<fnb; i2++) {

    o << "Feature " << i2 << " : " << fName(i2) << ", " << fType(i2)
    << ", " << fSmbTable(i2) << endl;

  }

  o << endl;

  return o;

}
