/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): F. Godin & O. Puech (godin@cirad.fr)
 *
 *       $Source$
 *       $Id: msvoxel_funs.cpp 3573 2007-09-05 16:59:56Z dufourko $
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
#include "aml/msvoxel_funs.h"

#include "msvoxel/mvs_msvoxel.h"
#include "plantgl/algo/grid/octree.h"

#include "plantgl/gui/viewer/pglapplication.h"

#include "mtg/linetree.h"

#include "aml/geomscene_funs.h"

TOOLS_USING_NAMESPACE
using namespace std;

#define  MODULE_NAME            "MSVOXEL"
#define  ERR_MSG_ARRAY          msvoxel_err_msgs_aml

 // ******************* FFT ***********************************
Array* FFT(vector<map<const int, double> >& input, int mode)
{
  Array* output = new SLArray;
  for( int j = 0 ; j < input.size() ; j++){
    Array* ret2 = new SLArray;
    map<const int, double>::iterator it;
             
    int k = 0;
    int k2 = 0;

    // sizeJ
    while(k < input[j].size())
	  {
      it = input[j].find(k2);
      if(it != input[j].end()) k++;
      k2++;
    }
    int sizeJ = k2;
//    realFFTData fftData(sizeJ);
 //   realFFT rfft(&fftData);
           
    // FFT input
    k2 = 0;
    while(k2 < sizeJ)
	  {
       it = input[j].find(k2);
    /*  if(it != input[j].end())
        fftData.in[k2] = real_t( (*it).second ) ;
      else fftData.in[k2] = 0 ;
      */
     // fftData.in[k2] = cos(k2*6*2*pi/sizeJ);
      k2++;
    }
          
    // FFT output
//    rfft.fwdTransform(); 
    k2 = 0;
    if(mode ==0)
/*      while(k2 < sizeJ) (*ret2) += AMObj( AMObjType::REAL, fftData.out[k2++]); 
    else
    {
      fftData.compPowerSpec();
      while(k2 < (sizeJ+1)/2) (*ret2) += AMObj( AMObjType::REAL, fftData.power_spectrum[k2++]); 
    }
*/
    (*output) += AMObj(AMObjType::ARRAY, ret2) ;
  }
  return output;
}
Array* FFT(vector<map<const int, long> >& input, int mode)
{
  Array* output = new SLArray;
  for( int j = 0 ; j < input.size() ; j++){
    Array* ret2 = new SLArray;
    map<const int, long>::iterator it;
             
    int k = 0;
    int k2 = 0;

    // sizeJ
    while(k < input[j].size())
	  {
      it = input[j].find(k2);
      if(it != input[j].end()) k++;
      k2++;
    }
    int sizeJ = k2;
//    realFFTData fftData(sizeJ);
 //   realFFT rfft(&fftData);
           
    // FFT input
    k2 = 0;
    while(k2 < sizeJ)
	  {
      it = input[j].find(k2);
    /*  if(it != input[j].end())
        fftData.in[k2] = real_t( (*it).second ) ;
      else fftData.in[k2] = 0 ;*/
      
     
      k2++;
    }
          
    // FFT output
//    rfft.fwdTransform();
    
    //fftData.sqrtPowerSpec () ;
    k2 = 0;
 /*   if(mode ==0)
      while(k2 < sizeJ) (*ret2) += AMObj( AMObjType::REAL, fftData.out[k2++]); 
    else
    {
      fftData.compPowerSpec();
      while(k2 < (sizeJ+1)/2) (*ret2) += AMObj( AMObjType::REAL, fftData.power_spectrum[k2++]); 
    }
*/
    (*output) += AMObj(AMObjType::ARRAY, ret2) ;
  }
  return output;
}
// ******************************

enum MSVOXEL_ERRORLABEL {
  MSVOXEL_OPTION_BADVALUE_s,
  MSVOXEL_OPTION_NB_ARG_ERR_sd
};

const char *msvoxel_err_msgs_aml[] = {
  "Option %s: bad value", // MSVOXEL_OPTION_BADVALUE_s
          "Erreur %s nb arg %d " // MSVOXEL_OPTION_NB_ARG_ERR_sd
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
  uint32_t scale;
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
  uint32_t scale;
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
  uint32_t scale;
  Vector3 plan;
};


struct conditionPlaneMSVoxel
{

public :

  bool operator()(const MSVoxelNode * a) const {
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
  uint32_t scale;
  Vector3 plan;
};

struct conditionPlane2MSVoxel
{
public :

  bool operator()(const MSVoxelNode * a) const {
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
  uint32_t scale;
  Vector3 plan;
};

struct conditionPlane3MSVoxel
{
public :
  bool operator()(const MSVoxelNode * a) const {
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
  uint32_t scale;
  Vector3 plan;
};

// =================
//  Class OCTREE
// =================

class AML_OCTREE : public Octree, public AMModel {

public:

  AML_OCTREE(const ScenePtr& scene,uint32_t maxscale): Octree(scene,maxscale) {}

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

  virtual AMObj plot(GP_window&, const AMObjVector& args) const;

  virtual AMObj extract(const AMObjVector& args) const;

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
	  cerr << "Depth = " << depth << endl;

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

AMObj AML_OCTREE::plot(GP_window&, const AMObjVector& args) const
  {
    int argth = 1;
    int len = args.length();
    PGLViewerApplication app;
    ScenePtr scene;
    CHECKCONDVA(len > 0 && len <= 6,
             genAMLError(ERRORMSG(K_NB_ARG_ERR_ssd), "Plot", "1", 6));

    int view_mode = 0;
    Vector3 plane(__center);
    plane -= Vector3(fabs(plane.x())/100,fabs(plane.y())/100,fabs(plane.z())/100);
    bool quarter = false;
    uint32_t scale = __maxscale;

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

        scale = (uint32_t)args[argth+1].val.i;


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
      scene = getCondRepresentation(*this,a);
    }
    else if(view_mode == 2){
      conditionPlane a;
      a.quarter = quarter;
      if(scale !=0)a.scale = scale;
      scene = ScenePtr(getCondRepresentation(*this,a));
    }
    else {
      conditionPlane3 a;
      a.quarter = quarter;
      if(quarter) a.plan = plane;
      if(scale !=0)a.scale = scale;
      scene = ScenePtr(getCondRepresentation(*this,a));
    }
    app.display(scene);
    return AMObj(AMObjType::VOID);
  }

AMObj AML_OCTREE::extract(const AMObjVector& args) const {

  int argth = 1;
  int len = args.length();
  int scale = -1;
  bool detail = false;
  bool mode = true;

  CHECKCONDVA(len > 0 && len <= 5,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ssd), "Extract", "1", 5));

   if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

   CHECKCONDVA(args[0].tag() ==AMObjType::OCTREE,
               genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Extract", args[0].tag.string().data(), "Octree"));


    AML_OCTREE * octree = (AML_OCTREE *)(args[0].val.p);

   while (argth < args.length()) { // treatment of options

     CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                 genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "OCTREE", (argth+1)/2+1));

     if (*(AMString*)(args[argth].val.p) == "Scale") {

       CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                   genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

       CHECKCONDVA(args[argth+1].val.i >= 0,
                   genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "positive"));

       scale = (uint32_t)args[argth+1].val.i;

     }
     if (*(AMString*)(args[argth].val.p) == "Voxel") {

       CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING || args[argth+1].tag() ==AMObjType::FNODE,
                   genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));
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
         genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "Size or Count");
        }
     }
     argth +=2;
   }
   if(detail){
     Array* ret = new SLArray;
     if(mode){
       vector< vector<uint32_t> > res = octree->getDetails();
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



// ================
// CLASS MSVOXEL
// ================

class AML_MSVOXEL : public MSVoxel, public AMModel {

public:

  AML_MSVOXEL(const ScenePtr& scene, vector<int> splittingList, Vector3 Center, Vector3 Size, uint32_t maxscale): MSVoxel(scene, splittingList, Center, Size, maxscale ) {}

  virtual ostream& displayOneLine(ostream& o) const
  {
     o << "Center = " << getCenter() << ", Size = " << getSize() << ", Shapes = " << getScene()->getSize() << ", Depth = " << getDepth()
                << ", SplittingList Size = " << getSplittingList().size() <<", DivisionSteps[ ";
         for(int i = 0; i < getSplittingList().size() ; i++)
                 o << getSplittingList()[i] <<" ";
         o << "].";
         return o;

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

  virtual AMObj plot(GP_window&, const AMObjVector& args) const;

  virtual AMObj extract(const AMObjVector& args) const;

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

static AMObj MSV_MSVOXEL(const AMObjVector& args) {

  int argth = 1;
  int len = args.length();
  int depth = 5;
  int data = 0;
  int max_elements = 0;

  Array* arrayTmp = NULL;
  vector<int> steps_array;
  Vector3 Center(0,0,0);
  Vector3 Size(0,0,0);
  LineTree * lt = NULL;
  AML_GeomScene * gs = NULL;
  string filename;

  CHECKCONDVA(len > 0 && len <= 10,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ssd), "MSVOXEL", "1", 10));


   if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

   CHECKCONDVA(args[0].tag() ==AMObjType::LINETREE || args[0].tag() ==AMObjType::GEOMSCENE || args[0].tag() ==AMObjType::STRING,
               genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "MSVOXEL", args[0].tag.string().data(), "LINETREE or Filename"));

   if(args[0].tag() == AMObjType::LINETREE)
     lt = (LineTree *)(args[0].val.p);
   else if( args[0].tag() == AMObjType::GEOMSCENE)
         gs = (AML_GeomScene *)(args[0].val.p);
   else
     filename = ((AMString*)(args[0].val.p))->data();

   while (argth < args.length()) { // treatment of options

     CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                 genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "MSVOXEL", (argth+1)/2+1));

     if (*(AMString*)(args[argth].val.p) == "Depth") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MSVOXEL", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      CHECKCONDVA(args[argth+1].val.i >= 0,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "MSVOXEL", (argth+1)/2+1, "positive"));

      depth = args[argth+1].val.i;

     }
     else if (*(AMString*)(args[argth].val.p) == "StopDecompositionNbElements") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MSVOXEL", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      CHECKCONDVA(args[argth+1].val.i >= 0,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "MSVOXEL", (argth+1)/2+1, "positive"));

      max_elements = args[argth+1].val.i;

     }
     else if (*(AMString*)(args[argth].val.p) == "DivisionSteps") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::ARRAY,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY"));

      if (args[argth+1].val.p) {

        arrayTmp = ((Array*)(args[argth+1].val.p));

        CHECKCONDVA(arrayTmp->surfaceType() ==AMObjType::INTEGER,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY(INT)"));

        ArrayIter* pnext = arrayTmp->iterator();
        ArrayIter& next = *pnext;
        while (next()) {
          steps_array.push_back(next.key().val.i);
        }
                delete pnext;

      }

    }
     else if (*(AMString*)(args[argth].val.p) == "Center") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::ARRAY,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY"));

      if (args[argth+1].val.p) {

        arrayTmp = ((Array*)(args[argth+1].val.p));

        CHECKCONDVA(arrayTmp->surfaceType() ==AMObjType::REAL,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY(REAL)"));

        ArrayIter* pnext = arrayTmp->iterator();
        ArrayIter& next = *pnext;
        int k=0;
        while (next() && (k<3)) {
          Center.setAt(k++,next.key().val.r);
        }
                delete pnext;

      }

    }
     else if (*(AMString*)(args[argth].val.p) == "Size") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::ARRAY,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY"));
      if (args[argth+1].val.p) {

        arrayTmp = ((Array*)(args[argth+1].val.p));
        CHECKCONDVA(arrayTmp->surfaceType() ==AMObjType::REAL,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY(REAL)"));
        ArrayIter* pnext = arrayTmp->iterator();
        ArrayIter& next = *pnext;
        int k=0;
        while (next() && (k<3)) {
          Size.setAt(k++, next.key().val.r);
        }
		delete pnext;

      }

    }
     else if (lt && *(AMString*)(args[argth].val.p) == "Data") {

       CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MSVOXEL", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

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
                   genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "MSVoxel", (argth+1)/2+1));
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
   else if(gs){
           scene = gs;
   }
   else scene = ScenePtr(new Scene(filename));

   AML_MSVOXEL * msvoxel = new AML_MSVOXEL(scene,steps_array,Center,Size,depth);

   return AMObj(AMObjType::MSVOXEL,msvoxel);
}

AMObj AML_MSVOXEL::plot(GP_window&, const AMObjVector& args) const
  {
    int argth = 1;
    int len = args.length();
    PGLViewerApplication app;
    ScenePtr scene;
    CHECKCONDVA(len > 0 && len <= 6,
             genAMLError(ERRORMSG(K_NB_ARG_ERR_ssd), "Plot", "1", 6));

    int view_mode = 0;
    Vector3 plane(__center);
    plane -= Vector3(fabs(plane.x())/100,fabs(plane.y())/100,fabs(plane.z())/100);
    bool quarter = false;
    uint32_t scale = __maxscale;

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

        scale = (uint32_t)args[argth+1].val.i;


        argth +=2;
      }
      else {
        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Plot", (argth+1)/2+1));
      }
    }

        scene = getScene();
    if(view_mode == 1){
      conditionPlane2MSVoxel a;
      a.quarter = quarter;
      if(scale !=0)a.scale = scale;
      //scene->merge(getCondRepresentation(a));
      scene = getCondRepresentation(*this,a);
    }
    else if(view_mode == 2){
      conditionPlaneMSVoxel a;
      a.quarter = quarter;
      if(scale !=0)a.scale = scale;
      //scene->merge(getCondRepresentation(a));
      scene = getCondRepresentation(*this,a);
    }
    else {
      conditionPlane3MSVoxel a;
      a.quarter = quarter;
      if(quarter) a.plan = plane;
      if(scale !=0)a.scale = scale;
      //scene->merge(getCondRepresentation(a));
      scene = getCondRepresentation(*this,a);
    }
    app.display(scene);
    return AMObj(AMObjType::VOID);
  }

AMObj AML_MSVOXEL::extract(const AMObjVector& args) const {

  Array* arrayTmp = NULL;
  int argth = 1;
  int len = args.length();
  int scale = -1;
  bool detail = false;
  bool mode = true;
  vector<int> Radius;
  int lacunarityType;
  char menu0 = -1;
  char menu1 = -1;
  char menu2 = -1;
  char menu3 = -1;
  bool b_units = false;
  bool b_volume = false;
  bool b_contraction = false;
  bool b_size = false;
  bool b_interceptedVoxels = false;

  int grid_data = -1;
  int bbox_mode = -1;

  CHECKCONDVA(len > 0 && len <= 10,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ssd), "Extract", "1", 10));


  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  
  CHECKCONDVA(args[0].tag() ==AMObjType::MSVOXEL,
	      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Extract", args[0].tag.string().data(), "Msvoxel"));
  
  
  AML_MSVOXEL * msvoxel = (AML_MSVOXEL *)(args[0].val.p);
  
  while (argth < args.length()) { // treatment of options
    
    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
		genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "MSVOXEL", (argth+1)/2+1));

    if (*(AMString*)(args[argth].val.p) == "Scale") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
		  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      CHECKCONDVA(args[argth+1].val.i >= 0,
		  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "positive"));
      
      scale = (uint32_t)args[argth+1].val.i;

    }
    else if (*(AMString*)(args[argth].val.p) == "Voxel") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING || args[argth+1].tag() ==AMObjType::FNODE,
		  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));
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
    }
    else if (*(AMString*)(args[argth].val.p) == "BoundingBox") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
		  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));
      CHECKCONDVA(*(AMString*)(args[argth+1].val.p) == "Center" || *(AMString*)(args[argth+1].val.p) == "Dimensions",
		  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "Size or Dimensions"));

      if (*(AMString*)(args[argth+1].val.p) == "Center") {
        bbox_mode = 0;
      }
      else if (*(AMString*)(args[argth+1].val.p) == "Dimensions") {
        bbox_mode = 1;
      }
      else assert(false);

    }
    else if (*(AMString*)(args[argth].val.p) == "GridData") {

      // cout << "GridData  " << endl; 
      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
		  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));
      if (( *(AMString*)(args[argth+1].val.p) == "FilledVoxelCoordinates")){
	grid_data = 0;
      }
      else if ((*(AMString*)(args[argth+1].val.p) == "InterceptedAreas")) {
	grid_data = 1;
      }
      else if ((*(AMString*)(args[argth+1].val.p) == "FilledVoxelVolumes")) {
	grid_data = 2;	 
      }
    }
    else if (*(AMString*)(args[argth].val.p) == "ScaleVariation") {
      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
		  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));
      menu0 = 0;
      if (*(AMString*)(args[argth+1].val.p) == "InterceptedVoxels") {
	menu1 = 0;
	b_interceptedVoxels = true;
      }
      else if (*(AMString*)(args[argth+1].val.p) == "Volume") {
	menu1 = 1;
	b_volume = true;
      }
      else if (*(AMString*)(args[argth+1].val.p) == "Units") {
	menu1 = 2;
	b_units = true;
      }
      else if (*(AMString*)(args[argth+1].val.p) == "BuilderStats") {
	menu1 = 3;
	b_units = true;
      }
      else if(*(AMString*)(args[argth+1].val.p) == "Area") {
	menu1 = 4;
      }
      else if(*(AMString*)(args[argth+1].val.p) == "MassDimension") {
        menu1 = 5; 
      }
      else {
	genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "All, MicroOnly or MacroOnly");
      }
    }
    else if (*(AMString*)(args[argth].val.p) == "Units") {
	
      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
		  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));
      if (*(AMString*)(args[argth+1].val.p) == "Contraction") {
	menu2 = 0;
	b_contraction = true;
      }
      else if(*(AMString*)(args[argth+1].val.p) == "Volume") {
	b_volume = true;
	menu2 = 1;
      }
      else {
	genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "All, MicroOnly or MacroOnly");
      }
    }
    else if (*(AMString*)(args[argth].val.p) == "BuilderStats") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
		  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));
      if (*(AMString*)(args[argth+1].val.p) == "ElapsedTime") {
	menu2 = 0;
      }
      else if(*(AMString*)(args[argth+1].val.p) == "NbTriangles") {
	menu2 = 1;
      }
      else {
	genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "All, MicroOnly or MacroOnly");
      }
    }
    else if (*(AMString*)(args[argth].val.p) == "Area") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
		  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));
      if (*(AMString*)(args[argth+1].val.p) == "Average") {
	menu2 = 0;
      }
      else if(*(AMString*)(args[argth+1].val.p) == "Variance") {
	menu2 = 1;
      }
      else {
	genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "All, MicroOnly or MacroOnly");
      }
    }
    else if (*(AMString*)(args[argth].val.p) == "Lacunarity") {
		  
      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
		  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));
      if (*(AMString*)(args[argth+1].val.p) == "LMoins") {
	lacunarityType = 0;
	menu0 = 1;
	menu1 = 0;
      }
      else if(*(AMString*)(args[argth+1].val.p) == "LPlus") {
	lacunarityType = 1;
	menu0 = 1;
	menu1 = 0;
      }
      else if(*(AMString*)(args[argth+1].val.p) == "L") {
	lacunarityType = 2;
	menu0 = 1;
	menu1 = 0;
      }
      else {
	genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "All, MicroOnly or MacroOnly");
      }
    }
    else if((*(AMString*)(args[argth].val.p) == "Nmass") && (menu0 == 1) && (menu1 == 1)) {

      if( args[argth+1].tag() ==AMObjType::ARRAY ) {
	CHECKCONDVA(args[argth+1].tag() ==AMObjType::ARRAY,
		    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY"));
	  
	if (args[argth+1].val.p) {
	    
	  arrayTmp = ((Array*)(args[argth+1].val.p));
	    
	  CHECKCONDVA(arrayTmp->surfaceType() ==AMObjType::INTEGER,
		      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY(INT)"));
	  ArrayIter* pnext = arrayTmp->iterator();
	  ArrayIter& next = *pnext;
	  while (next()) {
	    Radius.push_back(next.key().val.i);
	  }
	  delete pnext;
	}
      }
      else if (args[argth+1].tag() ==AMObjType::STRING){

	CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
		    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));
		  
	if(*(AMString*)(args[argth+1].val.p) == "FFT") {
	  menu2 = 1;
	}
	else if(*(AMString*)(args[argth+1].val.p) == "compPower") {
	  menu2 = 2;
	}
      }
    }
    else if((*(AMString*)(args[argth].val.p) == "Pmass") && (menu0 == 1) && (menu1 == 2)) {

      if( args[argth+1].tag() ==AMObjType::ARRAY ) {
	CHECKCONDVA(args[argth+1].tag() ==AMObjType::ARRAY,
		    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY"));
	  
	if (args[argth+1].val.p) {
	    
	  arrayTmp = ((Array*)(args[argth+1].val.p));
	    
	  CHECKCONDVA(arrayTmp->surfaceType() ==AMObjType::INTEGER,
		      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY(INT)"));
	    
	  ArrayIter* pnext = arrayTmp->iterator();
	  ArrayIter& next = *pnext;
	  while (next()) {
	    Radius.push_back(next.key().val.i);
	  }
	  delete pnext;
	}
      }
      else if (args[argth+1].tag() ==AMObjType::STRING){

	CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
		    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extract", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));
		  
	if(*(AMString*)(args[argth+1].val.p) == "FFT") {
	  menu2 = 1;
	}
	else if(*(AMString*)(args[argth+1].val.p) == "compPower") {
	  menu2 = 2;
	}
      }
    }
    else {
      genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "Size or Count");
    }
      
    argth +=2;

  } // while (argth < args.length()
   
  if(detail){
    Array* ret = new SLArray;
    if(mode){
      vector< vector<uint32_t> > res = msvoxel->getDetails();
      if(scale < 0 || scale > msvoxel->getDepth()){
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
    } // end if (mode)
    else {
      vector< Vector3 > res = msvoxel->getSizes();
      if(scale < 0 || scale > msvoxel->getDepth()){
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
  } // end if (detail)
  else if (menu0 != -1) {

    switch (menu0) {
    case 0: 
      {
	switch (menu1) {
	case 0 : 
	  {
	    const vector<int>& interceptedVoxels = msvoxel->getInterceptedVoxels();
	    Array* ret = new SLArray;
	    for( int j = 0 ; j < interceptedVoxels.size();j++){
	      (*ret) += AMObj(AMObjType::INTEGER, interceptedVoxels[j]);
	    }
	    return AMObj(AMObjType::ARRAY,ret);
	  }
	case 1 :
	  {
	    vector<real_t> volume = msvoxel->getVolume();
	    Array* ret = new SLArray;
	    for( int j = 0 ; j < volume.size();j++){
	      (*ret) += AMObj(AMObjType::REAL, volume[j]);
	    }
	    return AMObj(AMObjType::ARRAY,ret);
	  }
	case 2 :
	  {
	    switch (menu2) {
	    case 0 :
	      {
		vector<int> contraction = msvoxel->getContraction();
		Array* ret = new SLArray;
		for( int j = 0 ; j < contraction.size();j++){
		  (*ret) += AMObj(AMObjType::INTEGER, contraction[j]);
		}
		return AMObj(AMObjType::ARRAY,ret);
	      }
	    case 1 :
	      {
		vector<real_t> vUnits = msvoxel->getVolumeUnits();
		Array* ret = new SLArray;
		for( int j = 0 ; j < vUnits.size();j++){
		  (*ret) += AMObj(AMObjType::REAL, vUnits[j]);
		}
		return AMObj(AMObjType::ARRAY,ret);
	      }
	    default:
	      return AMObj(AMObjType::ERROR);
	    }
	  }
	case 3 :
	  {
	    switch (menu2) {
	    case 0:
	      {
		Array* ret = new SLArray;
		const vector<real_t>& elapsedTime = msvoxel->getBuilderStatByScale().elapsedTime();
		for( int j = 0 ; j < elapsedTime.size();j++){
		  (*ret) += AMObj(AMObjType::REAL, elapsedTime[j]);
		}
		return AMObj(AMObjType::ARRAY,ret);
	      }
	    case 1:
	      {
		Array* ret = new SLArray;
		const vector<int>& nbTriangles = msvoxel->getBuilderStatByScale().nbTriangles();
		for( int j = 0 ; j < nbTriangles.size();j++){
		  (*ret) += AMObj(AMObjType::INTEGER, nbTriangles[j]);
		}
		return AMObj(AMObjType::ARRAY,ret);
	      }
	    default:
	      return AMObj(AMObjType::ERROR);
	    } 
	  }
	case 4 :
	  {
	    switch (menu2) {
	    case 0:
	      {
		Array* ret = new SLArray;
		const vector<double>& averageArea = msvoxel->getBuilderStatByScale().averageArea();
		for( int j = 0 ; j < averageArea.size();j++){
		  (*ret) += AMObj(AMObjType::REAL, averageArea[j]);
		}
		return AMObj(AMObjType::ARRAY,ret);
	      }
	    case 1:
	      {
		Array* ret = new SLArray;
		const vector<double>& varianceArea = msvoxel->getVarianceArea();
		for( int j = 0 ; j < varianceArea.size();j++){
		  (*ret) += AMObj(AMObjType::REAL, varianceArea[j]);
		}
		return AMObj(AMObjType::ARRAY,ret);
	      }
	    default:
	      return AMObj(AMObjType::ERROR);
	    } 
	  }
	case 5 :
	  {
	    Array* ret = new SLArray;
	    real_t v;
		  
	    v = real_t(msvoxel->getAverageMassDimension());
	    (*ret) += AMObj(AMObjType::REAL, v );
	    v = real_t(msvoxel->getVarianceMassDimension());
	    (*ret) += AMObj(AMObjType::REAL, v );
	    v = real_t(msvoxel->getMinMassDimension());
	    (*ret) += AMObj(AMObjType::REAL, v );
	    v = real_t(msvoxel->getMaxMassDimension());
	    (*ret) += AMObj(AMObjType::REAL, v );
		  
	    v = real_t(msvoxel->getAverageYIntercept());
	    (*ret) += AMObj(AMObjType::REAL, v );
	    v = real_t(msvoxel->getVarianceYIntercept());
	    (*ret) += AMObj(AMObjType::REAL, v );
	    v = real_t(msvoxel->getMinYIntercept());
	    (*ret) += AMObj(AMObjType::REAL, v );
	    v = real_t(msvoxel->getMaxYIntercept());
	    (*ret) += AMObj(AMObjType::REAL, v );
		  
	    v = real_t(msvoxel->getAverageR2());
	    (*ret) += AMObj(AMObjType::REAL, v );
	    v = real_t(msvoxel->getVarianceR2());
	    (*ret) += AMObj(AMObjType::REAL, v );
	    v = real_t(msvoxel->getMinR2());
	    (*ret) += AMObj(AMObjType::REAL, v );
	    v = real_t(msvoxel->getMaxR2());
	    (*ret) += AMObj(AMObjType::REAL, v );
		  
	    return AMObj(AMObjType::ARRAY,ret);
	  }
	}
      }
    case 1 : 
      {
	switch(menu1) {
	case 0 : 
	  {
	    vector<real_t> lacunarity = msvoxel->getLacunarity(lacunarityType);
	    Array* ret = new SLArray;
	    for( int j = 0 ; j < lacunarity.size();j++){
	      (*ret) += AMObj(AMObjType::REAL, lacunarity[j]);
	    }
	    return AMObj(AMObjType::ARRAY,ret);
	  } 
	case 1 : 
	  {
	    int j;
	    vector<map<const int, long> > Nmass = msvoxel->getNmassr(Radius);
	    if(menu2 == 1)
	      return AMObj(AMObjType::ARRAY,FFT(Nmass,0));
	    else if(menu2 == 2)
	      return AMObj(AMObjType::ARRAY,FFT(Nmass,1));
	    else {
	      Array* ret1 = new SLArray;
	      for( j = 0 ; j < Nmass.size() ; j++){
		Array* ret2 = new SLArray;
		map<const int, long>::iterator it;
		  
		int k = 0;
		int k2 = 0;
		while(k < Nmass[j].size()) {
		  it = Nmass[j].find(k2);
		  if(it != Nmass[j].end()) {
		    (*ret2) += AMObj( AMObjType::INTEGER, 
				      int( (*it).second ) ); k++;
		  }
		  else (*ret2) += AMObj( AMObjType::INTEGER, 0 );
		  k2++;
		}
		(*ret1) += AMObj(AMObjType::ARRAY, ret2) ;
	      }
	      return AMObj(AMObjType::ARRAY,ret1);
	    }
	  } 
	case 2 : 
	  {
	    vector<map<const int, double> > Pmass = msvoxel->getQSr(Radius);
	    if(menu2 == 1)
	      return AMObj(AMObjType::ARRAY,FFT(Pmass,0));
	    else if(menu2 == 2)
	      return AMObj(AMObjType::ARRAY,FFT(Pmass,1));
	    else {
	      Array* ret1 = new SLArray;
	      for( int j = 0 ; j < Pmass.size();j++){
		Array* ret2 = new SLArray;
		map<const int, double>::iterator it;
		int k = 0;
		int k2 = 0;
		if(Pmass[j].size())
		  while(k < Pmass[j].size()) {
		    it = Pmass[j].find(k2);
		    if(it != Pmass[j].end()) {
		      (*ret2) += AMObj( AMObjType::REAL, 
					real_t( (*it).second ) ); k++;
		    }
		    else (*ret2) += AMObj( AMObjType::REAL, real_t(0) );
		    k2++;
		  }
		else (*ret2) += AMObj( AMObjType::REAL, real_t(0) );
		  
		(*ret1) += AMObj(AMObjType::ARRAY, ret2) ;
	      }
	      return AMObj(AMObjType::ARRAY,ret1);
	    }
	  }
	default: 
	  return AMObj(AMObjType::ERROR);
	}
      }
      break;
    }
  } // end if (menu0 != -1) 
  else if (grid_data != -1) { // by default scale is 0

    switch (grid_data) {
    case 0: // FilledVoxelCoordinates
      {

	Array* ret = new SLArray;
	 
        int n=0;
        if (scale == -1)n =  msvoxel->getNbFilledNodes(); // if scale not defined, all scales are assumed
	else n = msvoxel->getNbFilledNodes(scale);

	// cerr << "NbFilledNodes = " << n << endl;
	 
	const MSVoxelNode* node = 0;
	 
	for (int i=0; i<n;i++) { // i is the relative index at scale scale
	   
	  if (scale == -1) node=msvoxel->getFilledNodes(i);
          else node=msvoxel->getFilledNodes(scale, i);
	   
	  Array* ret1 = new SLArray;
	   
	  int k = node->getGridIndex();
	  // cerr << "(n=" << i << ",k=" << k << ",s=" << nodeScale(k) << ") " << flush;
          
          /*
	  cerr << "(n=" << i << ",k=" << k << ",s=" << nodeScale(k) << ") " 
               << "(cx=" << msvoxel->getFilledNodesX(k) 
               << "cy=" << msvoxel->getFilledNodesY(k) 
               << "cz=" << msvoxel->getFilledNodesZ(k) 
               << ") " << endl;
          */

	  (*ret1) += AMObj(AMObjType::INTEGER, msvoxel->getFilledNodesX(k));
	  (*ret1) += AMObj(AMObjType::INTEGER, msvoxel->getFilledNodesY(k));
	  (*ret1) += AMObj(AMObjType::INTEGER, msvoxel->getFilledNodesZ(k));

	  (*ret) += AMObj(AMObjType::ARRAY, ret1) ;
	   
	}
	 
	return AMObj(AMObjType::ARRAY,ret);
	 
      }
    case 1: // InterceptedAreas
      {
	Array* ret = new SLArray;
	 
	int n = 0;
        if (scale == -1) n = msvoxel->getNbFilledNodes();
        else n = msvoxel->getNbFilledNodes(scale);

	const MSVoxelNode* node = 0;
	 
	double s = 0;
	 
	for (int i=0; i<n;i++) {

	  if (scale == -1) node=msvoxel->getFilledNodes(i);
          else node=msvoxel->getFilledNodes(scale, i);

	  s = node->getArea();

          (*ret) += AMObj(AMObjType::REAL, s);

	}
	 
	return AMObj(AMObjType::ARRAY,ret);
      }
    case 2: // FilledVolumes
      {
	Array* ret = new SLArray;
	 
	int n = 0;
        if (scale == -1) n = msvoxel->getNbFilledNodes();
	else n = msvoxel->getNbFilledNodes(scale);

	const MSVoxelNode* node = 0;
	 
	Vector3 v;
	real_t s = 0;
	 
	for (int i=0; i<n;i++) {
	   
	  if (scale == -1) node=msvoxel->getFilledNodes(i);
          else node=msvoxel->getFilledNodes(scale, i);
	   
	  v = node->getSize()*2;
	  s = v.x()*v.y()*v.z();
	   
          (*ret) += AMObj(AMObjType::REAL, s);

	}
	 
	return AMObj(AMObjType::ARRAY,ret);
	 
      }
    default:
      return AMObj(AMObjType::ERROR);
    }
     
  } // else if (grid_data != -1) { 
  else if (bbox_mode != -1) {

    if (bbox_mode == 0) { // Center
      
      Vector3 v = msvoxel->getCenter();

      Array* a = new SLArray;

      (*a) += AMObj(AMObjType::REAL, v.x());
      (*a) += AMObj(AMObjType::REAL, v.y());
      (*a) += AMObj(AMObjType::REAL, v.z());
      
      return AMObj(AMObjType::ARRAY,a);

    }
    else if (bbox_mode == 1) { // Dimensions

      Vector3 v = msvoxel->getSize()*2;

      Array* a = new SLArray;

      (*a) += AMObj(AMObjType::REAL, v.x());
      (*a) += AMObj(AMObjType::REAL, v.y());
      (*a) += AMObj(AMObjType::REAL, v.z());
      
      return AMObj(AMObjType::ARRAY,a);

    }
    else return AMObj(AMObjType::ERROR);

  }
  else if (true) {
    cout << "Global Volume ..." << endl;
    real_t vol = msvoxel->getVolume(scale)[scale];
    return AMObj(AMObjType::REAL,vol);
  }
  else return AMObj(AMObjType::ERROR);

}



void installMSVOXELModule() {

  AMObjType type[10];          // max number of arguments
  AMObj var;
  RWCString varname;

  // OCTREE functions

  type[0] = AMObjType::ANY;
  installFNode("Octree", OCT_OCTREE, 1, type, AMObjType::OCTREE);


  // MSVOXEL functions

  type[0] = AMObjType::ANY;
  installFNode("MSVoxel", MSV_MSVOXEL, 1, type, AMObjType::MSVOXEL);

}
