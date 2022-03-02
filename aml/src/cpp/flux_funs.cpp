/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): N. Dones (dones@clermont.inra.fr)
 *                       Ch. Godin (christophe.godin@cirad.fr)
 *
 *       $Source$
 *       $Id: flux_funs.cpp 3573 2007-09-05 16:59:56Z dufourko $
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




#include <iostream>

#include "tool/rw_hset.h"
//#include <rw/tvsrtvec.h>

#include "aml/fnode.h"
#include "aml/array.h"

#include "aml/parseraml.h"
#include "aml/mtg_funs.h"
#include "aml/kernel_err.h"
#include "aml/kernel_funs.h"
#include "aml/flux_funs.h"
#include "flux/electrical_model.h"


#define  ERR_MSG_ARRAY          flux_err_msgs_aml
#define  MODULE_NAME            "FLUX"

using namespace std;

enum MTG_ERRORLABEL {
  NO_MTG_LOADED_ERR = KERNEL_ERR_OFFSET,
  MTG_UNDEF_FEAT_NAME_ss,
  MTG_OPTION_BADVALUE_s
};


const char *flux_err_msgs_aml[] = {
  "Cannot proceed: no MTG loaded",
  "function %s: undefined feature %s",     // MTG_UNDEF_FEAT_NAME_ss
  "Option %s: bad value"                   //
};


// extern const char *Plot_prefix;


// -------------------------------------------
// Interface Class for the Flux module
// -------------------------------------------

class AML_ElectricalModel : public ElectricalModel, public AMModel {

private:

  FNode* _resistance_fun;
  FNode* _flux_fun;
  FNode* _potential_fun;

public:

  AML_ElectricalModel(MTG* g,
                      VId root,
                      FNode* resistance_fun,
                      FNode* flux_fun,
                      FNode* potential_fun,
                      double base_potential);

  bool computeArrays();

  virtual ostream& displayOneLine(ostream& o) const {return ElectricalModel::displayOneLine(o);}
  virtual ostream& display(ostream& o, int line_size = 0) const {
    if (line_size) return ElectricalModel::display(o);
    else return ElectricalModel::display(o);
  }
  virtual AMObj display(ostream& o, const AMObjVector& args) const {assert(&args); display(o); return AMObj(AMObjType::VOID);}

  virtual AMObj plot(GP_window&, const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}
  virtual AMObj extract(const AMObjVector& args) const;// {assert(&args); return AMObj(AMObjType::VOID);}

  virtual AMObj print(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}
  virtual AMObj save(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}

};

AML_ElectricalModel::AML_ElectricalModel(MTG* g,
                                         VId root,
                                         FNode* resistance_fun,
                                         FNode* flux_fun,
                                         FNode* potential_fun,
                                         double base_potential) :
  ElectricalModel(g,root, base_potential)
{
  _resistance_fun = resistance_fun;
  _flux_fun = flux_fun;
  _potential_fun = potential_fun;


  if ( false ) {

    _isValid = false;

    // + Error message

  }


}

bool AML_ElectricalModel::computeArrays()  {

  assert(_resistance_array);
  assert(_flux_array);
  assert(_potential_array);

  AMObj arg(AMObjType::VTX);
  AMObj ret;

  AMObjVector arglist(1);  // nb of argument of such a FNode = 1 (the vtx)

  if (_resistance_fun) {

    for(int i = 0; i<_nb_desc; i++)
      {

        arg.val.v = (*_vlist)[i];
        arg.tag = AMObjType::INTEGER;
        arglist[0] = arg;

        ret = (*_resistance_fun)(arglist);

        switch(ret.tag()) {
        case  AMObjType::INTEGER:
          _resistance_array->setAt(i,ret.val.i);
          break;
        case  AMObjType::REAL:
          _resistance_array->setAt(i,ret.val.r);
          break;
        default:
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Resistance",ret.tag.string().data(), "REAL or INT");
        }

      }

  }

  if (_flux_fun) {

    for(int i = 0; i<_nb_desc; i++)
      {

        arg.val.v = (*_vlist)[i];
        arg.tag = AMObjType::INTEGER;
        arglist[0] = arg;

        ret = (*_flux_fun)(arglist);

        switch(ret.tag()) {
        case  AMObjType::INTEGER:
          _flux_array->setAt(i,ret.val.i);
          break;
        case  AMObjType::REAL:
          _flux_array->setAt(i,ret.val.r);
          break;
        default:
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Flux",ret.tag.string().data(), "REAL or INT");
        }

      }
  }

  if (_potential_fun) {

    for(int i = 0; i<_nb_desc; i++)
      {

        arg.val.v = (*_vlist)[i];
        arg.tag = AMObjType::INTEGER;
        arglist[0] = arg;

        ret = (*_potential_fun)(arglist);

        switch(ret.tag()) {
        case  AMObjType::INTEGER:
          _potential_array->setAt(i,ret.val.i);
          break;
        case  AMObjType::REAL:
          _potential_array->setAt(i,ret.val.r);
          break;
        default:
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "Potential",ret.tag.string().data(), "REAL or INT");
        }

      }
  }
  return true;

}


AMObj AML_ElectricalModel::extract(const AMObjVector& args) const {

  int argth = 1;
  int len = args.length();
  VId vtx = 0;
  Array* ret = NULL;
  bool isVtxList = FALSE;

 // CHECKCONDVA(len > 0,
//            genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "Extract"));
  CHECKCONDVA(len > 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Extract",2));

  if (! args[0].isaAMModel()) return AMObj(AMObjType::UNDEF);

  while (argth < args.length())  // treatment of options
    {
      CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Extract", (argth+1)/2+1));

      assert(argth + 1 < args.length()); // must contain at least two parameters : this is verified syntactically

      if (*(AMString*)(args[argth].val.p) == "Data") // treatment of different options
        {
          CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                      genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "a STRING"));

          if (*(AMString*)(args[argth+1].val.p) == "Resistance")
            {
              ret = new SLArray;
              for(int i=0;i<_nb_desc;i++)
                (*ret) += AMObj(AMObjType::REAL,(double)_resistance_array->getAt(i));
            }
          else if(*(AMString*)(args[argth+1].val.p) =="Flux")
            {
              ret = new SLArray;
              for(int i=0;i<_nb_desc;i++)
                (*ret) += AMObj(AMObjType::REAL,(double)_flux_array->getAt(i));
            }
          else if(*(AMString*)(args[argth+1].val.p) =="Potential")
            {
              ret = new SLArray;
              for(int i=0;i<_nb_desc;i++)
                (*ret) += AMObj(AMObjType::REAL,(double)_potential_array->getAt(i));
            }
          else if(*(AMString*)(args[argth+1].val.p) =="VtxList")
            {
              ret = new SLArray;
              for(int i=0;i<_nb_desc;i++)
                (*ret) += AMObj(AMObjType::VTX,(*_vlist)[i]);
              isVtxList=TRUE;
            }

          else
            {
              genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "''Resistance'' or ''Flux'' or ''Potential'' or ''VtxList''");
              return  AMObj(AMObjType::UNDEF);
            }
        }

      else if(*(AMString*)(args[argth].val.p) == "Vtx")  //selection of a Vtx
        {
          CHECKCONDVA(args[argth+1].tag() == AMObjType::VTX || args[argth+1].tag() == AMObjType::INTEGER,
                      genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Extract", (argth+1)/2+1, "a VTX"));

          vtx = args[argth+1].val.v;

          /*    AMObj v(AMObjType::REAL);
                VId vtx=args[argth+1].val.v;
                cout<<vtx;
                //v.val.r = _resistance_array->getAt(ElectricalModel::vtxToIndex(vtx));
                return v;
          */

        }
      else {

        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Extract", (argth+1)/2+1));

      }

      argth += 2;

    }

  if (ret){ // returned Array computed

    if (vtx && !isVtxList){ // value of

      AMObj v(AMObjType::REAL);
      VtxList::iterator _it;
      _it=_vlist->begin();
      int index = 0;
      bool find = false;
      while(!find && _it!=_vlist->end()){
        if(*_it==vtx){
          find=true;
          index--;
        }
        index++;
        _it++;
      }

      if(find){
        v.val.r=(ret->at(index)).val.r;
        return v;
      }
      else
        genAMLError(ERRORMSG (K_OPTION_VALUES_ERR_ss), "Extract"," no data for this vertex in ElectricalModel");
        return AMObj(AMObjType::ERROR);
    }

    else
      return AMObj(AMObjType::ARRAY,ret);
  }

  else
    return AMObj(AMObjType::VOID);
}



// --------------
//  Constructors
// --------------

static AMObj FLUX_ElectricalModel(const AMObjVector& args) {

  int argth = 1;
  int len = args.length();

  VId vtx = -1;
  int scale = -1;

  VId root; // root of the tree graph defined by the user using g, vtx, scale (cf: like in PlantFrame)

  FNode* flow_fun = NULL;
  FNode* resistance_fun = NULL;
  FNode* potential_fun = NULL;
  double base_potential = 0;

  MTG* mtg = 0;


  CHECKCONDVA(len > 0,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s), "ElectricalModel"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "ElectricalModel", args[0].tag.string().data(), "VTX"));

  vtx = args[0].val.i;

  mtg = activeMTG_MTG();
  // cerr << "Nb de vertex = " <<  mtg->vertexNb() << endl;

  CHECKCOND(mtg,NO_MTG_LOADED_ERR);

//  scale = mtg->si_scale(vtx) + 1;
  scale = (mtg->si_scale(vtx)==mtg->scaleNb()) ? mtg->si_scale(vtx) : mtg->si_scale(vtx) + 1;

  // cerr << "step1" << endl;

  while (argth < args.length()) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "ElectricalModel", (argth+1)/2+1));

    assert(argth + 1 < args.length()); // must contain at least two parameters : this is verified syntactically

    if (*(AMString*)(args[argth].val.p) == "Scale") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "ElectricalModel", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      scale = args[argth+1].val.i;

    }
    else if (*(AMString*)(args[argth].val.p) == "Flux") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "ElectricalModel", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      flow_fun = (FNode*) args[argth+1].val.p;

    }
    else if (*(AMString*)(args[argth].val.p) == "Resistance") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "ElectricalModel", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      resistance_fun = (FNode*) args[argth+1].val.p;

    }
    else if (*(AMString*)(args[argth].val.p) == "Potential") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "ElectricalModel", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      potential_fun = (FNode*) args[argth+1].val.p;

    }
    else if (*(AMString*)(args[argth].val.p) == "BasePotential") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::REAL,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "ElectricalModel", (argth+1)/2+1, args[argth+1].tag.string().data(), "REAL"));

        base_potential = (double) args[argth+1].val.r;

    }
    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "ElectricalModel", (argth+1)/2+1));

    }

    argth += 2;

  }

  root = mtg->si_defineSubTreeRoot(vtx, scale);

  if (root != -1) {

    AML_ElectricalModel* elec_model = new AML_ElectricalModel(mtg,
                                                              root,
                                                              resistance_fun,
                                                              flow_fun,
                                                              potential_fun,
                                                              base_potential);
    assert(mtg);

    if (! elec_model->computeArrays()) {

      AMLCOMMENT("Building errors : ElectricalModel could not be computed ...");
      return AMObj(AMObjType::ERROR);
    }

    elec_model->computeEM();

    if (elec_model->isValid()) {

      AMLCOMMENT("ElectricalModel computed ...");
      return AMObj(AMObjType::ELECTRICAL_MODEL,elec_model);
    }
    else {

      AMLCOMMENT("Building errors : ElectricalModel could not be computed ...");
      return AMObj(AMObjType::ERROR);
    }

  }
  else {
    // error the root vertex could not be found
      return AMObj(AMObjType::ERROR);
  }

}



void installFLUXModule() {

  AMObjType type[10];          // max number of arguments
  AMObj var;
  RWCString varname;

  // ElectricalModel functions

  type[0] = AMObjType::ANY;
  installFNode("ElectricalModel", FLUX_ElectricalModel, 1, type, AMObjType::ELECTRICAL_MODEL);

}
