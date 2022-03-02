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


#ifndef __tools_config_h__
#define __tools_config_h__

#include "../pgl_config.h"

/* ----------------------------------------------------------------------- */

/*! \def GEOM_NODLL
    \brief Not creating dll

    Uncomment to use this functionnality
        Do nothing on other platform than windows
*/
/*! \def GEOM_DLL
    \brief Using lib GEOM as a dll

    Uncomment to use this functionnality
        Do nothing on other platform than windows
*/
/*! \def GEOM_MAKEDLL
    \brief Creating GEOM dll

    Uncomment to use this functionnality
        Do nothing on other platform than windows
*/
#if defined(_WIN32)
#if defined(TOOLS_NODLL)
#undef TOOLS_MAKEDLL
#undef TOOLS_DLL
#else
#ifndef TOOLS_DLL
#define TOOLS_DLL
#endif
#endif

#if defined(TOOLS_MAKEDLL)
#ifndef TOOLS_DLL
#define TOOLS_DLL
#endif
#endif

#ifdef TOOLS_DLL

#ifdef TOOLS_MAKEDLL             /* create a Geom DLL library */
#define TOOLS_API  __declspec(dllexport)
#undef TOOLS_FWDEF
#else                                                   /* use a Geom DLL library */
#define TOOLS_API  __declspec(dllimport)
#endif

#define TOOLS_TEMPLATE_API(T) template class TOOLS_API T;
#endif

#else // OS != _WIN32

#undef TOOLS_MAKEDLL             /* ignore these for other platforms */
#undef TOOLS_DLL

#endif

#ifndef TOOLS_API
#define TOOLS_API
#define TOOLS_TEMPLATE_API(T) 
#endif


/* ----------------------------------------------------------------------- */

#ifdef NO_NAMESPACE

#ifdef TOOLS_NAMESPACE
#undef TOOLS_NAMESPACE
#endif

#ifdef TOOLS_NAMESPACE_NAME
#undef TOOLS_NAMESPACE_NAME
#endif

#else

/// Macro that enable the tools namespace
#define TOOLS_NAMESPACE

#endif

#ifdef TOOLS_NAMESPACE


#ifndef TOOLS_NAMESPACE_NAME

/// Macro that contains the tools namespace name
#define TOOLS_NAMESPACE_NAME TOOLS
#endif

/// Macro for beginning the tools namespace.
#define TOOLS_BEGIN_NAMESPACE namespace TOOLS_NAMESPACE_NAME {

/// Macro for ending the tools namespace.
#define TOOLS_END_NAMESPACE };

/// Macro for using the tools namespace.
#define TOOLS_USING_NAMESPACE using namespace TOOLS_NAMESPACE_NAME;

/// Macro for using an object of the tools namespace.
#define TOOLS_USING(obj) using TOOLS_NAMESPACE_NAME::obj;

/// Macro to use an object from the tools namespace.
#define TOOLS(obj) TOOLS_NAMESPACE_NAME::obj

#else

#ifdef _MSC_VER 
#  pragma message "namespace TOOLS not used"
#else
#  warning namespace TOOLS not used
#endif

/// Macro for beginning the tools namespace.
#define TOOLS_BEGIN_NAMESPACE  

/// Macro for ending the tools namespace.
#define TOOLS_END_NAMESPACE  

/// Macro for using the tools namespace.
#define TOOLS_USING_NAMESPACE  

/// Macro for using an object of the tools namespace.
#define TOOLS_USING(obj)

/// Macro to use an object from the tools namespace.
#define TOOLS(obj) obj

#endif

/* ----------------------------------------------------------------------- */

// __config_h__
#endif
