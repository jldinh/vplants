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
 *       $Id: feat_mtg.cpp 17611 2014-10-17 13:20:41Z pradal $
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
#include "tool/rw_time.h"
//#include <rw/rwtime.h>

#include "error.h"
#include "mtg.h"

//static const char rcsid[] = "$Id: feat_mtg.cpp 17611 2014-10-17 13:20:41Z pradal $";


// --------- Les attributs d'un vertex ----------


// In an fsetlist fsets are ordered wrt increasing dates

FSetId MTG::firstFSet(VId v) const {

  assert(existsVertex(v));

  const FSetIdList* fslist = vertex(v).fsetIds();

  if (!fslist) return UNDEF;
  else return fslist->first();

}

FSetId MTG::lastFSet(VId v) const {

  assert(existsVertex(v));

  const FSetIdList* fslist = vertex(v).fsetIds();

  if (!fslist) return UNDEF;
  else return fslist->last();

}

Date MTG::date(FSetId id) const {

  assert(existsFSetId(id));

  if (isDefFeature(DATE_F)) {

    if (existsFSetId(id)) {

      return _fs(id, fIndex(DATE_F)).i;

    }
    else return (unsigned long)LUNDEF;

  }
  else return (unsigned long)LUNDEF;

}


Date MTG::firstDate(VId id) const {

  assert(existsVertex(id));

  if (isDefFeature(DATE_F)) {

    if (!hasFeatures(id)) return firstDate(vprefix(id));

    FSetId fsid = firstFSet(id);
    if (fsid != UNDEF) return (Date) this->feature(fsid, DATE_F).i;
    else return (unsigned long)LUNDEF;
  }
  else return (unsigned long)LUNDEF;

}

Date MTG::lastDate(VId id) const {

  assert(existsVertex(id));

  if (isDefFeature(DATE_F)) {

    if (!hasFeatures(id)) return (unsigned long)LUNDEF; // lastDate(vprefix(id));

    FSetId fsid = lastFSet(id);
    /*
    cerr << "last fset(" << id << ") = " << fsid;
    if (fsid != UNDEF) cerr << ", date = " << printDate(RWTime(feature(fsid, DATE_F).i), DDMM) << endl;
    else cerr << endl;
    */
    if (fsid != UNDEF) return (Date) feature(fsid, DATE_F).i;
    else return (unsigned long)LUNDEF;
  }
  else return (unsigned long)LUNDEF;

}

AmlBoolean MTG::isDefAtDate(VId id, Date date) const {

  if(existsVertex(id)) {

    if (!hasFeatures(id)) return isDefAtDate(vprefix(id), date);

    Date infdate = firstDate(id);

    if (infdate == (unsigned long)LUNDEF) return FALSE;

    if (date >= infdate) return TRUE;
    else return FALSE;

  }
  else return FALSE;

}


const Feature* MTG::feature(VId v, FIndex i, Date t) const {

  assert(i<=featureNb()&&i>=0);

  FSetId fs = fsetAt(v, t);

  if (existsFSetId(fs)) return &(this->feature(fs,i));

  else return NULL;

}


IntList* MTG::dateSample(VId id) {

  assert(existsVertex(id));

  IntList* list = new IntList;
  int d;

  const FSetIdList* fslist = vertex(id).fsetIds();
  if (fslist) {
    FSetIdListIter next(*(FSetIdList*)fslist);

    while(next()) {

      d = (int) feature(next.key(), DATE_F).i;

      list->insert(d);

    }
  }

  return list;

}


FSetId MTG::fsetAt(VId v, Date d) const {

  assert(existsVertex(v));

  if (hasFeatures(v)) {

    if (d == (unsigned long)LUNDEF) {

      if (!isDefFeature(DATE_F)) {

        const FSetIdList* fslist = vertex(v).fsetIds();

        if (fslist) {

          FSetIdListIter next(*(FSetIdList*)fslist);
          next();
          return next.key(); // return the first and only element

        }
        else return UNDEF;

      }
      else return UNDEF;

    }
    if (isDefFeature(DATE_F)) {

      const FSetIdList* fslist = vertex(v).fsetIds();

      if (fslist) {
        FSetIdListIter next(*(FSetIdList*)fslist);
        FSetId fsid;

        while(next()) {

          fsid = next.key();
          if(date(fsid) == d) return fsid;

        }
      }
      return UNDEF;

    }
    else return UNDEF;
  }
  else return UNDEF;
}


FSetId MTG::fsetBefore(VId v, Date d) const {

  assert(existsVertex(v));

  if (isDefFeature(DATE_F)) {

    const FSetIdList* fslist = vertex(v).fsetIds();

    if(fslist) {
      FSetIdListIter next(*(FSetIdList*)fslist);

      FSetId pfsid = UNDEF;
      FSetId fsid;

      while(next()) {

        fsid = next.key();
        if(date(fsid) >= d) return pfsid;
        pfsid = fsid;

      }
    }
    return UNDEF;

  }
  else return UNDEF;

}


FSetId MTG::fsetAfter(VId v, Date d) const {

  assert(existsVertex(v));

  if (isDefFeature(DATE_F)) {

    const FSetIdList* fslist = vertex(v).fsetIds();

    if (fslist) {
      FSetIdListIter next(*(FSetIdList*)fslist);
      FSetId fsid;

      while(next()) {

        fsid = next.key();
        if(date(fsid) > d) return fsid;

      }
    }
    return UNDEF;

  }
  else return UNDEF;

}

FSetId MTG::fsetAtWithValueEQ(VId v, Date d, FIndex fi, const Feature* val) const {

  assert(existsVertex(v));
  assert(fi<=featureNb()&&fi>=0);

  if (isDefFeature(DATE_F)) {

    const FSetIdList* fslist = vertex(v).fsetIds();

    if (fslist) {
      FSetIdListIter next(*(FSetIdList*)fslist);
      FSetId fsid;

      while(next()) {

        fsid = next.key();

        if (val == NULL) {
          if(date(fsid) == d && feature(fsid,fi).i != (unsigned long)LUNDEF) return fsid;
        }
        else {
          if(date(fsid) == d && feature(fsid,fi) == *(Feature*)val) return fsid;
        }
      }
    }
    return UNDEF;

  }
  else return UNDEF;

}

FSetId MTG::fsetBeforeWithValueEQ(VId v, Date d, FIndex fi, const Feature* val) const {

  assert(existsVertex(v));
  assert(fi<=featureNb()&&fi>=0);

  if (isDefFeature(DATE_F)) {

    const FSetIdList* fslist = vertex(v).fsetIds();

    if (fslist) {

      FSetIdListIter next(*(FSetIdList*)fslist);

      FSetId pfsid = UNDEF;
      FSetId fsid;

      while(next()) {

        fsid = next.key();

        if (val == NULL) {
          if(date(fsid) >= d && feature(fsid,fi).i != (unsigned long)LUNDEF) return pfsid;
        }
        else {
          if(date(fsid) >= d && feature(fsid,fi) == *(Feature*)val) return pfsid;
        }
        pfsid = fsid;

      }
    }
    return UNDEF;

  }
  else return UNDEF;

}

FSetId MTG::fsetAfterWithValueEQ(VId v, Date d, FIndex fi, const Feature* val) const {

  assert(existsVertex(v));
  assert(fi<=featureNb()&&fi>=0);

  if (isDefFeature(DATE_F)) {

    const FSetIdList* fslist = vertex(v).fsetIds();

    if (fslist) {
      FSetIdListIter next(*(FSetIdList*)fslist);
      FSetId fsid;

      while(next()) {

        fsid = next.key();

        if (val == NULL) {
          if(date(fsid) > d && feature(fsid,fi).i != (unsigned long)LUNDEF) return fsid;
        }
        else {
          if(date(fsid) > d && feature(fsid,fi) == *(Feature*)val) return fsid;
        }

      }
    }
    return UNDEF;

  }
  else return UNDEF;

}

int MTG::cumulatedFValueOnComponentsAt(VId v, Date d, FIndex fi) {

  assert(existsVertex(v));
  assert(fi<=featureNb()&&fi>=0);

  if (isDefFeature(DATE_F)) {

    VIdList* slist = compoSons(v);
    assert(slist);

    VIdListIter next(*(VIdList*)slist);

    unsigned long sum = 0;
    FSetId fset;
    VId vson;

    while(next()) {

      vson = next.key();

      fset = fsetBeforeWithValueEQ(vson, d, fi);
      if(VALID(fset)) sum += feature(fset, fi).i;

    }

    delete slist;

    return sum;

  }
  else return UNDEF;

}

