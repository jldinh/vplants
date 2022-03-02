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
 *       $Id: kernel_funs.h 3263 2007-06-06 14:07:06Z dufourko $
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




#ifndef FUNS_HEADER
#define FUNS_HEADER

extern void installFNode(const char* name, PFUN fun, int argnb, AMObjType* type, AMObjType rettype);


extern void installKERNELModule();

/*
class KernelEnv : public ModuleEnv {

  FType _dateformat;

public:
  
  KernelEnv();

  virtual ~KernelEnv() {} 

  virtual RWCString name() {return "Kernel";}

  // virtual AMObj list();
  virtual AMObj show(RWCString object_type, RWCString attribute_name);
  virtual AMObj set(RWCString attribute_name, const AMObj&);

};

*/

#endif
