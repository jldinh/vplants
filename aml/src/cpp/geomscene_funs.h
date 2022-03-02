/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): C. Godin  (godin@cirad.fr)
 *
 *       $Source$
 *       $Id: geomscene_funs.h 3573 2007-09-05 16:59:56Z dufourko $
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




#ifndef GEOMSCENE_FUNS_HEADER
#define GEOMSCENE_FUNS_HEADER


#include "aml/parseraml.h"
#include "aml/fnode.h"
#include "aml/array.h"

#include "plantgl/scenegraph/scene/scene.h"


PGL_USING_NAMESPACE

// ================
// CLASS GEOMSCENE
// ================

class AML_GeomScene : public Scene, public AMModel {

public:

  AML_GeomScene(const std::string& filename): Scene(filename) {}

  virtual std::ostream& displayOneLine(std::ostream& o) const
  {
    return o << "scene" << std::endl;
  }

  virtual std::ostream& display(std::ostream& o, int line_size = 0) const {
    return displayOneLine(o);
  }

  virtual AMObj display(std::ostream& o, const AMObjVector& args) const
  {
    assert(&args);
    display(o);
    return AMObj(AMObjType::VOID);
  }

  virtual AMObj plot(GP_window&, const AMObjVector& args) const;

  virtual AMObj extract(const AMObjVector& args) const;

  virtual AMObj print(const AMObjVector& args) const
  {
    assert(&args);
    std::cerr << "Not yet Implemented" << std::endl;
    return AMObj(AMObjType::VOID);
  }

  virtual AMObj save(const AMObjVector& args) const
  {
    assert(&args);
    std::cerr << "Not yet Implemented" << std::endl;
    return AMObj(AMObjType::VOID);
  }

};

extern void installGEOMSCENEModule();

#endif
