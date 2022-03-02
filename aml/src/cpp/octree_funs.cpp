/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): F. Boudon (frederic.boudon@cirad.fr)
 *
 *       $Source$
 *       $Id: octree_funs.cpp 3573 2007-09-05 16:59:56Z dufourko $
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

#include "aml/parseraml.h"
#include "aml/fnode.h"
#include "aml/array.h"

#include "aml/kernel_funs.h"
#include "aml/kernel_err.h"
#include "aml/octree_funs.h"

#include "MSVoxel/mvs_octree.h"
#include "GEOM/view_application.h"

#include "MTG/linetree.h"

TOOLS_USING_NAMESPACE

#define  MODULE_NAME            "OCTREE"
#define  ERR_MSG_ARRAY          octree_err_msgs_aml

enum OCTREE_ERRORLABEL {
  OCTREE_OPTION_BADVALUE_s
};

const char *octree_err_msgs_aml[] = {
  "Option %s: bad value"// OCTREE_OPTION_BADVALUE_s
};

struct conditionPlane
{

public :

  bool operator()(const OctreeNode * a) const {
    if(a->getType() == Tile::Empty || a->getType() == Tile::Undetermined)return false;
    if(quarter &&
       a->getLowerLeftCorner().x() - plan.x() >= - GEOM_EPSILON &&
       a->getLowerLeftCorner().y() - plan.y() >= - GEOM_EPSILON &&
       a->getLowerLeftCorner().z() - plan.z() >= - GEOM_EPSILON
             ){
      return false;
    }
    if(a->getScale() <= scale)return true;
    else return false;
  }

  bool quarter;
  uint32 scale;
  Vector3 plan;
};

struct conditionPlane2
{
public :

  bool operator()(const OctreeNode * a) const {
    if(a->getType() == Tile::Empty ) return false;
    if(a->isDecomposed() && a->getScale() < scale ) return false;
    if(quarter &&
       a->getLowerLeftCorner().x() -  plan.x() >= - GEOM_EPSILON &&
       a->getLowerLeftCorner().y() -  plan.y() >= - GEOM_EPSILON &&
       a->getLowerLeftCorner().z() -  plan.z() >= - GEOM_EPSILON
       )return false;
    if(a->getScale() <= scale)return true;
    else return false;
  }

  bool quarter;
  uint32 scale;
  Vector3 plan;
};

struct conditionPlane3
{
public :
  bool operator()(const OctreeNode * a) const {
    if(a->isDecomposed()  && a->getScale() < scale) return false;
    if(quarter &&
       a->getLowerLeftCorner().x() - plan.x() >= - GEOM_EPSILON &&
       a->getLowerLeftCorner().y() - plan.y() >= - GEOM_EPSILON &&
       a->getLowerLeftCorner().z() - plan.z() >= - GEOM_EPSILON
       )return false;
    if(a->getScale() <= scale)return true;
    else return false;
    return true;
  }

  bool quarter;
  uint32 scale;
  Vector3 plan;
};


class AML_OCTREE : public Octree, public AMModel {

public:

  AML_OCTREE(const ScenePtr& scene,uint32 maxscale): Octree(scene,maxscale) {}

  virtual ostream& displayOneLine(ostream& o) const
  {
    return o << "Center = " << getCenter() << ", Size = " << getSize() << ", Shapes = " << getScene()->getSize() << ", Depth = " << getDepth() << ".";
  }

  virtual ostream& display(ostream& o, int line_size = 0) const {
    return displayOneLine(o);
  }

  virtual AMObj display(ostream& o, const AMObjVector& args) const
  {
    assert(&args);
    display(o);
    return AMObj(AMObjType::VOID);
  }

  virtual AMObj plot(GP_window&, const AMObjVector& args) const
  {
    int argth = 1;
    int len = args.length();
    ViewerApplication app;
    ScenePtr scene;
    CHECKCONDVA(len > 0 && len <= 6,
             genAMLError(ERRORMSG(K_NB_ARG_ERR_ssd), "Plot", "1", 6));

    int view_mode = 0;
    Vector3 plane(__center);
    plane -= Vector3(fabs(plane.x())/100,fabs(plane.y())/100,fabs(plane.z())/100);
    bool quarter = false;
    uint32 scale = __maxscale;

    while (argth < args.length()) { // treatment of options

      CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Plot", (argth+1)/2+1));

/*      CHECKCONDVA(args[argth].tag() == AMObjType::STRING,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "Display, Scale or Cut"));*/

      if (*(AMString*)(args[argth].val.p) == "Display") {
        CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "a STRING"));

        if (*(AMString*)(args[argth+1].val.p) == "All") {
          view_mode = 0;
        }
        else if (*(AMString*)(args[argth+1].val.p) == "Intersected") {
          view_mode = 1;
        }
        else if (*(AMString*)(args[argth+1].val.p) == "Filled") {
          view_mode = 2;
        }
        else {
          genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "All, Intersect or Filled");
        }
        argth +=2;
      }
      else if (*(AMString*)(args[argth].val.p) == "Cut") {
        CHECKCONDVA(args[argth+1].tag() == AMObjType::ARRAY || args[argth+1].tag() == AMObjType::BOOL ,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "an ARRAY or a BOOL"));
        if(args[argth+1].tag() == AMObjType::BOOL){
          quarter = (bool)(args[argth+1].val.b);
        }
        else {
          Array* ar = (Array*)(args[argth+1].val.p);
          if(ar->entries() != 3 || (ar->at(0).tag() != AMObjType::REAL && ar->at(0).tag() != AMObjType::INTEGER)
             || (ar->at(1).tag() != AMObjType::REAL && ar->at(1).tag() != AMObjType::INTEGER)
             || (ar->at(2).tag() != AMObjType::REAL && ar->at(2).tag() != AMObjType::INTEGER)  ){
            genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "ARRAY3 of REAL");
          }
          else {
            quarter = true;
            if(ar->at(0).tag() == AMObjType::REAL)
              plane.x() = (real_t)(ar->at(0).val.r);
            else
              plane.x() = (real_t)(int)(ar->at(0).val.i);

            if(ar->at(1).tag() == AMObjType::REAL)
              plane.y() = (real_t)(ar->at(1).val.r);
            else
              plane.y() = (real_t)(int)(ar->at(1).val.i);

            if(ar->at(2).tag() == AMObjType::REAL)
              plane.z() = (real_t)(ar->at(2).val.r);
            else
              plane.z() = (real_t)(int)(ar->at(2).val.i);
          }
        }
        cerr << "Cutting Plane = " << plane << endl;
        argth +=2;

      }
      else if (*(AMString*)(args[argth].val.p) == "Scale") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

        CHECKCONDVA(args[argth+1].val.i > 0,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "positive"));

        scale = (uint32)args[argth+1].val.i;


        argth +=2;
      }
      else {
        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Plot", (argth+1)/2+1));
      }
    }
    if(view_mode == 1){
      conditionPlane2 a;
      a.quarter = quarter;
      if(scale !=0)a.scale = scale;
      scene = getCondRepresentation(a);
    }
    else if(view_mode == 2){
      conditionPlane a;
      a.quarter = quarter;
      if(scale !=0)a.scale = scale;
      scene = ScenePtr(getCondRepresentation(a));
    }
    else {
      conditionPlane3 a;
      a.quarter = quarter;
      if(quarter) a.plan = plane;
      if(scale !=0)a.scale = scale;
      scene = ScenePtr(getCondRepresentation(a));
    }
    app.display(scene);
    return AMObj(AMObjType::VOID);
  }

  virtual AMObj print(const AMObjVector& args) const
  {
    assert(&args);
    cerr << "Not yet Implemented" << endl;
    return AMObj(AMObjType::VOID);
  }

  virtual AMObj save(const AMObjVector& args) const
  {
    assert(&args);
    cerr << "Not yet Implemented" << endl;
    return AMObj(AMObjType::VOID);
  }

};

// --------------
//  Constructors
// --------------

static AMObj OCT_OCTREE(const AMObjVector& args) {
  int argth = 1;
  int len = args.length();
  int depth = 5;
  int data = 0;
  LineTree * lt = NULL;
  string filename;

  CHECKCONDVA(len > 0 && len <= 5,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ssd), "OCTREE", "1", 5));


   if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

   CHECKCONDVA(args[0].tag() ==AMObjType::LINETREE || args[0].tag() ==AMObjType::STRING,
               genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "OCTREE", args[0].tag.string().data(), "LINETREE or Filename"));

   if(args[0].tag() == AMObjType::LINETREE)
     lt = (LineTree *)(args[0].val.p);
   else
     filename = ((AMString*)(args[0].val.p))->data();

   while (argth < args.length()) { // treatment of options

     CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                 genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "OCTREE", (argth+1)/2+1));

     if (*(AMString*)(args[argth].val.p) == "Depth") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "OCTREE", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      CHECKCONDVA(args[argth+1].val.i >= 0,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "OCTREE", (argth+1)/2+1, "positive"));

      depth = args[argth+1].val.i;

     }
     else if (lt && *(AMString*)(args[argth].val.p) == "Data") {

       CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "OCTREE", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

       if (*(AMString*)(args[argth+1].val.p) == "All") {
         data = 2;
       }
       else if (*(AMString*)(args[argth+1].val.p) == "MicroOnly") {
         data = 0;
       }
       else if (*(AMString*)(args[argth+1].val.p) == "MacroOnly") {
         data = 1;
       }
       else {
         genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "All, MicroOnly or MacroOnly");
       }
     }
     else {
       CHECKCONDVA(FALSE,
                   genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Octree", (argth+1)/2+1));
     }
     argth +=2;
   }
   ScenePtr scene;
   if(lt){
     if(data == 2){
       scene = lt->getScene();
       scene->merge(lt->getMacroScene());
     }
     else if (data == 1){
       scene = lt->getMacroScene();
     }
     else {
       scene = lt->getScene();
     }
   }
   else scene = ScenePtr(new Scene(filename));
   AML_OCTREE * octree = new AML_OCTREE(scene,depth);
   return AMObj(AMObjType::OCTREE,octree);
}

static AMObj OCT_Volume(const AMObjVector& args) {

  int argth = 1;
  int len = args.length();
  int scale = -1;
  bool detail = false;
  bool mode = true;

  CHECKCONDVA(len > 0 && len <= 5,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ssd), "Volume", "1", 5));

   if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

   CHECKCONDVA(args[0].tag() ==AMObjType::OCTREE,
               genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Volume", args[0].tag.string().data(), "Octree"));


    AML_OCTREE * octree = (AML_OCTREE *)(args[0].val.p);

   while (argth < args.length()) { // treatment of options

     CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                 genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "OCTREE", (argth+1)/2+1));

     if (*(AMString*)(args[argth].val.p) == "Scale") {

       CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                   genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Volume", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

       CHECKCONDVA(args[argth+1].val.i >= 0,
                   genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Volume", (argth+1)/2+1, "positive"));

       scale = (uint32)args[argth+1].val.i;

     }
     if (*(AMString*)(args[argth].val.p) == "Voxel") {

       CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING || args[argth+1].tag() ==AMObjType::FNODE,
                   genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Volume", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));
       if ((args[argth+1].tag() ==AMObjType::STRING && *(AMString*)(args[argth+1].val.p) == "Size")||
           (args[argth+1].tag() ==AMObjType::FNODE && ((FNode*)(args[argth+1].val.p))->name() == ":Size")){
         detail = true;
         mode = false;
       }
       else if ((args[argth+1].tag() ==AMObjType::STRING && *(AMString*)(args[argth+1].val.p) == "Count")||
                (args[argth+1].tag() ==AMObjType::FNODE && ((FNode*)(args[argth+1].val.p))->name() == ":Count")) {
         detail = true;
         mode = true;
       }
       else {
         genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Volume", (argth+1)/2+1, "Size or Count");
        }
     }
     argth +=2;
   }
   if(detail){
     Array* ret = new SLArray;
     if(mode){
       vector< vector<uint32> > res = octree->getDetails();
       if(scale < 0 || scale > octree->getDepth()){
         cerr << "1" << endl;
         for( int i = 0 ; i < res.size();i++){
           Array* ret2 = new SLArray;
           for( int j = 0 ; j < res[i].size();j++){
             (*ret2) += AMObj(AMObjType::INTEGER,(int)res[i][j]);
           }
           (*ret) += AMObj(AMObjType::ARRAY,ret2);
         }
       }
       else {
         cerr << "2" << endl;
         for( int j = 0 ; j < res[scale].size();j++){
           (*ret) += AMObj(AMObjType::INTEGER,(int)res[scale][j]);
         }
       }
     }
     else {
       vector< Vector3 > res = octree->getSizes();
       if(scale < 0 || scale > octree->getDepth()){
         for( int i = 0 ; i < res.size();i++){
           Array* ret2 = new SLArray;
           (*ret2) += AMObj(AMObjType::REAL,res[i].x());
           (*ret2) += AMObj(AMObjType::REAL,res[i].y());
           (*ret2) += AMObj(AMObjType::REAL,res[i].z());
           (*ret) += AMObj(AMObjType::ARRAY,ret2);
         }
       }
       else {
         (*ret) += AMObj(AMObjType::REAL,res[scale].x());
         (*ret) += AMObj(AMObjType::REAL,res[scale].y());
         (*ret) += AMObj(AMObjType::REAL,res[scale].z());
       }
     }
     return AMObj(AMObjType::ARRAY,ret);
   }
   else {
     real_t vol = octree->getVolume(scale);
     return AMObj(AMObjType::REAL,vol);
   }
}


void installOCTREEModule() {

  AMObjType type[10];          // max number of arguments
  AMObj var;
  RWCString varname;


  // OCTREE functions

  type[0] = AMObjType::ANY;
  installFNode("Octree", OCT_OCTREE, 1, type, AMObjType::OCTREE);

  type[0] = AMObjType::OCTREE;
  installFNode("Volume", OCT_Volume, 1, type, AMObjType::REAL);

}
