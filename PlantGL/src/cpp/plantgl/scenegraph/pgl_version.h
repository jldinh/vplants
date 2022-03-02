/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: Modeling Plant Geometry
 *
 *       Copyright 2000-2006 - Cirad/Inria/Inra - Virtual Plant Team
 *
 *       File author(s): F. Boudon (frederic.boudon@cirad.fr)
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

/*! \file pgl_version.h
    \brief File for accessing to PGL version.
*/


#ifndef __pgl_version_h__
#define __pgl_version_h__

#include "../version.h"

#include "sg_config.h"
#include <string>
#include <vector>

/// PGL Version
extern SG_API float getPGLVersion();
extern SG_API int getPGLRevision();
extern SG_API int getPGLSvnRevision();

/// PGL Version String
extern SG_API std::string getPGLVersionString();
extern SG_API int getPGLVersionNumber();
extern SG_API std::string getPGLRevisionString();

#define PGL_LIB_VERSION_CHECK \
	 assert( PGL_VERSION == getPGLVersionNumber() && \
             "PlantGL version of the loaded library is different from the one at linking.");

extern SG_API const std::vector<std::string>& get_pgl_supported_extensions();
extern SG_API bool pgl_support_extension(const std::string& ext);

#endif


