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
 *       $Id: viewer_funs.cpp 3573 2007-09-05 16:59:56Z dufourko $
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


#include "aml/viewer_funs.h"

#include "aml/erroraml.h"
#include "aml/parseraml.h"
#include "aml/fnode.h"
#include "aml/kernel_err.h"
#include "aml/kernel_funs.h"
#include "aml/global.h"

#include "aml/set.h"
#include "aml/array.h"
#include "aml/list.h"

#include "plantgl/gui/viewer/pglapplication.h"

PGL_USING_NAMESPACE
using namespace std;

#define  ERR_MSG_ARRAY          kernel_err_msgs_aml
#define  MODULE_NAME            "Viewer"

/*  ------------------------------------------------------------------------ */

static AMObj V_StartViewer(const AMObjVector& args) {

  bool uset = true;
  bool def = false;

  CHECKCONDVA(args.length() <= 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "StartViewer", 1));

  if(args.length() == 2){
    if(*(AMString*)(args[0].val.p) == "Thread" ) {

      CHECKCONDVA(args[1].tag() == AMObjType::BOOL,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "StartViewer", 0 , "a BOOL"));

      if(args[1].tag() == AMObjType::BOOL){
        def = true;
        if(args[1].val.b == TRUE)uset = true;
        else uset = false;
      }
    }
    else {
      cerr << "Wrong option name : '" << (*(AMString*)(args[0].val.p)) << "' must be Thread" << endl;
      return AMObj(AMObjType::BOOL,FALSE);
    }
  }
  bool b = true;
  if(def){
    b = PGLViewerApplication::useThread(uset);
  }
  PGLViewerApplication::display(ScenePtr(new Scene()));
  return AMObj(AMObjType::BOOL,b);
}

/*  ------------------------------------------------------------------------ */

static AMObj V_SetViewer(const AMObjVector& args) {

  bool uset = true;
  bool def = false;

  CHECKCONDVA(args.length() <= 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "SetViewer", 1));

  if(args.length() == 2){
    if(*(AMString*)(args[0].val.p) == "Thread" ) {

      CHECKCONDVA(args[1].tag() == AMObjType::BOOL,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "SetViewer", 0 , "a BOOL"));

      if(args[1].tag() == AMObjType::BOOL){
        def = true;
        if(args[1].val.b == TRUE)uset = true;
        else uset = false;
      }
    }
    else {
      cerr << "Wrong option name : '" << (*(AMString*)(args[0].val.p)) << "' must be Thread" << endl;
      return AMObj(AMObjType::BOOL,FALSE);
    }
  }
  bool b = true;
  if(def){
    b = ViewerApplication::useThread(uset);
  }
  return AMObj(AMObjType::BOOL,b);
}

/*  ------------------------------------------------------------------------ */

static AMObj V_StopViewer(const AMObjVector& args) {
  CHECKCONDVA(args.length() == 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "StopViewer", 1));
  bool b = PGLViewerApplication::stop();
  return AMObj(AMObjType::BOOL,b);
}

/*  ------------------------------------------------------------------------ */

static AMObj V_ViewerSelection(const AMObjVector& args) {
  CHECKCONDVA(args.length() == 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "ViewerSelection", 1));
  vector<uint32_t> select = PGLViewerApplication::getSelection();
  if(select.empty()) return AMObj(AMObjType::UNDEF);
  Array* ret = new SLArray;
  VId vtx;
//  cerr << "Select = " << flush;
  for(vector<uint32_t>::iterator _it = select.begin();
      _it != select.end();
      _it++){
//    cerr << *_it;
    vtx = *_it;
    (*ret) += AMObj(AMObjType::VTX,vtx);
  }
//  cerr << endl;
  return AMObj(AMObjType::ARRAY,ret);
}

/*  ------------------------------------------------------------------------ */

static AMObj V_WaitViewer(const AMObjVector& args) {

  unsigned long time_m = 0;
  bool def = false;

  CHECKCONDVA(args.length() <= 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "WaitViewer", 1));

  if(args.length() == 2){
    if(*(AMString*)(args[0].val.p) == "Timeout" ) {

      CHECKCONDVA(args[1].tag() == AMObjType::DATE,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "WaitViewer", 0 , "a DATE"));

      if(args[1].tag() == AMObjType::DATE){
        def = true;
        time_m = *(unsigned long *)args[1].val.d;
      }
    }
    else {
      cerr << "Wrong option name : '" << (*(AMString*)(args[0].val.p)) << "' must be Timeout" << endl;
      return AMObj(AMObjType::BOOL,FALSE);
    }
  }
  bool b = true;
  if(def)
    b = PGLViewerApplication::wait(time_m);
  else
    b = PGLViewerApplication::wait();

  return AMObj(AMObjType::BOOL,b);
}

/*  ------------------------------------------------------------------------ */

static AMObj V_ViewerIsRunning(const AMObjVector& args) {

  CHECKCONDVA(args.length() <= 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "ViewerIsRunning", 1));

  return AMObj(AMObjType::BOOL, PGLViewerApplication::running());
}

/*  ------------------------------------------------------------------------ */

static AMObj V_ViewerHelp(const AMObjVector& args) {

//  FNode* func = NULL;
  RWCString  func_name;
  bool option = false;

  CHECKCONDVA(args.length() <= 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "ViewerHelp", 1));

  if(args.length() == 1){
    if (args[0].tag() == AMObjType::STRING) {
      func_name = RWCString((*(AMString*)(args[0].val.p)));
      option = true;
    }
    else if (args[0].tag() == AMObjType::FNODE) {
      func_name = ((FNode*) args[0].val.p)->name();
      option = true;
    }
    else cerr << "Found : " << args[0].tag.string().data() << endl;
  }
  else if(args.length() == 2){
    if (*(AMString*)(args[0].val.p) == "Function") {

      CHECKCONDVA(args[1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "ViewerHelp", 1, args[1].tag.string().data(), "FUNC"));

      func_name = ((FNode*) args[1].val.p)->name();
      option = true;
    }
  }

  cerr << "Help for Viewer Module" << endl;
  if(option)
    cerr << "Functions : '" << func_name << '\'' << endl;
  else cerr << "Functions :" << endl;
  if(!option || func_name == ":SetViewer"){
    cerr << " * SetViewer([Thread->BOOL]) :" << endl;
    cerr << "   - Set Viewer functionalities : " << endl;
    cerr << "     - Use of Thread or Not. " << endl;
    cerr << "   - Return True if success, else False." << endl;
  }
  if(!option || func_name == ":StartViewer"){
    cerr << " * StartViewer([Thread->BOOL]) :" << endl;
    cerr << "   - Start Viewer process : " << endl;
    cerr << "     - Use of Thread or Not. " << endl;
    cerr << "   - Return True if success, else False." << endl;
  }
  if(!option || func_name == ":StopViewer"){
    cerr << " * StopViewer() :" << endl;
    cerr << "   - Stop Viewer process : " << endl;
    cerr << "   - Return True if success, else False." << endl;
  }
  if(!option || func_name == ":ViewerIsRunning"){
    cerr << " * ViewerIsRunning() :" << endl;
    cerr << "   - Test if Viewer process is running." << endl;
    cerr << "   - Return True if viewer is running, else False." << endl;
  }
  if(!option || func_name == ":ViewerHelp"){
    cerr << " * ViewerHelp([Function->Func]) :" << endl;
    cerr << "   - Display Help about Viewer Module or function Func." << endl;
    cerr << "   - Return Nothing." << endl;
  }
  if(!option || func_name == ":ViewerSelection"){
    cerr << " * ViewerSelection() :" << endl;
    cerr << "   - Get the Viewer last selection." << endl;
    cerr << "   - Return an array of VTX or Undef." << endl;
  }
  if(!option || func_name == ":ViewerWait"){
    cerr << " * WaitViewer([Timeout->Date]) :" << endl;
    cerr << "   - Wait for end of Viewer process until timeout." << endl;
    cerr << "   - Return True if Viewer finished, False if timeout." << endl;
  }
  return AMObj(AMObjType::VOID);
}

/*  ------------------------------------------------------------------------ */

void installVIEWERModule() {

  AMObjType type[10]; // max number of arguments
  AMObj var;
  RWCString varname;


  type[0] = AMObjType::STRING;
  type[1] = AMObjType::STRING;

  installFNode("SetViewer",       V_SetViewer,       1, type, AMObjType::BOOL);

  installFNode("StartViewer",     V_StartViewer,     1, type, AMObjType::BOOL);

  type[0] = AMObjType::VOID;
  type[1] = AMObjType::VOID;

  installFNode("StopViewer",      V_StopViewer,      1, type, AMObjType::ARRAY);

  installFNode("ViewerIsRunning", V_ViewerIsRunning, 1, type, AMObjType::BOOL);

  installFNode("ViewerSelection", V_ViewerSelection, 1, type, AMObjType::BOOL);

  installFNode("ViewerHelp",      V_ViewerHelp,      1, type, AMObjType::VOID);

  type[0] = AMObjType::STRING;
  type[1] = AMObjType::DATE;

  installFNode("WaitViewer",      V_WaitViewer,      1, type, AMObjType::BOOL);

}
