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
 *       $Id: linetree.cpp 17611 2014-10-17 13:20:41Z pradal $
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


// OLD INCLUDES
// #include "GEOM/geom.h"
// #include "GEOM/actn_x3dprinter.h"
// #include "GEOM/actn_vgstarprinter.h"
// #include "GEOM/actn_surfcomputer.h"
// #include "GEOM/actn_volcomputer.h"
// #include "GEOM/view_application.h"
// #include "GEOM/ligfile.h"
// #include "../Geomext/actn_fit.h"
#include "plantgl/gui/viewer/pglapplication.h"
#include "plantgl/pgl_algo.h"
#include "plantgl/pgl_transformation.h"
#include "plantgl/scenegraph/core/smbtable.h"
#include "plantgl/algo/codec/x3dprinter.h"

#include "quotientgeometrycomputer.h"


#include "aml/ammodel.h"
#include "aml/array.h"
#include "aml/list.h"

#include "plantframe.h"
#include "dresser.h"
#include "dressingdata.h"
#include "dressingfile.h"

#include "linetree.h"

#include <stdlib.h>


#include "sam_msg.h"

#include "tool/dirnames.h"
#include "tool/util_string.h"
#include "tool/bfstream.h"

VPTOOLS_USING_NAMESPACE
TOOLS_USING(Vector3)
TOOLS_USING(cross)

using namespace std;

//#include "aml/kernel_funs.h"
#include "aml/kernel_err.h"

#define  ERR_MSG_ARRAY          mtg_err_msgs_aml
#define  MODULE_NAME            "MTG"
extern const char *mtg_err_msgs_aml[];

static const char* protection = "!&@V3@aFFv5</p*kRE=fCUSB9-;/Q[RS9@nq=9PL22^RE[%<pTIsMvS6mUoL8?RJmQWrM%a.Sj@rl8cO";

static char* VIEWER_NAME = "3D viewer";

//static ViewerApplication* p_appli = NULL; // there must be only one application object in QT.
#ifdef __GNUC__
#include <time.h>
#endif

/* ----------------------------------------------------------------------- */


LineTree::LineTree(const char* file_name,
                   const PlantFrame* plantframe,
                   Dresser* dresser,
                   VirtualElements* leaves,
                   VirtualElements* fruits,
                   VirtualElements* flowers):
  _pf(plantframe),
  _dr(dresser),
  _default_mat(new Material("Default_Brown",Color3((uchar)22,(uchar)18,(uchar)8),
                            4.7,
                            // Color3((uchar)42,(uchar)42,(uchar)17),
							Color3((uchar)0,(uchar)0,(uchar)0),
                            Material::DEFAULT_EMISSION,
                            1,
							0)), // default color is brown
  _qgc(0),
  _base_symbol_list(0)
{
  _qgc = new QuotientGeometryComputer(this);

  _state = FALSE;
  _isEnvironementSet=FALSE;

  _virtualTable=new VirtualSymbolTable;

  _areFruits=FALSE;
  _areFlowers=FALSE;
  _areLeaves=FALSE;

  _vertexNumber=0;   // maximum index of virtual elements added
  _addedBranch=NULL; // branch containing virtual elements

  const Plant& plant = *(plantframe->_plant);

  if (leaves) makeVirtualLeaves(leaves);
  if (fruits) makeVirtualLeaves(fruits);
  if (flowers) makeVirtualLeaves(flowers);

  _dr->dressThePlant(this);
  _state = TRUE;

}

LineTree::~LineTree() {
    if (_isEnvironementSet)
    {
        if (_addedBranch!=NULL)
        {
// ! Make a seg fault : to be resolved.
//          Ramifications* r=_pf->_plant->_branches;
//          if(r)r->remove(_addedBranch);
//          delete _addedBranch;
        }
    }
    delete _virtualTable;
    delete _qgc;
}


/*
  Diplays the plantframe using the integrated 3D viewer.

  - plantframe : contains all the information related to the plantframe
  that must be displayed (basically it is a MTG at one scale).

  - filename : is not yet used here. It would be the name of a file to
  save an ascii representation of the plant geometry.

  - dresser contains the information used to dress the plantframe (see below)

  - filter is a user-defined function that filters the entity that are
  to be displayed

Dressing Data information:

  Plantframes are computed independently of any particular geometric
  models.  Each plantframe entity is characterized by a location in
  space, 3 directions defining its orientation, a bottom diameter, a
  top diameter and a length.

  Normalized (included in a box 1,1,1) geometric models can be
  attached to plant entities so that the final geometric model of the
  entity is obtained by a translated, oriented transformed of a
  tapered transform of the primitive.

  Attachment of geometric models to MTG entities in plantframes is
  done in the dressing file as follows:

  Geometry = file1
  Geometry = file2

  Class A = name1
  Class B = name2
  ...

  the files file1 and file2 contain definition of geometric models
  which are labelled with different geometry names (name1, name2,
  ...). This information is produced by the parser of the geometry
  files and is stored in the dressingfile object in the field
  _symbol_table. Then a geometry model class name is attached to each
  symbol of the MTG using the Class A = name notation.

  + symb_list : is a list of pairs (char, filename) which associates a
    class with a geometric representation of type SMBModel if any

  + color_table: is a table containing pairs (char, material) where
  material is a set of vectors
  (diffuse,ambiant,specular,shininess). This list contains all the
  combinations of classes and colors that have been identified when
  dressing the plantframe (see the class Dresser). The char is meant
  to represent a geometric symbol, corresponding to a file name which
  is stored in array symb_list.

  + corr_table : is a table containing pairs (vtx,material_index).
  Material_index is an index into the table color_table, which
  contains all the (char/material) pairs that are used with the
  vertices of this plant frame.


 */

/* computes a list of object material mat_list associated with the
   list of colors in color_table.  The new list is simply a
   translation of color_table in terms of (GeometryPtr, MaterialPtr).
   The GeometryPtr contains a normalized geom object (i.e.
   included in a bounding box (1, 1, 1) ).
   see below for a description of the variables.  */

static void createBaseShapeList(const Dresser* dresser,
                                 const ColorsTable& color_table,
                                 const SymbLib& symb_lib,
                                 ShapeVector& base_symbol_list) {

    IntType nb_colors=color_table.entries();

    RWCString path_to_symbol = dresser->dressingFile()->symbolPath();

    bool error_detected = false;

    //  computes the list of symbols used in the color_table
    // (one symbol may appear several times in the color_table)

    // cerr << "Directory name of symbols : " << path_to_symbol << endl;
    // cerr << "the color table contains " << nb_colors << " entries" << endl;

    for(IntType i=0;i<nb_colors;i++)
    {

      GeometryPtr psymbol; // pt on the geometry primitive corresponding to the ith entry

      // gets the class of the ith entry of the table
      char a_symb=color_table.at(i).getSymbol();

      // cerr << "color_table.at(i).getSymbol() = " << a_symb << endl;

      // gets the tuple (char, symbolic_name, filename) corresponding to the Geometric Model
      // associated with class a_symb.
      MySymbol symbol(symb_lib.lookForASymbol(a_symb));

      // extract the symbolic name of this class
      // ex: Class A = name1
      // this extracts name1 (for class A)
      RWCString geom_symbolic_name=symbol.getSymbolName();

      // a set of geom objects has been declared in the dressing file: Geometry = "file"
      // gets the geom symbol table
      // returns 0 (default value) if not the case.
      GeometrySymbolTable* pst = dresser->dressingFile()->_geom_table;

      // If the GeometrySymbolTable pst is non NULL and the geom_symbolic_name
      // is found, then this geom_symbolic_name is initialized from table pst
      // Otherwise, we look whether the geom_symbolic_name may correspond
      // to a SMB model.

      /*
        cerr << "geom assign: class " << a_symb
        << ": looking for geom model labelled : " << geom_symbolic_name << endl;
      */

      if (pst) {

        GeometrySymbolTable::iterator psti = pst->find(geom_symbolic_name.data());

        if (psti!= pst->end()) {

          // cerr << "geometric model found ..." << endl;
          psymbol = psti->second;

          /*
          Printer pp(cerr,cerr);
          psymbol->apply(pp)
          */
        }
        else {

          //cerr << "Geometric model " << geom_symbolic_name.data() << " NOT found !!!" << endl;

        }
      }

      if (!psymbol) {

        // In case of a SMB model one must find the corresponding file, and load it

        if ( path_to_symbol != "") {

          string dir(path_to_symbol);                 // directory part of the name
          string name = symbol.getSymbolFileName().data(); // file part

		  if(!name.empty()){
			string filename = cat_dir_file(dir, name);  // cat dir and file part
			filename = append_suffix(filename, ".smb"); // adds extension .smb if necessary
			
			// cerr << "Complete SMB filename : " << filename << endl;
			
			if(exists(filename))
			  psymbol = GeometryPtr(new AmapSymbol(filename,FaceSet::DEFAULT_SOLID));
			else {
			  cerr << "symbol  : " << filename << " NOT valid !!!" << '\n';
			  psymbol = 0;
			}
		  }
          else  psymbol = 0;
		  
          /* If the symbol could not be read, it is invalid and it
             will be replaced by a default symbol later.  */

          if (!error_detected) {
            if (!psymbol ||!psymbol->isValid()) {
               cerr << "--> using default basic geometric model (tapered cylinder) " << '\n';

            }
            // else cerr << "symbol is valid : " << sname << endl;
            error_detected = true;
          }
        }

      }

      // At this stage, the psymbol is initialized with a GeometryPtr
      // which is either valid or invalid. If valid, psymbol must
      // contain a normalized geometric object (object included in a
      // box (1,1,1)).

      // Now we must compute the colors defined for the different classes
      // Colors are computed herafter, and material will override these
      // settings if any in the final computation of the shape of a vertex
      // (see function viewer hereafter).

      MyVector e(color_table.at(i).emissionComponent());
      MyVector a(color_table.at(i).ambientComponent());
      MyVector d(color_table.at(i).diffuseComponent());
      MyVector s(color_table.at(i).specularComponent());

      e.multiply(255);
      a.multiply(255);
      d.multiply(255);
      s.multiply(255);

      real_t vald = 1.0;
      if(a[0] != 0 && a[1] != 0 && a[2] != 0)
          vald = ((((d[0]/a[0])+(d[1]/a[1])+(d[2]/a[2])))/3);

      /*
        cerr << (int)d[0] << "," << (int)d[1] << "," << (int)d[2] << endl;
        cerr << (int)s[0] << "," << (int)s[1] << "," << (int)s[2] << endl;
        cerr << (int)e[0] << "," << (int)e[1] << "," << (int)e[2] << endl;
      */

      real_t shininess = color_table.at(i).shininessComponent();

  //    if (psymbol)
        {
        base_symbol_list.push_back(Shape(psymbol,
                                             AppearancePtr(new Material(Color3((unsigned char)a[0],
                                                                               (unsigned char)a[1],
                                                                               (unsigned char)a[2]),
                                                                        vald,
                                                                        Color3((unsigned char)s[0],
                                                                               (unsigned char)s[1],
                                                                               (unsigned char)s[2]),
                                                                        Color3((unsigned char)e[0],
                                                                               (unsigned char)e[1],
                                                                               (unsigned char)e[2]),
                                                                        shininess,
                                                                        0)),
                                             0)
                                   );
        }

     }

}

static void printPercentComputed(double ratio) {

    cerr << "\x0d" << "Already computed : " << (int)(ratio*100) << " % " << flush;
}

#define ToVector3(a) Vector3(a[0],a[1],a[2])

bool LineTree::geomptr(const BranchElement& branch_element, 
					   SymbType symbol, 
					   GeometryPtr& psmb, 
					   Discretizer & dis) const {

  bool defined_geom = false;
  LigRecord lg;
  lg.setValues(ToVector3(branch_element.getDirp()),
			   ToVector3(branch_element.getDirs()),
			   ToVector3(branch_element.getDirt()),
			   ToVector3(branch_element.getOrigin()),
			   branch_element.getBotDia(),
			   branch_element.getTopDia());
  VId vtx1 = branch_element.getVertex();
  GeometryPtr geometry = _dr->computeGeometry(vtx1);
  if (!geometry) { // the geometry was defined by a function	  
    if (symbol >=0 && symbol < _base_symbol_list.size()) {
     geometry = _base_symbol_list[symbol].geometry;
    }
  }
  if(geometry)defined_geom = true;
  psmb = lg.getTransformed(geometry,dis);
  return defined_geom;


  /***** ORIENTATION AND LOCATION OF THE ELEMENT ********/

  MyVector origin = branch_element.getOrigin();
  MyVector v1 = branch_element.getDirp();      // ATTENTION NORME !!
  MyVector v2 = branch_element.getDirs();
  MyVector v3 = branch_element.getDirt();

  real_t length = (real_t) v1.computeLength();
  v1.norm();
  v2.norm();
  v3.norm();

  /*
    cerr << v1.computeLength() << endl;
    cerr << v2.computeLength() << endl;
    cerr << v3.computeLength() << endl;
    cerr << "dirp(" << branch_element.getVertex() << ") = " << endl;
    v1.report();
    cerr << "dirs(" << branch_element.getVertex() << ") = " << endl;
    v2.report();
  */

  real_t radius_top = (real_t) branch_element.getTopDia(); //returns a ValType
  real_t radius_bot = (real_t) branch_element.getBotDia();

  Vector3 dirp(v1[0],v1[1],v1[2]);
  Vector3 dirs(v2[0],v2[1],v2[2]);
  Vector3 dirt(v3[0],v3[1],v3[2]);
  dirp.normalize();
  dirs.normalize();
  if(!dirs.isOrthogonalTo(dirt))
    dirt = cross(dirp,dirs);
  dirt.normalize();

  Vector3 the_origin(origin[0],origin[1],origin[2]);

  /***** GEOMETRY OF THE ELEMENT ********/

  // First check whether the geometry has been defined by a geometry function
  // passed as an argument to Plot(f, Geometry->geomfun)

  VId vtx = branch_element.getVertex();

  psmb = _dr->computeGeometry(vtx);

  // cerr << "Symbol = " << symbol << endl;
  GeometryPtr _primitive;

  if (psmb) _primitive = psmb; // the geometry was defined by a function
  else {

    // if not, look for a definition from the dressing file (e.g. Class U = name1)
    if (symbol >=0 && symbol < _base_symbol_list.size()) {

      /*
      cerr << "GeometryPtr = " << _base_symbol_list[symbol].geometry << endl;

      Printer pp(cerr,cerr,cerr);
      _base_symbol_list[symbol].geometry->apply(pp);
      */
     _primitive = _base_symbol_list[symbol].geometry;
    }
  }
  PrimitivePtr primitive = dynamic_pointer_cast<Primitive>(_primitive);
  // PrimitivePtr primitive(_base_symbol_list[symbol].geometry);

  // cerr << "POINTEUR = " << primitive.operator->() << endl;

  /*  Tapered can be applied only on primitive. So we discretize the geometry
      found in the base symbol list if it isn't a primitive.
      No problems for Transformed. If the geometry found is a group,
          there is no guaranty to find an unique discretized geometry of the group.
  */

  if(!primitive){
      if(_primitive) {
          if(radius_bot == radius_top){
              if (length == 1.0 && radius_bot == 1.0) {
                  psmb = GeometryPtr(_primitive);
              }
              else {
                  psmb = GeometryPtr(
                      (new Scaled
                       (Vector3(radius_bot,radius_bot,length),_primitive)));
              }
              if (fabs(length) > GEOM_EPSILON)
                  psmb =  GeometryPtr(new Oriented(dirs,dirt,psmb)); // see comment below

              if(fabs(the_origin.x()) > GEOM_EPSILON ||
                 fabs(the_origin.y()) > GEOM_EPSILON ||
                 fabs(the_origin.z()) > GEOM_EPSILON)
                  psmb = GeometryPtr(new Translated(the_origin, psmb));

              defined_geom = true;
          }
          else if(_primitive->apply(dis)){
              primitive = dis.getDiscretization();
              if(_primitive->isNamed()) primitive->setName(_primitive->getName());
          }
      }
  }

  if (primitive) {

    // Creates a tapered geometry
    // The geometric model is defined in a reference system Rl = (x,y,z)
    // AMAPmod defines the coordinates of a reference system R = (P,S,T)
    // with respect to a global reference system R0
    // Since z is the primary direction P, x is the secundary direction S
    // and y is the ternary direction, the passage matrix M(R/RL) from RL
    // to R is: [[0,1,0]t, [0,0,1]t, [1,0,0]t]
    // We then need to express how to pass from Rl to R0 :
    // X/R0 = M(R/R0) . M(R/RL) . X/Rl
    //      = [P,S,T] . [[0,1,0]t, [0,0,1]t, [1,0,0]t] . X/Rl
    //      = [S,T,P] . X/Rl

      defined_geom = true;

      // Creates a tapered geometry
      if (radius_bot == radius_top) {
          if (length == 1.0 && radius_bot == 1.0) {
              psmb = GeometryPtr(primitive);
          }
          else {
              psmb = GeometryPtr(
                  (new Scaled
                   (Vector3(radius_bot,radius_bot,length),GeometryPtr(primitive))));
          }
      }
      else
          psmb = GeometryPtr
              (new Scaled
               (Vector3(1,1,length),GeometryPtr
                (new Tapered
                 (radius_bot, radius_top,primitive)
                    )));

      if (fabs(length) > GEOM_EPSILON)
          psmb =  GeometryPtr(new Oriented(dirs,dirt,psmb)); // see comment above

      if(fabs(the_origin.x()) > GEOM_EPSILON ||
         fabs(the_origin.y()) > GEOM_EPSILON ||
         fabs(the_origin.z()) > GEOM_EPSILON)
          psmb = GeometryPtr(new Translated(the_origin, psmb));

  }

  if (!defined_geom) {

    /*
      The geometry of the component was not defined : a default
      geometry will be used: a frustum from the geom library
    */
    real_t ratio;
    if (radius_bot > REAL_EPSILON) ratio = radius_top/radius_bot;
    else ratio = REAL_MAX;

    GeometryPtr shape(0);

    // if the radius is non-zero, define a "default" geometric object:
    if(radius_bot > REAL_EPSILON){

      if(length > REAL_EPSILON)
        shape = GeometryPtr(new Frustum(radius_bot,length, ratio, false, 6));// false for open cylinder, six faces
      else
        shape = GeometryPtr(new Disc(radius_bot,6));

      if((dirt != Vector3::ORIGIN)&&
         (dirs != Vector3::ORIGIN)){
        GeometryPtr oriented_shape(new Oriented(dirs,dirt,shape)); // see comment above
        psmb = GeometryPtr(new Translated(the_origin,oriented_shape));
      }
      else
        psmb = shape;
    }

    return false; // the geometric symbol was not defined: default is used

  }
  else return true; // the geometric symbol was defined

}

bool LineTree::matptr(VId vtx, SymbType symbol, MaterialPtr& pmat) const {

  // First check whether the material has been defined by a material function
  // passed as an argument to Plot(f, Material->matfun)
  pmat = dynamic_pointer_cast<Material>(_dr->computeMaterial(vtx));

  if (!(pmat)) { // No function was defined for defining Material

    // then, search for the symbol_indexth element of the base_symbol_list
    // this list is a translation of the color_table list of the dresser
    // into the new data structures associated with the Geom module
    // i.e. pairs of (GeometryPtr,MaterialPtr).

    if (symbol >=0 && symbol < _base_symbol_list.size())
      pmat = dynamic_pointer_cast<Material>( _base_symbol_list[symbol].appearance);
    else {
      pmat = dynamic_pointer_cast<Material>(_default_mat);
    }
  }
  return ((pmat)&&(pmat->isValid()));
}

AmlBoolean LineTree::viewer(const FNode* filter, bool display_on)
{

  // table defining a list of pairs of class and "standard" AML colors
  // (char, diffuse, ambiant, specular, shininess)
  // This table was computed by the Dresser constructor (which builds a Painter, ...)
  // just before the LineTree constructor is built
  const ColorsTable* color_table=&_dr->getColorsTable();

  // table for class defined by SMB symbol = (char, smb_filename)
  const SymbLib* symb_list=&_dr->getSymbLib();

  // table defining for each vtx an index in array color_table, containing a material
  // (vtx, index_in_color_table)
  const CorrTable* corr_table=&_dr->getCorrTable();

  // This function computes an array associating
  // each Class of entity with a Geometry and a Material
  // These values may be override subsequently by geomptr() and matptr()
  // (see below)
  createBaseShapeList(_dr, *color_table, *symb_list, _base_symbol_list);

  // the plantframe contains both the _plant (topology)
  // and the _geomcomputer (module computing the plant geometry)

  const Plant* plant = _pf->_plant;

  IntType nb=plant->nbBranches();

  // list that will be passed to the viewer
  // containing the geometric description of all the vertices
  // that will be passed to the viewer

  _scene = ScenePtr(new Scene);

  bool first_geom = true; // detects if a warning message must be issued for the first time
  bool first_mat = true;

  double prev_ratio = 0.0;
  double ratio = 0.0;

  // Could be usefull for creating geom shape.
  Discretizer dis;

  for (IntType i=0;i<nb;i++)
  {

    // cerr << "branch nb =" << i << endl;

    ratio = ((double)i)/(double)nb;

    if (ratio >= prev_ratio+0.1) {
      prev_ratio = ratio;
      printPercentComputed(ratio);
    }

    const Branch branch = plant->findBranch(i);
    const BranchCompoList branch_compo_list = branch.branchComponents();

    IntType number=branch_compo_list.entries();

    // Loop on all the branch vertices
    int vtx;



    for (IntType j=0;j<number;j++)
    {

      // cerr << "\t vertex nb =" << j << endl;

      BranchElement branch_element=branch_compo_list.at(j);

      vtx = branch_element.getVertex();

      AMObjVector argobjs(1);
      argobjs[0] = AMObj(AMObjType::VTX, vtx);

      if (branch_element.isValid() &&
          (filter == 0 ||
           filter != 0 && (int) ((*filter)(argobjs)).val.i)) {

        /*****  SHAPE OF THE ELEMENT ********/

        // For each vertex, corr_table contains an index into the color array which
        // enables us to retreive the "shape"( =(geometry,color) ) of this vertex.


        size_t index=corr_table->index(vtx); // index of vtx in coor_table

        // index in the color_table of the geometric information associated to this vertex
        SymbType symbol_index=corr_table->at(index).getSymbol()-1; // stored from 1 to N

        /***** 1. GEOMETRY OF THE ELEMENT ********/

        GeometryPtr pgeom;

        bool geom_not_default = geomptr(branch_element, symbol_index, pgeom, dis);
        if (!geom_not_default) {
          if (first_geom) { // Prints this message once
            cerr << "Geom not defined or not valid --> default tapered cylinder is used. " << '\n';
            first_geom = false;
          }
        }

        /***** 2. MATERIAL OF THE ELEMENT ********/

        MaterialPtr pmat;

        bool mat_not_default = matptr(vtx, symbol_index, pmat);

        if (!mat_not_default) {
          if (first_mat) { // Prints this message once
            cerr << "material not found --> default material used" << '\n';
            first_mat = false;
          }
        }


        /***** STORING THE SHAPE OF THE ELEMENT ********/
        if(pgeom && pgeom->isValid()){
          VId father = plant->topoFather(vtx,ANY);
          _scene->add(ShapePtr(new Shape(pgeom,AppearancePtr(pmat),vtx,father == UNDEF?Shape::NOID:father )));
        }

      }

    }
  }

  cerr << "\x0d" << "Already computed : 100 % ... Done" << '\n';

  if (display_on) _plot();

  return TRUE;

}


VirtualSymbol LineTree::getVirtualSymbol(IntType virtual_vertex) const
{
  VirtualSymbol v(virtual_vertex);

  // cerr << virtual_vertex << endl;

  size_t index=_virtualTable->index(v);

  assert(index!=RW_NPOS);

  return _virtualTable->at(index);
}

void LineTree::makeVirtualFruits(VirtualElements* fruits)
{
  _areFruits=TRUE;
  _virtualFruits=fruits;
}


void LineTree::makeVirtualLeaves(VirtualElements* leaves)
{
  _areLeaves=TRUE;
  _virtualLeaves=leaves;
}

void LineTree::makeVirtualFlowers(VirtualElements* flowers)
{
  _areFlowers=TRUE;
  _virtualFlowers=flowers;
}


AMObj LineTree::display(ostream& o, const AMObjVector& args) const {
    int len = args.length();
    int argth = 1;
    int view_mode =0;
    if (*(AMString*)(args[argth].val.p) == "Display") {
        CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Display", (argth+1)/2+1, "a STRING"));

        if (*(AMString*)(args[argth+1].val.p) == "All") {
            view_mode = 0;
        }
        else if (*(AMString*)(args[argth+1].val.p) == "MicroOnly") {
            view_mode = 1;
        }
        else if (*(AMString*)(args[argth+1].val.p) == "MacroOnly") {
            view_mode = 2;
        }
        else if (*(AMString*)(args[argth+1].val.p) == "HIDE") {
            view_mode = 3;
        }
        else {
            genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Display", (argth+1)/2+1, "All, MicroOnly, MacroOnly or HIDE");
        }
    }
    else {
        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Display", (argth+1)/2+1));
    }

#ifdef WITH_OLD_GEOM
//    Printer _printer(cout,cout,cout);
    if(!_scene->isEmpty() && view_mode !=2&&view_mode!=3)
        cout << *_scene << '\n';
//      _scene->apply(_printer);
    if(!_qgc->isSceneEmpty() && view_mode !=1&&view_mode!=3)
        cout << *_qgc->getScene() << '\n';
//      _qgc->getScene()->apply(_printer);
#else
    Printer _printer(cout);
    _scene->apply(_printer);
    _qgc->getScene()->apply(_printer);

#endif

    return AMObj(AMObjType::VOID);
}

AMObj LineTree::plot(GP_window&, const AMObjVector& args) const {

  int len = args.length();
  int argth = 1;

  FNode* geometry = NULL;
  FNode* material = NULL;
  FNode* showMicro = NULL;
  FNode* showMacro = NULL;

  int quotient_scale = -1 ;
  FNode* quotient_fun = NULL;
  FNode* quotient_geometry_fun = NULL;
  FNode* quotient_appearance_fun = NULL;
  FNode* quotient_consider_fun = NULL;
  string quotient_geometry_name;
  bool recompute = false;
  int view_mode = -1;
  bool symbol;
  real_t compress_rate = -1;
  int sorttype = 0;


  CHECKCONDVA(len > 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Linetree", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Linetree", 1, args[0].tag.string().data(), "Linetree"));

  while (argth < len) { // treatment of options

    // cerr << "arg = " << argth << args[argth].tag << endl;

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Plot", (argth+1)/2+1));

    assert(argth + 1 < len); // must contain at least two parameters : this is verified syntactically

    if (*(AMString*)(args[argth].val.p) == "Geometry") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      geometry = (FNode*) args[argth+1].val.p;
      _dr->makeGeometryFun(geometry);

    } else if (*(AMString*)(args[argth].val.p) == "Symbol") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      geometry = (FNode*) args[argth+1].val.p;
      _dr->makeGeometryFun(geometry);
	  symbol = true;
	  

    } else if (*(AMString*)(args[argth].val.p) == "Appearance") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      material = (FNode*) args[argth+1].val.p;
      _dr->makeMaterialFun(material);

    } else if (*(AMString*)(args[argth].val.p) == "Quotient") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE || args[argth+1].tag() ==AMObjType::INTEGER 
				  || (args[argth+1].tag() ==AMObjType::STRING && *(AMString*)(args[argth+1].val.p) == "SAME"),
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC or INT or 'SAME'"));

      if (args[argth+1].tag() ==AMObjType::FNODE) {
        quotient_fun = (FNode*) args[argth+1].val.p;
		if(quotient_geometry_name.empty())
        _qgc->setQuotientGeometryComputer(quotient_fun,
										  quotient_geometry_fun,
										  quotient_appearance_fun,
										  quotient_consider_fun);
		else
        _qgc->setQuotientGeometryComputer(quotient_fun,
										  quotient_geometry_name,
										  quotient_appearance_fun,
										  quotient_consider_fun);
      }
      else if (args[argth+1].tag() ==AMObjType::INTEGER){
        quotient_scale = (int)args[argth+1].val.i;
		if(quotient_geometry_name.empty())
        _qgc->setQuotientGeometryComputer(quotient_scale,
										  quotient_geometry_fun,
										  quotient_appearance_fun,
										  quotient_consider_fun);
		else
        _qgc->setQuotientGeometryComputer(quotient_scale,
										  quotient_geometry_name,
										  quotient_appearance_fun,
										  quotient_consider_fun);
      }
	  else {
		recompute = true;
//		quotient_fun = _qgc->getQuotientFun();
//		if(quotient_fun == NULL)
//		  quotient_scale = _qgc->getQuotientScale();
	  }
    }
    else if (*(AMString*)(args[argth].val.p) == "QuotientGeometry") {

      CHECKCONDVA((args[argth+1].tag() ==AMObjType::FNODE || args[argth+1].tag() ==AMObjType::STRING),
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC or ALGONAME"));

      if (args[argth+1].tag() ==AMObjType::FNODE) {
		quotient_geometry_fun = (FNode*) args[argth+1].val.p;
		_qgc->setQuotientGeometryFun(quotient_geometry_fun);
	  }
	  else {
		string algo = ((AMString*)(args[argth+1].val.p))->data();
		if(!Fit::available(algo)){
		  cerr << '\'' << algo << "' unavailable." << '\n';
		  CHECKCONDVA(false,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "AVAILABLE ALGONAME"));		  
		}
		quotient_geometry_name = algo;
		_qgc->setQuotientGeometryName(quotient_geometry_name);

	  }

    }
    else if (*(AMString*)(args[argth].val.p) == "QuotientAppearance") {
      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      quotient_appearance_fun = (FNode*) args[argth+1].val.p;
      _qgc->setQuotientAppearanceFun(quotient_appearance_fun);

    }
    else if (*(AMString*)(args[argth].val.p) == "QuotientConsider") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      quotient_consider_fun = (FNode*) args[argth+1].val.p;
      _qgc->setConsiderFun(quotient_consider_fun);

    }
    else if (*(AMString*)(args[argth].val.p) == "Compress") {
      CHECKCONDVA((args[argth+1].tag() ==AMObjType::INTEGER || args[argth+1].tag() ==AMObjType::REAL),
		genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "REAL In [0-100]"));
	  switch(args[argth+1].tag()) {		
	  case  AMObjType::INTEGER:
		compress_rate =  args[argth+1].val.i;
		break;
	  default:
		compress_rate = args[argth+1].val.r;
		break;
	  }
      CHECKCONDVA((compress_rate >=0 && compress_rate <= 100),
		genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "REAL In [0-100]"));
	  if(view_mode == -1)view_mode = 2;
	}
    else if (*(AMString*)(args[argth].val.p) == "Sort") {
      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING ,
		genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "DECSIZE [or SIZE or DECREASINGSIZE], INCSIZE, DECORDER [or ORDER], INCORDER or NONE"));
		string sortalgo = ((AMString*)(args[argth+1].val.p))->data();
		sortalgo = toUpper(sortalgo);
		if(sortalgo == "SIZE" || sortalgo == "DECSIZE" || sortalgo == "DECREASINGSIZE")
		  sorttype = 2;
		else if (sortalgo == "INCSIZE" || sortalgo == "INCREASINGSIZE")
		  sorttype = 3;
		else if(sortalgo == "ORDER" || sortalgo == "DECORDER" || sortalgo == "DECREASINGORDER")
		  sorttype = 0;
		else if (sortalgo == "INCORDER" || sortalgo == "INCREASINGORDER")
		  sorttype = 1;
		else if (sortalgo == "NONE")
		  sorttype = 4;
		else genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "DECSIZE [or SIZE or DECREASINGSIZE], INCSIZE, DECORDER [or ORDER], INCORDER or NONE");
	}
    else if (*(AMString*)(args[argth].val.p) == "ShowMicro" || 
			 *(AMString*)(args[argth].val.p) == "Show" ) {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      showMicro = (FNode*) args[argth+1].val.p;
    }
    else if (*(AMString*)(args[argth].val.p) == "ShowMacro") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      showMacro = (FNode*) args[argth+1].val.p;
    }
    else if (*(AMString*)(args[argth].val.p) == "Display") {
        CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "All, MicroOnly, MacroOnly or HIDE"));

        if (*(AMString*)(args[argth+1].val.p) == "All") {
            view_mode = 0;
        }
        else if (*(AMString*)(args[argth+1].val.p) == "MicroOnly") {
            view_mode = 1;
        }
        else if (*(AMString*)(args[argth+1].val.p) == "MacroOnly") {
            view_mode = 2;
        }
        else if (*(AMString*)(args[argth+1].val.p) == "HIDE") {
            view_mode = 3;
        }
        else {
          genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "All, MicroOnly, MacroOnly or HIDE");
        }
    }
    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds), "Plot", (argth+1)/2+1,
				  "Geometry, Symbol, Appearance, Quotient,"
				  " QuotientGeometry, QuotientAppearance, QuotientConsider,"
				  " ShowMicro, ShowMacro, Display"));

    }

    argth += 2;

  }

  if(view_mode == -1)view_mode =0;
   _qgc->setViewMode(view_mode);

  if (geometry || material) {

    for (Scene::iterator psti = _scene->getBegin(); psti != _scene->getEnd(); psti++) {
      ShapePtr _shape = dynamic_pointer_cast<Shape>(*psti);
      if(_shape){
        VId vtx = _shape->id;
        // cerr << "vtx = " << vtx << '\n';

        if (geometry) {

          GeometryPtr pgeom = _dr->computeGeometry(vtx);

          if (pgeom && symbol) {

			LigRecord lg;
			BranchElement branch_element = _pf->_plant->searchForElement(vtx);

			lg.setValues(ToVector3(branch_element.getDirp()),
			  ToVector3(branch_element.getDirs()),
			  ToVector3(branch_element.getDirt()),
			  ToVector3(branch_element.getOrigin()),
			  branch_element.getBotDia(),
			  branch_element.getTopDia());
			  pgeom = lg.getTransformed(pgeom);
		  }
			
		  if (pgeom)_shape->geometry = pgeom;
        }
        if (material) {

          MaterialPtr pmat = dynamic_pointer_cast<Material>(_dr->computeMaterial(vtx))  ;
          if (pmat) {
            _shape->appearance = pmat;

          }
        }
      }
    }

  }
    // Treatment of quotiented graphs and their geometric representation

  if(quotient_scale != -1 || quotient_fun != NULL)
      _qgc->computeGeometry(_pf);
  else if(recompute){
      _qgc->recomputeGeometry(_pf);
  }
  else if(compress_rate>-1){
	real_t time = 0;
	real_t ftime = 0;
	real_t rate = compress_rate;
	_qgc->compressGeometry(_pf,rate,time,ftime,sorttype);
    _plot(showMicro,showMacro);
    Array* ret = new SLArray;
	(*ret)+=  AMObj(AMObjType::REAL,compress_rate);
	(*ret)+=  AMObj(AMObjType::REAL,rate);
	(*ret)+=  AMObj(AMObjType::REAL,time);
	(*ret)+=  AMObj(AMObjType::REAL,ftime);
    return AMObj(AMObjType::ARRAY,ret);
  }


  _plot(showMicro,showMacro);
  return args[0];

}

AMObj LineTree::_plot() const {
  return _plot(NULL,NULL);
}

AMObj LineTree::_plot(FNode* showMicro,FNode* showMacro) const {
  
  if(_qgc->getViewMode()!=3){
	
    //ViewerApplication p_appli;
	
	
    if(_qgc->isSceneEmpty()){
      assert(_scene->isValid());
	  PGLViewerApplication::display(_scene);
    }
    else{
      if(_qgc->getViewMode()==0){
        assert(_scene->isValid());
        assert(_qgc->getScene()->isValid());
        ScenePtr _scenetodisplay(new Scene());
		if(showMicro == NULL)
		  _scenetodisplay->merge(_scene);
		else {
		  ShapePtr shape;
		  AMObjVector argobjs(1);
		  for(Scene::const_iterator _it = _scene->getBegin();
		  _it != _scene->getEnd(); _it++){
			shape = dynamic_pointer_cast<Shape>(*_it);
			if(shape){
			  argobjs[0] = AMObj(AMObjType::VTX,(VId)shape->getId());
			  AMObj res = (*showMicro)(argobjs);
			  if(res.type() == AMObjType::BOOL){
				if(res.val.b == TRUE){
				  _scenetodisplay->add(Shape3DPtr(shape));
				}
			  }
			  else 
				cerr << "Error in returned value of function ShowMicro for " << shape->getId() << '\n';
			}
		  }
		}
		if(showMacro == NULL)
		  _scenetodisplay->merge(_qgc->getScene());
		else {
		  ShapePtr shape;
		  AMObjVector argobjs(1);
		  for(Scene::const_iterator _it = _qgc->getScene()->getBegin();
		  _it != _qgc->getScene()->getEnd(); _it++){
			shape = dynamic_pointer_cast<Shape>(*_it);
			if(shape){
			  argobjs[0] = AMObj(AMObjType::VTX, (VId)shape->getId());
			  AMObj res = (*showMacro)(argobjs);
			  if(res.type() == AMObjType::BOOL){
				if(res.val.b == TRUE){
				  _scenetodisplay->add(Shape3DPtr(shape));
				}
			  }
			  else 
				cerr << "Error in returned value of function ShowMacro for " << shape->getId() << '\n';
			}
		  }
		}
		PGLViewerApplication::display(_scenetodisplay);
      }
      else if(_qgc->getViewMode()==1){
        assert(_scene->isValid());
        ScenePtr _scenetodisplay(new Scene());
		if(showMicro == NULL)
		  _scenetodisplay->merge(_scene);
		else {
		  ShapePtr shape;
		  AMObjVector argobjs(1);
		  for(Scene::const_iterator _it = _scene->getBegin();
		  _it != _scene->getEnd(); _it++){
			shape = dynamic_pointer_cast<Shape>(*_it);
			if(shape){
			  argobjs[0] = AMObj(AMObjType::VTX, (VId)shape->getId());
			  AMObj res = (*showMicro)(argobjs);
			  if(res.type() == AMObjType::BOOL){
				if(res.val.b == TRUE){
				  _scenetodisplay->add(Shape3DPtr(shape));
				}
			  }
			  else 
				cerr << "Error in returned value of function ShowMicro for " << shape->getId() << '\n';
			}
		  }
		}
		PGLViewerApplication::display(_scenetodisplay);
      }
      else if(_qgc->getViewMode()==2){
        assert(_qgc->getScene()->isValid());
        ScenePtr _scenetodisplay(new Scene());
		if(showMacro == NULL)
		  _scenetodisplay->merge(_qgc->getScene());
		else {
		  ShapePtr shape;
		  AMObjVector argobjs(1);
		  for(Scene::const_iterator _it = _qgc->getScene()->getBegin();
		  _it != _qgc->getScene()->getEnd(); _it++){
			shape = dynamic_pointer_cast<Shape>(*_it);
			if(shape){
			  argobjs[0] = AMObj(AMObjType::VTX, (VId)shape->getId());
			  AMObj res = (*showMacro)(argobjs);
			  if(res.type() == AMObjType::BOOL){
				if(res.val.b == TRUE){
				  _scenetodisplay->add(Shape3DPtr(shape));
				}
			  }
			  else 
				cerr << "Error in returned value of function ShowMacro for " << shape->getId() << '\n';
			}
		  }
		}
		PGLViewerApplication::display(_scenetodisplay);
	  }
	}
  } 
  return AMObj(AMObjType::VOID); 
}

ostream& LineTree::displayOneLine(ostream& o) const {

    o << "Linetree : " << _scene->getSize() << " shape(s)" ;
    if(!_qgc->isSceneEmpty()) o << " + " << _qgc->getScene()->getSize() << " macro-shape(s)" ;
    o << "." << '\n';

  return o;

}

bool LineTree::isVirtualElement(const VId id) const
{
	if(_virtualTable == NULL || _virtualTable->empty())return false;
	VId a = _virtualTable->at(0)._element;
//	cerr << id << " compare to " << a << '\n';
	if(id < a)return false;
	if(id == a)return true;
	VId c = id - a;
	if(c >= _virtualTable->entries()){
	  cerr << "Virtual Element" << '\n';
	  return true;
	}
	return false;
}

VId LineTree::fatherOfVirtualElement(const VId id) const
{
	if(_virtualTable == NULL || _virtualTable->empty())return VId(-1);
	VId a = _virtualTable->at(0)._element;
	if(a > id)return VId(-1);
	VId c = id - a;
	if(c >= _virtualTable->entries())return VId(-1);
    if(_virtualTable->at(c)._element == id)
		return _virtualTable->at(c)._bearing_element;
	else return VId(-1);

/*	for(int i = 0; i < _virtualTable->entries(); i++)
	  if(_virtualTable->at(i)._element == id)
		return _virtualTable->at(i)._bearing_element;
	return VId(-1);*/
}

VId LineTree::complexOfVirtualElement(const VId id, int s) const
{
	VId a = fatherOfVirtualElement(id);
	if(a == -1) return -1;
	return _pf->_plant->getMtg()->si_complex(a,s);
}

AMObj LineTree::extract(const AMObjVector& args) const {

  int argth = 1;
  int len = args.length();

  Array* ret = new SLArray;
  int nb_virtual_symbols = _virtualTable->entries();

  // cerr << nb_virtual_symbols << " virtual symbols are defined in this linetree" << '\n';

  CHECKCONDVA(len > 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Extract",2));

  if (! args[0].isaAMModel()) return AMObj(AMObjType::UNDEF);

  while (argth < args.length())  { // treatment of options
      CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Extract", (argth+1)/2+1));

      assert(argth + 1 < args.length()); // must contain at least two parameters : this is verified syntactically

      if (*(AMString*)(args[argth].val.p) == "Data") { // treatment of different options

        CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "VirtualVertices, ActualVertices or QuotientedGraph"));

        if (*(AMString*)(args[argth+1].val.p) == "VirtualVertices") {
          for(int i=0;i<nb_virtual_symbols;i++)
            (*ret) += AMObj(AMObjType::VTX,_virtualTable->at(i)._element);
        }
        else if(*(AMString*)(args[argth+1].val.p) =="ActualVertices") {
          for(int i=0;i<nb_virtual_symbols;i++)
            (*ret) += AMObj(AMObjType::VTX,_virtualTable->at(i)._bearing_element);
        }
        else if(*(AMString*)(args[argth+1].val.p) =="QuotientedGraph") {
            if(_qgc->getQuotientFun())
                ret =_qgc->computeQuotientedGraph(_pf);
            else return  AMObj(AMObjType::UNDEF);
        }
        else {
          genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "VirtualVertices, ActualVertices or QuotientedGraph");
          return  AMObj(AMObjType::UNDEF);
        }
      }
      else if (*(AMString*)(args[argth].val.p) == "Info") { // treatment of different options

        CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "ClassName or Appearance"));

        if (*(AMString*)(args[argth+1].val.p) == "ClassName") {
            vector< string > classnames = Fit::getClassNames();
            for(int i=0;i<classnames.size();i++){
                (*ret) += AMObj(AMObjType::STRING,new AMString(classnames[i].c_str()));
            }
            (*ret) += AMObj(AMObjType::STRING,new AMString("SELF"));
            (*ret) += AMObj(AMObjType::STRING,new AMString("NONE"));
        }
        if (*(AMString*)(args[argth+1].val.p) == "VolumeClassName") {
            vector< string > classnames = Fit::getVolumeClassNames();
            for(int i=0;i<classnames.size();i++){
                (*ret) += AMObj(AMObjType::STRING,new AMString(classnames[i].c_str()));
            }
        }
        else if (*(AMString*)(args[argth+1].val.p) == "Appearance") {
          AppearanceSymbolTable * app = _pf->getDressingFile()->_mat_table;
          if(app != NULL){
          for(AppearanceSymbolTable::iterator _ait = app->begin() ;
              _ait != app->end() ;_ait++ ){
            (*ret) += AMObj(AMObjType::STRING,new AMString(_ait->first.c_str()));
          }
          }
        }
        else {
          genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "ClassName, VolumeClassName or Appearance");
          return  AMObj(AMObjType::UNDEF);
        }
      }
      else if (*(AMString*)(args[argth].val.p) == "Surface") { // treatment of different options
		  CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
			  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "Macro or Micro"));

		  if (*(AMString*)(args[argth+1].val.p) == "Micro") {
			  if(_scene){
				  Discretizer dis;
				  SurfComputer surf(dis);
				  for(Scene::iterator _it = _scene->getBegin();
				  _it != _scene->getEnd();
				  _it++){
					  if((*_it)->apply(surf)){
						  List * s = new SLList;
						  (*s) += AMObj(AMObjType::VTX,VId((*_it)->getId()));
						  (*s) += AMObj(AMObjType::REAL,surf.getSurface());
						  (*ret) += AMObj(AMObjType::LIST,s);
					  }
				  }
			  }
		  }
		  else if (*(AMString*)(args[argth+1].val.p) == "Macro"){
			  if(_qgc->getScene()){
				  Discretizer dis;
				  SurfComputer surf(dis);
				  for(Scene::iterator _it = _qgc->getScene()->getBegin();
				  _it != _qgc->getScene()->getEnd();
				  _it++){
					  if((*_it)->apply(surf)){
						  List* s = new SLList;
						  (*s) += AMObj(AMObjType::VTX,VId((*_it)->getId()));
						  (*s) += AMObj(AMObjType::REAL,surf.getSurface());
						  (*ret) += AMObj(AMObjType::LIST,s);
					  }
				  }
			  }
		  }
        else {
          genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "Macro or Micro");
          return  AMObj(AMObjType::UNDEF);
        }

      }
      else if (*(AMString*)(args[argth].val.p) == "Volume") { // treatment of different options
		  CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
			  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "Macro or Micro"));
		  if (*(AMString*)(args[argth+1].val.p) == "Micro") {
			  if(_scene){
				  Discretizer dis;
				  VolComputer vol(dis);
				  for(Scene::iterator _it = _scene->getBegin();
				  _it != _scene->getEnd();
				  _it++){
					  if((*_it)->apply(vol)){
						  List* s = new SLList;
						  (*s) += AMObj(AMObjType::VTX,VId((*_it)->getId()));
						  (*s) += AMObj(AMObjType::REAL,vol.getVolume());
						  (*ret) += AMObj(AMObjType::LIST,s);
					  }
				  }
			  }
		  }
		  else if (*(AMString*)(args[argth+1].val.p) == "Macro"){
			  if(_qgc->getScene()){
				  Discretizer dis;
				  VolComputer vol(dis);
				  for(Scene::iterator _it = _qgc->getScene()->getBegin();
				  _it != _qgc->getScene()->getEnd();
				  _it++){
					  if((*_it)->apply(vol)){
						  List* s = new SLList;
						  (*s) += AMObj(AMObjType::VTX,VId((*_it)->getId()));
						  (*s) += AMObj(AMObjType::REAL,vol.getVolume());
						  (*ret) += AMObj(AMObjType::LIST,s);
					  }
				  }
			  }
		  }
        else {
          genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1,"Macro or Micro");
          return  AMObj(AMObjType::UNDEF);
        }

      }
      else if (*(AMString*)(args[argth].val.p) == "SceneId") { // treatment of different options
		  CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
			  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "Macro or Micro"));

		  if (*(AMString*)(args[argth+1].val.p) == "Micro") {
			  if(_scene){
                return AMObj(AMObjType::INTEGER,(int)ptr_to_uint32(_scene));
			  }
		  }
		  else if (*(AMString*)(args[argth+1].val.p) == "Macro"){
			  if(_qgc->getScene()){
                return  AMObj(AMObjType::INTEGER,(int)ptr_to_uint32(_qgc->getScene()));
			  }
		  }
        else {
          genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "Macro or Micro");
          return  AMObj(AMObjType::UNDEF);
        }

      }
     else if (*(AMString*)(args[argth].val.p) == "Hack") { 
	 }
     else {
        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds), "Extract", (argth+1)/2+1,"Data, Info, Surface or Volume"));
      }

        argth += 2;
    }

  return AMObj(AMObjType::ARRAY,ret);

}

AMObj LineTree::save(const AMObjVector& args) const {

  int argth = 1;
  int len = args.length();
  int view_mode = 0;
  int format = 0;
  string filename, geomfilename, appfilename, shapefilename;

  Array* ret = new SLArray;

  // cerr << nb_virtual_symbols << " virtual symbols are defined in this linetree" << '\n';

  CHECKCONDVA(len > 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Save",2));

  if (! args[0].isaAMModel()) return AMObj(AMObjType::UNDEF);

  while (argth < len)  { // treatment of options
      CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Save", (argth+1)/2+1));

      assert(argth + 1 < args.length()); // must contain at least two parameters : this is verified syntactically

      if (*(AMString*)(args[argth].val.p) == "Format") { // treatment of different options

        CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Save", (argth+1)/2+1, "GEOM, BGEOM, PovRay, AMAP, VGStar, VRML or XML"));

        if (*(AMString*)(args[argth+1].val.p) == "GEOM") {
            format = 0;
        }
        else if(*(AMString*)(args[argth+1].val.p) =="PovRay") {
            format = 1;
        }
        else if(*(AMString*)(args[argth+1].val.p) =="AMAP") {
            format = 2;
        }
        else if(*(AMString*)(args[argth+1].val.p) =="VGStar") {
            format = 3;
        }
        else if(*(AMString*)(args[argth+1].val.p) =="VRML") {
            format = 4;
        }
        else if(*(AMString*)(args[argth+1].val.p) =="BGEOM") {
            format = 5;
        }
        else if(*(AMString*)(args[argth+1].val.p) =="XML") {
            format = 6;
        }
        else {
          genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Save", (argth+1)/2+1, "GEOM, BGEOM, PovRay, AMAP, VGStar, VRML or XML");
          return  AMObj(AMObjType::UNDEF);
        }
      }
      else if (*(AMString*)(args[argth].val.p) == "File") {
          if((!geomfilename.empty())&&(!appfilename.empty())&&(!shapefilename.empty())){
              CHECKCONDVA(FALSE,
                          genAMLError(ERRORMSG(K_OPTION_VALUES_INCOMPATIBLE_ERR_sd), "Save",(argth+1)/2+1));
              return  AMObj(AMObjType::UNDEF);
          }
          filename = ((AMString*)(args[argth+1].val.p))->data();
      }
      else if (*(AMString*)(args[argth].val.p) == "Geometry") {
          if(!filename.empty()&&format!=0){
              CHECKCONDVA(FALSE,
                          genAMLError(ERRORMSG(K_OPTION_VALUES_INCOMPATIBLE_ERR_sd), "Save",(argth+1)/2+1));
              return  AMObj(AMObjType::UNDEF);
          }
          geomfilename = ((AMString*)(args[argth+1].val.p))->data();
      }
      else if (*(AMString*)(args[argth].val.p) == "Appearance") {
          if(!filename.empty()&&format!=0){
              CHECKCONDVA(FALSE,
                          genAMLError(ERRORMSG(K_OPTION_VALUES_INCOMPATIBLE_ERR_sd), "Save",(argth+1)/2+1));
              return  AMObj(AMObjType::UNDEF);
          }
          appfilename = ((AMString*)(args[argth+1].val.p))->data();
      }
      else if (*(AMString*)(args[argth].val.p) == "Shape") {
          if(!filename.empty()&&format!=0){
              CHECKCONDVA(FALSE,
                          genAMLError(ERRORMSG(K_OPTION_VALUES_INCOMPATIBLE_ERR_sd), "Save",(argth+1)/2+1));
              return  AMObj(AMObjType::UNDEF);
          }
          shapefilename = ((AMString*)(args[argth+1].val.p))->data();
      }
      else if (*(AMString*)(args[argth].val.p) == "Display") {
          CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                      genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Save", (argth+1)/2+1, "All, MicroOnly, MacroOnly or HIDE"));

          if (*(AMString*)(args[argth+1].val.p) == "All") {
              view_mode = 0;
          }
          else if (*(AMString*)(args[argth+1].val.p) == "MicroOnly") {
              view_mode = 1;
          }
          else if (*(AMString*)(args[argth+1].val.p) == "MacroOnly") {
              view_mode = 2;
          }
          else if (*(AMString*)(args[argth+1].val.p) == "HIDE") {
              view_mode = 3;
          }
        else {
            genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Save", (argth+1)/2+1, "All, MicroOnly, MacroOnly or HIDE");
        }
      }
      else {

        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds), "Save", (argth+1)/2+1,"Format, (File || Geometry, Appearance, Shape) or Display"));

      }

        argth += 2;
    }

  switch (format) {
      case 1 : // PovRay
          if(!filename.empty()){
              ofstream stream(filename.c_str());
              if (! (stream)) {
                  genAMLError(ERRORMSG(K_F_FILE_ERR_sss),"Save",filename.c_str(),".");
                  return AMObj(AMObjType::UNDEF);
              };
              Tesselator _tesselator;
              PovPrinter _printer(stream,_tesselator);
              if(!_scene->isEmpty()&&view_mode!=2&&view_mode!=3)_scene->apply(_printer);
              if(!_qgc->isSceneEmpty()&&view_mode!=1&&view_mode!=3)_qgc->getScene()->apply(_printer);
              cerr << "Save Linetree on " << filename << '\n';
          }
          else
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s),"Save");
          break;
      case 2 : // AMAP
        {

          Plant* plant = _pf->_plant;
          const ColorsTable& color_table= _dr->getColorsTable();
          const SymbLib& symblib= _dr->getSymbLib();
          const CorrTable& corr_table= _dr->getCorrTable();

          int _state = FALSE;
          if (makeLigFile(*plant,filename.c_str(),corr_table))
            if (makeInfFile(plant->minPoint(), plant->maxPoint(), filename.c_str() ))
              if (makeDtaFile(color_table,symblib,filename.c_str())) _state = TRUE;
          if (!_state)
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s),"Save");
        }
          break;
      case 3 : // VGStar
          if(!filename.empty()){
              ofstream stream(filename.c_str());
              if (! (stream)) {
                  genAMLError(ERRORMSG(K_F_FILE_ERR_sss),"Save",filename.c_str(),".");
                  return AMObj(AMObjType::UNDEF);
              };
              Tesselator _tesselator;
              VgstarPrinter _printer(stream,_tesselator);
              if(!_scene->isEmpty())_scene->apply(_printer);
              if(!_qgc->isSceneEmpty())_qgc->getScene()->apply(_printer);
          }
          else
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s),"Save");
          cerr << "Not Yet Implemented" << '\n';
          break;
      case 4 : // VRML
          if(!filename.empty()){
              ofstream stream(filename.c_str());
              if (! (stream)) {
                  genAMLError(ERRORMSG(K_F_FILE_ERR_sss),"Save",filename.c_str(),".");
                  return AMObj(AMObjType::UNDEF);
              };
              Discretizer _discretizer;
              VrmlPrinter _printer(stream,_discretizer);
              if(!_scene->isEmpty()&&view_mode!=2&&view_mode!=3)_scene->apply(_printer);
              if(!_qgc->isSceneEmpty()&&view_mode!=1&&view_mode!=3)_qgc->getScene()->apply(_printer);
              cerr << "Save Linetree on " << filename << '\n';
          }
          else
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s),"Save");
          break;
      case 5 : // Binary GEOM
          if(!filename.empty()){
              ofstream * stream = new ofstream(filename.c_str());
              if (! (stream)) {
                  genAMLError(ERRORMSG(K_F_FILE_ERR_sss),"Save",filename.c_str(),".");
                  delete stream;
                  return AMObj(AMObjType::UNDEF);
              };
              delete stream;
              if((!_scene->isEmpty()&&view_mode==1)||(_qgc->isSceneEmpty()&&view_mode==0))
                BinaryPrinter::print(_scene,filename,"This file is generated by AMAPmod");
              else if((!_qgc->isSceneEmpty()&&view_mode==2)||(_scene->isEmpty()&&view_mode==0))
                BinaryPrinter::print(_qgc->getScene(),filename,"This file is generated by AMAPmod");
              else if (view_mode==0){
                ScenePtr _bigscene(new Scene(*_scene));
                _bigscene->merge(_qgc->getScene());
                BinaryPrinter::print(_bigscene,filename,"This file is generated by AMAPmod");
              }
              cerr << "Save Linetree on " << filename << '\n';
          }
          else
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s),"Save");
          break;
      case 6 : // XML
          if(!filename.empty()){
              ofstream * stream = new ofstream(filename.c_str());
              if (! (stream)) {
                  genAMLError(ERRORMSG(K_F_FILE_ERR_sss),"Save",filename.c_str(),".");
                  delete stream;
                  return AMObj(AMObjType::UNDEF);
              };
              delete stream;
              saveAsXML(filename.c_str());
              cerr << "Save Linetree in XML on " << filename << '\n';
          }
          else
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s),"Save");
          break;
       case 0 : // Geom Format
          if(!filename.empty()){
              ofstream stream(filename.c_str());
              if (! (stream)) {
                  genAMLError(ERRORMSG(K_F_FILE_ERR_sss),"Save",filename.c_str(),".");
                  return AMObj(AMObjType::UNDEF);
              };
              stream << " # -Geometry File-" << '\n';
              Printer _printer(stream,stream,stream);
              if(!_scene->isEmpty()&&view_mode!=2&&view_mode!=3)_scene->apply(_printer);
              if(!_qgc->isSceneEmpty()&&view_mode!=1&&view_mode!=3)_qgc->getScene()->apply(_printer);
              cerr << "Save Linetree on " << filename << '\n';
          }
          else if(!geomfilename.empty()){
              ofstream * geomstream = new ofstream(geomfilename.c_str());
              if (! (*geomstream)) {
                  genAMLError(ERRORMSG(K_F_FILE_ERR_sss),"Save",geomfilename.c_str(),".");
                  return AMObj(AMObjType::UNDEF);
              };

              ofstream * appstream, * shapestream ;
              if(!appfilename.empty()){
                  appstream = new ofstream(appfilename.c_str());
                  if (! (*appstream)) {
                      genAMLError(ERRORMSG(K_F_FILE_ERR_sss),"Save",appfilename.c_str(),".");
                      return AMObj(AMObjType::UNDEF);
                  };
              }
              else appstream = geomstream;
              if(!shapefilename.empty()){
                  shapestream = new ofstream(shapefilename.c_str());
                  if (! (*shapestream)) {
                      genAMLError(ERRORMSG(K_F_FILE_ERR_sss),"Save",shapefilename.c_str(),".");
                      return AMObj(AMObjType::UNDEF);
                  };
              }
              else shapestream = geomstream;

              *shapestream << '\n';
              if(!shapefilename.empty())
                  *shapestream << ":include " << geomfilename.c_str() << '\n';
              if(!appfilename.empty())
                  *shapestream << ":include " << appfilename.c_str() << '\n';
              *shapestream << '\n';

              Printer _printer(*shapestream,*geomstream,*appstream);
              if(!_scene->isEmpty()&&view_mode!=2&&view_mode!=3)_scene->apply(_printer);
              if(!_qgc->isSceneEmpty()&&view_mode!=1&&view_mode!=3)_qgc->getScene()->apply(_printer);
              cerr << "Save Geometry of Linetree on " << geomfilename << '\n';
              if(!appfilename.empty())cerr << "Save Appearance of Linetree on " << appfilename << '\n';
              if(!shapefilename.empty())cerr << "Save Shape of Linetree on " << shapefilename << '\n';
          }
          else
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s),"Save");
      break;
  }

  return AMObj(AMObjType::VOID);

}



AmlBoolean LineTree::makeLigFile(const Plant& plant,
                              const char* file_name,
                              const CorrTable& corr_table) const
{
  // Create the .lig file

  // Make the copy of the 80 first characters

  AmlBoolean result = FALSE;

  RWCString extended_name(file_name);

  size_t pos=extended_name.last('.');

  if (pos!=RW_NPOS)
  {
    extended_name.replace(pos,extended_name.length(),".lig");
  }
  else
  {
    extended_name+=".lig";
  }

  // Big Endian is use to generate old format .lig used only on SGI stations.
  beofstream* file=new beofstream (extended_name.data());

  if (file) {

//    if (file->Exists()){
//      file->Erase();
//    }

      file->write(protection,80);

    for (Scene::iterator it=_scene->getBegin();it!= _scene->getEnd(); it++) {
      ShapePtr _shape = dynamic_pointer_cast<Shape>(*it);;
      if(_shape){
        VId vtx = _shape->id;
        LineRecord record;

        size_t index=corr_table.index(vtx);
        SymbType symbol=corr_table.at(index).getSymbol();
        ValType range=corr_table.at(index).getRange();

        BranchElement branch_element = plant.searchForElement(vtx);

        if (branch_element.isValid()) {

        /*
          cout << "vertex " << vtx << endl;
          cout << "symbol " << symbol << endl;
          cout << "range " << range << endl;
          cout << "coords"; branch_element.getOrigin().report();
          cout << "direction primaire"; branch_element.getDirp().report();
          cout << "direction secondaire"; branch_element.getDirs().report();
          cout << "direction tertiaire"; branch_element.getDirt().report();
          cout << "topdia : " << branch_element.getTopDia() << endl;
          cout << "bottomdia : " << branch_element.getBotDia() << endl;
          cout << endl;
        */

          MyVector dirp = branch_element.getDirp();
          MyVector dirs = branch_element.getDirs();
          MyVector dirt = branch_element.getDirt();

/*                Vector3 _dirp(dirp[0],dirp[1],dirp[2]);
                  Vector3 _dirs(dirs[0],dirs[1],dirs[2]);
                  Vector3 _dirt(dirt[0],dirt[1],dirt[2]);
                  real_t n = _dirt.normalize();
                  _dirt = cross(_dirp,_dirs);
                  _dirt *= n;
                  dirt = MyVector(_dirt.x(),_dirt.y(),_dirt.z());*/

          writeRecord(symbol,
                      vtx,
                      (long int)range,
                                          dirp,
                      dirs,
                      dirt,
                      branch_element.getOrigin(),
                      branch_element.getTopDia(),
                      branch_element.getBotDia(),
                      record);

          // file->Write((char*) &record, sizeof(record));
          *file <<  record.symbol << record.val1 << record.val2 << record.range;
          for(int i=0;i<3;i++)
            for(int j=0;j<4;j++)
              *file <<  record.matrix[i][j];
          *file <<  record.base_dia <<  record.sommit_dia <<  record.entity_number;
        }
      }
    }

    cerr << "File: " << extended_name << " created" << '\n';

    result=TRUE;

  }
  else {

    result=FALSE;

    cout << APPL_MSG[LINE_ERR] << '\n';

  }

  delete file;

  return result;
}

AmlBoolean LineTree::makeInfFile(const MyVector& min,
                              const MyVector& max,
                              const char* file_name ) const
{

  AmlBoolean result=FALSE;
  IntType simplification=0;
  IntType seed=10;
  IntType age=5;
  IntType nbb=1;


  RWCString extended_name (file_name);

  IntType pos=extended_name.last('.');

  if (pos!=RW_NPOS)
  {
    extended_name.replace(pos, extended_name.length(), ".inf");
  }
  else
  {
    extended_name+=".inf";
  }

  ofstream inf_file(extended_name.data());

  if (!inf_file)
  {
    cerr << "Cannot open file " << extended_name << " for writing." << '\n';
    result=FALSE;
  }
  else
  {
    IntType nb=1;

    inf_file << "File : 1" << PROTECT_FILE_NAME << "\n";
    inf_file.precision(5);

    inf_file << "Age : " << age << "   " << nb << " pattern(s) number of branches " << nbb << '\n';
    inf_file << "Random_seed " << seed << " Simplification " << simplification << '\n';

    inf_file.precision(6);

    inf_file << max[0] << " " << max[1] << " " << max[2] << '\n';
    inf_file << min[0] << " " << min[1] << " " << min[2] << '\n';

    inf_file << "entre-noeud 1        nentn105  1" << '\n';

    inf_file.close();

    result=TRUE;

  }

  cerr << "File: " << extended_name << " created" << '\n';
  return result;

}

AmlBoolean LineTree::makeDtaFile(const ColorsTable& color_table,
                              const SymbLib& symb_lib,
                              const char* file_name) const
{

  AmlBoolean result=TRUE;

  RWCString extended_name (file_name);

  size_t pos=extended_name.last('.');

  if (pos!=RW_NPOS)
  {
    extended_name.replace(pos, extended_name.length(), ".dta");
  }
  else
  {
    extended_name+=".dta";
  }

  ofstream dta_file(extended_name.data());

  if (!dta_file)
  {
    cerr << "Cannot open file " << extended_name << " for writing." << '\n';
    result=FALSE;
  }
  else
  {
    IntType nb_colors=color_table.entries();
    SymbolsTable* list=new SymbolsTable;


    for(IntType i1=0;i1<nb_colors;i1++)
    {
      char a_symb=color_table.at(i1).getSymbol();

      MySymbol symbol=MySymbol (symb_lib.lookForASymbol(a_symb));
      if (!list->contains(symbol))
      {
        list->insert(symbol);
      }
     }

    char string[6];
    numberToString(nb_colors,string);
    dta_file << "   " << string << "  symbole(s)" << '\n';

  /*  IntType nb_symbols=list->entries();

    for(i=0;i<nb_symbols;i++)
    {
      RWCString pattern_file_name=list->at(i).getSymbolFileName();
      RWCString pattern_name=list->at(i).getSymbolName();

      dta_file << pattern_name << "                                     ";
      numberToString(i+1,string);
      dta_file << string  << "   " << pattern_file_name << "     1" << '\n';
    }*/

    for (IntType i2=0;i2<nb_colors;i2++)
    {
      char a_symb=color_table.at(i2).getSymbol();
      MySymbol symbol=MySymbol (symb_lib.lookForASymbol(a_symb));

      size_t index=list->index(symbol);

      assert(index!=RW_NPOS);

      RWCString pattern_file_name=list->at(index).getSymbolFileName();
      RWCString pattern_name=list->at(index).getSymbolName();

      dta_file << pattern_name << "                                     ";
      numberToString(i2+1,string);
      dta_file << string  << "   " << pattern_file_name << "     1" << '\n';
    }


    for(IntType i=0;i<nb_colors;i++)
    {
     /* char a_symb=color_table.at(i).getSymbol();
      MySymbol symbol(a_symb);
      IntType number=list->index(symbol)+1; */

      IntType number=i+1;
      MyVector compo;

      dta_file << "Symbole   " << number << '\n';

    /*  if (color_table.at(i).isInterpoled())
      {
        cout << "INTERPOLATION   " << color_table.at(i).getMax()-color_table.at(i).getMin() << '\n';
        dta_file << "INTERPOLATION   " << color_table.at(i).getMax()-color_table.at(i).getMin() << '\n';
      }*/

      compo=color_table.at(i).emissionComponent();
      dta_file << "EMISSION  " << compo[0] << " " << compo[1] << " " << compo[2] << '\n';
      compo=color_table.at(i).ambientComponent();
      dta_file << "AMBIENT   " << compo[0] << " " << compo[1] << " " << compo[2] << '\n';
      compo=color_table.at(i).diffuseComponent();
      dta_file << "DIFFUSE   " << compo[0] << " " << compo[1] << " " << compo[2] << '\n';
      compo=color_table.at(i).specularComponent();
      dta_file << "SPECULAR  " << compo[0] << " " << compo[1] << " " << compo[2] << '\n';
      ValType shine=color_table.at(i).shininessComponent();
      dta_file << "SHININESS " << shine << '\n';
    }


    delete list;
  }

  cerr << "File: " << extended_name << " created" << '\n';

  return result;
}


/*
AmlBoolean LineTree::makeArcFile(const Plant& plant,
                              const char* file_name)
{
  return TRUE;
}

*/

AmlBoolean LineTree::saveAsXML(const char* file_name) const
{
  ofstream stream(file_name);
  if(!stream)return FALSE;

  // table defining a list of pairs of class and "standard" AML colors
  // (char, diffuse, ambiant, specular, shininess)
  // This table was computed by the Dresser constructor (which builds a Painter, ...)
  // just before the LineTree constructor is built

  // const ColorsTable* color_table=&_dr->getColorsTable();

  // table for class defined by SMB symbol = (char, smb_filename)

  // const SymbLib* symb_list=&_dr->getSymbLib();

  // table defining for each vtx an index in array color_table, containing a material
  // (vtx, index_in_color_table)

  const CorrTable* corr_table=&_dr->getCorrTable();

  // This function computes an array associating
  // each Class of entity with a Geometry and a Material
  // These values may be override subsequently by geomptr() and matptr()
  // (see below)

  // createBaseShapeList(_dr, *color_table, *symb_list, _base_symbol_list);

  // the plantframe contains both the _plant (topology)
  // and the _geomcomputer (module computing the plant geometry)

  const Plant* plant = _pf->_plant;
  const MTG * _mtg = plant->getMtg();

  string indent;
  string IND = "    ";
  int size_ind = IND.size();

  IntType nb=plant->nbBranches();
  stream  << "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" << '\n';
  stream  << "<HEADER>" << '\n';
  indent+=IND;
  stream  << indent << "<meta name='filename' content='" << file_name << "'/>" << '\n';
#ifdef __GNUC__
  stream  << indent << "<meta name='author' content='" << getenv("LOGNAME") << "'/>" << '\n';
  time_t temps;
  struct tm * tm;
  time (& temps);
  tm = localtime ( &temps);
  stream  << indent << "<meta name='revised' content='" << tm->tm_mday<< " " << tm->tm_mon << " " << (1900 + (tm->tm_year)) << "'/>" << '\n';
#endif
  stream  << indent << "<meta name='generator' content='AMAPmod'/>" << '\n';
  indent.erase(indent.end() - size_ind,indent.end());
  stream  << "</HEADER>" << '\n';
  stream  << indent << "<Plant>" << '\n';
  indent+=IND;

  GeometryPtr __default_geom(new Cylinder(1,1,false));
  __default_geom->setName("DefaultGeom");
  Discretizer dis;
  X3DPrinter x3dprinter(stream,dis);

  for (IntType i=0;i<nb;i++)
    {

      // cerr << "branch nb =" << i << '\n';
      const Branch branch = plant->findBranch(i);
      const BranchCompoList branch_compo_list = branch.branchComponents();

      IntType number=branch_compo_list.entries();

      // Loop on all the branch vertices
      int vtx;
      int _order;

      for (IntType j=0;j<number;j++)
        {

          // cerr << "\t vertex nb =" << j << '\n';

          BranchElement branch_element=branch_compo_list.at(j);
          vtx = branch_element.getVertex();

          if(j == 0){
            _order = _mtg->si_order(vtx);
            if(_order==0){
              stream << indent << "<Trunk>" << '\n';
              indent+=IND;
            }
            else {
              VId _father = _mtg->si_father(vtx);
              stream << indent << "<Axe Id='" << i << "' Order='" << _order << "' Father='" << _father << "' >" << '\n';
              indent+=IND;
            }
          }
          stream << indent << "<Node Id='" << vtx << "'" << '\n';

          AMObjVector argobjs(1);
          argobjs[0] = AMObj(AMObjType::VTX, vtx);

          if (branch_element.isValid()) {

            /*****  SHAPE OF THE ELEMENT ********/

            // For each vertex, corr_table contains an index into the color array which
            // enables us to retreive the "shape"( =(geometry,color) ) of this vertex.


            size_t index=corr_table->index(vtx); // index of vtx in coor_table

            // index in the color_table of the geometric information associated to this vertex
            SymbType symbol_index=corr_table->at(index).getSymbol()-1; // stored from 1 to N

            /***** 1. GEOMETRY OF THE ELEMENT ********/


            /***** ORIENTATION AND LOCATION OF THE ELEMENT ********/

            MyVector origin = branch_element.getOrigin();
            stream << indent << "      " << "Origin='" << origin[0] << " " << origin[1]<< " " << origin[2]<< "'" << '\n';
            MyVector v1 = branch_element.getDirp();      // ATTENTION NORME !!
            MyVector v2 = branch_element.getDirs();
            MyVector v3 = branch_element.getDirt();

            real_t length = (real_t) v1.computeLength();
            v1.norm();
            v2.norm();
            v3.norm();

            stream << indent << "      " << "OrientationP='" << v2[0] << " " << v2[1]<< " " << v2[2]<< "'" << '\n';
            stream << indent << "      " << "OrientationS='" << v3[0] << " " << v3[1]<< " " << v3[2]<< "' " << '\n';
            stream << indent << "      " << "OrientationT='" << v1[0] << " " << v1[1]<< " " << v1[2]<< "' " << '\n';
            stream << indent << "      " << "Length='" << length << "' " << '\n';

            real_t radius_top = (real_t) branch_element.getTopDia(); // radius.
            real_t radius_bot = (real_t) branch_element.getBotDia();
            stream << indent << "      " << "TopDiameter='" << radius_top << "' " << '\n';
            stream << indent << "      " << "BottomDiameter='" << radius_bot << "'>" << '\n';
            indent+=IND;

            /***** GEOMETRY OF THE ELEMENT ********/

            // First check whether the geometry has been defined by a geometry function
            // passed as an argument to Plot(f, Geometry->geomfun)

            GeometryPtr geom = _dr->computeGeometry(vtx);
            stream << indent << "<geometry>" << '\n';
            indent+=IND;
            if(geom){
              geom->apply(dis);
              dis.getDiscretization()->apply(x3dprinter);
              // stream << indent << "<Geometry USE='" << geom->getName() <<"' />" << '\n';
            }
            else {
              x3dprinter.addIndent(indent.size());
              __default_geom->apply(x3dprinter);
            }
            indent.erase(indent.end() - size_ind,indent.end());
            stream << indent << "</geometry>" << '\n';
            /***** 2. MATERIAL OF THE ELEMENT ********/

            MaterialPtr pmat;

            bool mat_not_default = matptr(vtx, symbol_index, pmat);

            stream  << indent << "<appereance>" << '\n';
            indent+=IND;
            if (!mat_not_default)
              pmat->setName("DefaultMat");
            x3dprinter.addIndent(indent.size());
            pmat->apply(x3dprinter);
            indent.erase(indent.end() - size_ind,indent.end());
            stream  << indent << "</appereance>" << '\n';
            indent.erase(indent.end() - size_ind,indent.end());
            stream  << indent << "</Node>" << '\n';
          }
          else {
            stream << "/>" << '\n';
          }
        }
      indent.erase(indent.end() - size_ind,indent.end());
      if(_order == 0)stream  << indent << "</Trunk>" << '\n';
      else stream  << indent << "</Axe>" << '\n';
    }
  indent.erase(indent.end() - size_ind,indent.end());
  stream  << indent << "</Plant>" << '\n';
  return TRUE;
}


void LineTree::writeRecord(const SymbType symbol,
                           const LongType entity_number,
                           const LongType range,
                           const MyVector dirp,
                           const MyVector dirs,
                           const MyVector dirt,
                           const MyVector origin,
                           const ValType sommit_dia,
                           const ValType base_dia,
                           LineRecord& result) const
{
  result.symbol=symbol;
  result.entity_number=entity_number;
  result.range=range;
  result.sommit_dia=sommit_dia;
  result.base_dia=base_dia;
  result.val1=1;
  result.val2=1;

  for(IntType i=0;i<3;i++)
  {
    result.matrix[i][0]=dirp[i];
    result.matrix[i][1]=dirs[i];
    result.matrix[i][2]=dirt[i];
    result.matrix[i][3]=origin[i];
  }
}

void LineTree::numberToString( ValType number, char* result) const
{
  IntType i=(IntType)number;
  char chaine[6];
  int nb;
  char chaine2[6];

  i=IntType(number);
  numberToString(i,chaine);
  result[1]='.';
  result[0]=chaine[0];
  i=IntType((number-i)*1000);
  numberToString(i,chaine);
  nb=strlen(chaine);

  for (i=0;i<3-nb;i++)
  {
    chaine2[i]='0';
  }
  for (i=0;i<nb;i++)
  {
    chaine2[i+3-strlen(chaine)]=chaine[i];
  }
  for (i=0;i<3;i++)
  {
    result[i+2]=chaine2[i];
  }
  result[5]=(char)(0);
}

void LineTree::numberToString(IntType number,char* result) const
{
  // Number must be less than 9999 and more or equal to 0.

  IntType i;
  ValType f=number;
  ValType fact;
  IntType nb;
  IntType j;

  if (number<=9)
  {
    fact=1;nb=1;
  }
  if (number>9)
  {
    fact=10;nb=2;
  }
  if (number>99)
  {
    fact=100;nb=3;
  }
  if (number>999)
  {
    fact=1000;nb=4;
  }

  f=number/fact;

  for (i=1;i<=nb;i++)
  {
    j=(IntType)f;
    result[i-1]=(char)(j+48);
    //f=(f-j)*10;
    number=number-j*(IntType)fact;
    fact=fact/10;
    f=number/fact;
  }
  result[i-1]=(char)(0);
}

  const ScenePtr LineTree::getMacroScene() const {
    if(_qgc) return _qgc->getScene();
    return ScenePtr();
  };
