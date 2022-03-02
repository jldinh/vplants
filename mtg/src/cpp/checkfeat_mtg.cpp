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
 *       $Id: checkfeat_mtg.cpp 17611 2014-10-17 13:20:41Z pradal $
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



#include "tool/config.h"
#ifdef STL_EXTENSION
	#include <sstream>
#else
	#include <strstream>
#endif

#include <assert.h>

#include "tool/rw_tokenizer.h"

#include "error.h"
#include "errormsgs.h"
#include "parser_dec.h"
#include "mtg.h"

//static const char rcsid[] = "$Id: checkfeat_mtg.cpp 17611 2014-10-17 13:20:41Z pradal $";



AmlBoolean MTG::checkAlias(VId vtx, const Feature* fset, int findex) const {

  assert(existsVertex(vtx));


  return TRUE;

}

AmlBoolean MTG::checkDate(VId vtx, const Feature* fset, int findex) const {

  assert(existsVertex(vtx));

  RWTime t = fset[findex].i;
  RWTime first = firstDate(vtx);
  RWTime lastt = lastDate(vtx);

  /*
  cerr << "\n--- Checking date ---- " << vertex(vtx) << " at Date : " <<  printDate(t, DDMM) << endl;
  cerr << "---  Current features are : " << endl;
  const FSetIdList* fslist = vertex(vtx).fsetIds();
  if (!fslist) cerr << "\tNULL" << endl;
  else {
    int n = fslist->entries();
    for (int i = 0; i < n ; i++) {
      int id = (*fslist)[i];
      Date d =_fs(id, fIndex(DATE_F)).i;
      cerr << "\td= " << printDate(d, DDMM) << endl;
    }

  }
  */


  if (lastt != (unsigned long)LUNDEF) {

    /*
    cerr << "vtx  = " << vtx << endl;
    cerr << "firsd= " << printDate(first, DDMM) << endl;
    cerr << "lastd= " << printDate(lastt, DDMM) << endl;
    cerr << "currd= " << printDate(t, DDMM) << endl;
    */

    if (t == lastt) {
      yyerror(LOGICALERR);
      COMPLETEERRORITEM(ALREADYDEFINEDATSAMEDATE_0);
      return FALSE;
    }

    if (t < lastt) {
      yyerror(LOGICALERR);
      COMPLETEERRORITEM(DATENOTINCREASING_0);
      return FALSE;
    }
  }

  VId ant = vprefix(vtx);
  first = firstDate(ant);
  lastt = lastDate(ant);

  /*
  cerr << "loc = " << ant << endl;
  cerr << "firsd loc= " << printDate(first, DDMM) << endl;
  cerr << "lastd loc= " << printDate(lastt, DDMM) << endl;
  */

  if (t < first && first != (unsigned long)LUNDEF) { // for VId 0 root
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(DATEINVALIDLOC_0);
    return FALSE;
  }

  ant = topoFather(vtx, ANYTOPO);
  if (ant != UNDEF) {
    first = firstDate(ant);
    if (t < first && first != (unsigned long)LUNDEF) {
      yyerror(LOGICALERR);
      COMPLETEERRORITEM(DATEINVALIDTOPOFATHER_0);
      return FALSE;
    }
  }

  ant = compoFather(vtx);
  if (ant != UNDEF) {
    first = firstDate(ant);
    if (t < first && first != (unsigned long)LUNDEF) {
      yyerror(LOGICALERR);
      COMPLETEERRORITEM(DATEINVALIDCOMPLEX_0);
      return FALSE;
    }
  }


  if (isDefFeature(STATE_F)) {



  }


  if (isDefFeature(NBEL_F)) {

    ant = topoFather(vtx, LESS);

    if (ant != UNDEF) {

      FIndex i = fIndex(NBEL_F);

      FSetId fsbefore = fsetBeforeWithValueEQ(ant, fset[findex].i, i);
      FSetId fsafter = fsetAfterWithValueEQ(ant, fset[findex].i, i);

      if (fsbefore != UNDEF && fsafter != UNDEF) {

        if ( (feature(fsafter,i).i - feature(fsbefore,i).i) > 0 ) {
          yyerror(LOGICALERR);
          COMPLETEERRORITEM(DATEGRWNBELERR_0);
          return FALSE;
        }

      }

    }

  }

  if (isDefFeature(LENGTH_F)) {

    ant = topoFather(vtx, LESS);

    if (ant != UNDEF) {

      FIndex i = fIndex(LENGTH_F);

      FSetId fsbefore = fsetBeforeWithValueEQ(ant, fset[findex].i, i);
      FSetId fsafter = fsetAfterWithValueEQ(ant, fset[findex].i, i);

      if (fsbefore != UNDEF && fsafter != UNDEF) {

        if ( (feature(fsafter,i).i - feature(fsbefore,i).i) > 0 ) {
          yyerror(LOGICALERR);
          COMPLETEERRORITEM(DATEPRUNEDTFATHER_0);
          return FALSE;
        }

      }

    }

  }

  return TRUE;

}

AmlBoolean MTG::checkState(VId vtx, const Feature* fset, int findex) const {

  assert(existsVertex(vtx));

  if (isDefFeature(DATE_F)) {

  }

  return TRUE;

}

AmlBoolean MTG::checkNbEl(VId vtx, const Feature* fset, int findex) const {

  assert(existsVertex(vtx));

  if (isDefFeature(DATE_F)) {

  }
  if (isDefFeature(STATE_F)) {

  }

  return TRUE;
}

AmlBoolean MTG::checkDiam(VId vtx, const Feature* fset, int findex) const {

  assert(existsVertex(vtx));

  if (isDefFeature(DATE_F)) {

  }
  if (isDefFeature(STATE_F)) {

  }

  return TRUE;
}

AmlBoolean MTG::checkLength(VId vtx, const Feature* fset, int findex) const {

  assert(existsVertex(vtx));

  if (isDefFeature(DATE_F)) {

  }
  if (isDefFeature(STATE_F)) {

  }

  return TRUE;
}



AmlBoolean MTG::checkFeature(VId vtx, const Feature* fset, int findex) const {

  FFlag feat_nature = fFlag(findex);

  switch (feat_nature) {

  case ALIAS_F:
    return checkAlias(vtx, fset, findex);
  case DATE_F:
    return checkDate(vtx, fset, findex);
  case STATE_F:
    return checkState(vtx, fset, findex);
  case NBEL_F:
    return checkNbEl(vtx, fset, findex);
  case DIAM_F:
    return checkDiam(vtx, fset, findex);
  case LENGTH_F:
    return checkLength(vtx, fset, findex);
  default: // unsed, unknown or undef
    return TRUE;

 }


}

