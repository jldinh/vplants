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
 *       $Id: edit_mtg.cpp 17611 2014-10-17 13:20:41Z pradal $
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
#include <strstream>
#include "tool/rw_time.h"
//#include <rw/rwtime.h>

#include "error.h"
#include "errormsgs.h"
#include "parser_dec.h"
#include "mtg.h"
//static const char rcsid[] = "$Id: edit_mtg.cpp 17611 2014-10-17 13:20:41Z pradal $";


#if 0
#define DEBUGFORMB
#endif

using namespace std;

// ------------- MODIFICATIONS DU GTM --------------

// Le probleme est ici d'integrer un nouveau vertex dans un graphe
// coherent et qui doit le rester.
//
// Les parametres de la fonction sont des parametres qui ont ete
// calcules par le parser. Rien ne prouve qu'ils verifient les contraintes
// d'un gtm.
//
// Cette insertion doit donc etre coherente topologiquement independamment de la
// date associee a l'observation de ce vertex.
//
//

// Un vertex a au minimum une classe et un index. En plus, on donne un numero
// de ligne du fichier de codage ou il est defini
// La fonction retourne l'identificateur du vertex si la creation a reussie
// ou bien un entier negatif traduisant une erreur (cf defs.h)

VId MTG::addVertex(VClass vclass, int index) {

  assert(isValidClass(vclass));
  assert(isValidIndex(index));

  // L'index est-il un index Valide ?

  if (ISFALSE(isValidIndex(index))) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(INDEXERR_0); // create the error message in the static globale variable ErrItem::curr_err_mess;
    return CHECKERROR;
  }

  // allocation d'un nouveau vertex

  VId id = _v.length(); // identificateur du nouvel element

  if (id == _estimated_size) {
    cerr << "Warning : Estimated MTG size (" << id << ") too small" << endl;
    cerr << "          => Try to use option VtxNumber to speed up the loading process." << endl;
  }


  Vertex v(id , vclass, index); // creation d'un Vertex

  _v.append(v); // on copie v dans le tableau _v

  return id; // si tout s'est bien passe on retourne l'identificateur

}

// to insert one entity in a GTM, one has to find
// - its topoFather if any
// - its compoFather if any
// - its vprefix
//
// One can remark that the order of the GTM entries has to respect
// this logical order of definition: a node can only be entered after
// its 2 fathers and its vprefix
//
// To do this, one has to consider one of 3 possible situations of vprefix:
//
// 1. scale(loc) = scale(x).
//      loc is the topoFather of x. x is not at the boundary of this complex entity.
//      etype can only be one of PLUS or LESS. Necessarily, x has the same
//      complexe father as loc.
//
// 2. scale(loc) < scale(x).
//      one has to find the compoAncestor z of loc such that scale(z) = scale(x).
//      Then z is the topoAncestor of x. etype can only be one of PLUS or LESS.
//      Necessarily, x has the same complexe father as z.
//
// In fact case 2 and 1 can be merged (1 is a special case of 2)
//
// 3. scale(loc) > scale(x)
//      Necessarily, scale(loc) = scale(x)-1. loc is the compoFather of x.
//      Let z = vprefix(loc), the topoAncestor of x is defined by
//      the compoAncestor of location of z whose scale is scale(x).
//

VId MTG::addVertexByName_A(char cc, int index, VId loc, EType etype) {

  assert(isValidIndex(index));
  assert(existsVertex(loc));

  VClass vcl = classId(cc);
  if (ISFALSE(isValidClass(vcl))) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(CLASSERR_0);
    return CHECKERROR;
  }

  int ret;

  int x = addVertex(vcl, index);
  if (!VALID(x)) return x;

  int xscale = vscale(x);
  int lscale = vscale(loc);

  if ((xscale == lscale + 1) && (classVdecomp(vclass(loc)) == NONE_D)) { // NE SERT A RIEN : REpris plus bas !!!

    if (ISFALSE(etype == SLASH)) {
      char stg[2];
      stg[0] = classSymbol(vclass(loc));
      stg[1] = '\0';
      yyerror(LOGICALERR);
      COMPLETEERRORITEM1(NODECOMP_1, stg);
      return CHECKERROR;
    }

    ret = addCompoEdge(loc,x);
    if (!VALID(ret)) return ret;

  }
  else {

    // Determine y = topoFather(x) and z=compoFather(x)

    VId y = UNDEF, z = UNDEF;
    EType edgetype;

    if (lscale >= xscale) {

      if (lscale == xscale) {

        y = loc;
        z = compoFather(loc);
        edgetype = etype;

      }
      else { // lscale > xscale

        y = findCompoAncestorAtScale(loc, xscale);
        z = compoFather(y);
        edgetype = etype;

      }

    }
    else { // lscale < xscale, i.e xscale is one scale deeper than lscale


      z = loc; // compofather is loc

      VId w = UNDEF;
      w = location(loc);

      if (w != UNDEF) y = findCompoAncestorAtScale(w, xscale);
      else y = UNDEF;

      w = topoFather(loc, ANYTOPO);

      if (w != UNDEF) edgetype = edgeType(w,loc);

    }


    if (y != UNDEF && classVdecomp(vclass(compoFather(y))) != NOTCONNECTED) {

      if (ISFALSE(isValidTopoEdgeType(edgetype))) {
        yyerror(LOGICALERR);
        COMPLETEERRORITEM(NOTTOPOREL_0);
        return CHECKERROR;
      }

      ret = addTopoEdge(y,x,edgetype);
      if (!VALID(ret)) return ret;
    }

    if (z != UNDEF) {
      ret = addCompoEdge(z,x);
      if (!VALID(ret)) return ret;
    }

  }

  ret = setVPrefix(x, loc);
  if (!VALID(ret)) return ret;

  ret = checkVertexInsertion(x);
  if (!VALID(ret)) return ret;

  return x;

}


// The following properties are imposed on the MTG to use B-FORM code:
//
// 1 - Every class of entity
//     must have a decomposition nature <-LINEAR or UNCONNECTED, which means that
//     an entity can only be decomposed into a sequence of vertex each of
//     which has at most one son and these entities must be linked
//     only by a <-edge. Or the entity is made of unconnected entities.
//
// 2 - Every class C at any scale must max(C,<) <= 1.
//
// 3 - Entities which are used as a vprefix of carried entities such as x in 'x+y'
//     must have a class C such that max(C,+) = 1.
//
// As a consequence, if the B-name of an entity is of the form x+y, then necessarily
// y is an entity whose complex father has a decomposition property UNCONNECTED.
//
// We assume these constraints are met to compute the corresponding vertex interpretations.

VId MTG::addVertexByName_B(char cc, int index, VId loc, EType etype) {

  assert(index >=0);
  assert(loc != UNDEF);
  assert(etype != PLUSPLUS && etype != LESSLESS);

/*
  cerr << "PLUS      = " << PLUS << endl;
  cerr << "LESS      = " << LESS << endl;
  cerr << "SLASH     = " << SLASH << endl;
  cerr << "PLUSPLUS  = " << PLUSPLUS << endl;
  cerr << "LESSLESS  = " << LESSLESS << endl;
  cerr << "NONE      = " << NONE << endl;
  cerr << "~NONE     = " << ~NONE << endl;
  cerr << "ANY       = " << ANY << endl;
  cerr << "ANYTOPO   = " << ANYTOPO << endl;

  cerr << "etype = " << etype << endl;
*/

  VClass vcl = classId(cc);

  if (ISFALSE(isValidClass(vcl))) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(CLASSERR_0);
    return CHECKERROR;
  }
  int ret;
  int x = loc;
  int y = addVertex(vcl, index);
  if (!VALID(y)) return y;

  int yscale = vscale(y);
  int lscale = vscale(x);

  if ((yscale == lscale + 1) && (classVdecomp(vclass(loc)) == NOTCONNECTED)) {

    ret = addCompoEdge(loc,y);
    if (!VALID(ret)) return ret;

    ret = setVPrefix(y, loc);
    if (!VALID(ret)) return ret;

  }
  else { // vertex which can be connected

    if (etype == SLASH) { // code name of the form x/y

      if (ISFALSE(yscale == lscale + 1)) {
        yyerror(LOGICALERR);
        COMPLETEERRORITEM(A4FAILED_0);
        return CHECKERROR;
      }

      // Finding the insertion points, lpred and lsucc, among the components of x

      int lpred = UNDEF; // local predecessor
      int lsucc = UNDEF; // local successor

      VIdList* list = findLocalTopoRoots(x);
      assert(list);

#ifdef DEBUGFORMB
      cerr << "local topo roots = ";
      VIdListIter nn(*list);
      while (nn()) cerr << nn.key() << " " << flush;
      cerr << endl;
#endif

      if (ISFALSE(list->entries() <= 1)) {
        delete list;
        yyerror(LOGICALERR);
        COMPLETEERRORITEM(A4FAILED_0);
        return CHECKERROR;
      }

      if (list->entries() == 1) {

        int first_x_component = list->first();

        delete list;

        lsucc = findInsertionPointInLocalLessSequence(first_x_component, vcl, index);

        if (lsucc != UNDEF) {

          lpred = localTopoFather(lsucc, ANYTOPO);

          if (lpred != UNDEF) {               // lsucc != UNDEF && lpred != UNDEF (case a.)

#ifdef DEBUGFORMB
            cerr << "CODE FORM-B: x/y : lpred = " << lpred << ", lsucc = " << lsucc << endl;
#endif
            cutVertexConnection(lpred, lsucc);

            ret = addTopoEdge(lpred,y,LESS);
            if (!VALID(ret)) return ret;
            ret = addTopoEdge(y,lsucc,LESS);
            if (!VALID(ret)) return ret;

            // if complexFather(y) == complexFather(lsucc) it might
            // be necessary to remove lsucc from the compoSonList of x
            // since this list must only contain localtoporoots of x
            removeCompoSon(x,lsucc);

            ret = addCompoEdge(x,y);
            if (!VALID(ret)) return ret;

            setVPrefix(y, vprefix(lsucc));
            setVPrefix(lsucc, y);

          }
          else {                              // lsucc != UNDEF && lpred == UNDEF (case b.)

#ifdef DEBUGFORMB
            cerr << "CODE FORM-B: x/y : lpred = " << lpred << ", lsucc = " << lsucc << endl;
#endif
            VId pred = topoFather(lsucc, ANYTOPO);

            if (pred != UNDEF) {

              EType et = edgeType(pred, lsucc);

              cutVertexConnection(pred, lsucc);

              ret = addTopoEdge(pred,y,et);
              if (!VALID(ret)) return ret;

            }

            ret = addTopoEdge(y,lsucc,LESS);
            if (!VALID(ret)) return ret;

            removeCompoSon(x,lsucc);

            ret = addCompoEdge(x,y);
            if (!VALID(ret)) return ret;

            ret = setVPrefix(y, x);
            if (!VALID(ret)) return ret;

            ret = setVPrefix(lsucc, y);
            if (!VALID(ret)) return ret;

          }

        }
        else { // lsucc == UNDEF

          lpred = findLastComponent(x);

          if (lpred != UNDEF) {               // lsucc == UNDEF && lpred != UNDEF (case c.)

#ifdef DEBUGFORMB
            cerr << "CODE FORM-B: x/y : lpred = " << lpred << ", lsucc = " << lsucc << endl;
#endif
            VIdList* succlist = topoSons(lpred, LESS);
            assert(succlist);
            // assert(succlist->entries() <= 1);

            if (succlist->entries() > 0) {

              VId succ = succlist->first();
              cutVertexConnection(lpred, succ);

              ret = addTopoEdge(y,succ,LESS);
              if (!VALID(ret)) return ret;

            }
            delete succlist;

            ret = addTopoEdge(lpred,y,LESS);
            if (!VALID(ret)) return ret;

            ret = addCompoEdge(x,y);
            if (!VALID(ret)) return ret;

            ret = setVPrefix(y, findLastFinestElement(lpred));
            if (!VALID(ret)) return ret;

            VId z = findCoarsestSuccessorAtLoc(lpred);

            if (z != UNDEF) {
              ret = setVPrefix(z, y);
              if (!VALID(ret)) return ret;
            }

          }
          else {          // lsucc == UNDEF && lpred == UNDEF : ERROR since list->entries() == 1

            assert(FALSE);

          }

        }
      }
      else {                                   // list->entries() == 0 : not yet any component in x
        // lsucc == UNDEF && lpred == UNDEF (case d.)

#ifdef DEBUGFORMB
        cerr << "CODE FORM-B: x/y : lpred = " << lpred << ", lsucc = " << lsucc << endl;
#endif
        delete list;

        // lpred and lsucc are correctly initialized to UNDEF
        VId z = UNDEF;

        // iterate through the list of compoAncestors(x);
        MTGDepthFirstIter next(this, x, &MTG::fathers, SLASH);

        while(next()) {

          VId father = next.key();
          VIdList* succlist = topoSons(father, LESS);
          assert(succlist);
          //assert(succlist->entries() <= 1);

          if (succlist->entries() == 0) {
            delete succlist;
            z = UNDEF;
            break;
          }
          else { // succlist->entries() >= 1
            VId succ_father = succlist->first();
            delete succlist;
            if (compoFather(succ_father) == compoFather(father)) {
              z = succ_father;
              break;
            }
            else z = UNDEF;

          }

        }

        if (z != UNDEF) {

          ret = setVPrefix(z, y);
          if (!VALID(ret)) return ret;

        }

        VId tfx = topoFather(x, ANYTOPO);

        if (tfx != UNDEF) {

          EType et = edgeType(tfx, x);

          if (et == PLUS) {

            VId exactloc = location(x);

            VId pred = findCompoAncestorAtScale(exactloc, yscale);

            if (pred != UNDEF) {
              ret = addTopoEdge(pred,y,PLUS);
              if (!VALID(ret)) return ret;
            }

          }
          else
          if (et == LESS) {

            VId pred = findLastComponent(tfx);

            if (pred != UNDEF) {
              ret = addTopoEdge(pred,y,LESS);
              if (!VALID(ret)) return ret;

            }
          }
          else {

            assert(FALSE);

          }
        }

        VIdList* succlist = topoSons(x, LESS);
        assert(succlist);
        // assert(succlist->entries() <= 1);

        if (succlist->entries() >= 1) {

          VId succ = findFirstComponent(succlist->first());
          if (succ != UNDEF) {
            ret = addTopoEdge(y,succ,LESS);
            if (!VALID(ret)) return ret;
          }

        }

        delete succlist;

        ret = addCompoEdge(x,y);
        if (!VALID(ret)) return ret;

        ret = setVPrefix(y, x);
        if (!VALID(ret)) return ret;

      }

    }
    else
    if (etype == PLUS) {   // code name of the form x+y

      // class(x) must be such that MAX(class(x),+) = 1
      // Let X be the complex ancestor of x at scale yscale
      // Let firsty be the first component (before the insertion of y)
      // of the Less-Sequence carried by X at scale yscale.
      // i.e. if firsty is not UNDEF,
      // one must have compoFather(X) == compoFather(firsty)

      if (ISFALSE(lscale >= yscale)) {
        yyerror(LOGICALERR);
        COMPLETEERRORITEM(A4FAILED_0);
        return CHECKERROR;
      }

      VId X = findCompoAncestorAtScale(x, yscale);
      assert(X != UNDEF);

      VId cfy = compoFather(X); // which is also the compofather(y)

      // Finding the insertion points, lpred and lsucc, among the carried entities of x

      // VId firsty = UNDEF;

      VId lpred = UNDEF; // local predecessor
      VId lsucc = UNDEF; // local successor

      lsucc = findInsertionPointInCarriedLocalLessSequenceAtLoc(x, vcl, index);

      if (lsucc != UNDEF) {

        // firsty = findFirstVertexInLocalLessSequence(lsucc);

        lpred = localTopoFather(lsucc, LESS);

        if (lpred != UNDEF) {             // lsucc != UNDEF && lpred != UNDEF

#ifdef DEBUGFORMB
          cerr << "CODE FORM-B: x+y : lpred = " << lpred << ", lsucc = " << lsucc << endl;
#endif
          EType et = edgeType(lpred, lsucc);

          cutVertexConnection(lpred, lsucc);

          ret = addTopoEdge(lpred,y,et);
          if (!VALID(ret)) return ret;

          ret = addTopoEdge(y,lsucc,LESS);
          if (!VALID(ret)) return ret;

          removeCompoSon(cfy,lsucc);

          ret = addCompoEdge(cfy,y);
          if (!VALID(ret)) return ret;

          ret = setVPrefix(y, vprefix(lsucc));
          if (!VALID(ret)) return ret;

          ret = setVPrefix(lsucc, y);
          if (!VALID(ret)) return ret;

        }
        else { // lpred == UNDEF          // lsucc != UNDEF && lpred == UNDEF

#ifdef DEBUGFORMB
          cerr << "CODE FORM-B: x+y : lpred = " << lpred << ", lsucc = " << lsucc << endl;
#endif
          // this means that y becomes the first element of the carried local
          // LESS sequence.

          cutVertexConnection(X, lsucc);

          ret = addTopoEdge(X, y, PLUS);
          if (!VALID(ret)) return ret;

          ret = addTopoEdge(y, lsucc, LESS);
          if (!VALID(ret)) return ret;

          removeCompoSon(cfy,lsucc);

          ret = addCompoEdge(cfy,y);
          if (!VALID(ret)) return ret;

          ret = setVPrefix(y, x);
          if (!VALID(ret)) return ret;

          ret = setVPrefix(lsucc, y);
          if (!VALID(ret)) return ret;


        }

      }
      else { // lsucc == UNDEF

        // defined uniquely since MAX(class(x),+) = 1
        lpred = findLastVertexInCarriedLocalLessSequenceAtLoc(x, yscale);

        if (lpred != UNDEF) {             // lsucc == UNDEF && lpred != UNDEF

#ifdef DEBUGFORMB
          cerr << "CODE FORM-B: x+y : lpred = " << lpred << ", lsucc = " << lsucc << endl;
#endif
          // y and X have the same complex father and this one has no connexion
          // with another vertex neither a toposon nor a topofather
          // therefore, lpred cannot be the vprefix of another vertex

          //

          ret = addTopoEdge(lpred, y, LESS);
          if (!VALID(ret)) return ret;

          ret = addCompoEdge(cfy,y);
          if (!VALID(ret)) return ret;

          ret = setVPrefix(y, findLastFinestElement(lpred));
          if (!VALID(ret)) return ret;

        }
        else { // lpred == UNDEF          // lsucc == UNDEF && lpred == UNDEF

#ifdef DEBUGFORMB
          cerr << "CODE FORM-B: x+y : lpred = " << lpred << ", lsucc = " << lsucc << endl;
#endif
          // which means that this vertex is the first one which is declared
          // being carried by X

          ret = addTopoEdge(X, y, PLUS);
          if (!VALID(ret)) return ret;

          ret = addCompoEdge(cfy,y);
          if (!VALID(ret)) return ret;

          ret = setVPrefix(y, x);
          if (!VALID(ret)) return ret;

        }


      }

    }
    else {

      assert(FALSE);
    }

  }

  ret = checkVertexInsertion(y);
  if (!VALID(ret)) return ret;

  return y;

}


// Topological edge from x to y

int MTG::addTopoEdge(VId x, VId y, EType topoedge) {

  assert(existsVertex(x) && existsVertex(y));
  assert(isValidTopoEdgeType(topoedge));


   // determination du niveau du vertex

   int xscale = classScale(vclass(x));
   int yscale = classScale(vclass(y));

   // Axiome A2 : x doit etre different de y

   if (ISFALSE(x!=y)) {
     yyerror(LOGICALERR);
     COMPLETEERRORITEM(A2FAILED_0);
     return CHECKERROR;
   }

  // Axiome A1 : classe a dte de x et classe a gauche de y

  int itvmax;

  if (topoedge == PLUS || topoedge == PLUSPLUS) {

    itvmax = _header->plus(vclass(x),vclass(y)).Max();

  }
  else
  if (topoedge == LESS || topoedge == LESSLESS) {
    itvmax = _header->less(vclass(x),vclass(y)).Max();
  }
  else {
    itvmax = 0;
  }

  VIdList* slist = topoSonsWithClass(x, vclass(y), topoedge);
  assert(slist);

  int son_nb = slist->entries();
  delete(slist);

  if (ISFALSE(son_nb < itvmax)) {

    // if (!(son_nb < itvmax))  cerr << "\tson_nb(" << x << ",edgetype=" << topoedge << ") = " << son_nb << " , itvmax = " << itvmax << endl;

    RWCString tmps(classSymbol(vclass(x)));

    char stg[20];     // index
    {

      ostrstream ost(stg,20);
      ost << vindex(x);
      ost << '\0';

      tmps += stg;
    }
    tmps += " --";
    tmps += RWCString(edgeSymbol(topoedge));
    tmps += "--> ";

    {

      ostrstream ost(stg,20);
      ost << classSymbol(vclass(y));
      ost << vindex(y);
      ost << '\0';

      tmps += stg;
    }

    yyerror(LOGICALERR);
    COMPLETEERRORITEM1(A1_1FAILED_1, tmps.data());
    return CHECKERROR;
  }

  // Axiome A3 : x doit avoir meme niveau que y a moins que l'un des deux ait un niveau 0

  int xs = vscale(x);
  int ys = vscale(y);

  if (ISFALSE(xs==ys)) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(A3FAILED_0);
    return CHECKERROR;
  }

  // Tests passed! => add the edge
  // - create the new edge e
  // - add e as a topo mother of x
  // - add e as a topo daugther of y

  EId id = _e.length(); // identificateur du nouvel element

  Edge e(id, topoedge, y, x); // creation d'une edge

  _e.append(e);

  vertex(x).addTopoDaughter(id);
  vertex(y).addTopoMother(id);

#ifdef DEBUGMTG
  if (topoedge == PLUS) cerr << "----> + edge added : (" << x << "," << y << ")" << endl;
  if (topoedge == LESS) cerr << "----> < edge added : (" << x << "," << y << ")" << endl;
  if (topoedge == PLUSPLUS) cerr << "----> ++ edge added : (" << x << "," << y << ")" << endl;
  if (topoedge == LESSLESS) cerr << "----> << edge added : (" << x << "," << y << ")" << endl;
#endif

  return id; // si tout s'est bien passe on retourne l'identificateur

}

// Compo Edge from complex to x

int MTG::addCompoEdge(VId complex, VId x) {

  assert(existsVertex(complex) && existsVertex(x));

  // Axiome A4 : x doit etre d'un niveau superieur a son complexe

  if (ISFALSE(vscale(x) == vscale(complex)+1)) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(A4FAILED_0);
    return CHECKERROR;
  }

  // Axiome A5 : x ne peut etre la racine du graphe r

  if (ISFALSE(!isMTGRoot(x))) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(A5FAILED_0);
    return CHECKERROR;
  }

  // Axiome A6 : x doit avoir un complexe unique

  VId f = compoFather(x);

  if (ISFALSE(f == UNDEF)) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(A6FAILED_0);
    return CHECKERROR;
  }

  // Update of the GTM:
  // - add complex as a compo father of x
  // - if x has no topo father, add x as a composon of father
  //
/*
  cerr << "**** vertex = " << x << endl;
  cerr << "**** compofather = " << complex << endl;;

  cerr << "0.  A la sortie de addCompoEdge le vertex " << x << " = " << &vertex(x) << x <<" vaut : " << endl;
  vertex(x).print(cerr);
*/
  vertex(x).addCompoFather(complex);

  VId tf = topoFather(x, ANYTOPO);
  if (tf == UNDEF || compoFather(tf) != complex) vertex(complex).addCompoSon(x);

  return TRUE;
}


int MTG::setVPrefix(VId x, VId vprefix) {

  assert(existsVertex(x));

  if (vprefix == UNDEF) {
    vertex(x).setVPrefix(vprefix);
    return TRUE;
  }

  // verification de la coherence de la localisation

  int xscale = vscale(x);
  int lscale = vscale(vprefix);

  if (xscale == 0) {

    assert(xscale != 0); // not yet implemented

  }
  else if (xscale == lscale+1) {

    // vprefix has then to be THE compoFather(x)

    if (ISFALSE(vprefix == compoFather(x))) {
      yyerror(LOGICALERR);
      COMPLETEERRORITEM(LOCERR2_0);
      return CHECKERROR;
    }

  }
  else if (xscale <= lscale) {

    /*
    // x must have a defined topoFather
    VId f = topoFather(x);

    if (ISFALSE(f != UNDEF)) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(LOCERR_0); // create the error message in the static globale variable ErrItem::curr_err_mess;
    return CHECKERROR;
    }

    // vprefix has to be a descendant of topofather(x)

    if (ISFALSE(isCompoDescendantOf(f, vprefix))) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(LOCERR_0); // create the error message in the static globale variable ErrItem::curr_err_mess;
    return CHECKERROR;
    }
    */
  }
  else { // error

    assert(FALSE);

  }

  //check(isCompoAncestorOf(x, vprefix), VERTEXIDERR);

  vertex(x).setVPrefix(vprefix);

  return TRUE;
}


// f is a pointer on a prepared fset

int MTG::addFSet(VId id, Feature* f) {

  assert(f);

  if (existsVertex(id)) {

    FSetId fsres = _fs.addFSet(f);

    assert(fsres != UNDEF);
    vertex(id).addFSetId(fsres);

    //Date date = (unsigned long)LUNDEF;
    //if (isDefFeature(DATE_F)) date = f[fIndex(DATE_F)].i;

    return TRUE;
  }
  else  return FALSE;
}

// change a topo edge (y,z) in an edge (y,x)

void MTG::changeTopoEdgeSon(VId y, VId z, VId x) {

  EId e =  topoEdge(y, z);

  edge(e).setSon(x);

  vertex(x).addTopoMother(e);

  // no need to modify vertex(y) since it has a correct topoDaugther edge


}

AmlBoolean MTG::checkVertexInsertion(VId x) const {

  // Axiome A7 : si x et y ont pour complexes respectifs X et Y, que X != Y
  //             alors il doit exister une relation de type topoedge entre X et Y.


  // 1. cas des fils de x

  VIdList* slist = topoSons(x, ANYTOPO);
  assert(slist);

  AmlBoolean flagerr = FALSE;

  VIdListIter nexts(*slist);

  VId xf = compoFather(x);

  if (xf != UNDEF) { // i.e. scale(x) == 1

    while(nexts()) {

      VId w = nexts.key();
      VId wf = compoFather(w);

      if (wf != xf) {
        EId fe = topoEdge(xf,wf);

        if (fe == UNDEF) {
          flagerr = TRUE;
          break;
        }
        else if (edge(fe).type() != edgeType(x,w)) {
          flagerr = TRUE;
          break;
        }
      }

    }

  }

  delete slist;

  if (ISFALSE(flagerr == FALSE)) {
    yyerror(LOGICALERR);
    COMPLETEERRORITEM(A7FAILED_0);
    return CHECKERROR;
  }

  // 2. cas du pere de x

  flagerr = FALSE;
  VId y = topoFather(x, ANYTOPO);

  if (y != UNDEF) {

    VId yf = compoFather(y);

    if (yf != xf) {

      EId fe = topoEdge(yf,xf);

      if (fe == UNDEF) {
        flagerr = TRUE;
      }
      else if (edge(fe).type() != edgeType(y,x)) {
        flagerr = TRUE;
      }

      if (ISFALSE(flagerr == FALSE)) {
        yyerror(LOGICALERR);
        COMPLETEERRORITEM(A7FAILED_0);
        return CHECKERROR;
      }
    }
  }
  else {

    // Axiome A8 : x a un unique antecedent topologique ou aucun si c'est la racine

    // check(FALSE, A8FAILED);
  }

  // Axiome sur les localisations:
  // si x a pour antecedent topologique y et que (xp = compofather(x)) != (yp = compofather(y))
  // alors scale(loc(xp)) >= scale(x)

  // .... A ECRIRE

  return TRUE;

}
