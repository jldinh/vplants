/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: Modeling Plant Geometry
 *
 *       Copyright 2000-2006 - Cirad/Inria/Inra - Virtual Plant Team
 *
 *       File author(s): F. Boudon (frederic.boudon@cirad.fr)
 *
 *       $Source: /usr/cvsmaster/AMAPmod/src/GEOM/geom_version.cpp,v $
 *       $Id: geom_version.cpp,v 1.11 2006/09/04 13:10:59 fboudon Exp $
 *
 *       Development site : https://gforge.inria.fr/projects/openalea/
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



#include <plantgl/tool/util_string.h>
#include "view_version.h"

using namespace std;

TOOLS_USING_NAMESPACE;

float getViewer3Version(){
  return float(VIEWER_VERSION);
}

float getViewer3Release(){
  return float(VIEWER_RELEASE);
}

std::string getViewer3VersionString(){
  return number(VIEWER_VERSION)+'.'+number(VIEWER_RELEASE);
}

