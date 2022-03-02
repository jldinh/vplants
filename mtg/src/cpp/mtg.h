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
 *       $Id: mtg.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef MTG_HEADER
#define MTG_HEADER

#include "tool/rw_vector.h"
#include "tool/rw_stack.h"
#include "tool/rw_queue.h"
#include "tool/rw_cstring.h"


#include "aml/defs.h"
#include "aml/date.h"
#include "utils.h"
#include "vertex.h"
#include "header.h"
#include "fset.h"

#include <vector>

typedef RWTValOrderedVector<Vertex>     VertexArray;
typedef RWTValOrderedVector<Edge>       EdgeArray;
typedef RWTValDlistIterator<VId>        VIdListIter;
typedef RWTValDlistIterator<EId>        EIdListIter;
typedef RWTValDlistIterator<FSetId>     FSetIdListIter;

typedef RWTValDlist<int>                IntList;
typedef RWTValDlistIterator<int>        IntListIter;


// Pile d'entiers implementee comme un vecteur
typedef RWTStack<VId, RWTValOrderedVector<VId> > VIdStack;
typedef RWTQueue<VId, RWTValOrderedVector<VId> > VIdQueue;

typedef RWTStack< RWCString, RWTValOrderedVector<RWCString> > StringStack;

typedef std::vector<VId> VtxList; // STL equivalent for VIdList

#ifndef SYSTEM_IS__IRIX
#include "plantgl/pgl_scene.h"
#else
typedef IntList ScenePtr; // Shapelist is not used on IRIX. This dummy type is only used for compiling
#endif

class MTG {

  friend std::ostream& operator<<(std::ostream&, const MTG&);
  friend int yyparse();

  friend class MTGVertexIter;
  friend class MTGEdgeIter;
  friend class MTGArtist;

  RWCString _filename;  // fichier dans lequel ce MTG est defini

  MTGHeader* _header;   // tous les mtg d'un fichier (imbriques) ont le meme header

  int _error_nb;                // is set by the constructor to qualify an MTG as Valid or not

  VertexArray _v;       // Tableau des vertex du GTM
  EdgeArray _e;         // Tableau des edge du GTM
  FSetArray _fs;        // _fs[i] (de type Feature*) pointe sur le debut de l'ensemble
                        // attributs associe a _v[i]. _fs[i][j] renvoie la jieme feature
                        // de l'ensemble de features d'indice i.
  int _estimated_size;

  int binaryStoreSize() const;

  const MTGHeader* header() const {return _header;}

  // conversion of a vertex
  // the vertex id or the pointer have to be valid

  Vertex& vertex(VId vtx) const {assert(existsVertex(vtx)); return *(((Vertex*)_v.data())+vtx);}
  VId vid(const Vertex& vtx) const {return vtx.vid();}
  VId vid(const Vertex* pvtx) const {assert(pvtx); return pvtx->vid();}

  Edge& edge(EId e) const {assert(existsEdge(e)); return *(((Edge*)_e.data())+e);}
  EId eid(const Edge& e) const {return e.eid();}
  EId eid(const Edge* pe) const {assert(pe); return pe->eid();}

  // Edges of a given vertex

  // id has to be an existing vertex.
  // return UNDEF if no edges is found.
  EId topoMother(VId id, EType filter) const;

  // return the emptylist if no edge is found. Never return the NULL pointer.
  // the list returned has to be deleted afterwards.
  EIdList* topoDaughters(VId id, EType filter) const;

  // To be used exclusively in reading form-B
  void addCompoSon(VId complex, VId son);
  void removeCompoSon(VId complex, VId son);
  void removeEdge(VId id1, VId id2);

  // cut the connexion (LESS or PLUS type) between two vertex and
  // recursively through their descendance
  // the vertex id1 and id2 must be linked by a topological edge
  // otherwise nothing is done.
  // vertex id1 and id2 must be valid vertex of the same scale >= 1
  void cutVertexConnection(VId id1, VId id2);

  AmlBoolean checkAlias(VId vtx, const Feature* fset, int findex) const;
  AmlBoolean checkDate(VId vtx, const Feature* fset, int findex) const;
  AmlBoolean checkState(VId vtx, const Feature* fset, int findex) const;
  AmlBoolean checkNbEl(VId vtx, const Feature* fset, int findex) const;
  AmlBoolean checkDiam(VId vtx, const Feature* fset, int findex) const;
  AmlBoolean checkLength(VId vtx, const Feature* fset, int findex) const;

  // Accessing FSetIds

  AmlBoolean existsFSetId(FSetId f) const {if (f < _fs.length() && f >=0) return TRUE; else return FALSE;}

  // may return a null pointer if the entity has no features
  const FSetIdList* fsetIds(VId id) const {assert(existsVertex(id));
                                           return vertex(id).fsetIds();}

  FSetId firstFSet(VId) const; // first and last wrt Date
  FSetId lastFSet(VId) const;

  Feature& storeFeature(FSetId fs, int fi) {assert(existsFSetId(fs));
                                             assert(fi<=featureNb()&&fi>=0);
                                             return _fs(fs, fi);}
  Feature& storeFeature(FSetId fs, FFlag ff) {assert(existsFSetId(fs));
                                               return _fs(fs, fIndex(ff));}

  const Feature& feature(FSetId fs, int fi) const {assert(existsFSetId(fs));
                                             assert(fi<=featureNb()&&fi>=0);
                                             return _fs(fs, fi);}
  const Feature& feature(FSetId fs, FFlag ff) const {assert(existsFSetId(fs));
                                               return _fs(fs, fIndex(ff));}

  Date date(FSetId) const; // revoie la date de ce fset, DATEERR si pas de date definie

  FSetId fsetAt(VId, Date = (unsigned long)LUNDEF) const;
  FSetId fsetBefore(VId, Date) const;
  FSetId fsetAfter(VId, Date) const;

  // Dans les fonctions suivantes, si on souhaite recuperer un FSetId contenant
  // une valeur differente de VOIDVAL, il faut mettre le dernier argument a NULL
  // (valeur par defaut)

  FSetId fsetAtWithValueEQ(VId, Date, FIndex, const Feature* val = NULL) const;
  FSetId fsetBeforeWithValueEQ(VId, Date, FIndex, const Feature* val = NULL) const;
  FSetId fsetAfterWithValueEQ(VId, Date, FIndex, const Feature* val = NULL) const;

  // filename, cldef and fsetdef have to be non-NULL pointers
  void initMTG(int scale_nb,
               ClassDef* cldef,
               FSetDef* fsetdef,
               int line_nb);

public:

  ///@name Constructors
  //@{

  MTG(const char*, int vtxsize = 0, std::ostream& errstream = std::cerr, int maxerrornb = FILEMAXERROR, int resize = 1);          // parse a file and build the corresponding MTG
  MTG(char* filename, int nodenb, int seed);    // generate a random MTG with a given nodenb

  ~MTG();

  //@}

public:
  ///@name General properties
  //@{

  const char* filename() const {return _filename.data();}

  /// allocated size of _v, _e and _fs in bytes (_v.capacity() does not exist in RW)
  int capacity() const {return _v.entries();}
  int isValid() const {return !_error_nb;}

  int vertexNb() const {return _v.entries();}
  int scaleNb() const {return _header->scaleNb();}
  int classNb() const {return _header->classNb();}

  // Arguments can be not valid

  AmlBoolean existsVertex(VId v) const {if (v < (VId)_v.entries() && v >=0) return TRUE; else return FALSE;}
  AmlBoolean existsEdge(EId e) const {if (e < (VId)_e.entries() && e>=0) return TRUE; else return FALSE;}

  /** relative name of id in the context of id0.
   the arguments need be valid and return a NULL pointer in case of nonsense
   if id = mtgRoot;
  */
  RWCString* relativeName(VId id0, VId id) const;

  //@}

public:

  ///@name Header properties
  //@{

  AmlBoolean isValidClass(VClass vclass) const {return _header->isValidClass(vclass);}
  AmlBoolean isValidClass(char cc) const {return _header->isValidClass(cc);}
  AmlBoolean isValidScale(int scale) const {return scale >=0 || scale<= scaleNb();}
  AmlBoolean isValidIndex(int index) const {return index>=0;}
  AmlBoolean isValidTopoEdgeType(EType edgetype) const {return *(edgetype & ANYTOPO);} //
  AmlBoolean existsFType(FType type) const {return _header->existsFType(type);}
  AmlBoolean existsFName(const String& name) const {return _header->existsFName(name);}
  AmlBoolean existsFIndex(int index) const {return _header->existsFIndex(index);}
  AmlBoolean isDefFeature(FFlag f) const {return _header->isFFlagSet(f);}

  /// finds the feature index of the first feature being of type type. UNDEF if not found.
  int fTypeIndex(FType type) const {return _header->fTypeIndex(type);}
  /// finds the feature index of the feature with name name. UNDEF if not found.
  int fNameIndex(const String& name) const {return _header->fNameIndex(name);}

  int featureNb() const {return _header->fNb();}
  int fIndex(FFlag f) const {if (isDefFeature(f)) return _header->fIndex(f); else return UNDEF;}
  FFlag fFlag(int index) const {return _header->fFlag(index);}
  String fname(int index) const {return _header->fName(index);}
  FType fType(int index) {return _header->fType(index);}
  void* fSmbTable(int index) const {return _header->fSmbTable(index);}

  // Arguments have to be valid
  int classScale(VClass c) const {assert(isValidClass(c)); return _header->scale(c);}
  int classVdecomp(VClass c) const {assert(isValidClass(c)); return _header->vdecomp(c);}
  int vdef(VClass c) const {assert(isValidClass(c)); return _header->vdef(c);}
  char classSymbol(VClass c) const {assert(isValidClass(c)); return _header->symbol(c);}
  VClass classId(char c) const {assert(isValidClass(c)); return _header->vClass(c);}

  // Arguments need not be valid
  char edgeSymbol(EType e) const;

  //@}

public:

  ///@name Vertices
  //@{

  // General root of the Graph wrt every edge types
  VId mtgRoot() const {if (_v.entries() == 0) return UNDEF; else return 0;}

  // Argument need not be valid
  AmlBoolean isMTGRoot(VId id) const {return id == mtgRoot();}

  // Arguments need be valid
  VClass vclass(VId id) const {assert(existsVertex(id)); return vertex(id).vclass();}
  char symbol(VId id) const {assert(existsVertex(id)); return classSymbol(vclass(id));}
  int vindex(VId id) const {assert(existsVertex(id)); return vertex(id).index();}
  int vscale(VId id) const {assert(existsVertex(id)); return classScale(vertex(id).vclass());}
  int vdecomp(VId id) const {assert(existsVertex(id)); return classVdecomp(vclass(id));}

  VId vprefix(VId id) const;

  VId findVertexByName_A(char c, int index, VId loc, EType etype);
  VId findVertexByName_B(char c, int index, VId loc, EType etype);

  //@}

public:

  ///@name Edges
  //@{

  EId topoEdge(VId v1, VId v2) const; // returns UNDEF if no edge
  EType edgeType(VId v1, VId v2) const; // returns NONE if no edge

  // Arguments need not be valid
  AmlBoolean scaleEdge(VId v1, VId v2) const;

  const char* edgeLabel(EId) const;

  //@}

public:

  ///@name Vertex attributes
  //@{

  // --------- Les attributs d'un vertex ----------

  // All these functions only applies to defined vertex.

  AmlBoolean hasFeatures(VId id) const {return fsetIds(id) != NULL;}

  FType fType(int index) const {assert(index<=featureNb()&&index>=0);
                                return _header->fType(index);}
  FType fType(FFlag flag) const {return _header->fType(fIndex(flag));}

  const Feature* feature(VId v, FIndex i, Date t) const;

  Date firstDate(VId id) const;
  Date lastDate(VId id) const;

  IntList* dateSample(VId id);

  // argument need not be defined
  AmlBoolean isDefAtDate(VId, Date) const; // is the first observation date LESS THAN date ?

  int cumulatedFValueOnComponentsAt(VId, Date, FIndex);

  AmlBoolean checkFeature(VId vtx, const Feature* fset, int findex) const;

  //@}


public:

  ///@name Topological/Scale moves
  //@{

  /** Arguments need be valid, return UNDEF or empty list never NULL-pointer.
      the list returned must be deleted after use
  */
  VId topoFather(VId id, EType filter) const;
  VId localTopoFather(VId id, EType filter) const;

  /// complexes.
  VId compoFather(VId id) const;
  VId compoFather(VId id, int scale) const;

  // find the vertex which consists in the most precise vprefix (finest scale)
  // of vertex x on its topofather. return UNDEF if there exists no topoFather
  // or no such vprefix on it

  VId location(VId x) const;

  // these functions always return a valid list (which may be empty but never NULL)
  VIdList* topoSons(VId id, EType filter) const;
  VIdList* localTopoSons(VId id, EType filter) const;
  VIdList* topoDescendants(VId id, EType filter) const;
  VIdList* topoAncestors(VId id, EType filter) const;
  VIdList* localTopoDescendants(VId id, EType filter) const;
  VIdList* localTopoAncestors(VId id, EType filter) const;
  VIdList* topoSonsWithClass(VId id, VClass cl, EType filter) const;
  VIdList* compoSons(VId id) const;
  VIdList* compoSons(VId id, int scale) const;
  VIdList* fathers(VId, EType filter) const;
  VIdList* sons(VId, EType filter) const;

  VIdList* topoExtremities(VId id, EType filter) const;
  VIdList* localTopoExtremities(VId id, EType filter) const;

  // find the complex ascendant of vertex x at scale.

  VId findCompoAncestorAtScale(VId x, int scale) const;

  //@}


public:

  ///@name Paths
  //@{

  VIdList* path(VId v1, VId v2) const;

  // Arguments need not be valid
  AmlBoolean isCompoAncestorOf(VId father, VId x) const; // (notamment vrai si father == x)
  AmlBoolean isCompoDescendantOf(VId son, VId x) const; // (notamment vrai si father == x)
  AmlBoolean isTopoAncestorOf(VId father, VId x, EType filter) const; // (notamment vrai si father == x)
  AmlBoolean isTopoDescendantOf(VId son, VId x, EType filter) const; // (notamment vrai si son == x)

  // Arguments need not be valid
  AmlBoolean isGlobalTopoRoot(VId id) const;
  AmlBoolean isLocalTopoRoot(VId id) const;

  // positive only distance : give the number of CONTIGUOUS EDGES OF TYPE FILTER between v1 and v2
  // pathLength(v1,v2,filter)>0       <=> v2 topodescendant of v1 (including v1 itself) on path of type filter
  // pathLength(v1,v2,filter) = 0     <=> v1 = v2
  // pathLength(v1,v2,filter) = UNDEF <=> v2 is neither a topodescendant in any path of type filter of v1 nor v1 itself
  // filter must be a topo type only

  int pathLength(VId v1, VId v2, EType filter) const;

  int algPathLength(VId v1, VId v2, EType filter) const; // algebric distance: like dist but <0 if v2 ancestor of v1


  // pathEdgeNb: give the number of EDGES OF TYPE FILTER between v1 and v2
  // !!! not necessarily contiguous !!!
  // order(v1,v2)>0 <=> v2 topodescendant according filter of v1 (including v1 itself)
  // filter must be a topo type only

  int pathEdgeNb(VId v1, VId v2, EType filter) const;

  int algPathEdgeNb(VId v1, VId v2, EType filter) const; // algebric: like pathEdgeNb but <0 if v2 ancestor of v1

  //@}

public:

  ///@name Axes and Bits of axes
  //@{

  // ------------- EXPLORATION DU GTM --------------

  // All these functions must have a valid arguments !
  // they return UNDEF in case of a failure.

  // LESS-SEQUENCES :
  // --------------
  //
  // all these functions work only if all the entities at scale scale(x)
  // have a class X which defines max(X,Y<)<=1 for all Y. This enables to define
  // less-sequences as linearly <-connected sets of entities. Local less-sequences
  // refer to partial less-sequences whose entities have the same complex-father,
  // whereas global less-sequence refer to the botanic entities called axis.

  VIdList* findLessSequence(VId firstv) const;
  VIdList* findLocalLessSequence(VId firstv) const;

  // given a vertex vtx, they find the first (last) vertex of a sequence of vertex
  // linked by a < edge and belonging to the same compoFather(vtx) (cf the word local).

  VId findFirstVertexInLocalLessSequence(VId firstv) const;
  VId findLastVertexInLocalLessSequence(VId firstv) const;

  // find a vertex with a given label in a linear less-sequence of vertex
  // starting at vertex firstv

  VId findLabelInLocalLessSequence(VId firstv, VClass csymb, int index) const;

  // this function only applies if the class X of loc is such that max(X,Y,+) <= 1 for all Y.
  // find a vertex with a given label in a linear less-sequence of vertex
  // starting at vertex firstv. the less-sequence is specified by a vprefix
  // on a carrying ('+' link) vertex

  VId findLabelInCarriedLocalLessSequenceAtLoc(VId loc, VClass csymb, int index) const;

  // find a vertex Xi0 in a linear less-sequence of vertex Xi such that
  // - index(Xi0-1) < index if Xi0-1 exists
  // - index(Xi0) >= index if Xi0 exists (else return UNDEF)
  //
  // i.e. the given label  has to be inserted just BEFORE the vertex
  // returned. If UNDEF is returned, the vertex has to be inserted
  // at the end of the axis.

  VId findInsertionPointInLocalLessSequence(VId firstv, VClass c, int index) const;
  VId findInsertionPointInGlobalLessSequence(VId firstv, VClass c, int index) const;
  VId findInsertionPointInCarriedLocalLessSequenceAtLoc(VId loc, VClass c, int index) const;
  VId findInsertionPointInCarriedGlobalLessSequenceAtLoc(VId loc, VClass c, int index) const;

  // find the last vertex of the carried LESS-SEQUENCE whose loc is loc
  // and whose scale is scl
  VId findLastVertexInCarriedLocalLessSequenceAtLoc(VId loc, int scale) const;

  // find the last vertex of a Local LessSequence at a given scale of a complex vertex
  // for both these functions the father vertex has to be of LINEAR type of class

  VId findFirstComponent(VId father) const;
  VId findLastComponent(VId father) const;
  VId findFirstComponentAtScale(VId father, int scl) const;
  VId findLastComponentAtScale(VId father, int scl) const;

  // This function applies for any kind of LINEAR entity
  // if there is no component the function returns vtx itself.
  // it returns UNDEF if this finest element cannot be computed
  // (entity not linear, etc.)

  VId findLastFinestElement(VId vtx) const;

  // find the vertex component which is a successor of the ancestor
  // X of loc at the lowest possible scale. loc cannot be a '/'-vprefix
  // The returned value z is such that scale(loc) <= scale(z).

  VId findCoarsestSuccessorAtLoc(VId loc) const;
  //@}

public:

  ///@name Roots
  //@{

  // These functions work with no condition on classes
  //
  // Find the local root wrt the complex-father of startv of the topotree
  // at the same level as startv.

  VId findLocalTopoRoot(VId startv, EType etype) const;
  VId findGlobalTopoRoot(VId startv, EType etype) const;

  // These functions return in general a list of roots. This list
  // can be empty.

  VIdList* findLocalTopoRoots(VId complex) const;
  VIdList* findLocalTopoRootsAtScale(VId complex, int scale) const;
  VIdList* findGlobalTopoRootsAtScale(int scale) const;

  //@}


public:

  ///@name Modifying the MTG
  //@{


  // All these functions return a negative integer CHECKERROR on failure,
  // with possibly an error message
  // describing the kind of error that occurred and send to the
  // global error message list.

  VId addVertex(VClass vclass, int index);

  VId addVertexByName_A(char c, int index, VId loc, EType etype);
  VId addVertexByName_B(char c, int index, VId loc, EType etype);

  int addTopoEdge(VId x, VId y, EType topoedge); // must be called first
  int addCompoEdge(VId complex, VId x);          // must be called second
  int setVPrefix(VId x, VId vprefix);          // must be called third

  int addFSet(VId, Feature*);

  void changeTopoEdgeSon(VId y,VId z,VId x);// change a topo edge (y,z) in an edge (y,x)

  // call this member once a vertex has been fully inserted in the MTG
  AmlBoolean checkVertexInsertion(VId x) const;

  //@}


public:

  ///@name Printing
  //@{

  std::ostream& printTopoSons(std::ostream&, VId) const;
  std::ostream& printCompoSons(std::ostream&, VId) const;
  std::ostream& printTopoFather(std::ostream& o, VId i) const;
  std::ostream& printCompoFather(std::ostream& o, VId i) const;

  std::ostream& printVertex(std::ostream&) const;
  std::ostream& printEdge(std::ostream&) const;
  std::ostream& printStat(std::ostream&) const;

  std::ostream& displayOneLine(std::ostream& o) const;

  std::ostream& print(std::ostream&) const;
  std::ostream& printAll(std::ostream&) const;

  //@}

public:

  ///@name Geometry
  //@{

  PGL::ScenePtr shape(int scale, VId root = -1) const;
  //  ShapeList shape(int scale, VId root = -1) const;

  //@}

public:

  ///@name Standardized Interface Methods
  //@{

  // All these methods have a standard interface: they return an error value on
  // failure ('\0' for a char, -1 for an int, a vertex, or an enum, NULL for a list,
  // -1 for a union (e.g. feature).

  VId si_mtgRoot() const;
  VId si_complex(VId v, int s = -1) const ; // s = scale
  VId si_father(VId v, int s = -1) const ;
  VtxList* si_sons(VId v, int s =-1, EType edgetype = ANYTOPO) const ;
  VtxList* si_ancestors(VId v) const ;
  VtxList* si_descendants(VId v, int s =-1) const ;
  VtxList* si_extremities(VId v, int s =-1) const ;
  VtxList* si_components(VId v, int s =-1) const ;
  VtxList* si_componentRoots(VId v, int s =-1) const ;
  VtxList* si_path(VId v1, VId v2) const ;
  VtxList* si_axis(VId v1, int s = -1) const ;
  char si_class(VId v) const ;
  int si_index(VId v) const ;
  int si_scale(VId v) const ;
  char si_edgeType(VId v1, VId v2) const;
  const Feature* si_feature(VId v, FIndex i) const ;
  const Feature* si_feature(VId v, std::string fname) const ;
  const FType si_fType(FIndex i) const ;
  const bool si_isDefined(Feature* f) const ;
  int si_order(VId v) const ;
  int si_rank(VId v) const ;
  VId si_defineSubTreeRoot(VId vertex, int scale) const;

  //@}

};

std::ostream& operator<<(std::ostream& o, const MTG& obj);


// Definition de tous les iterateurs sur un MTG
// on peut imaginer:
//
// iterer sur les peres topologiques a partir d'un vertex donne
// iterer sur les peres complexes a partir d'un vertex donne
// iterer sur le contexte topologique a partir d'un vertex donne
// parcourir le mtg a un niveau donne en profondeur d'abord a partir d'un vertex de ce niveau
// idem mais parcours sur les composants d'un vertex
// idem mais parcours sur les contextes topologiques
// parcours en largeur d'abord limite par un parametre (rang, ordre, ...)
//
// pour tous ces iterateurs
//
// - donner la possibilite de parametrer la recherche par des bornes
// - donner la possibilite d'executer une fonction de selection booleenne
// qui permet a l'iterateur de filtrer les elements sur lesquels il itere


// prototype d'une fonction faisant un test booleen sur une vertex donne.

typedef AmlBoolean VertexTester(MTG*, VId, void*);

typedef VIdList* (MTG::* SonListFunc)(VId, EType) const;


class MTGVertexIter {

  MTG* _g;

  VId _cv; // current vertex

public:

  MTGVertexIter(MTG* g) {assert(g); _g = g; _cv = UNDEF;}
   ~MTGVertexIter() {}

  MTG* container() const {return _g;}

   AmlBoolean operator++() {return (++_cv < (VId)_g->_v.entries());}
   AmlBoolean operator+=(int n);
   AmlBoolean operator()() {return (++_cv < (VId)_g->_v.entries());}
   AmlBoolean findNext(VertexTester _fun, void* _pdata) {
    // Note: Il semble que la syntaxe if ((*fun)(_g, _cv, pdata)) ... soit egalement
    // permise: c'est teste dans test1
    while((*this)()) if ((*_fun)(_g,_cv, _pdata)) return TRUE;
    return FALSE;
   }

  void reset() {_cv = UNDEF;}

  VId key() const {return _cv;}

};


class MTGEdgeIter {

  MTG* _g;

  EId _ce; // current edge

public:

  MTGEdgeIter(MTG* g) {assert(g);_g = g; _ce = UNDEF;}
   ~MTGEdgeIter() {}

  MTG* container() const {return _g;}

   AmlBoolean operator++() {return (++_ce < (VId)_g->_e.entries());}
   AmlBoolean operator+=(int n);
   AmlBoolean operator()() {return (++_ce < (VId)_g->_e.entries());}
   AmlBoolean findNext(VertexTester fun , void* pdata){
        while((*this)()) if ((*fun)(_g, _ce, pdata)) return TRUE;
        return FALSE;
   }


  void reset() {_ce = UNDEF;}

  EId key() const {return _ce;}

};


class MTGDepthFirstIter {

  MTG* _g;
  EType _filter; // Type d'edge topo considere
  VIdStack _s;

  SonListFunc _pmf;

  VId _cv;

  void push(VIdList*);

public:

  MTGDepthFirstIter(MTG* g, VId vstart, SonListFunc, EType type);
   ~MTGDepthFirstIter() {}

  MTG* container() const {return _g;}

   AmlBoolean operator++() {return (*this)();}
   AmlBoolean operator+=(int n);
   AmlBoolean operator()();
   AmlBoolean findNext(VertexTester fun , void* pdata) {
          while((*this)()) if ((*fun)(_g, _cv, pdata)) return TRUE;
          return FALSE;
        }

  void reset();

  VId key() const {return _cv;}

};


class MTGPostFixIter {

  MTG* _g;
  EType _filter; // Type d'edge topo considere
  VIdStack _s;
  VIdStack _used;

  SonListFunc _pmf;

  VId _cv;

  void push(VIdList*);
  void mark(VId);
  AmlBoolean isMarked(VId);

public:

  MTGPostFixIter(MTG* g, VId vstart, SonListFunc, EType type);
   ~MTGPostFixIter() {}

  MTG* container() const {return _g;}

   AmlBoolean operator++() {return (*this)();}
   AmlBoolean operator+=(int n);
   AmlBoolean operator()();
   AmlBoolean findNext(VertexTester fun , void* pdata){
          while((*this)()) if ((*fun)(_g,_cv, pdata)) return TRUE;
          return FALSE;
        }

  void reset();

  VId key() const {return _cv;}

};

/*

// L'instantiation de VIdQueue genere un WARNING

class MTGBreadthFirstIter {

  MTG* _g;
  EType _filter; // Type d'edge topo considere
  VIdQueue _q;   // Une queue pour une recherche en largeur d'abord

  SonListFunc _pmf;

  VId _cv;

  void push(VIdList*);

public:

  MTGBreadthFirstIter(MTG* g, VId vstart, SonListFunc, EType type);
  ~MTGBreadthFirstIter() {}

  MTG* container() const {return _g;}


  AmlBoolean operator++() {return (*this)();}
  AmlBoolean operator+=(int n);

  AmlBoolean operator()();
  AmlBoolean findNext(VertexTester, void*);

  void reset();

  VId key() const {return _cv;}

};

*/

#endif



