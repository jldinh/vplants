/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2003 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): F. Boudon & C. Godin (godin@cirad.fr)
 *
 *       $Source$
 *       $Id: geomscene_funs.cpp 5640 2008-10-29 12:51:01Z boudon $
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

#include "aml/geomscene_funs.h"

#include "aml/kernel_funs.h"
#include "aml/kernel_err.h"


#include "plantgl/gui/viewer/pglapplication.h"
#include "plantgl/algo/base/discretizer.h"
#include "plantgl/algo/base/bboxcomputer.h"
#include "plantgl/algo/base/volcomputer.h"
#include "plantgl/algo/base/surfcomputer.h"

#include "plantgl/scenegraph/geometry/boundingbox.h"


TOOLS_USING_NAMESPACE
using namespace std;

#define  MODULE_NAME            "GEOMSCENE"
#define  ERR_MSG_ARRAY          geomscene_err_msgs_aml

enum GEOMSCENE_ERRORLABEL {
  GEOMSCENE_OPTION_BADVALUE_s
};

const char *geomscene_err_msgs_aml[] = {
  "Option %s: bad value"// GEOMSCENE_OPTION_BADVALUE_s
};


// --------------
//  Constructors
// --------------

AMObj AML_GeomScene::extract(const AMObjVector& args) const
  {
    assert(&args);
  int argth = 1;
  int len = args.length();


  CHECKCONDVA(len > 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Extract",2));

  if (! args[0].isaAMModel()) return AMObj(AMObjType::UNDEF);

  while (argth < args.length())  { // treatment of options
      CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Extract", (argth+1)/2+1));

      assert(argth + 1 < args.length()); // must contain at least two parameters : this is verified syntactically

      if (*(AMString*)(args[argth].val.p) == "Data") { // treatment of different options

        CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "Data->[BBox (BoundingBox),BBoxCenter, BBoxSize Volume or Surface]"));
		  if (*(AMString*)(args[argth+1].val.p) == "BBox" || *(AMString*)(args[argth+1].val.p) == "BoundingBox") {
				  argth++;
				  Discretizer dis;
				  BBoxComputer bbxcmp(dis);
				  bbxcmp.process(*this);
				  if(!bbxcmp.getBoundingBox())return AMObj(AMObjType::VOID);
				  Array* ret = new SLArray;
				  *ret += AMObj(AMObjType::REAL,bbxcmp.getBoundingBox()->getLowerLeftCorner().x());
				  *ret += AMObj(AMObjType::REAL,bbxcmp.getBoundingBox()->getLowerLeftCorner().y());
				  *ret += AMObj(AMObjType::REAL,bbxcmp.getBoundingBox()->getLowerLeftCorner().z());
				  *ret += AMObj(AMObjType::REAL,bbxcmp.getBoundingBox()->getUpperRightCorner().x());
				  *ret += AMObj(AMObjType::REAL,bbxcmp.getBoundingBox()->getUpperRightCorner().y());
				  *ret += AMObj(AMObjType::REAL,bbxcmp.getBoundingBox()->getUpperRightCorner().z());
				  return AMObj(AMObjType::ARRAY,ret);
			  }
		  else if (*(AMString*)(args[argth+1].val.p) == "BBoxCenter" || *(AMString*)(args[argth+1].val.p) == "BoundingBoxCenter") {
				  argth++;
				  Discretizer dis;
				  BBoxComputer bbxcmp(dis);
				  bbxcmp.process(*this);
				  if(!bbxcmp.getBoundingBox())return AMObj(AMObjType::VOID);
				  Array* ret = new SLArray;
				  *ret += AMObj(AMObjType::REAL,bbxcmp.getBoundingBox()->getCenter().x());
				  *ret += AMObj(AMObjType::REAL,bbxcmp.getBoundingBox()->getCenter().y());
				  *ret += AMObj(AMObjType::REAL,bbxcmp.getBoundingBox()->getCenter().z());
				  return AMObj(AMObjType::ARRAY,ret);
			  }
		  else if (*(AMString*)(args[argth+1].val.p) == "BBoxSize" || *(AMString*)(args[argth+1].val.p) == "BoundingBoxSize") {
				  argth++;
				  Discretizer dis;
				  BBoxComputer bbxcmp(dis);
				  bbxcmp.process(*this);
				  if(!bbxcmp.getBoundingBox())return AMObj(AMObjType::VOID);
				  Array* ret = new SLArray;
				  *ret += AMObj(AMObjType::REAL,bbxcmp.getBoundingBox()->getSize().x());
				  *ret += AMObj(AMObjType::REAL,bbxcmp.getBoundingBox()->getSize().y());
				  *ret += AMObj(AMObjType::REAL,bbxcmp.getBoundingBox()->getSize().z());
				  return AMObj(AMObjType::ARRAY,ret);

			  }
		  else if (*(AMString*)(args[argth+1].val.p) == "Surface") {
				  argth++;
				  return AMObj(AMObjType::REAL,sceneSurface(*this));
			  }
		  else if (*(AMString*)(args[argth+1].val.p) == "Volume") {
				  argth++;
				  return AMObj(AMObjType::REAL,sceneVolume(*this));
			  }
		  else {
			CHECKCONDVA(false,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "Data->[BBox (BoundingBox),BBoxCenter, BBoxSize Volume or Surface]"));
			return AMObj(AMObjType::VOID);
		  }
	  }
	  else {
			CHECKCONDVA(false,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "Data"));
			return AMObj(AMObjType::VOID);
	  }
	  argth++;
  }
    return AMObj(AMObjType::VOID);
}

static AMObj AML_GEOMSCENE(const AMObjVector& args) {

  int argth = 1;
  int len = args.length();
  int depth = 5;
  int data = 0;
  int max_elements = 0;

  string filename;

  CHECKCONDVA(len > 0 && len <= 5,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ssd), "GEOMSCENE", "1", 5));


   if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

   CHECKCONDVA(args[0].tag() ==AMObjType::STRING,
               genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss),
               "GEOMSCENE", args[0].tag.string().data(), "Filename"));

   filename = ((AMString*)(args[0].val.p))->data();

   while (argth < args.length()) { // treatment of options

     CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                 genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "GEOMSCENE", (argth+1)/2+1));

     if (*(AMString*)(args[argth].val.p) == "") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "GEOMSCENE", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      CHECKCONDVA(args[argth+1].val.i >= 0,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "GEOMSCENE", (argth+1)/2+1, "positive"));

     }
     else {
       CHECKCONDVA(FALSE,
                   genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "GeomScene", (argth+1)/2+1));
     }
     argth +=2;
   }


   AML_GeomScene* geomscene = new AML_GeomScene(filename);

   return AMObj(AMObjType::GEOMSCENE,geomscene);
}

AMObj AML_GeomScene::plot(GP_window&, const AMObjVector& args) const
  {
    int argth = 1;
    int len = args.length();
    PGLViewerApplication app;

    while (argth < args.length()) { // treatment of options

      CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Plot", (argth+1)/2+1));

      CHECKCONDVA(args[argth].tag() == AMObjType::STRING,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "Display, Scale or Cut"));

      if (*(AMString*)(args[argth].val.p) == "") {
        CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "a STRING"));

         argth +=2;
      }
          /*
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
          */
      else {
        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Plot", (argth+1)/2+1));
      }
    }

   /*
    if(view_mode == 1){
      conditionPlane2GeomScene a;
      a.quarter = quarter;
      if(scale !=0)a.scale = scale;
      scene = ScenePtr(getCondRepresentation(a));
    }
    else if(view_mode == 2){
      conditionPlaneGeomScene a;
      a.quarter = quarter;
      if(scale !=0)a.scale = scale;
      scene = ScenePtr(getCondRepresentation(a));
    }
    else {
      conditionPlane3GeomScene a;
      a.quarter = quarter;
      if(quarter) a.plan = plane;
      if(scale !=0)a.scale = scale;
      scene = ScenePtr(getCondRepresentation(a));
    }
        */

        ScenePtr psc = ScenePtr((AML_GeomScene *)this);
    app.display(psc);
    return AMObj(AMObjType::VOID);
  }

void installGEOMSCENEModule() {

  AMObjType type[10];          // max number of arguments
  AMObj var;
  RWCString varname;

  // GEOMSCENE functions

  type[0] = AMObjType::ANY;
  installFNode("GeomScene", AML_GEOMSCENE, 1, type, AMObjType::GEOMSCENE);

}
