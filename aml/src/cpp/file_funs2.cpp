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
 *       $Id: file_funs2.cpp 3573 2007-09-05 16:59:56Z dufourko $
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


#ifndef __GNUC__

#include <qfile.h>
#include <qtextstream.h>

#include "file_funs.h"

#include "aml/erroraml.h"
#include "aml/parseraml.h"
#include "aml/fnode.h"
#include "aml/kernel_err.h"
#include "aml/kernel_funs.h"
#include "aml/global.h"

#include "aml/set.h"
#include "aml/array.h"
#include "aml/list.h"

#include "aml/file_funs2.h"

#define  ERR_MSG_ARRAY  	kernel_err_msgs_aml
#define  MODULE_NAME		"File"        

AMObj F_Copy(const AMObjVector& args) {
  CHECKCONDVA(args.length() == 2,
	      genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Copy", 2));
  if (args[0].tag() != AMObjType::STRING ){
    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Copy", 0, "<STRING>");
    return AMObj(AMObjType::UNDEF);
  }
  if (args[1].tag() != AMObjType::STRING){
    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Copy", 1, "<STRING>");
    return AMObj(AMObjType::UNDEF);
  }
  if (QFile::exists(((AMString*)(args[1].val.p))->data())){
    AMLOUTPUT << "File " << (*(AMString*)(args[1].val.p)) << " already exist." << endl;
    return AMObj(AMObjType::BOOL,FALSE);
  }
  AMObjVector argsE(3);
  argsE[0] = args[0];
  argsE[1] = AMObj(AMObjType::STRING, new AMString("Type"));
  argsE[2] = AMObj(AMObjType::STRING, new AMString("File"));
  QFile f( (*(AMString*)(args[0].val.p) ).data() );
  if(f.exists()){
	  QFile f2( (*(AMString*)(args[1].val.p)).data());
	  if ( f.open( IO_ReadOnly ) &&  f2.open( IO_WriteOnly )) {
		  QTextStream t1(&f);
		  QTextStream t2(&f2);
		  t2 << t1.read();
		  f.close();
		  f2.close();
		  return AMObj(AMObjType::BOOL,TRUE);
	  } 
	  else return AMObj(AMObjType::BOOL,FALSE);
  }
  else {
    AMLOUTPUT << "File " << (*(AMString*)(args[0].val.p)) << " does not exist." << endl;
    return AMObj(AMObjType::BOOL,FALSE);
  }
}

#endif
