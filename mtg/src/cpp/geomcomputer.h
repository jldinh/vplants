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
 *       $Id: geomcomputer.h 17611 2014-10-17 13:20:41Z pradal $
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





#ifndef _GEOM_COMPUTER_SAMIR_DEF_
#define _GEOM_COMPUTER_SAMIR_DEF_


class Plant;
class DressingFile;
class Branch;
class BranchElement;

#include "definitions.h"
#include "vector.h"
#include "measures.h"


// Abstract class for geometry computing
// A Inquired Coordinates Computing Class will inherit 
// from this one.


class GeomComputer
{

 public:

  GeomComputer(Plant* plant,
	       MTG* mtg,
	       Measures* teta,
	       Measures* phi,
	       Measures* psi,
	       FNode* eulerf,
	       const DressingFile* dressing_file
	       );

  virtual ~GeomComputer();

  // A constructor with FNODEs may be delared further.


  AmlBoolean isAValidGeometry() const {return _isAValidGeometry;};

  virtual void computeGeometry()=0; 
  virtual void coord3D(VId, ValType*) const=0;
  virtual void coord3DOrigin(VId, ValType* v) const=0;

  MyVector direction;

    // fonction donnee par l'utilisateur pour tester si on utilise les angles d'Euler
    // pour calculer l'orientation d'un element
    FNode* _eulerf; 
    Measures* _teta;
    Measures* _phi;
    Measures* _psi;
    
    AmlBoolean euler(VId) const; 

 protected:

  Plant* _plant;
  MTG* _mtg;
  const DressingFile* _dressingFile;
  AmlBoolean _isAValidGeometry;

  // Some FNODE*s munbers must be declared here

};


// Classe StandardGeom

// class Measures;
class Diameters;



class StandardGeom : public GeomComputer
{
 public:
  
  StandardGeom(Plant*,
	       MTG*,
	       FNode*,RWCString, FNode*,FNode*,FNode*,FNode*,FNode*,FNode*,FNode*,FNode*,FNode*,
	       ValType  dist,
	       const DressingFile*
    )
	       ;

  ~StandardGeom();

  virtual void computeGeometry();
  virtual void coord3D(VId vertex, ValType* v) const;
  virtual void coord3DOrigin(VId, ValType* v) const;


 private:

  Measures *_coordinates,*_length,*_azimut,*_alpha,*_category;
  Diameters *_diameters;

};

// Classe CoordGeom


class CoordGeom : public GeomComputer
{
 public:
  
  CoordGeom(Plant*,
	    MTG*,
	    FNode* lengthf,
	    RWCString,
	    FNode* topf,
	    FNode* botf,
	    FNode* alphaf,
	    FNode* azimutf,
	    FNode* teta,
	    FNode* phi,
	    FNode* psi,
	    FNode* eulerf,
	    FNode* categoryf,
	    FNode* xxf,
	    FNode* yyf,
	    FNode* zzf,
	    CoordsType,
	    ValType dist,
	    const DressingFile*,
	    FNode* digitizedf	    
	    );

  ~CoordGeom();

  virtual void computeGeometry();
  virtual void coord3D(VId, ValType* v) const;
  virtual void coord3DOrigin(VId, ValType* v) const;


  // if a function defines digitized points for each vertex,
  // parametric models (like nurbs) are estimated for each
  // vertex.
  void estimateParametricModels(); 

  Measures *_length;

  private:

  Measures *_coordinates,*_azimut,*_alpha,*_category;
  Diameters *_diameters;

  FNode* _digitizedf;

};


#endif










