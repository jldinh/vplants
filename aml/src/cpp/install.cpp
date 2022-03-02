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
 *       $Id: install.cpp 3265 2007-06-06 14:41:54Z dufourko $
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





#include "mtg_funs.h"
#include "stat_funs.h"
#include "kernel_funs.h"
#include "flux_funs.h"
#include "file_funs.h"
#include "viewer_funs.h"
#include "msvoxel_funs.h"
#include "geomscene_funs.h"


void installAMLModules() {

  // Loading modules

  // ModuleEnv* env;

  installKERNELModule();
  installFILEModule();

#ifndef WITHOUT_MTG
  installMTGModule();
#endif
#ifndef WITHOUT_STAT
  installSTATModule();
#endif
#ifndef WITHOUT_FLUX
  installFLUXModule();
#endif
#ifndef WITHOUT_MSVOXEL
  installMSVOXELModule();
#endif
#ifndef WITHOUT_GEOM
  installGEOMSCENEModule();
  installVIEWERModule();
#endif

}

	
