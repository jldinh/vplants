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
 *       $Id: mtg_funs.cpp 17611 2014-10-17 13:20:41Z pradal $
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
#include <fstream>


#include "aml/parseraml.h"
#include "aml/fnode.h"

#include "aml/set.h"
#include "aml/array.h"
#include "aml/list.h"

#include "aml/kernel_funs.h"
#include "aml/kernel_err.h"
#include "aml/mtg_funs.h"

#include "mtg/plantframe.h"
#include "mtg/virtualelements.h"
#include "mtg/dressingfile.h"
#include "mtg/linetree.h"

#include "mtg/mtg.h"

#include "mtg/lsystemToMTG_parser.h"

#ifdef BISON_HPP
#include "mtg/lsystemToMTG_parser.hpp"
#else
#include "mtg/lsystemToMTG_parser.cpp.h"
#endif

#include "mtg/lsystemToMTG_scanner.h"
#include "tool/gparser.h"

#include "tree_matching/treematch.h"
#include "aml/aml_treematch.h"

#include "stat_tool/distance_matrix.h"
#include "aml/stat_module.h"

#ifndef SYSTEM_IS__IRIX
#include "plantgl/gui/viewer/pglapplication.h"
#include "plantgl/math/util_matrix.h"
TOOLS_USING(Matrix3)
TOOLS_USING(Vector3)
#endif

#include "tool/dirnames.h"
VPTOOLS_USING_NAMESPACE

extern const char *Plot_prefix;

enum Restriction {SAMEAXIS, SAMECOMPLEX, NORESTRICTION} Restriction;

class AML_MTG : public MTG, public AMModel {

public:

  AML_MTG(const char* file, int vtxnb, int maxerrornb, int resize): MTG(file, vtxnb, AMLOUTPUT, maxerrornb, resize) {}

  virtual ostream& displayOneLine(ostream& o) const {return MTG::displayOneLine(o);}
  virtual ostream& display(ostream& o, int line_size = 0) const {
    if (line_size) return MTG::displayOneLine(o);
    else return MTG::displayOneLine(o);
  }
  virtual AMObj display(ostream& o, const AMObjVector& args) const {assert(&args); display(o); return AMObj(AMObjType::VOID);}

  virtual AMObj plot(GP_window&, const AMObjVector& args) const;

  virtual AMObj print(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}
  virtual AMObj save(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}

};

#define  ERR_MSG_ARRAY          mtg_err_msgs_aml
#define  MODULE_NAME            "MTG"

enum MTG_ERRORLABEL {
  NO_MTG_LOADED_ERR = KERNEL_ERR_OFFSET,
  MTG_UNDEF_FEAT_NAME_ss,
  MTG_OPTION_BADVALUE_s
};


const char *mtg_err_msgs_aml[] = {
  "Cannot proceed: no MTG loaded",
  "function %s: undefined feature %s",                          // MTG_UNDEF_FEAT_NAME_ss
  "Option %s: bad value"// MTG_UNDEF_FEAT_NAME_ss
};

// ----------
// some tools
// ----------

AMObj activeMTG() {

  AMObj var;

  amobjTable()->findValue(":CurrentMTG", var);

  return var;

}

MTG* activeMTG_MTG() {

  AMObj var;
  MTG* g = 0;

  amobjTable()->findValue(":CurrentMTG", var);

  if (var.tag == AMObjType::UNDEF) return 0;
  else g = (AML_MTG*) var.val.p;

  return g;

}

void resetActiveMTG() {

  AMObj var(AMObjType::MTG, 0);

  amobjTable()->insert(":CurrentMTG", var);

}

void activateMTG(AMObj g) {

  assert(g.tag() == AMObjType::MTG);
  amobjTable()->insert(":CurrentMTG", g);

}

AmlBoolean isCurrentMTGValid() {

  return activeMTG().val.p != 0;

}


// returns the index identifying the feature in the mtg
// returns UNDEF if not found
static FIndex checkExistsFeature(const char* feat_name) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  assert(feat_name);
  assert(active_mtg);

  FIndex findex = active_mtg->fNameIndex(feat_name);

  return findex;

}

static AMObjType featureType(FIndex index) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;
  assert(active_mtg);

  FType ftype = active_mtg->fType(index);

  switch(ftype) {

  case INTEGER:
    return AMObjType::INTEGER;
  case REAL:
    return AMObjType::REAL;
  case ALPHA:
    return AMObjType::STRING;
  default:
    return AMObjType::DATE;

  }

}

// --------------
//  Constructors
// --------------

static AMObj MTG_MTG(const AMObjVector& args) {

  int argth = 1;
  int len = args.length();

  int adjust_size = 1; // reajuste la taille d'un MTG par defaut
  int vtx_size = 0;
  int err_nb = 10;

	// for DataType = L_System
  string data_type("MTG");
  string input_file;
  string output_file; // only for l-system case
  string header_file;
  string discard_symbols;
  Array* feature_list =0;
  Array* feature_map=0;

  SyntaxData sd;
  sd.nbTopoColumns = 8; // by default

  CHECKCONDVA(len > 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ss), "MTG", "1"));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss), "MTG", args[0].tag.string().data(), "STRING"));
 
  input_file = ((AMString*)(args[0].val.p))->data();

  while (argth < args.length()) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "MTG", (argth+1)/2+1));

    assert(argth + 1 < args.length()); // must contain at least two parameters : this is verified syntactically

    if (*(AMString*)(args[argth].val.p) == "ErrorNb") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      CHECKCONDVA(args[argth+1].val.i > 0,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "MTG", (argth+1)/2+1, "positive"));

      err_nb = args[argth+1].val.i;

    }
    else if (*(AMString*)(args[argth].val.p) == "VtxNumber") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      CHECKCONDVA(args[argth+1].val.i > 0,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "MTG", (argth+1)/2+1, "positive"));

      vtx_size = args[argth+1].val.i;

    }
    else if (*(AMString*)(args[argth].val.p) == "AdjustSize") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER || args[argth+1].tag() ==AMObjType::BOOL,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT or BOOL"));

      if (!args[argth+1].val.i)
        adjust_size = args[argth+1].val.i;
	}
    else if (*(AMString*)(args[argth].val.p) == "DataType") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      if (args[argth+1].val.p)
        data_type = ((AMString*)(args[argth+1].val.p))->data();
    }
    else if (*(AMString*)(args[argth].val.p) == "FeatureList") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::ARRAY,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      if (args[argth+1].val.p)
        feature_list = ((Array*)(args[argth+1].val.p));
    }
    else if (*(AMString*)(args[argth].val.p) == "FeatureMap") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::ARRAY,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      if (args[argth+1].val.p)
        feature_map = ((Array*)(args[argth+1].val.p));
    }
    else if (*(AMString*)(args[argth].val.p) == "OutputFile") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      if (args[argth+1].val.p)
        output_file = ((AMString*)(args[argth+1].val.p))->data();
    }
    else if (*(AMString*)(args[argth].val.p) == "HeaderFile") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      if (args[argth+1].val.p)
        header_file = ((AMString*)(args[argth+1].val.p))->data();
    }
    else if (*(AMString*)(args[argth].val.p) == "NbTopoColumns") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      CHECKCONDVA(args[argth+1].val.i > 0,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "MTG", (argth+1)/2+1, "positive"));

      sd.nbTopoColumns = args[argth+1].val.i;

    }
    else if (*(AMString*)(args[argth].val.p) == "DiscardSymbols") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "MTG", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      if (args[argth+1].val.p)
        discard_symbols = ((AMString*)(args[argth+1].val.p))->data();
    }
    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "MTG", (argth+1)/2+1));

    }

    argth += 2;

  }



  AML_MTG* mtg=NULL;

  if (data_type == "LSystem") {

    // Input stream comes from the first argument
	ifstream is(input_file.c_str());
	if (!is) {
		cerr << "Error in reading file " << input_file << endl;
		return AMObj(AMObjType::ERROR);
	}
	else cerr << "File " << input_file << " opened for reading ..." << endl;

	// Output stream (default is cout)
	ofstream os(output_file.c_str());
	if (!os) {
		cerr << "Error in opening file " << output_file << endl;
		return AMObj(AMObjType::ERROR);
	}
	else cerr << "File " << output_file << " opened for writing ..." << endl;

	// Building the lexer
	LsystemToMTGLexer l_system_lexer(&is, &cerr); 

	// Building the L-SystemToMTG parser
    GenericParser<float> l_system_parser(lsystemToMTG_yyparse);

	// Writing the header to the MTG file
	ifstream hs(header_file.c_str());
	if (!hs) {
		cerr << "Error in reading file " << header_file << endl;
		return AMObj(AMObjType::ERROR);
	}	

	// tranferring the header data into the MTG file
    string tmp_s;
	char c;
	while (hs.get(c)) tmp_s += c;
	os << tmp_s;
	hs.close();

	// Creating the list of features
	os << "FEATURES:" << endl;
	os << "NAME\tTYPE" << endl;

	// builds the list of feature names

	list<string> feature_names;
	sd.featureNb = 0;

	if (feature_list) {
	  sd.featureNb = feature_list->entries();
      ArrayIter* pnext = feature_list->iterator();
      ArrayIter& next = *pnext;
      while (next()) {
        feature_names.push_back(*(AMString*)(next.key().val.p));
		os << feature_names.back() << "\tREAL" << endl;
      }
	  delete pnext;
	}

	// builds the feature map 
	int nb_symbols = 0;
	char symbol;
	if (feature_map) {
	  nb_symbols = feature_map->entries();
      ArrayIter* pnext1 = feature_map->iterator();
      ArrayIter& next1 = *pnext1;
      while (next1()) { // Loop on pairs of symbol and lists of indexes
		// Check first that this element is a list containing two elements
		List* pair = (List*)(next1.key().val.p);
        ListIter* pnext2 = pair->iterator();
        ListIter& next2 = *pnext2;
		int k = 1;
        while (next2()) {
		  // checks that the first element is a char
		  if (k==1) {
		    symbol = next2.key().val.c;
		  }
		  // checks that the second element is an array
		  if (k==2) {
			Array* indexes = (Array*)(next2.key().val.p);
            ArrayIter* pnext3 = indexes->iterator();
            ArrayIter& next3 = *pnext3;
			vector<int> v(feature_list->entries());
            while (next3()) { // loop on the indexes of symbol
			  v.push_back(next3.key().val.i);
 			}
		    delete pnext3;
            (sd.mapSymbolArgs)[symbol] = v;
		  }
		  if (k>2) {
			  // generates an error
			  break;
		  }
		  k++;
		}
		delete pnext2;
	  }
	  delete pnext1;
	}

	// creates the first line of the MTG code
	os << endl;
	os << "MTG:" << endl;
    os << "TOPO"; 
	for (int j=0; j<sd.nbTopoColumns; j++) os << "\t";
	for (list<string>::iterator pp=feature_names.begin();
	     pp!= feature_names.end();
		 pp++) os << *pp << "\t";
	os << endl;

	// string of symbols that can be discarded
	sd.discard_symbols = discard_symbols;

	// Parsing the l-system string and generating the MTG
	  bool ret = l_system_parser.parse(&l_system_lexer, os, (void*)(&sd));
    
	is.close();
	os.close();

	// The parser returns true if succeed 
	// In this case, the output file contains the corresponding MTG
	input_file = output_file;
 
  }


   mtg = new AML_MTG(input_file.c_str(), vtx_size, err_nb, adjust_size);
   assert(mtg);

	if (mtg && mtg->isValid()) {
	   AMLCOMMENT("MTG loaded ...");
	   activateMTG(AMObj(AMObjType::MTG,mtg));
	   return AMObj(AMObjType::MTG,mtg);
	}
    else {
      delete mtg;
      AMLCOMMENT("Parse errors : MTG could not be loaded ...");
      return AMObj(AMObjType::ERROR);
	}

}

static AmlBoolean vtxTestScale(MTG* g, VId v, void* pscale) {

  assert(g);
  assert(pscale);

  if (g->vscale(v) == *(int*)pscale) return TRUE;
  else return FALSE;

}

static AMObj MTG_VtxList(const AMObjVector& args) {

  int len = args.length();

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 0 || len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ssd), "VtxList", "0", 2));

  if( args.length() == 2) { // treatment of options

    if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

    CHECKCONDVA(args[0].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "VtxList",1));

    CHECKCONDVA((*(AMString*)args[0].val.p) == "Scale",
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds), "VtxList",1,"Scale"));

    CHECKCONDVA(args[1].tag() ==AMObjType::INTEGER,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VtxList", 1, args[1].tag.string().data(), "INT"));

    CHECKCONDVA(args[1].val.i > 0,
                genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "MTG", 1, "positive"));

    CHECKCONDVA(args[1].val.i <= active_mtg->scaleNb(),
                genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "MTG", 1, "a valid scale"));

    int scale = args[1].val.i;

    Array* p = new SLArray;
    MTGVertexIter next(active_mtg);

    while (next.findNext(vtxTestScale, &scale)) {

      *p += AMObj(AMObjType::VTX, next.key());

    }

    return AMObj(AMObjType::ARRAY,p);
  }
  else {

    Array* p = new SLArray;
    MTGVertexIter next(active_mtg);

    while (next()) {

      *p += AMObj(AMObjType::VTX, next.key());

    }

    return AMObj(AMObjType::ARRAY,p);
  }

}

// ----------------------------------
// Operators giving Vertex Attributes
// ----------------------------------

static AMObj MTG_Class(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Class", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() == AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Class", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");


  AMObj d(AMObjType::CHAR);
  d.val.c = active_mtg->symbol(args[0].val.i);
  return d;

}

static AMObj MTG_Index(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Index", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Index", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  AMObj d(AMObjType::INTEGER);
  d.val.i = active_mtg->vindex(args[0].val.i);
  return d;

}

static AMObj MTG_Scale(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Scale", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER || args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Scale", 1, args[0].tag.string().data(), "VTX or PLANTFRAME or LINETREE"));

  if(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER){
      CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                      "Vertex undefined");

      AMObj d(AMObjType::INTEGER);
      d.val.i = active_mtg->vscale(args[0].val.i);
      return d;
  }
  else if(args[0].tag() ==AMObjType::PLANTFRAME){
     PlantFrame *  pf = (PlantFrame*)args[0].val.p;
     int s = pf->_plant->getLevel();
     AMObj d(AMObjType::INTEGER);
     d.val.i = s;
     return d;
  }
  else if(args[0].tag() ==AMObjType::LINETREE){
     PlantFrame *  pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;
     int s = pf->_plant->getLevel();
     AMObj d(AMObjType::INTEGER);
     d.val.i = s;
     return d;
  }
  return AMObj(AMObjType::UNDEF);
}

static AMObj MTG_ClassScale(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "ClassScale", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::CHAR|| args[0].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "ClassScale", 1, args[0].tag.string().data(), "CHAR"));

  char classname;
  if (args[0].tag() ==AMObjType::CHAR)
    classname = args[0].val.c;
  else 
    {
    RWCString optionval(*(AMString*)args[0].val.p);
    if (optionval.size() != 1)
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "ClassScale", 1, args[0].tag.string().data(), "CHAR");
    else 
      classname= optionval(0);
    }
  VClass classid = active_mtg->classId(classname);

  CHECKDEFINECOND(active_mtg->isValidClass(classid),
                  "Class undefined");

  AMObj d(AMObjType::INTEGER);
  d.val.i = active_mtg->classScale(classid);
  return d;

}


static AMObj MTG_EdgeType(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "EdgeType", 2));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "EdgeType", 1, args[0].tag.string().data(), "VTX"));

  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "EdgeType", 2, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  CHECKDEFINECOND(active_mtg->existsVertex(args[1].val.i),
                  "Vertex undefined");

  AMObj d(AMObjType::CHAR);
  d.val.c = active_mtg->edgeSymbol(active_mtg->edgeType(args[0].val.v, args[1].val.v));
  return d;

}

static AMObj MTG_Feature(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 2 || args.length() == 3,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Feature", 2));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args.length() == 3) if (args[2].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Feature", 1, args[0].tag.string().data(), "VTX"));
  CHECKCONDVA(args[1].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Feature", 2, args[1].tag.string().data(), "STRING"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  static RWCString lastfeat;
  static MTG* last_active_mtg = 0; // mtg used during the previous call to an MTG function
  static FIndex findex = UNDEF;


  RWCString feat_name(*(AMString*)(args[1].val.p));

  //cerr << "lastfeature     = " << lastfeat << endl;
  //cerr << "current feature = " << feat_name << endl;

  // To avoid searching at each call the findex associated with that feature name
  if (active_mtg != last_active_mtg || lastfeat != feat_name) {

    // cerr << "Retrieving new feature name ... ";

    findex = checkExistsFeature(feat_name.data());

    // cerr << "findex found is " << findex << endl;

    CHECKCONDVA(findex != UNDEF,
                genAMLError(ERRORMSG(MTG_UNDEF_FEAT_NAME_ss), "Feature", feat_name.data()));

    // cerr << "findex found is " << findex << endl;

    last_active_mtg = active_mtg;

    lastfeat = feat_name;

  }

  CHECKCONDVA(findex != UNDEF,
              genAMLError(ERRORMSG(MTG_UNDEF_FEAT_NAME_ss), "Feature", feat_name.data()));

  if (args.length() == 3)
  CHECKCONDVA(args[2].tag() == AMObjType::DATE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Feature", 3, args[2].tag.string().data(), "DATE"));

  // cerr << "Feature retrieved : " << active_mtg->feature(args[0].val.i, findex, LUNDEF)->i << endl;
  // cerr << "sizeof(Feature) : " << sizeof(Feature) << endl;

  //cerr << "arg[0] = " << args[0] << endl;
  //cerr << "findex = " << findex << endl;

  const Feature* f;
  if (args.length() == 2) f = active_mtg->feature(args[0].val.i, findex, LUNDEF);
  else f = active_mtg->feature(args[0].val.i, findex, args[2].val.d);

  if (f) {

    if (f->i == -1) return AMObj(AMObjType::UNDEF);

    // copy from union Feature to union AMObj
    switch(featureType(findex)()) {

    case AMObjType::STRING:
      return AMObj(AMObjType::STRING, new AMString(f->s));
    case AMObjType::REAL:
      return AMObj(AMObjType::REAL, f->r); // float
    case AMObjType::INTEGER:
      return AMObj(AMObjType::INTEGER, (int) f->i); // int <- long !!!
    case AMObjType::DATE:
      return AMObj(AMObjType::DATE, (long) f->i); // long = long
    default:
      return  AMObj(AMObjType::UNDEF);
    }
  }
  else return AMObj(AMObjType::UNDEF);

}


static AMObj MTG_DateSample(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;
  int argth = 1;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() < 6,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "DateSample", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "DateSample", 1, args[0].tag.string().data(), "VTX"));

  Date mind = (long) -1;
  Date maxd = (long) -1;

  while (argth < args.length()) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "DateSample", (argth+1)/2+1));

    assert(argth + 1 < args.length()); // must contain at least two parameters : this is verified syntactically

    if (*(AMString*)(args[argth].val.p) == "MaxDate") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::DATE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "DateSample", (argth+1)/2+1, args[argth+1].tag.string().data(), "DATE"));


      maxd = args[argth+1].val.d;

    }
    else if (*(AMString*)(args[argth].val.p) == "MinDate") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::DATE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "DateSample", (argth+1)/2+1, args[argth+1].tag.string().data(), "DATE"));

      mind = args[argth+1].val.d;

    }
    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "MTG", (argth+1)/2+1));

    }

    argth += 2;

  }


  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");


  IntList* list = active_mtg->dateSample(args[0].val.i);

  Array* p = new SLArray;

  IntListIter next(*list);

  int minok, maxok;

  while (next()) {

    minok = (mind == -1 || (mind != -1 && mind <= (long) next.key()));
    maxok = (maxd == -1 || (maxd != -1 && maxd >= (long) next.key()));

    if (minok && maxok)
        *p += AMObj(AMObjType::DATE,(long) next.key());

  }


  delete list;

  return AMObj(AMObjType::ARRAY, p);

}


static AMObj MTG_FirstDefinedFeature(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() < 7,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "FirstDefinedFeature", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "FirstDefinedFeature", 1, args[0].tag.string().data(), "VTX"));
  CHECKCONDVA(args[1].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "FirstDefinedFeature", 2, args[1].tag.string().data(), "STRING"));

  Date mind = (long)-1;
  Date maxd = (long)-1;

  RWCString feat_name(*(AMString*)(args[1].val.p));

  FIndex findex = UNDEF;
  findex = checkExistsFeature(feat_name.data());
  CHECKCONDVA(findex != UNDEF,
              genAMLError(ERRORMSG(MTG_UNDEF_FEAT_NAME_ss), "FirstDefinedFeature", feat_name.data()));


  int argth = 2;

  while (argth < args.length()) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "FirstDefinedFeature", (argth+1)/2+1));

    assert(argth + 1 < args.length()); // must contain at least two parameters : this is verified syntactically

    if (*(AMString*)(args[argth].val.p) == "MaxDate") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::DATE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "FirstDefinedFeature", (argth+1)/2+1, args[argth+1].tag.string().data(), "DATE"));


      maxd = args[argth+1].val.d;

    }
    else if (*(AMString*)(args[argth].val.p) == "MinDate") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::DATE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "FirstDefinedFeature", (argth+1)/2+1, args[argth+1].tag.string().data(), "DATE"));

      mind = args[argth+1].val.d;

    }
    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "MTG", (argth+1)/2+1));

    }

    argth += 2;

  }


  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");


  IntList* list = active_mtg->dateSample(args[0].val.i);

  IntListIter next(*list);

  int minok, maxok;
  const Feature* f;

  Date date = (long)-1;

  while (next()) {

    minok = (mind == -1 || (mind != -1 && mind <= (long) next.key()));
    maxok = (maxd == -1 || (maxd != -1 && maxd >= (long) next.key()));

    if (minok && maxok) {
      date = (long) next.key();
      f = active_mtg->feature(args[0].val.i, findex, date);
      if (f && f->i != -1) break;
    }

  }

  delete list;

  if (date == -1) return AMObj(AMObjType::UNDEF);
  else return AMObj(AMObjType::DATE, (long) date);

}


static AMObj MTG_LastDefinedFeature(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() < 7,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "LastDefinedFeature", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[1].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "LastDefinedFeature", 1, args[0].tag.string().data(), "VTX"));
  CHECKCONDVA(args[1].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "LastDefinedFeature", 2, args[1].tag.string().data(), "STRING"));

  Date mind = (long)-1;
  Date maxd = (long)-1;

  RWCString feat_name(*(AMString*)(args[1].val.p));

  FIndex findex = UNDEF;
  findex = checkExistsFeature(feat_name.data());
  CHECKCONDVA(findex != UNDEF,
              genAMLError(ERRORMSG(MTG_UNDEF_FEAT_NAME_ss), "LastDefinedFeature", feat_name.data()));


  int argth = 2;

  while (argth < args.length()) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "LastDefinedFeature", (argth+1)/2+1));

    assert(argth + 1 < args.length()); // must contain at least two parameters : this is verified syntactically

    if (*(AMString*)(args[argth].val.p) == "MaxDate") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::DATE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "LastDefinedFeature", (argth+1)/2+1, args[argth+1].tag.string().data(), "DATE"));


      maxd = args[argth+1].val.d;

    }
    else if (*(AMString*)(args[argth].val.p) == "MinDate") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::DATE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "LastDefinedFeature", (argth+1)/2+1, args[argth+1].tag.string().data(), "DATE"));

      mind = args[argth+1].val.d;

    }
    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "MTG", (argth+1)/2+1));

    }

    argth += 2;

  }


  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");


  IntList* list = active_mtg->dateSample(args[0].val.i);

  IntListIter next(*list);

  int minok, maxok;
  const Feature* f;

  Date date = (long)-1;

  while (next()) {

    minok = (mind == -1 || (mind != -1 && mind <= (long) next.key()));
    maxok = (maxd == -1 || (maxd != -1 && maxd >= (long) next.key()));

    if (minok && maxok) {
      date = (long) next.key();
      f = active_mtg->feature(args[0].val.i, findex, (long) next.key());
      if (f && f->i != -1) date = (long) next.key();
    }

  }

  delete list;

  if (date == -1) return AMObj(AMObjType::UNDEF);
  else return AMObj(AMObjType::DATE, (long) date);

}


static AMObj MTG_NextDate(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "NextDate", 2));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "NextDate", 1, args[0].tag.string().data(), "VTX"));
  CHECKCONDVA(args[1].tag() ==AMObjType::DATE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "NextDate", 1, args[1].tag.string().data(), "DATE"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  IntList* list = active_mtg->dateSample(args[0].val.i);

  Date d0 = args[1].val.d;
  Date d = d0;

  IntListIter next(*list);

  while (next()) {

    if (d0 < (long) next.key()) {
      d = (long) next.key();
      break;
    }

  }

  delete list;

  return AMObj(AMObjType::DATE, (long) d);

}

static AMObj MTG_PreviousDate(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "PreviousDate", 2));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);
  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PreviousDate", 1, args[0].tag.string().data(), "VTX"));
  CHECKCONDVA(args[1].tag() ==AMObjType::DATE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PreviousDate", 1, args[1].tag.string().data(), "DATE"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  IntList* list = active_mtg->dateSample(args[0].val.i);

  Date d0 = args[1].val.d;
  Date d = d0;

  IntListIter next(*list);

  while (next()) {

    if (d0 <= next.key()) {
      break;
    }
    d = (long) next.key();

  }

  delete list;

  return AMObj(AMObjType::DATE, (long) d);

}

// ----------------------------
// Operators returning a Vertex
// ----------------------------

static AMObj MTG_MTGRoot(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 0,
              genAMLError(ERRORMSG(K_NO_ARG_ERR_s), "MTGRoot"));

  AMObj d(AMObjType::VTX);
  d.val.i = active_mtg->mtgRoot();
  return d;

}

static AMObj MTG_Defined(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Defined", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::BOOL, FALSE);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Defined", 1, args[0].tag.string().data(), "VTX"));


  AMObj d(AMObjType::BOOL);
  d.val.i = active_mtg->existsVertex(args[0].val.i);
  return d;

}

static AMObj topoOptions(const char* fname, const AMObjVector& args, int argth, int& restriction, VId& container, EType& edgeType, int& scale) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;
  int len = args.length();

  assert(args[0].tag() == AMObjType::VTX || args[0].tag() == AMObjType::INTEGER);
  VId the_vtx = args[0].val.i; // In all the functions using topoOptions() the first arg should be a VTX

  while (argth < len) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), fname, (argth+1)/2+1));

    RWCString option(*(AMString*)(args[argth].val.p));

    if (restriction >= -1 && option == "RestrictedTo") { // discard this option if container = -1

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), fname, (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      RWCString optionval(*(AMString*)args[argth+1].val.p);

      if (optionval == "SameComplex") {

        restriction = SAMECOMPLEX;

      }
      else if (optionval == "SameAxis") {

        restriction = SAMEAXIS;

      }
      else if (optionval == "NoRestriction") {

        restriction = NORESTRICTION;

      }
      else {

        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), fname, (argth+1)/2+1, "one of CSameComplex, SameAxis, NoRestriction"));
      }

    }
    else if (container >= -1 && option == "ContainedIn") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER || args[argth+1].tag() ==AMObjType::VTX,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), fname, (argth+1)/2+1, args[argth+1].tag.string().data(), "VTX"));

      CHECKCONDVA(active_mtg->existsVertex(args[argth+1].val.i),
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), fname, (argth+1)/2+1, "a defined vertex"));

      CHECKCONDVA(active_mtg->vscale(args[argth+1].val.i) < active_mtg->vscale(the_vtx),
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), fname, (argth+1)/2+1, "at a less detailed scale"));

      container = args[argth+1].val.i;

    }
    else if (edgeType != NONE && option == "EdgeType") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::CHAR || args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), fname, (argth+1)/2+1, args[argth+1].tag.string().data(), "CHAR"));

	  char edgetype;
	  if(args[argth+1].tag() ==AMObjType::CHAR) edgetype = args[argth+1].val.c;
	  else {
		RWCString optionval(*(AMString*)args[argth+1].val.p);
		if (optionval.size() != 1)
			genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), fname, (argth+1)/2+1, args[argth+1].tag.string().data(), "CHAR");
		else edgetype = optionval(0);
	  }

      switch (edgetype) {

      case '+':
        edgeType = PLUS;
        break;
      case '<':
        edgeType = LESS;
        break;
      case '*':
        edgeType = ANYTOPO;
        break;
      default:
        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), fname, (argth+1)/2+1, "one of '+' , '<', '*'"));

      }

    }
    else if (scale >= -1 && option == "Scale") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), fname, (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      CHECKCONDVA(active_mtg->isValidScale(args[argth+1].val.i),
                  genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), fname, (argth+1)/2+1, "a valid scale"));

      scale = args[argth+1].val.i;

    }
    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), fname, (argth+1)/2+1));

    }

    argth += 2;

  }

  // Check for option compatibility

  CHECKCONDVA(!(restriction == SAMEAXIS && edgeType == PLUS),
              genAMLError(ERRORMSG(K_OPTION_VALUES_INCOMPATIBLE_ERR_sd), fname, (argth-1)/2+1));


  return AMObj(AMObjType::VOID);

}

static AMObj MTG_Father(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;
  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);

  CHECKCONDVA(len >= 1 && len <=7,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ss), "Father", 1));

  if (args[0].tag == AMObjType::UNDEF) return AMObj(AMObjType::UNDEF);

  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Father", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  AMObj d(AMObjType::VTX);

  // Treatment of options
  int restriction = NORESTRICTION;
  VId container = -1;
  EType edgeType = ANYTOPO;
  int scaleopt = -1;

  AMObj op_res = topoOptions("Father", args, 1, restriction, container, edgeType, scaleopt);

  if (op_res.tag == AMObjType::ERROR) return op_res;


  if (restriction == NORESTRICTION) {

    if (scaleopt <= -1) {

      d.val.i = active_mtg->topoFather(args[0].val.i, edgeType);

    }
    else {

      int loc = active_mtg->location(args[0].val.i);

      if (loc != -1)
        d.val.i = active_mtg->findCompoAncestorAtScale(loc, scaleopt);
      else d.val.i = -1;

      if (d.val.i == active_mtg->findCompoAncestorAtScale(args[0].val.i, scaleopt)) d.val.i = -1;

    }

    if (container != -1 && active_mtg->existsVertex(d.val.i)) {

      if (!active_mtg->isCompoAncestorOf(container, d.val.i)) d.val.i = -1;

    }

  }
  else if (restriction == SAMECOMPLEX) {

    if (scaleopt <= -1) d.val.i = active_mtg->localTopoFather(args[0].val.i, edgeType);
    else {

      int loc = active_mtg->location(args[0].val.i);
      int container = active_mtg->compoFather(args[0].val.i);

      if (loc != -1)
        d.val.i = active_mtg->findCompoAncestorAtScale(loc, scaleopt);
      else d.val.i = -1;

      if (!active_mtg->isCompoAncestorOf(container, d.val.i)) d.val.i = -1;

    }

  }
  else if (restriction == SAMEAXIS) {

    d.val.i = active_mtg->topoFather(args[0].val.i, LESS);
    if (scaleopt > -1) {

      if (d.val.i != -1) { // le pere est bien sur le meme axe

        int loc = active_mtg->location(args[0].val.i);
        if (loc != -1)
          d.val.i = active_mtg->findCompoAncestorAtScale(loc, scaleopt);
        else d.val.i = -1;

      }

    }

    if (container != -1 && active_mtg->existsVertex(d.val.i)) {
            if (!active_mtg->isCompoAncestorOf(container, d.val.i)) d.val.i = -1;
    }
  }
  else assert(FALSE);

  if (d.val.i == -1) return AMObj(AMObjType::UNDEF);
  else return d;

}


static AMObj MTG_Predecessor(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;
  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);

  CHECKCONDVA(len >= 1 && len <=5,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_ss), "Predecessor", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Predecessor", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  AMObj d(AMObjType::VTX);

  // Treatment of options
  int restriction = NORESTRICTION;
  VId container = -1;
  EType edgeType = NONE; // this option is not allowed here
  int scaleopt = -1;

  AMObj op_res = topoOptions("Predecessor", args, 1, restriction, container, edgeType, scaleopt);

  edgeType = LESS;

  if (op_res.tag == AMObjType::ERROR) return op_res;


  if (restriction == NORESTRICTION) {

    d.val.i = active_mtg->topoFather(args[0].val.i, edgeType);

    if (container != -1 && active_mtg->existsVertex(d.val.i)) {

      if (!active_mtg->isCompoAncestorOf(container, d.val.i)) d.val.i = -1;

    }

  }
  else if (restriction == SAMECOMPLEX) {

    d.val.i = active_mtg->localTopoFather(args[0].val.i, edgeType);

  }
  else if (restriction == SAMEAXIS) {

    d.val.i = active_mtg->topoFather(args[0].val.i, LESS);

    if (container != -1 && active_mtg->existsVertex(d.val.i)) {

      if (!active_mtg->isCompoAncestorOf(container, d.val.i)) d.val.i = -1;

    }

  }
  else assert(FALSE);


  if (d.val.i == -1) return AMObj(AMObjType::UNDEF);
  else return d;

}

static AMObj MTG_Sons(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;
  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len >= 1 && len <=7,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Sons", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Sons", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  // Treatment of options
  int restriction = NORESTRICTION;
  VId container = -1;
  EType edgeType = ANYTOPO;
  int scaleopt = -1;

  AMObj op_res = topoOptions("Sons", args, 1, restriction, container, edgeType, scaleopt);
  if (op_res.tag == AMObjType::ERROR) return op_res;

  VIdList* list;

  int argscale = active_mtg->vscale(args[0].val.i);

  if (restriction == NORESTRICTION) {

    if (scaleopt <= -1 || argscale == scaleopt) {

      list = new VIdList;
      VIdList* sonlist = active_mtg->topoSons(args[0].val.i, edgeType);

      VIdListIter next(*sonlist);

      while (next()) {

        if (container != -1) {
          if (active_mtg->isCompoAncestorOf(container, next.key())) list->append(next.key());
        }
        else list->append(next.key());

      }
      delete sonlist;

    }
    else { // scaleopt > -1 && argscale != scaleopt

      argscale = active_mtg->vscale(args[0].val.i);

      if (argscale > scaleopt) {

        VId complex = active_mtg->findCompoAncestorAtScale(args[0].val.i, scaleopt);
        list = new VIdList;
        VIdList* sonlist = active_mtg->topoSons(complex, edgeType);

        // puis on filtre ceux qui n'ont pas la bonne location

        VIdListIter next(*sonlist);
        int loc;
        while (next()) {

          loc = active_mtg->location(next.key());

          if (loc != -1)
            complex = active_mtg->findCompoAncestorAtScale(loc, argscale);
          else complex = -1;

          if (complex == args[0].val.i) list->append(next.key());

        }
        delete sonlist;

      }
      else { // argscale < scaleopt

        VIdList* componentlist;
        VIdList* sonlist;
        list = new VIdList;

        componentlist = active_mtg->compoSons(args[0].val.i, scaleopt);

        assert(componentlist);

        VIdListIter next(*componentlist);

        while (next()) {

          sonlist = active_mtg->topoSons(next.key(), edgeType);
          if (sonlist) {
            VIdListIter next2(*sonlist);
            while (next2()) {
              if (active_mtg->findCompoAncestorAtScale(next2.key(), argscale)!=args[0].val.i)
                list->insert(next2.key());
            }
            delete sonlist;
          }
        }

        delete componentlist;

      }

    }

  }
  else if (restriction == SAMECOMPLEX) {

    list = active_mtg->localTopoSons(args[0].val.i, edgeType);

  }
  else if (restriction == SAMEAXIS) {

    VIdList* sonlist = active_mtg->topoSons(args[0].val.i, LESS);;
    list = new VIdList;

    VIdListIter next(*sonlist);

    while (next()) {

      if (container != -1) {
        if (active_mtg->isCompoAncestorOf(container, next.key())) list->append(next.key());
      }
      else list->append(next.key());

    }

    delete sonlist;

  }
  else assert(FALSE);

  Array* p = new SLArray(list);
  delete list;

  return AMObj(AMObjType::ARRAY, p);

}


static AMObj MTG_Successor(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;
  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len >= 1 && len <=5,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Successor", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Successor", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  // Treatment of options
  int restriction = NORESTRICTION;
  VId container = -1;
  EType edgeType = NONE;
  int scaleopt = -1;

  AMObj op_res = topoOptions("Sons", args, 1, restriction, container, edgeType, scaleopt);
  if (op_res.tag == AMObjType::ERROR) return op_res;

  edgeType = LESS;

  VIdList* list;

  if (restriction == NORESTRICTION) {

    VIdList* sonlist = active_mtg->topoSons(args[0].val.i, edgeType);
    list = new VIdList;

    VIdListIter next(*sonlist);

    while (next()) {

      if (container != -1) {
        if (active_mtg->isCompoAncestorOf(container, next.key())) list->append(next.key());
      }
      else list->append(next.key());

    }
    delete sonlist;

  }
  else if (restriction == SAMECOMPLEX) {

    list = active_mtg->localTopoSons(args[0].val.i, edgeType);

  }
  else if (restriction == SAMEAXIS) {

    VIdList* sonlist = active_mtg->topoSons(args[0].val.i, LESS);
    list = new VIdList;

    VIdListIter next(*sonlist);

    while (next()) {

      if (container != -1) {
        if (active_mtg->isCompoAncestorOf(container, next.key())) list->append(next.key());
      }
      else list->append(next.key());

    }
    delete sonlist;

  }
  else assert(FALSE);

  VId succ = -1;

  if (list->entries()) succ = list->first();

  delete list;

  if (succ == -1) return AMObj(AMObjType::UNDEF);
  else return AMObj(AMObjType::VTX, succ);

}


static AMObj MTG_Descendants(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;
  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len >= 1 && len <=7,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Descendants", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Descendants", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");


  // Treatment of options
  int restriction = NORESTRICTION;
  VId container = -1;
  EType edgeType = ANYTOPO;
  int scaleopt = -1;

  AMObj op_res = topoOptions("Descendants", args, 1, restriction, container, edgeType, scaleopt);
  if (op_res.tag == AMObjType::ERROR) return op_res;

  VIdList* list;

  if (restriction == NORESTRICTION) {

    VIdList* sonlist = active_mtg->topoDescendants(args[0].val.i, edgeType);
    list = new VIdList;

    VIdListIter next(*sonlist);

    while (next()) {

      if (container != -1) {
        if (active_mtg->isCompoAncestorOf(container, next.key())) list->append(next.key());
      }
      else list->append(next.key());

    }
    delete sonlist;

  }
  else if (restriction == SAMECOMPLEX) {

    list = active_mtg->localTopoDescendants(args[0].val.i, edgeType);

  }
  else if (restriction == SAMEAXIS) {

    VIdList* sonlist = active_mtg->topoDescendants(args[0].val.i, LESS);
    list = new VIdList;

    VIdListIter next(*sonlist);

    while (next()) {

      if (container != -1) {
        if (active_mtg->isCompoAncestorOf(container, next.key())) list->append(next.key());
      }
      else list->append(next.key());

    }
    delete sonlist;

  }
  else assert(FALSE);

  Array* p = new SLArray(list);
  delete list;

  return AMObj(AMObjType::ARRAY,p);

}


static AMObj MTG_Ancestors(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;
  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len >= 1 && len <=7,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Ancestors", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Ancestors", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");


  // Treatment of options
  int restriction = NORESTRICTION;
  VId container = -1;
  EType edgeType = ANYTOPO;
  int scaleopt = -1;

  AMObj op_res = topoOptions("Ancestors", args, 1, restriction, container, edgeType, scaleopt);
  if (op_res.tag == AMObjType::ERROR) return op_res;

  VIdList* list;

  if (restriction == NORESTRICTION) {

    VIdList* sonlist = active_mtg->topoAncestors(args[0].val.i, edgeType);
    list = new VIdList;

    VIdListIter next(*sonlist);

    while (next()) {

      if (container != -1) {
        if (active_mtg->isCompoAncestorOf(container, next.key())) list->append(next.key());
      }
      else list->append(next.key());

    }
    delete sonlist;

  }
  else if (restriction == SAMECOMPLEX) {

    list = active_mtg->localTopoAncestors(args[0].val.i, edgeType);

  }
  else if (restriction == SAMEAXIS) {

    VIdList* sonlist = active_mtg->topoAncestors(args[0].val.i, LESS);
    list = new VIdList;

    VIdListIter next(*sonlist);

    while (next()) {

      if (container != -1) {
        if (active_mtg->isCompoAncestorOf(container, next.key())) list->append(next.key());
      }
      else list->append(next.key());

    }
    delete sonlist;

  }
  else assert(FALSE);

  Array* p = new SLArray(list);
  delete list;

  return AMObj(AMObjType::ARRAY,p);

}

static AMObj MTG_Root(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;
  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len >= 1 && len <=7,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Root", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Root", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");


  // Treatment of options
  int restriction = NORESTRICTION;
  VId container = -1;
  EType edgeType = ANYTOPO;
  int scaleopt = -1;

  AMObj op_res = topoOptions("Root", args, 1, restriction, container, edgeType, scaleopt);
  if (op_res.tag == AMObjType::ERROR) return op_res;

  AMObj d(AMObjType::VTX);

  if (restriction == NORESTRICTION) {

    d.val.i = active_mtg->findGlobalTopoRoot(args[0].val.i, edgeType);

    if (container != -1 && active_mtg->existsVertex(d.val.i)) {

      if (!active_mtg->isCompoAncestorOf(container, d.val.i)) d.val.i = -1;

    }

  }
  else if (restriction == SAMECOMPLEX) {

    d.val.i = active_mtg->findLocalTopoRoot(args[0].val.i, edgeType);

  }
  else if (restriction == SAMEAXIS) {

    d.val.i = active_mtg->findGlobalTopoRoot(args[0].val.i, LESS);

    if (container != -1 && active_mtg->existsVertex(d.val.i)) {

      if (!active_mtg->isCompoAncestorOf(container, d.val.i)) d.val.i = -1;

    }

  }
  else assert(FALSE);

  if (d.val.i == -1) return AMObj(AMObjType::UNDEF);
  else return d;

}

static AMObj MTG_Extremities(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;
  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len >= 1 && len <=7,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Extremities", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Extremities", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");


  // Treatment of options
  int restriction = NORESTRICTION;
  VId container = -1;
  EType edgeType = ANYTOPO;
  int scaleopt = -1;

  AMObj op_res = topoOptions("Extremities", args, 1, restriction, container, edgeType, scaleopt);
  if (op_res.tag == AMObjType::ERROR) return op_res;

  VIdList* list;

  if (restriction == NORESTRICTION) {

    VIdList* sonlist = active_mtg->topoExtremities(args[0].val.i, edgeType);
    list = new VIdList;

    VIdListIter next(*sonlist);

    while (next()) {

      if (container != -1) {
        if (active_mtg->isCompoAncestorOf(container, next.key())) list->append(next.key());
      }
      else list->append(next.key());

    }
    delete sonlist;

  }
  else if (restriction == SAMECOMPLEX) {

    list = active_mtg->localTopoExtremities(args[0].val.i, edgeType);

  }
  else if (restriction == SAMEAXIS) {

    VIdList* sonlist = active_mtg->topoExtremities(args[0].val.i, LESS);
    list = new VIdList;

    VIdListIter next(*sonlist);

    while (next()) {

      if (container != -1) {
        if (active_mtg->isCompoAncestorOf(container, next.key())) list->append(next.key());
      }
      else list->append(next.key());

    }
    delete sonlist;

  }
  else assert(FALSE);

  Array* p = new SLArray(list);
  delete list;

  return AMObj(AMObjType::ARRAY,p);

}




static AMObj compoOptions(const char* fname, const AMObjVector& args, int argth, int& scale) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;
  int len = args.length();

  //assert(args[0].tag() == AMObjType::VTX || args[0].tag() == AMObjType::INTEGER);
  //VId the_vtx = args[0].val.i; // In all the functions using topoOptions() the first arg should be a VTX

  while (argth < len) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), fname, (argth+1)/2+1));

    if (*(AMString*)(args[argth].val.p) == "Scale") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), fname, (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      CHECKCONDVA(args[argth+1].val.i > 0,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), fname, (argth+1)/2+1, "positive"));

      CHECKCONDVA(args[argth+1].val.i <= active_mtg->scaleNb(),
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), fname, (argth+1)/2+1, "a valid scale"));

      scale = args[argth+1].val.i;

    }
    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), fname, (argth+1)/2+1));

    }

    argth += 2;

  }

  return AMObj(AMObjType::VOID);

}

static AMObj MTG_Complex(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 1 || args.length() == 3,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Complex", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Complex", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  int scale = -1;

  AMObj op_res = compoOptions("Complex", args, 1, scale);
  if (op_res.tag == AMObjType::ERROR) return op_res;

  AMObj d(AMObjType::VTX);

  // returns -1 if the scale is not coherent

  if (scale == -1) d.val.i = active_mtg->compoFather(args[0].val.i);
  else d.val.i = active_mtg->findCompoAncestorAtScale(args[0].val.i, scale);

  if (d.val.i == -1) return AMObj(AMObjType::UNDEF);
  else return d;

}

static AMObj MTG_Components(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 1 || args.length() == 3,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Components", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Components", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  int scale = -1;

  AMObj op_res = compoOptions("Components",args, 1, scale);
  if (op_res.tag == AMObjType::ERROR) return op_res;

  VIdList* list;
  if (scale != -1) list = active_mtg->compoSons(args[0].val.i, scale);
  else list = active_mtg->compoSons(args[0].val.i);

  if (list) {
    Array* p = new SLArray(list);
    delete list;

    return AMObj(AMObjType::ARRAY,p);
  }
  else return AMObj(AMObjType::UNDEF);

}

static AMObj MTG_ComponentRoots(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 1 || args.length() == 3,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "ComponentRoots", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "ComponentRoots", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  int scale = -1;

  AMObj op_res = compoOptions("ComponentRoots",args, 1, scale);
  if (op_res.tag == AMObjType::ERROR) return op_res;

  VIdList* list;

  if (scale == -1)
  list = active_mtg->findLocalTopoRoots(args[0].val.i);
  else
  list = active_mtg->findLocalTopoRootsAtScale(args[0].val.i, scale);

  Array* p = new SLArray(list);
  delete list;

  return AMObj(AMObjType::ARRAY,p);

}

static AMObj MTG_Trunk(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 1 || args.length() == 3,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Trunk", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Trunk", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  int scale = -1;

  AMObj op_res = compoOptions("Trunk",args, 1, scale);
  if (op_res.tag == AMObjType::ERROR) return op_res;

  VIdList* list;

  if (scale == -1)
    list = active_mtg->findLocalTopoRoots(args[0].val.i);
  else {
    CHECKCONDVA(active_mtg->isValidScale(scale),
                genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "Trunk", 2, "a valid scale"));
    CHECKCONDVA(scale > active_mtg->vscale(args[0].val.i),
                genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "Trunk", 2, "a scale finer than the scale of the argument"));
    list = active_mtg->findLocalTopoRootsAtScale(args[0].val.i, scale);
  }

  VIdList* axis;
  VId firstv = UNDEF;

  if (list->entries()) {
    firstv = list->first();
    axis = active_mtg->findLessSequence(firstv);
  }
  else {
    axis = new VIdList;
  }

  Array* p = new SLArray(axis);
  delete list;
  delete axis;

  return AMObj(AMObjType::ARRAY,p);

}

static AMObj MTG_Location(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 1 || args.length() == 3,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Location", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Location", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  int scale = -1;

  AMObj op_res = compoOptions("Location",args, 1, scale);
  if (op_res.tag == AMObjType::ERROR) return op_res;

  AMObj d(AMObjType::VTX);

  d.val.i = active_mtg->location(args[0].val.i);

  if (scale != -1 && d.val.i != -1) {

    d.val.i = active_mtg->findCompoAncestorAtScale(d.val.i, scale);

  }

  if (d.val.i == -1) return AMObj(AMObjType::UNDEF);
  else return d;

}

// --------------------------
// Operators returning a SLList
// --------------------------

static AMObj MTG_Path(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 1 || args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Path", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Path", 1, args[0].tag.string().data(), "VTX"));
  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");
  VIdList* list;

  if (args.length() == 2) {
    CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Path", 2, args[1].tag.string().data(), "VTX"));
    CHECKDEFINECOND(active_mtg->existsVertex(args[1].val.i),
                  "Vertex undefined");

    list =  active_mtg->path(args[0].val.i, args[1].val.i);

  }
  else {

    VId root = active_mtg->findGlobalTopoRoot(args[0].val.i, ANYTOPO);

    list =  active_mtg->path(root, args[0].val.i);

  }

  Array* p = new SLArray(list);

  delete list;

  return AMObj(AMObjType::ARRAY,p);

}


static AMObj MTG_Axis(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 1 || args.length() == 3,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Axis", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Axis", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  int scale = -1;

  AMObj op_res = compoOptions("Axis", args, 1, scale);
  if (op_res.tag == AMObjType::ERROR) return op_res;

  VId firstv = active_mtg->findGlobalTopoRoot(args[0].val.i, LESS);

  int vscale = active_mtg->vscale(args[0].val.i);

  if (scale != -1 && vscale != scale) {

    if (scale < vscale) firstv = active_mtg->findCompoAncestorAtScale(firstv, scale);
    else firstv = active_mtg->findFirstComponentAtScale(firstv, scale);

  }

  if (!active_mtg->existsVertex(firstv)) return AMObj(AMObjType::UNDEF);

  VIdList* list = active_mtg->findLessSequence(firstv);
  Array* p = new SLArray(list);
  delete list;
  return AMObj(AMObjType::ARRAY,p);

}


// ----------------------------
// Operators between two Vertex
// ----------------------------

static AMObj MTG_Order(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() <= 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Order", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Order", 1, args[0].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  VId v1, v2;

  if (args.length() == 2) {

    CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Order", 2, args[1].tag.string().data(), "VTX"));
    CHECKDEFINECOND(active_mtg->existsVertex(args[1].val.i),
                    "Vertex undefined");

    v1 = args[0].val.i;
    v2 = args[1].val.i;

  }
  else {

    v2 = args[0].val.i;
    v1 = active_mtg->findGlobalTopoRoot(v2, ANYTOPO);

  }

  AMObj d(AMObjType::INTEGER);
  d.val.i = active_mtg->pathEdgeNb(v1, v2, PLUS);
  return d;

}

static AMObj MTG_Rank(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() <= 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Rank", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Rank", 1, args[0].tag.string().data(), "VTX"));
  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  VId v1, v2;

  if (args.length() == 2) {

    CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Order", 2, args[1].tag.string().data(), "VTX"));
    CHECKDEFINECOND(active_mtg->existsVertex(args[1].val.i),
                    "Vertex undefined");

    v1 = args[0].val.i;
    v2 = args[1].val.i;

  }
  else {

    v2 = args[0].val.i;
    v1 = active_mtg->findGlobalTopoRoot(v2, LESS);

  }

  AMObj d(AMObjType::INTEGER);
  d.val.i = active_mtg->pathLength(v1, v2, LESS);
  return d;

}

static AMObj MTG_Height(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() <= 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Height", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Height", 1, args[0].tag.string().data(), "VTX"));
  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");

  VId v1, v2;

  if (args.length() == 2) {

    CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Order", 2, args[1].tag.string().data(), "VTX"));
    CHECKDEFINECOND(active_mtg->existsVertex(args[1].val.i),
                    "Vertex undefined");

    v1 = args[0].val.i;
    v2 = args[1].val.i;

  }
  else {

    v2 = args[0].val.i;
    v1 = active_mtg->findGlobalTopoRoot(v2, ANYTOPO);

  }

  AMObj d(AMObjType::INTEGER);
  d.val.i = active_mtg->pathLength(v1, v2, ANYTOPO);
  return d;

}


static AMObj MTG_AlgOrder(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "AlgOrder", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "AlgOrder", 1, args[0].tag.string().data(), "VTX"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "AlgOrder", 2, args[1].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");
  CHECKDEFINECOND(active_mtg->existsVertex(args[1].val.i),
                  "Vertex undefined");

  AMObj d(AMObjType::INTEGER);
  d.val.i = active_mtg->algPathEdgeNb(args[0].val.i, args[1].val.i, PLUS);
  if (d.val.i == -1) d = AMObj(AMObjType::UNDEF);
  return d;

}

static AMObj MTG_AlgRank(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "AlgRank", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "AlgRank", 1, args[0].tag.string().data(), "VTX"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "AlgRank", 2, args[1].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");
  CHECKDEFINECOND(active_mtg->existsVertex(args[1].val.i),
                  "Vertex undefined");

  AMObj d(AMObjType::INTEGER);
  d.val.i = active_mtg->algPathLength(args[0].val.i, args[1].val.i, LESS);
  if (d.val.i == -1) d = AMObj(AMObjType::UNDEF);
  return d;

}

static AMObj MTG_AlgHeight(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "AlgHeight", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "AlgHeight", 1, args[0].tag.string().data(), "VTX"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "AlgHeight", 2, args[1].tag.string().data(), "VTX"));

  CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                  "Vertex undefined");
  CHECKDEFINECOND(active_mtg->existsVertex(args[1].val.i),
                  "Vertex undefined");

  AMObj d(AMObjType::INTEGER);
  d.val.i = active_mtg->algPathLength(args[0].val.i, args[1].val.i, ANYTOPO);
  if (d.val.i == -1) d = AMObj(AMObjType::UNDEF);
  return d;

}

// -----------------
// General operators
// -----------------

static AMObj MTG_Activate(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Activate", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::MTG,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Activate", 1, args[0].tag.string().data(), "MTG"));


  activateMTG(args[0]);

  AMObj d(AMObjType::MTG, args[0].val.p);

  return d;

}

static AMObj MTG_Active(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 0,
              genAMLError(ERRORMSG(K_NO_ARG_ERR_s), "Active"));

  AMObj current_mtg = activeMTG();

  if (!((AML_MTG*)activeMTG().val.p)) {

    AMLOUTPUT << "No MTG actif." << endl;

    return AMObj(AMObjType::UNDEF);

  }
  else return AMObj(AMObjType::MTG, (AML_MTG*)activeMTG().val.p);


  /*
  AMObjTableIter next(*amobjTable());

  while(next()) {

    if (next.value() == current_mtg && next.key() != ":CurrentMTG") return AMObj(AMObjType::STRING, new AMString(next.key()));

  }

  return AMObj(AMObjType::UNDEF);

  */


}




static AMObj MTG_PlantFrame(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();
  int argth = 1;

  FNode* lengthfun=NULL;
  FNode* categoryfun=NULL;
  FNode* alphafun=NULL;
  FNode* azimutfun=NULL;
  FNode* tetafun=NULL;
  FNode* phifun=NULL;
  FNode* psifun=NULL;
  FNode* topdiafun=NULL;
  FNode* botdiafun=NULL;
  FNode* xxfun=NULL;
  FNode* yyfun=NULL;
  FNode* zzfun=NULL;
  FNode* eulerfun=NULL;
  FNode* digitizedfun=NULL;
  Array* translation = NULL;
  Array* origin = NULL;
  ValType dist=0;
  AMString* stg_tmp = NULL;
  RWCString opt;
  RWCString length_algo;

  DressingFile* dressing_data = NULL;

  bool is_first_arg_array = false;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len > 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "PlantFrame", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER || args[0].tag() ==AMObjType::ARRAY ,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", 1, args[0].tag.string().data(), "VTX or ARRAY(VTX)"));

  int scale;

  if (args[0].tag() ==AMObjType::VTX || args[0].tag() ==AMObjType::INTEGER) {

    CHECKDEFINECOND(active_mtg->existsVertex(args[0].val.i),
                    "Vertex undefined");

    scale = active_mtg->vscale(args[0].val.i) + 1; // default scale

  }
  else { // the first argument is an array of vertices

    assert(args[0].tag() ==AMObjType::ARRAY);
    Array* array = (Array*) (args[0].val.p);

    CHECKCONDVA(array->entries() != 0,
                genAMLError(ERRORMSG(K_F_ARG_VALUE_NEG_ERR_sds), "PlantFrame", 1, "an empty array"));

    CHECKCONDVA(array->surfaceType() == AMObjType::VTX || array->surfaceType() == AMObjType::INTEGER,
                genAMLError(ERRORMSG(K_F_ARG_VALUE_NEG_ERR_sds), "PlantFrame", 1, "an empty array"));

    is_first_arg_array = true;

    const AMObj* pv = array->anElement();

    assert(pv);

    CHECKDEFINECOND(active_mtg->existsVertex((*pv).val.i),
                    "Vertex undefined");

    scale = active_mtg->vscale((*pv).val.i) + 1; // default scale

  }


  while (argth < len) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "PlantFrame", (argth+1)/2+1));

    assert(argth + 1 < len); // must contain at least two parameters : this is verified syntactically

    if (*(AMString*)(args[argth].val.p) == "Scale") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      CHECKCONDVA(args[argth+1].val.i > 0,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "PlantFrame", (argth+1)/2+1, "positive"));

      scale = args[argth+1].val.i;

    }else  if (*(AMString*)(args[argth].val.p) == "VoxelDist") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER || args[argth+1].tag() ==AMObjType::REAL,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT or REAL"));

      if (args[argth+1].tag() ==AMObjType::INTEGER) {
        CHECKCONDVA(args[argth+1].val.i >= 0,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "PlantFrame", (argth+1)/2+1, "positive"));

        dist = (ValType) args[argth+1].val.i;
      }
      else {
        CHECKCONDVA(args[argth+1].val.r >= 0,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "PlantFrame", (argth+1)/2+1, "positive"));

        dist = (ValType) args[argth+1].val.r;

      }


    }else  if (*(AMString*)(args[argth].val.p) == "TrunkDist" ||
               *(AMString*)(args[argth].val.p) == "TrunkDistance") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER || args[argth+1].tag() ==AMObjType::REAL,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT or REAL"));

      if (args[argth+1].tag() ==AMObjType::INTEGER) {
        CHECKCONDVA(args[argth+1].val.i >= 0,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "PlantFrame", (argth+1)/2+1, "positive"));

        dist = - (ValType) args[argth+1].val.i;

      }
      else {
        CHECKCONDVA(args[argth+1].val.r >= 0,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "PlantFrame", (argth+1)/2+1, "positive"));
        dist = - (ValType) args[argth+1].val.r;

      }


    } else if (*(AMString*)(args[argth].val.p) == "Length") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        lengthfun = (FNode*) args[argth+1].val.p;


    }
    else if (*(AMString*)(args[argth].val.p) == "LengthAlgo") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));


        stg_tmp = (AMString*) args[argth+1].val.p;
        length_algo=RWCString (stg_tmp->data());

    }
    else if (*(AMString*)(args[argth].val.p) == "Category") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        categoryfun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "TopDiameter") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        topdiafun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "BottomDiameter") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        botdiafun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "Alpha") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        alphafun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "Azimuth" ||
                *(AMString*)(args[argth].val.p) == "Azimut") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        azimutfun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "AA") { // angles d'euler

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        tetafun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "BB") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        phifun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "CC") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        psifun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "EulerAngles") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

        eulerfun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "DigitizedPoints") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

        digitizedfun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "XX") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        xxfun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "YY") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        yyfun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "ZZ") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        zzfun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "DressingData") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::DRESSING_DATA,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "DRESSING_DATA"));


        dressing_data = (DressingFile*) args[argth+1].val.p;


      }
      else if (*(AMString*)(args[argth].val.p) == "Mode") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));


        stg_tmp = (AMString*) args[argth+1].val.p;
        opt=RWCString (stg_tmp->data());

      }
      else if (*(AMString*)(args[argth].val.p) == "Translate") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::ARRAY,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY"));

        translation = (Array*) (args[argth+1].val.p);

      }
      else if (*(AMString*)(args[argth].val.p) == "Origin") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::ARRAY,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PlantFrame", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY"));

        origin = (Array*) (args[argth+1].val.p);

      }

    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "PlantFrame", (argth+1)/2+1));

    }

    argth += 2;

  }

  PlantFrame* tree_frame;

  if (!is_first_arg_array) { // the first arg is a vertex

    ValType* ptransl = 0;
    ValType* porigin = 0;

    // Translation et origin option que si c'est le trace d'un seul systeme ramifie.

    if (translation) {
      CHECKCONDVA(translation->entries() == 3,
                  genAMLError(ERRORMSG(MTG_OPTION_BADVALUE_s), "Translate"));

      ptransl = new ValType[3];

      ptransl[0] = (ValType) translation->at(0).val.r;
      ptransl[1] = (ValType) translation->at(1).val.r;
      ptransl[2] = (ValType) translation->at(2).val.r;
    }
    if (origin) {
      CHECKCONDVA(origin->entries() == 3,
                  genAMLError(ERRORMSG(MTG_OPTION_BADVALUE_s), "Origin"));

      porigin = new ValType[3];

      porigin[0] = (ValType) origin->at(0).val.r;
      porigin[1] = (ValType) origin->at(1).val.r;
      porigin[2] = (ValType) origin->at(2).val.r;

    }
    tree_frame = new PlantFrame(args[0].val.i, active_mtg, scale,
                                lengthfun,topdiafun,botdiafun,alphafun,azimutfun,tetafun,phifun,psifun,
                                categoryfun,xxfun,yyfun,zzfun,eulerfun,
                                opt,length_algo,dist,dressing_data, ptransl, porigin,
                                digitizedfun);

    delete [] ptransl;
  }
  else { // the first arg is an array of vertices

    ValType* porigin = 0;

    assert(args[0].tag() ==AMObjType::ARRAY);
    Array* array = (Array*) (args[0].val.p);

    VIdList list;

    int nb_vertices = array->entries();

    if (origin) {
      porigin = new ValType[3 * nb_vertices];

      CHECKCONDVA(origin->surfaceType() == AMObjType::ARRAY,
                  genAMLError(ERRORMSG(K_OPTION_VALUES_ERR_ss), "PlantFrame", "an array of arrays of REALs is expected for option Origin when the first argument is an array of vertices"));
      CHECKCONDVA(origin->entries() == nb_vertices,
                  genAMLError(ERRORMSG(K_OPTION_VALUES_ERR_ss), "PlantFrame", "the array of coordinates defined for Origin must have the same number elements as the array of vertices defined in argument 1"));

    }


    for(int i=0; i<nb_vertices; i++) {

      if (array->at(i).tag() != AMObjType::UNDEF) list.insert(array->at(i).val.i);

      if (origin) {

        Array* coords = (Array*) (origin->at(i).val.p);
        porigin[3*i]= coords->at(0).val.r;
        porigin[3*i+1]= coords->at(1).val.r;
        porigin[3*i+2]= coords->at(2).val.r;
      }

    }

    tree_frame = new PlantFrame(&list, active_mtg, scale,
                                lengthfun,topdiafun,botdiafun,alphafun,azimutfun,tetafun,phifun,psifun,
                                categoryfun,xxfun,yyfun,zzfun,eulerfun,
                                opt,length_algo,dist,dressing_data,porigin,
                                digitizedfun);

  }

  if (!tree_frame->isValid()) {
    // il y a eu une erreur dans le constructeur
    // on ne peut donc faire:
    // delete tree_frame
    // il faudrait mettre une fonction de nettoyage pour le cas ou le constructeur
    // plante.

    return AMObj(AMObjType::ERROR);
  }

  return AMObj(AMObjType::PLANTFRAME, tree_frame);

}


static AMObj MTG_VirtualPattern(const AMObjVector& args) {

  int len = args.length();
  int argth = 1;

  FNode* symbolfun=NULL;
  FNode* whorlfun=NULL;
  FNode* numberfun=NULL;
  FNode* colorfun=NULL;
  FNode* topdiafun=NULL;
  FNode* botdiafun=NULL;
  FNode* lengthfun=NULL;
  FNode* alphafun=NULL;
  FNode* betafun=NULL;
  FNode* gammafun=NULL;
  FNode* phyllofun=NULL;
  FNode* xxfun=NULL;
  FNode* yyfun=NULL;
  FNode* zzfun=NULL;
  FNode* tetafun=NULL;
  FNode* phifun=NULL;
  FNode* psifun=NULL;

  AMString* pattern_type;

  CHECKCONDVA(len > 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "VirtualPattern", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::STRING ,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", 1, args[0].tag.string().data(),"STRING"));

  pattern_type = (AMString*) args[0].val.p;

  CHECKCONDVA((*pattern_type) == "Fruit" ||
              (*pattern_type) == "Flower" ||
              (*pattern_type) == "DigitizedLeaf" ||
              (*pattern_type) == "Leaf",
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "VirtualPattern", 1,"one of Fruit, Flower, Leaf or DigitizedLeaf"));

  while (argth < len) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "VirtualPattern", (argth+1)/2+1));

    assert(argth + 1 < len); // must contain at least two parameters : this is verified syntactically

    if (*(AMString*)(args[argth].val.p) == "Class") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      symbolfun = (FNode*) args[argth+1].val.p;

    } else  if (*(AMString*)(args[argth].val.p) == "WhorlSize") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      whorlfun = (FNode*) args[argth+1].val.p;


    } else  if (*(AMString*)(args[argth].val.p) == "PatternNumber") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

//      numberfun = dynamic_cast<FNode*>(args[argth+1].val.p);
      numberfun = (FNode*) args[argth+1].val.p;


    } else if (*(AMString*)(args[argth].val.p) == "Color") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

      colorfun = (FNode*) args[argth+1].val.p;

      }else if (*(AMString*)(args[argth].val.p) == "TopDiameter") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        topdiafun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "BottomDiameter") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        botdiafun = (FNode*) args[argth+1].val.p;


      }else if (*(AMString*)(args[argth].val.p) == "Length") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        lengthfun = (FNode*) args[argth+1].val.p;


       }else if (*(AMString*)(args[argth].val.p) == "Alpha") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));


        alphafun = (FNode*) args[argth+1].val.p;

      }
	  else if (*(AMString*)(args[argth].val.p) == "Beta") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

        betafun = (FNode*) args[argth+1].val.p;

      }
	  else if (*(AMString*)(args[argth].val.p) == "Gamma") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

        gammafun = (FNode*) args[argth+1].val.p;

      }
	  else if (*(AMString*)(args[argth].val.p) == "Phyllotaxy") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

        phyllofun = (FNode*) args[argth+1].val.p;

      }
      else if (*(AMString*)(args[argth].val.p) == "XX") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

        xxfun = (FNode*) args[argth+1].val.p;

      }
      else if (*(AMString*)(args[argth].val.p) == "YY") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

        yyfun = (FNode*) args[argth+1].val.p;

      }
      else if (*(AMString*)(args[argth].val.p) == "ZZ") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

        zzfun = (FNode*) args[argth+1].val.p;

      }
    else if (*(AMString*)(args[argth].val.p) == "AA") { // angles d'euler

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

        tetafun = (FNode*) args[argth+1].val.p;

      }
      else if (*(AMString*)(args[argth].val.p) == "BB") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

        phifun = (FNode*) args[argth+1].val.p;

      }
      else if (*(AMString*)(args[argth].val.p) == "CC") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::FNODE,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "VirtualPattern", (argth+1)/2+1, args[argth+1].tag.string().data(), "FUNC"));

        psifun = (FNode*) args[argth+1].val.p;

      }

    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "VirtualPattern", (argth+1)/2+1));

    }

    argth += 2;

  }

  VirtualElements* pattern;

  if ((*pattern_type) == "Fruit") {

    pattern = new VirtualFruits(symbolfun, whorlfun, numberfun, colorfun, topdiafun, botdiafun, lengthfun, alphafun, betafun/*,gammafun,phyllofun*/);
  }
  else if ((*pattern_type) == "Flower") {

    pattern = new VirtualFlowers(symbolfun, whorlfun, numberfun, colorfun, topdiafun, botdiafun, lengthfun, alphafun, betafun/*,gammafun,phyllofun*/);

  }
  else if  ((*pattern_type) == "Leaf") {
    pattern = new VirtualLeaves(symbolfun, whorlfun, numberfun, colorfun, topdiafun, botdiafun, lengthfun, alphafun, betafun/*,gammafun,phyllofun*/);
  }
  else {
    assert((*pattern_type) == "DigitizedLeaf");

    pattern = new VirtualDigitizedLeaves(symbolfun, whorlfun, numberfun, colorfun, topdiafun, botdiafun, lengthfun, alphafun, /*gammafun,*/betafun, xxfun, yyfun, zzfun, tetafun, phifun, psifun);
  }


// if (!tree_frame.isValid()) {delete tree_frame; return AMObjType::ERROR;}

  return AMObj(AMObjType::VIRTUAL_PATTERN, pattern);

}



static AMObj MTG_DressingData(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len > 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "DressingData", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "DressingData", 1, args[0].tag.string().data(), "STRING"));

  DressingFile* dressing_data = new DressingFile(((AMString*)(args[0].val.p))->data());

  if (dressing_data->_isValid)
    return AMObj(AMObjType::DRESSING_DATA, dressing_data);
  else {
    delete dressing_data;
    return AMObj(AMObjType::ERROR);
  }

}

static AMObj MTG_Coord(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Coord", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Coord", 2, args[0].tag.string().data(), "PLANTFRAME or LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Coord", 1, args[1].tag.string().data(), "VTX"));


  ValType v[3];

  PlantFrame* pf;

  VId vtx = args[1].val.i;

  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  pf->coord3D(vtx, v);

  Array* vect = new SLArray;

  for(register int i=0; i<3; i++) (*vect) += AMObj(AMObjType::REAL, (double)v[i]);

  return AMObj(AMObjType::ARRAY, vect);

}

static AMObj MTG_Length(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Length", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Length", 1, args[0].tag.string().data(), "PLANTFRAME or LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Length", 2, args[1].tag.string().data(), "VTX"));


  PlantFrame* pf;

  VId vtx = args[1].val.i;

  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  ValType v = pf->length(vtx);

  return AMObj(AMObjType::REAL, v);

}

static AMObj MTG_TopDiameter(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "TopDiameter", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "TopDiameter", 2, args[0].tag.string().data(), "PLANTFRAME or LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "TopDiameter", 1, args[1].tag.string().data(), "VTX"));

  PlantFrame* pf;

  VId vtx = args[1].val.i;

  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  ValType v = pf->topDia(vtx);

  return AMObj(AMObjType::REAL, v);

}

static AMObj MTG_BottomDiameter(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "BottomDiameter", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "BottomDiameter", 2, args[0].tag.string().data(), "PLANTFRAME or LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "BottomDiameter", 1, args[1].tag.string().data(), "VTX"));

  PlantFrame* pf;

  VId vtx = args[1].val.i;

  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  ValType v = pf->botDia(vtx);

  return AMObj(AMObjType::REAL, v);

}

static AMObj MTG_BottomCoord(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "BottomCoord", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "BottomCoord", 2, args[0].tag.string().data(), "PLANTFRAME or LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "BottomCoord", 1, args[1].tag.string().data(), "VTX"));


  ValType v[3];

  PlantFrame* pf;

  VId vtx = args[1].val.i;

  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  pf->coord3DOrigin(vtx, v);

  Array* vect = new SLArray;

  for(register int i=0; i<3; i++) (*vect) += AMObj(AMObjType::REAL, (double)v[i]);

  return AMObj(AMObjType::ARRAY, vect);

}

static AMObj MTG_RelBottomCoord(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "RelBottomCoord", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "RelBottomCoord", 2, args[0].tag.string().data(), "PLANTFRAME or LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "RelBottomCoord", 1, args[1].tag.string().data(), "VTX"));

  ValType v[3];
  ValType o[3];

  PlantFrame* pf;

  VId vtx = args[1].val.i;

  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  VId origin = active_mtg->findGlobalTopoRoot(args[1].val.i, ANYTOPO);

  pf->coord3DOrigin(origin, o);
  pf->coord3DOrigin(vtx, v);

  Array* vect = new SLArray;

  for(register int i=0; i<3; i++) (*vect) += AMObj(AMObjType::REAL, (double)(v[i]-o[i]));

  return AMObj(AMObjType::ARRAY, vect);

}

static AMObj MTG_RelTopCoord(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "RelTopCoord", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "RelTopCoord", 2, args[0].tag.string().data(), "PLANTFRAME or LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "RelTopCoord", 1, args[1].tag.string().data(), "VTX"));


  ValType v[3];
  ValType o[3];

  PlantFrame* pf;

  VId vtx = args[1].val.i;

  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  VId  origin = active_mtg->findGlobalTopoRoot(vtx, ANYTOPO);

  pf->coord3DOrigin(origin, o);
  pf->coord3D(vtx, v);

  Array* vect = new SLArray;

  for(register int i=0; i<3; i++) (*vect) += AMObj(AMObjType::REAL, double(v[i]-o[i]));

  return AMObj(AMObjType::ARRAY, vect);

}

static AMObj MTG_TopCoord(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "TopCoord", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "TopCoord", 2, args[0].tag.string().data(), "PLANTFRAME or LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "TopCoord", 1, args[1].tag.string().data(), "VTX"));


  ValType v[3];

  PlantFrame* pf;

  VId vtx = args[1].val.i;

  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  pf->coord3D(vtx, v);

  Array* vect = new SLArray;

  for(register int i=0; i<3; i++) (*vect) += AMObj(AMObjType::REAL, (double)v[i]);

  return AMObj(AMObjType::ARRAY, vect);


}

static AMObj MTG_Alpha(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Alpha", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Alpha", 2, args[0].tag.string().data(), "PLANTFRAME or LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Alpha", 1, args[1].tag.string().data(), "VTX"));


  PlantFrame* pf;

  VId vtx = args[1].val.i;

  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  ValType v = pf->alpha(vtx);

  return AMObj(AMObjType::REAL, v);

}

static AMObj MTG_Azimuth(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Azimuth", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Azimuth", 2, args[0].tag.string().data(), "PLANTFRAME or LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Azimuth", 1, args[1].tag.string().data(), "VTX"));

  PlantFrame* pf;

  VId vtx = args[1].val.i;


  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  ValType v = pf->beta(vtx);

  return AMObj(AMObjType::REAL, v);

}


static AMObj MTG_PDir(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "PDir", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PDir", 2, args[0].tag.string().data(), "PLANTFRAME ot LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PDir", 1, args[1].tag.string().data(), "VTX"));


  Array* vect = new SLArray;

  ValType v[3];

  VId vtx = args[1].val.i;

  PlantFrame* pf;

  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  pf->pdir(args[1].val.i, v);

  for(register int i=0; i<3; i++) (*vect) += AMObj(AMObjType::REAL, (double)v[i]);

  return AMObj(AMObjType::ARRAY, vect);

}

static AMObj MTG_SDir(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "SDir", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "SDir", 2, args[0].tag.string().data(), "PLANTFRAME ot LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "SDir", 1, args[1].tag.string().data(), "VTX"));


  Array* vect = new SLArray;

  ValType v[3];

  VId vtx = args[1].val.i;

  PlantFrame* pf;

  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  pf->sdir(vtx, v);

  for(register int i=0; i<3; i++) (*vect) += AMObj(AMObjType::REAL, (double)v[i]);

  return AMObj(AMObjType::ARRAY, vect);

}

static AMObj MTG_EulerAngles(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "EulerAngles", 2));
  CHECKCONDVA(args[0].tag() ==AMObjType::PLANTFRAME || args[0].tag() ==AMObjType::LINETREE,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "EulerAngles", 2, args[0].tag.string().data(), "PLANTFRAME or LINETREE"));
  CHECKCONDVA(args[1].tag() ==AMObjType::VTX || args[1].tag() ==AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "PDir", 1, args[1].tag.string().data(), "VTX"));

  VId vtx = args[1].val.i;

  Array* angles = new SLArray;

  ValType v1[3];
  ValType v2[3];
  ValType v3[3];

  Vector3 v; // to store the result
  PlantFrame* pf;

  if (args[0].tag() ==AMObjType::PLANTFRAME) {

    CHECKDEFINECOND(active_mtg->existsVertex(vtx),
                    "Vertex undefined");

    pf = (PlantFrame*)args[0].val.p;

  }
  else {

    assert(args[0].tag() ==AMObjType::LINETREE);

    pf = (PlantFrame*)((LineTree*)args[0].val.p)->_pf ;

  }

  /*
  // This must take into account the change of coordinate system
  // (with respect to the global coordinate system, pdir is the 3rd direction
  // sdir is the first, and tdir is the secund.

  pf->pdir(vtx, v3);
  pf->sdir(vtx, v1);
  pf->tdir(vtx, v2);
  */

  pf->pdir(vtx, v1);
  pf->sdir(vtx, v2);
  pf->tdir(vtx, v3);

  // PDir is in general not normed. It should be normed before
  // being transformed into an orthogonal matrix
  MyVector nv1(v1[0],v1[1],v1[2]);
  nv1.norm();


  // used since it contain a method to compute euler factors
// matrix>3 ctor change: swap between row and column
//  Matrix3 refsys(nv1[0],nv1[1],nv1[2],v2[0],v2[1],v2[2],v3[0],v3[1],v3[2]);
  Matrix3 refsys( nv1[0],v2[0],v3[0],
                  nv1[1],v2[1],v3[1],
                  nv1[2],v2[2],v3[2] );

  v = refsys.eulerAnglesZYX();

  for(register int i=0; i<3; i++)
    (*angles) += AMObj(AMObjType::REAL, (double)v.getAt(i));

  return AMObj(AMObjType::ARRAY, angles);

}

static AMObj MTG_TreeMatching(const AMObjVector& args) {
  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();
  int argth = 1;

  Array* fnode_array = 0;
  RWCString ordered_type("Unordered");
  RWCString matching_type("Edition");
  RWCString mapping_type("Global");
  RWCString mapping("General");
  RWCString scale_type("SingleScale");
  double coeff =.71;

  VectorDistance vect_dist = VectorDistance();


  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);
  CHECKCONDVA(len > 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "TreeMatching", 1));
  CHECKCONDVA(args[0].tag() ==AMObjType::ARRAY ,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "TreeMatching", 1, args[0].tag.string().data(), "ARRAY(VTX)"));

  Array* array = (Array*) (args[0].val.p);

  CHECKCONDVA(array->entries() >= 1,
              genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "TreeMatching", 1, "an array with at least 2 elements"));
  CHECKCONDVA(array->surfaceType() == AMObjType::VTX || array->surfaceType() == AMObjType::INTEGER,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "TreeMatching", 1, array->surfaceType().string().data(), "ARRAY(VTX)"));
  const AMObj* pv = array->anElement();
  assert(pv);

  int self_similarity;
  if (array->entries() == 1)
    self_similarity = 1;
  else  self_similarity = 0;



  CHECKDEFINECOND(active_mtg->existsVertex((*pv).val.i),
                  "Vertex undefined");
  int scale = active_mtg->vscale((*pv).val.i);

  // Check if all vertex are at the same scale
  ArrayIter* pnext = array->iterator();
  ArrayIter& next = *pnext;
  AMObj v1;
  while (next()) {

    v1 = next.key();
    CHECKDEFINECOND(active_mtg->existsVertex(v1.val.i),
                    "Vertex undefined");

    if (active_mtg->vscale(v1.val.i) != scale) {
      delete pnext;
      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "TreeMatching", 1, "an array of vtx having same scale"));
    }

  }
  delete pnext;

  while (argth < len) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "TreeMatching", (argth+1)/2+1));

    assert(argth + 1 < len); // must contain at least two parameters : this is verified syntactically

    if (*(AMString*)(args[argth].val.p) == "FuncList") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::ARRAY,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "an ARRAY"));

      fnode_array = (Array*) (args[argth+1].val.p);

      CHECKCONDVA(fnode_array->entries() > 0,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "a non-empty array"));
      CHECKCONDVA(fnode_array->surfaceType() == AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "an ARRAY(FUNC)"));

    }
    else if (*(AMString*)(args[argth].val.p) == "VectorDistance") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::VECTOR_DISTANCE,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "VECTOR_DISTANCE"));

      vect_dist= (*((VectorDistance*)((STAT_model*)args[argth+1].val.p)->pt));
      //matching_type ="by_weights";
    }
    else  if (*(AMString*)(args[argth].val.p) == "MatchingType") {

      CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
              genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "a STRING"));

      matching_type = *(AMString*)(args[argth+1].val.p);
      CHECKCONDVA(matching_type == "by_inclusion"     || matching_type == "by_topology" ||
                  matching_type == "by_weights"  || matching_type == "by_component" ||
                  matching_type == "by_complex" ||matching_type == "test" || matching_type == "ordered"||
		  matching_type == "sequence" || matching_type == "selkow"|| matching_type == "endSpaceFree"||
		  matching_type == "fractal"||
		  // Nouvelles options de TreeMatching
		  matching_type == "Edition"     || matching_type == "Alignment" ||
                  matching_type == "SmallestCommonSuperTree"  || matching_type == "LargestCommonSubTree",
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, 
			      "one of Edition, Alignment, SmallestCommonSuperTree, LargestCommonSubTree \n ordered, by_inclusion ,by_weights, by_topology, by_component, by_complex, test, sequence, selkow, endSpaceFree,fractal "));
    }
    else  if (*(AMString*)(args[argth].val.p) == "OrderType") {

      CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
		  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "a STRING"));
      
      ordered_type = *(AMString*)(args[argth+1].val.p);
      CHECKCONDVA(ordered_type == "JiangWangZhang"     || ordered_type == "TichitFerraro" || ordered_type == "TichitFerraro1" 
		  || ordered_type == "FerraroOuangraoua"|| ordered_type == "FerraroOuangraoua1"|| ordered_type == "FerraroOuangraoua2"||
		  // Nouvelles options de TreeMatching
		  ordered_type == "Ordered" || ordered_type == "Unordered" || ordered_type == "PartiallyOrdered",
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "one of Ordered, Unordered, PartiallyOrdered \n or JiangWangZhang, TichitFerraro, TichitFerraro1, FerraroOuangraoua, FerraroOuangraoua1, FerraroOuangraoua2"));
    }
    else  if (*(AMString*)(args[argth].val.p) == "MappingType") {

      CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
		  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching_U", (argth+1)/2+1, "a STRING"));
      
      mapping_type = *(AMString*)(args[argth+1].val.p);
      CHECKCONDVA(mapping_type == "Global"     || mapping_type == "Local" ,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching_U", (argth+1)/2+1, "one of Global or Local"));
    }
    else  if (*(AMString*)(args[argth].val.p) == "InDelFactor") {
      
      CHECKCONDVA(args[argth+1].tag() == AMObjType::REAL,
		  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "a REAL"));
      
      coeff = args[argth+1].val.r;
      
    }
    else  if (*(AMString*)(args[argth].val.p) == "Mapping") {
      
      CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
		  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "a STRING"));
      
      mapping = *(AMString*)(args[argth+1].val.p);
      CHECKCONDVA(mapping == "global"     || mapping == "local"|| mapping == "self_similarity"||
		  // Nouvelles options de TreeMatching
		  mapping == "General"     || mapping == "MinimumConnectedComponents" || mapping == "EndSpaceFree" || mapping == "Lca" || mapping == "Distance" || mapping == "Similarity" ,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "one of General, MinimumConnectedComponents, EndSpaceFree , Lca, Distance, Similarity\n or global, local or self_similarity"));
      if (!strcmp(mapping.data(),"local"))
	self_similarity = 2;
      else  if (!strcmp(mapping.data(),"self_similarity"))
	self_similarity = 1;
      else self_similarity = 0;
      
    }
    else  if (*(AMString*)(args[argth].val.p) == "ScaleType") {
      
      CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
		  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching_U", (argth+1)/2+1, "a STRING"));
      
      scale_type = *(AMString*)(args[argth+1].val.p);
      CHECKCONDVA(scale_type == "SingleScale"     || scale_type == "MultiScale" || scale_type == "Quotiented" ,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching_U", (argth+1)/2+1, "one of SingleScale, MultiScale, Quotiented"));
    }
    else {
      
      CHECKCONDVA(FALSE,
		  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "TreeMatching", (argth+1)/2+1, "one of MatchingType, MappingType, Mapping, ScaleType, VectorDistance, InDelFactor, FuncList"));
      
    }

    argth += 2;
    
  }

  // Check array coherence
  
  

  AML_TreeMatch* treematch;

  if (self_similarity == 1){


    AML_TreeMatch* treematch;


       treematch = new AML_TreeMatch(*active_mtg,array, fnode_array,matching_type.data(),ordered_type.data(),self_similarity,vect_dist,coeff);
  
    return AMObj(AMObjType::TREEMATCHING, treematch);
  }
  

  if (!strcmp(ordered_type.data(),"Unordered")){


    AML_TreeMatch_U* treematch;


    treematch = new AML_TreeMatch_U(*active_mtg,array, fnode_array,matching_type.data(),mapping_type.data(),mapping.data(),scale_type.data(),vect_dist,coeff);
  
    return AMObj(AMObjType::TREEMATCHING, treematch);
  }
  else if (!strcmp(ordered_type.data(),"Ordered")){
    AML_TreeMatch_O* treematch;
    
    
    treematch = new AML_TreeMatch_O(*active_mtg,array, fnode_array,matching_type.data(),mapping_type.data(),mapping.data(),scale_type.data(),vect_dist,coeff);
    
    return AMObj(AMObjType::TREEMATCHING, treematch);
  }
  else if (!strcmp(ordered_type.data(),"PartiallyOrdered")){
    AML_TreeMatch_PO* treematch;
    
    treematch = new AML_TreeMatch_PO(*active_mtg,array, fnode_array,matching_type.data(),mapping_type.data(),mapping.data(),scale_type.data(),vect_dist,coeff);
    
    return AMObj(AMObjType::TREEMATCHING, treematch);
  }
  else{
    if (!strcmp(matching_type.data(),"by_weights"))
      {
	CHECKCONDVA( fnode_array != 0,
		     genAMLError(ERRORMSG(K_OPTION_VALUES_ERR_ss), "TreeMatching",
				 "The function list array must be defined if you want to use a weigthed local distance"))
	  }
    
    treematch = new AML_TreeMatch(*active_mtg,array, fnode_array,matching_type.data(),ordered_type.data(),self_similarity,vect_dist,coeff);
    
    return AMObj(AMObjType::TREEMATCHING, treematch);
  }
  
}






static AMObj MTG_TreeMatchingLoad(const AMObjVector& args)
{
  assert(&args);

  int len = args.length();

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  CHECKCONDVA( len > 0,
               genAMLError(ERRORMSG(K_NB_ARG_ERR_sd),
                          "TreeMatching", 1));

  CHECKCONDVA( args[0].tag() ==AMObjType::STRING ,
               genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss),
                           "TreeMatching", 1, args[0].tag.string().data(), "STRING"));

  RWCString file_name =  *(AMString*)(args[0].val.p);

  AML_TreeMatch* tree_match = new AML_TreeMatch();

//  RWFile file(file_name.data(),"r");

  // tree_match->restoreGuts(file);

  // tree_match->upDate(*active_mtg);

  AMObj obj(AMObjType::TREEMATCHING,tree_match);

  assert(obj.val.p);

  obj.val.p->displayOneLine(AMLOUTPUT);

  return(obj);

};


static AMObj MTG_MatchingExtract(const AMObjVector& args) {

  MTG* active_mtg = (AML_MTG*)activeMTG().val.p;

  int len = args.length();
  int argth = 1;

  CHECKCOND(active_mtg,NO_MTG_LOADED_ERR);

  CHECKCONDVA(len > 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd),
                          "MatchingExtract", 1));

  CHECKCONDVA(args[0].tag() ==AMObjType::TREEMATCHING ,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss),
                          "MatchingExtract", 1, args[0].tag.string().data(), "TREEMATCHING"));

  AML_TreeMatch* treematch = (AML_TreeMatch*) (args[0].val.p);
  RWCString viewpoint("Text");
  RWCString file_name("_MATCHING");
  int input_tree=-1;
  int reference_tree=1;

  while (argth < len) { // treatment of options

        CHECKCONDVA( args[argth].tag() == AMObjType::OPTION,
                     genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd),
                                 "MatchingExtract", (argth+1)/2+1));

        assert(argth + 1 < len); // must contain at least two parameters : this is verified syntactically

        if (*(AMString*)(args[argth].val.p) == "ViewPoint")
        {
                CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                            genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds),
                                        "MatchingExtract", (argth+1)/2+1, "a STRING"));

                viewpoint = *(AMString*)(args[argth+1].val.p);

                CHECKCONDVA( viewpoint == "Text" || viewpoint == "Mapping" || viewpoint == "Statistics" ||
                             viewpoint == "List" || viewpoint == "DistanceMatrix" || viewpoint== "Distance"||
			     viewpoint=="NormalizedDistance"||viewpoint=="ViewVertex"||viewpoint == "ParacladialCoefficient"||
			     viewpoint == "Paracladia"||viewpoint == "Coefficient"||viewpoint=="Paracladium"||viewpoint=="Time"||viewpoint=="SaveMTG"||viewpoint=="saveDistanceMatrix",
                             genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds),
                                         "MatchingExtract", (argth+1)/2+1, "one of Text,Mapping,Statistics,List,DistanceMatrix,Distance,NormalizedDistance,ViewVertex,ParacladialCoefficient,Paracladia,Coefficient,Paracladium,Time,SaveMTG,saveDistanceMatrix"));
        }
        else if (*(AMString*)(args[argth].val.p) == "FileName")
        {
                CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                        genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "MatchingExtract", (argth+1)/2+1, "a STRING"));

                file_name = *(AMString*)(args[argth+1].val.p);
        }
        else if (*(AMString*)(args[argth].val.p) == "InputTree")
        {
                CHECKCONDVA( (args[argth+1].tag() == AMObjType::VTX)||(args[argth+1].tag() == AMObjType::INTEGER),
                             genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds),
                                         "MatchingExtract", (argth+1)/2+1, "an Integer"));

                input_tree = args[argth+1].val.i;
        }
        else if (*(AMString*)(args[argth].val.p) == "ReferenceTree")
        {
                CHECKCONDVA(args[argth+1].tag() == AMObjType::INTEGER,
                            genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds),
                                        "MatchingExtract", (argth+1)/2+1, "an Integer"));

                reference_tree = args[argth+1].val.i;
        }
        else
        {
                CHECKCONDVA(FALSE,
                            genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd),
                                        "MatchingExtract", (argth+1)/2+1));
        }

        argth += 2;

  }

        TreeMatchExtract tme(*active_mtg,*treematch);
        if (viewpoint == "Text")
        {
          if (input_tree==-1)
          {
             treematch->viewAllMatching(AMLOUTPUT);
          }
          else
          {
            treematch->viewOneMatching(AMLOUTPUT,input_tree-1,reference_tree-1);
          }
        }
         else if (viewpoint == "Time")
          {
            double time;
			if (treematch->getNbTree()!=1)
				time=treematch->getTime(input_tree-1,reference_tree-1);
			else
				time=treematch->getTime(0,1);
            return AMObj(AMObjType::REAL,time);
          }
       else if (viewpoint == "Distance")
          {
            double distancebetweentree;
			if (treematch->getNbTree()!=1)
				distancebetweentree=treematch->viewDistanceMatching(AMLOUTPUT,input_tree-1,reference_tree-1);
			else
			  //distancebetweentree=treematch->getSelfSimilarDistance(input_tree,reference_tree);
			  distancebetweentree=treematch->getDistance(input_tree,reference_tree);
            return AMObj(AMObjType::REAL,distancebetweentree);
          }
        else if (viewpoint == "NormalizedDistance")
          {
            double distancebetweentree;
            distancebetweentree=treematch->viewNormalizedDistance(AMLOUTPUT,input_tree-1,reference_tree-1);
            return AMObj(AMObjType::REAL,distancebetweentree);
          }
        else if (viewpoint == "Coefficient")
          {
            double distancebetweentree;
            distancebetweentree=treematch->getC(AMLOUTPUT,input_tree,reference_tree);
            return AMObj(AMObjType::REAL,distancebetweentree);
           }
        else if (viewpoint == "Paracladium")
          {
            return AMObj(AMObjType::INTEGER,treematch->getParacladium(input_tree,reference_tree));
          }
        else if (viewpoint == "ParacladialCoefficient")
          {
            return AMObj(AMObjType::ARRAY,treematch->getParacladialCoefficients());
           }
        else if (viewpoint == "Paracladia")
          {
            return AMObj(AMObjType::ARRAY,treematch->getParacladia());
          }
	    else if (viewpoint == "ViewVertex")
          {
            int vertex;
            vertex=treematch->viewVertex(input_tree-1);
            return AMObj(AMObjType::INTEGER,vertex);
          }

        else if (viewpoint == "DistanceMatrix")
          {

            STAT_model* model = new STAT_model(treematch->getMatrix());

            return AMObj(AMObjType::DISTANCE_MATRIX,model);
          }
        else if (viewpoint == "List")
        {
                return(AMObj(AMObjType::ARRAY,treematch->getList(input_tree-1,reference_tree-1)));
        }
	else if (viewpoint == "SaveMTG")
	  {
	    ofstream out_file;
	    string name=file_name.data()+string(".mtg");
	    cout<<"Saving Mtg in "<<name<<endl;
	    out_file.open(name.c_str());
	    if (out_file.fail() != 0)
	      {
		return AMObj(AMObjType::ERROR);
	      }
	    treematch->mtg_write(name.c_str());
	    out_file.close();

	  }
	else if (viewpoint == "saveDistanceMatrix")
	  {
	    ofstream out_file;
	    string name=file_name.data();
	    cout<<"Saving Matrix in "<<name<<endl;
	    out_file.open(name.c_str());
	    if (out_file.fail() != 0)
	      {
		return AMObj(AMObjType::ERROR);
	      }
	    treematch->saveDistanceMatrix(out_file);
	    out_file.close();

	  }

        else if (viewpoint == "Statistics")
        {
          file_name.prepend(Plot_prefix);
	  // destruction des fichiers Gnuplot courants
          ifstream in_file;
          GP_window window;

          const int BUFFER_SIZE = 100;
#ifndef STL_EXTENSION
      char buffer[BUFFER_SIZE];
#else
	  const char* buffer;
#endif
#ifdef _WIN32
          if(VPTOOLS(exists)( string(Plot_prefix) + string(".plot") ) )
      {
          string buf= string("ERASE /F /Q ")+string(Plot_prefix)+string("*");
		  system(buf.c_str()); 
	    }
#else
#ifndef STL_EXTENSION
      ostrstream(buffer,BUFFER_SIZE) << "rm -f " << Plot_prefix << "*" << ends;
      system(buffer);
#else
	  ostringstream os;
	  os << "rm -f " << Plot_prefix << "*" << ends;
	  system(os.str().c_str());
	  os.str("");
#endif
#endif

          if (input_tree==-1)
          {
            tme.plot_statistics(file_name.data());
          }
          else
          {
            tme.plot_statistic(file_name.data(),input_tree-1,reference_tree-1);
          }

#ifndef _WIN32
#ifndef STL_EXTENSION
          ostrstream(buffer , BUFFER_SIZE) << "chmod 666 " << Plot_prefix << "*" << ends;
          system(buffer);
#else
	        os << "chmod 666 " << Plot_prefix << "*" << ends;
	        system(os.str().c_str());
	        os.str("");
#endif
#endif


      const char* prefix= file_name.data();
      string name=file_name+string(".plot");
      in_file.open(name.c_str());

      if (in_file.fail() != 0)
        {
        genAMLError(ERRORMSG(K_F_FILE_ERR_sss) , "Plot", "temporary file", Plot_prefix);
        return AMObj(AMObjType::ERROR);
        }
        in_file.close();
        window.session(prefix , AMLOUTPUT,FALSE );

      }
        else
        {
                assert(FALSE);
        }

  return AMObj(AMObjType::VOID);

}







AMObj AML_MTG::plot(GP_window&, const AMObjVector& args) const {

#ifndef SYSTEM_IS__IRIX
    int len = args.length();
    int argth = 1;

    CHECKCONDVA(len > 0,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "MTG", 1));
    CHECKCONDVA(args[0].tag() ==AMObjType::MTG,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", 1, args[0].tag.string().data(), "MTG"));

    int scale = 1;
    VId root = mtgRoot();

    while (argth < len) { // treatment of options

      // cerr << "arg = " << argth << args[argth].tag << endl;

      CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Plot", (argth+1)/2+1));

      assert(argth + 1 < len); // must contain at least two parameters : this is verified syntactically

      if (*(AMString*)(args[argth].val.p) == "Scale") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

        CHECKCONDVA(args[argth+1].val.i > 0,
                    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "positive"));

        scale = args[argth+1].val.i;

      }
      else if (*(AMString*)(args[argth].val.p) == "Vtx") {

        CHECKCONDVA(args[argth+1].tag() ==AMObjType::VTX || args[argth+1].tag() ==AMObjType::INTEGER,
                    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "Vtx"));

        CHECKDEFINECOND(existsVertex(args[argth+1].val.i),
                        "Vertex undefined");

        root = args[argth+1].val.i;

      }
      else {

        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Plot", (argth+1)/2+1));

      }

      argth += 2;

    }

    ScenePtr scene = shape(scale,root);

    if (scene) {

      PGLViewerApplication appli;
      appli.display(scene);

    }
    else cerr << "WARNING: No elements have a defined Geometry in this MTG." << endl;

#else // SGI/IRIX

    cerr << "Sorry, this functionality is not implemented on Silicon Graphics" << endl;

#endif

    return AMObj(AMObjType::VOID);

}



void installMTGModule() {

  AMObjType type[10];          // max number of arguments
  AMObj var;
  RWCString varname;

  var = AMObj(AMObjType::MTG, (AMModel*)0);
  varname = ":CurrentMTG";
  amobjTable()->insert(varname, var);

  // MTG functions

  type[0] = AMObjType::ANY;
  installFNode("MTG", MTG_MTG, 1, type, AMObjType::MTG);

  type[0] = AMObjType::VTX;
  installFNode("Class", MTG_Class, 1, type, AMObjType::CHAR);

  type[0] = AMObjType::VTX;
  installFNode("Index", MTG_Index, 1, type, AMObjType::INTEGER);

  type[0] = AMObjType::VTX;
  installFNode("Scale", MTG_Scale, 1, type, AMObjType::INTEGER);

  type[0] = AMObjType::CHAR;
  installFNode("ClassScale", MTG_ClassScale, 1, type, AMObjType::INTEGER);

  type[0] = AMObjType::VTX;
  type[1] = AMObjType::VTX;
  installFNode("EdgeType", MTG_EdgeType, 2, type, AMObjType::CHAR);

  type[0] = AMObjType::VTX;
  type[1] = AMObjType::ANY;
  installFNode("Feature", MTG_Feature, 2, type, AMObjType::ANY);

  type[0] = AMObjType::VTX;
  installFNode("DateSample", MTG_DateSample, 2, type, AMObjType::ANY);

  type[0] = AMObjType::VTX;
  type[1] = AMObjType::ANY;
  installFNode("FirstDefinedFeature", MTG_FirstDefinedFeature, 2, type, AMObjType::ANY);

  type[0] = AMObjType::VTX;
  type[1] = AMObjType::ANY;
  installFNode("LastDefinedFeature", MTG_LastDefinedFeature, 2, type, AMObjType::ANY);


  type[0] = AMObjType::VTX;
  type[1] = AMObjType::DATE;
  installFNode("NextDate", MTG_NextDate, 2, type, AMObjType::ANY);

  type[0] = AMObjType::VTX;
  type[1] = AMObjType::DATE;
  installFNode("PreviousDate", MTG_PreviousDate, 2, type, AMObjType::ANY);

  type[0] = AMObjType::VTX;
  type[1] = AMObjType::VTX;
  installFNode("Order", MTG_Order, 2, type, AMObjType::INTEGER);

  type[0] = AMObjType::VTX;
  type[1] = AMObjType::VTX;
  installFNode("Rank", MTG_Rank, 2, type, AMObjType::INTEGER);

  type[0] = AMObjType::VTX;
  type[1] = AMObjType::VTX;
  installFNode("Height", MTG_Height, 2, type, AMObjType::INTEGER);

  type[0] = AMObjType::VTX;
  type[1] = AMObjType::VTX;
  installFNode("AlgOrder", MTG_AlgOrder, 2, type, AMObjType::INTEGER);

  type[0] = AMObjType::VTX;
  type[1] = AMObjType::VTX;
  installFNode("AlgRank", MTG_AlgRank, 2, type, AMObjType::INTEGER);

  type[0] = AMObjType::VTX;
  type[1] = AMObjType::VTX;
  installFNode("AlgHeight", MTG_AlgHeight, 2, type, AMObjType::INTEGER);


  // MTG functions returning a Vertex

  installFNode("MTGRoot", MTG_MTGRoot, 0, type, AMObjType::VTX);

  type[0] = AMObjType::VTX;
  installFNode("Defined", MTG_Defined, 1, type, AMObjType::BOOL);

  type[0] = AMObjType::VTX;
  installFNode("Father", MTG_Father, 1, type, AMObjType::VTX);

  type[0] = AMObjType::VTX;
  installFNode("Predecessor", MTG_Predecessor, 1, type, AMObjType::VTX);

  type[0] = AMObjType::VTX;
  installFNode("Location", MTG_Location, 1, type, AMObjType::VTX);

  // MTG functions returning collections

  type[0] = AMObjType::VTX;
  installFNode("Sons", MTG_Sons, 1, type, AMObjType::ARRAY);

  type[0] = AMObjType::VTX;
  installFNode("Successor", MTG_Successor, 1, type, AMObjType::VTX);

  type[0] = AMObjType::VTX;
  installFNode("Descendants", MTG_Descendants, 1, type, AMObjType::ARRAY);

  type[0] = AMObjType::VTX;
  installFNode("Ancestors", MTG_Ancestors, 1, type, AMObjType::ARRAY);

  type[0] = AMObjType::VTX;
  installFNode("Root", MTG_Root, 1, type, AMObjType::ARRAY);

  type[0] = AMObjType::VTX;
  installFNode("Extremities", MTG_Extremities, 1, type, AMObjType::ARRAY);

  type[0] = AMObjType::VTX;
  installFNode("Complex", MTG_Complex, 1, type, AMObjType::VTX);

  type[0] = AMObjType::VTX;
  installFNode("Components", MTG_Components, 1, type, AMObjType::ARRAY);

  type[0] = AMObjType::VTX;
  installFNode("ComponentRoots", MTG_ComponentRoots, 1, type, AMObjType::ARRAY);

  type[0] = AMObjType::VTX;
  installFNode("Trunk", MTG_Trunk, 1, type, AMObjType::ARRAY);

  type[0] = AMObjType::INTEGER;
  installFNode("VtxList", MTG_VtxList, 1, type, AMObjType::ARRAY);

  // MTG functions working on axis

  type[0] = AMObjType::VTX;
  installFNode("Axis", MTG_Axis, 1, type, AMObjType::ARRAY);

  // MTG functions returning paths

  type[0] = AMObjType::VTX;
  type[1] = AMObjType::VTX;
  installFNode("Path", MTG_Path, 2, type, AMObjType::ARRAY);


  type[0] = AMObjType::ANY;
  installFNode("Activate", MTG_Activate, 1, type, AMObjType::VOID);

  installFNode("Active", MTG_Active, 0, type, AMObjType::VOID);

  type[0] = AMObjType::ANY;
  installFNode("TreeMatching", MTG_TreeMatching, 1, type, AMObjType::TREEMATCHING);

//   type[0] = AMObjType::ANY;
//   installFNode("TreeMatching_U", MTG_TreeMatching_U, 1, type, AMObjType::TREEMATCHING);

  type[0] = AMObjType::ANY;
  installFNode("MatchingExtract", MTG_MatchingExtract, 1, type, AMObjType::TREEMATCHING);

//   type[0] = AMObjType::ANY;
//   installFNode("MatchingExtract_U", MTG_MatchingExtract_U, 1, type, AMObjType::TREEMATCHING);

  type[0] = AMObjType::ANY;
  installFNode("TreeMatchingLoad", MTG_TreeMatchingLoad, 1, type, AMObjType::TREEMATCHING);

  type[0] = AMObjType::VTX;
  installFNode("PlantFrame", MTG_PlantFrame, 1, type, AMObjType::PLANTFRAME);
  type[0] = AMObjType::ANY;
  installFNode("VirtualPattern", MTG_VirtualPattern, 1, type, AMObjType::VIRTUAL_PATTERN);

  type[0] = AMObjType::STRING;
  installFNode("DressingData", MTG_DressingData, 1, type, AMObjType::DRESSING_DATA);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::VTX;
  installFNode("BottomCoord", MTG_BottomCoord, 2, type, AMObjType::BOOL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::VTX;
  installFNode("TopCoord", MTG_TopCoord, 2, type, AMObjType::BOOL);
  installFNode("RelTopCoord", MTG_RelTopCoord, 2, type, AMObjType::BOOL);
  installFNode("RelBottomCoord", MTG_RelBottomCoord, 2, type, AMObjType::BOOL);
  type[0] = AMObjType::ANY;
  type[1] = AMObjType::VTX;
  installFNode("PDir", MTG_PDir, 2, type, AMObjType::BOOL);
  type[0] = AMObjType::ANY;
  type[1] = AMObjType::VTX;
  installFNode("SDir", MTG_SDir, 2, type, AMObjType::BOOL);
  installFNode("EulerAngles", MTG_EulerAngles, 2, type, AMObjType::BOOL);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::VTX;
  installFNode("Coord", MTG_Coord, 2, type, AMObjType::BOOL); // same as TopCoord

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::VTX;
  installFNode("Length", MTG_Length, 2, type, AMObjType::BOOL);
  type[0] = AMObjType::ANY;
  type[1] = AMObjType::VTX;
  installFNode("TopDiameter", MTG_TopDiameter, 2, type, AMObjType::BOOL);
  type[0] = AMObjType::ANY;
  type[1] = AMObjType::VTX;
  installFNode("BottomDiameter", MTG_BottomDiameter, 2, type, AMObjType::BOOL);
  type[0] = AMObjType::ANY;
  type[1] = AMObjType::VTX;
  installFNode("Alpha", MTG_Alpha, 2, type, AMObjType::BOOL);
  type[0] = AMObjType::ANY;
  type[1] = AMObjType::VTX;
  installFNode("Beta", MTG_Azimuth, 2, type, AMObjType::BOOL);
  installFNode("Azimuth", MTG_Azimuth, 2, type, AMObjType::BOOL);// pour compatib. ascendante
}
