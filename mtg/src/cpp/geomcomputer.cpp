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
 *       $Id: geomcomputer.cpp 17611 2014-10-17 13:20:41Z pradal $
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





#include "aml/ammodel.h"
#include "geomcomputer.h"

#include "plant.h"
#include "dressingfile.h"
#include "measures.h"
#include "diameters.h"

#include "coordinates.h"

using namespace std;

static void printPercentComputed(double ratio) {

    cerr << "\x0d" << "Already computed : " << (int) (ratio*100) << " % " << flush;
}

GeomComputer::GeomComputer(Plant* plant,
                           MTG* mtg,
                           Measures* teta,
                           Measures* phi,
                           Measures* psi,
                           FNode* eulerf,
                           const DressingFile* dressing_file
                           )
{
  _mtg=mtg;
  _plant=plant;
  _teta = teta;
  _phi = phi;
  _psi = psi;
  _eulerf = eulerf;
  _dressingFile=dressing_file;

}

GeomComputer::~GeomComputer()
{
  // delete _eulerf;

  delete _teta;
  delete _phi;
  delete _psi;
}

AmlBoolean GeomComputer::euler(VId v) const {

  if (_eulerf) {

    AMObjVector argobjs(1); // Only one arg which is a vertex

    argobjs[0] = AMObj(AMObjType::VTX, v);

    AMObj result_obj = (*_eulerf)(argobjs);

    switch(result_obj.tag()) {

      case  AMObjType::BOOL:
        if (result_obj.val.b) return TRUE;
        else return FALSE;
      case  AMObjType::INTEGER:
        if (result_obj.val.i) return TRUE;
        else return FALSE;
      case  AMObjType::REAL:
        if (result_obj.val.r) return TRUE;
        else return FALSE;
      default:
        return FALSE;
    }
  }
  else return FALSE;

}

// StandardGeom.

StandardGeom::StandardGeom(Plant* plant,
                           MTG* mtg,
                           FNode* lengthf,
                           RWCString length_algo,
                           FNode* topf,
                           FNode* botf,
                           FNode* alphaf,
                           FNode* azimutf,
                           FNode* categoryf,
                           FNode* tetaf,
                           FNode* phif,
                           FNode* psif,
                           FNode* eulerf,
                           ValType dist,
                           const DressingFile* dressing_file
                           ):
  GeomComputer(plant,
               mtg,
               new Teta (plant,tetaf,dressing_file,dressing_file->getAlphaUnit()),
               new Phi (plant,phif,dressing_file,dressing_file->getAlphaUnit()),
               new Psi (plant,psif,dressing_file,dressing_file->getAlphaUnit()),
               eulerf,
               dressing_file
               )
{
  
  _length=new Length (_plant,_dressingFile,lengthf,_dressingFile->getLengthUnit());
  _diameters=new Diameters (_plant,topf,botf,_dressingFile,_dressingFile->getDiametersUnit());

  if (_dressingFile->isIndicePhillotaxy())
  {
    ValType nb_tours=_dressingFile->getNbTours();
    ValType nb_leaves=_dressingFile->getNbLeaves();
    _azimut=new Azimut (_plant,azimutf,nb_tours,nb_leaves,1);
  }
  else
  {
    _azimut=new Azimut (_plant,azimutf,_dressingFile->getPhillotaxy(),_dressingFile->getAzimutUnit());
  }
  _coordinates=new Coordinates (_plant,dressing_file,dist,1);
  _alpha=new Alpha (_plant,alphaf,_dressingFile,_dressingFile->getAlphaUnit());
  _category=new Category (_plant,categoryf,_dressingFile);


}

StandardGeom::~StandardGeom()
{
  delete _length;
  delete _diameters;
  delete _azimut;
  delete _coordinates;
  delete _alpha;
  delete _category;
}


void StandardGeom::coord3D(VId vertex, ValType* v) const
{
  _coordinates->coord3D(vertex,v);
}
void StandardGeom::coord3DOrigin(VId vertex, ValType* v) const
{
  _coordinates->coord3DOrigin(vertex,v);
}


void StandardGeom::computeGeometry()
{
  _azimut->computeAzimut();

  size_t nb_branches=_plant->nbBranches();

  double prev_ratio = 0.0;
  double ratio = 0.0;

  Ramifications::const_iterator c_branch = _plant->_branches->begin();
  for (size_t i=0;c_branch != _plant->_branches->end() && i<nb_branches;i++)
  { 

	Branch& branch = *(*c_branch);
    ratio = ((double)i)/(double)nb_branches;

    if (ratio >= prev_ratio+0.1) {
      prev_ratio = ratio;
      printPercentComputed(ratio);
    }


    
    if (branch.getSupport()==UNDEF)
    {
      _coordinates->newTrunk(i);
    }

    _category->computeBranchCategory(branch);
    _diameters->computeDiameters(branch);

    // Le deuxieme argument est passe pour homogeneite avec la methode equivalente
    // appelee dans le constructeur CoordGeom. Il n'est pas utilise ici

    _length->computeBranchLengths(branch, 0);   
    _alpha->computeBranchAlpha(branch);
    _coordinates->computeBranchCoordinates(branch);     
	c_branch++;
  }

  cerr << "\x0d" << "Already computed : 100 % ... Done." << endl;

  _coordinates->lastTrunk();
  _isAValidGeometry=(_coordinates->areValidCoordinates()) && (_length->areValidLengths());
  _isAValidGeometry=(_isAValidGeometry) && (_diameters->areValidDiameters());
  _plant->_isValid=_plant->isAValidPlant() && _isAValidGeometry;

  // Translation is made only if
  // the first argument of the plantframe is a single vertex
  // and the translation vector is non 0.

  if ((_plant->_root_list == NULL &&
       _plant->_translation && _plant->_translation->computeLength() != 0 )
      || (_plant->_root_list != NULL && _plant->_translation == NULL))
      _coordinates->translatePlantElements();

}


// CoordGeom


CoordGeom::CoordGeom(Plant* plant,
                     MTG* mtg,
                     FNode* lengthf,
                     RWCString length_algo,
                     FNode* topf,
                     FNode* botf,
                     FNode* alphaf,
                     FNode* azimutf,
                     FNode* tetaf,
                     FNode* phif,
                     FNode* psif,
                     FNode* eulerf,
                     FNode* categoryf,
                     FNode* xxf,
                     FNode* yyf,
                     FNode* zzf,
                     CoordsType coords_type,
                     ValType dist,
                     const DressingFile* dressing_file,
                     FNode* digitizedf
                     ):
  GeomComputer(plant,
               mtg,
               new Teta (plant,tetaf,dressing_file,dressing_file->getAlphaUnit()),
               new Phi (plant,phif,dressing_file,dressing_file->getAlphaUnit()),
               new Psi (plant,psif,dressing_file,dressing_file->getAlphaUnit()),
               eulerf,
               dressing_file
               )
{

  _length=new CoordLength (_plant,length_algo,lengthf,dressing_file,_dressingFile->getLengthUnit());
  _diameters=new Diameters (_plant,topf,botf,_dressingFile,_dressingFile->getDiametersUnit());

  // Pour les diametres : Il faut rajouter 1 au niveau de description.

  _coordinates=new RequiredCoords (_plant,xxf,yyf,zzf,coords_type,dressing_file,dist,1);

  if (_dressingFile->isIndicePhillotaxy())
  {
    ValType nb_tours=_dressingFile->getNbTours();
    ValType nb_leaves=_dressingFile->getNbLeaves();
    _azimut=new Azimut (_plant,azimutf,nb_tours,nb_leaves,1);
  }
  else
  {
    _azimut=new Azimut (_plant,azimutf,_dressingFile->getPhillotaxy(),_dressingFile->getAzimutUnit());
  }
  _alpha=new Alpha (_plant,alphaf,_dressingFile,_dressingFile->getAlphaUnit());
  _category=new Category (_plant,categoryf,_dressingFile);

  _digitizedf = digitizedf;

}

CoordGeom::~CoordGeom()
{
  delete _diameters;
  delete _length;
  delete _coordinates;
  delete _alpha;
  delete _azimut;
  delete _category;
}

void CoordGeom::computeGeometry()
{
  if (_coordinates->areValidCoordinates())
  {

    if (!_digitizedf) {
      // there is no function defined to specify digitized points
      // => the classic method is used to compute the plant geometry

      IntType nb_branches=_plant->nbBranches();

      _azimut->computeAzimut();

      double prev_ratio = 0.0;
      double ratio = 0.0;

	  Ramifications::const_iterator c_branch = _plant->_branches->begin();
      for (IntType i=0;c_branch != _plant->_branches->end() && i<nb_branches;i++)
	  {  
		Branch& branch = *(*c_branch);
		ratio = ((double)i)/(double)nb_branches;
		
		if (ratio >= prev_ratio+0.1) {
		  prev_ratio = ratio;
		  printPercentComputed(ratio);
		}
		
		if (branch.getSupport()==UNDEF)
		{
		  _coordinates->newTrunk(i);
		}
		
		_category->computeBranchCategory(branch);
		_alpha->computeBranchAlpha(branch);
		
		// On est oblige de passer un objet RequiredCoord (_coordinates) en
		// argument du fait que le calcul de la longueur d'une entite d'une
		// branche repose sur la detection de coordonnees valides sur ce point
		// (qui permettront le cas echeant de faire des interpolations lineaires
		// entre points renseignes.)
		
		_length->computeBranchLengths(branch, _coordinates);	
		_diameters->computeDiameters(branch);
		_coordinates->computeBranchCoordinates(branch);
		c_branch++;
	  } 
      _coordinates->lastTrunk();
	  
    }
    else { 
	  
      // digitizedf is defined, which means that the user wants 
      // to make an estimate of parametric models using NURBS, or other parametric curves
	  
      estimateParametricModels();
	  
    }
	
    cerr << "\x0d" << "Already computed : 100 % ... Done." << endl;
	
	
    // Translation is made only if the translation vector is non 0
    // Otherwise, the coordinates defined at the origin of the plant
    // are used.
    if (!_plant->_translation ||
	  _plant->_translation->computeLength() != 0)
      _coordinates->translatePlantElements();
	
    _isAValidGeometry=_coordinates->areValidCoordinates();
    _plant->_isValid=_plant->_isValid && _isAValidGeometry;
  }
  else
  {
    _isAValidGeometry=_coordinates->areValidCoordinates() && _diameters->areValidDiameters();
    _plant->_isValid=_plant->_isValid && _isAValidGeometry;
  }
}


void CoordGeom::coord3D(VId vertex, ValType* v) const
{
  _coordinates->coord3D(vertex,v);
}

void CoordGeom::coord3DOrigin(VId vertex, ValType* v) const
{
  _coordinates->coord3DOrigin(vertex,v);
}

