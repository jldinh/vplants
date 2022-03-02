/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture 
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): N. Dones (dones@clermont.inra.fr) 
 *                       UMR PIAF INRA-UBP Clermont-Ferrand
 *
 *       $Source$
 *       $Id: electrical_model.cpp 3266 2007-06-06 14:48:32Z dufourko $
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


#include "electrical_model.h"
using namespace std;

/*------------------------------------------------------------------------------*/

ElectricalModel::ElectricalModel(MTG* g, VId root,double base_pot)
{
  _isValid=false;

  assert(g);

  _g=g;
  _id=root;
  _base_potential=base_pot;
  
  //give the descendants of id at the same scale
  _vlist=_g->si_descendants(_id);
  
  _nb_desc=_vlist->size();
  
  //renseignement de la table vIdHTab
  VtxList::iterator _it;
  int i=0;
  for(_it=_vlist->begin();_it<_vlist->end();_it++)
    {
      _vIdHTab[*_it]=i;
      i++;
    }  
  
  //give the size of the arrays
  _resistance_array=new RealArray(_nb_desc);
  _flux_array=new RealArray(_nb_desc);
  _potential_array=new RealArray(_nb_desc);


  //---------------------------------------------------
  //remplissage des tableaux resistance,flux et potential
  string fname="Flux";
  FIndex _iFlux=_g->fNameIndex(fname.c_str());
  fname="Resistance";
  FIndex _iResist=_g->fNameIndex(fname.c_str());
  fname="Potential";
  FIndex _iPot=_g->fNameIndex(fname.c_str());

  for(_it=_vlist->begin();_it<_vlist->end();_it++)
    {
      int indice=_vIdHTab[*_it];
      if(_iFlux)
	if(_g->si_feature(*_it,_iFlux)->r>=0)
	  {
	    float _feature=_g->si_feature(*_it,_iFlux)->r;
	    _flux_array->setAt(indice,_feature);
	  }
	else
	  _flux_array->setAt(indice,0);
      if(_iResist)
	if(_g->si_feature(*_it,_iResist)->r>=0)
	  {
	    float _feature=_g->si_feature(*_it,_iResist)->r;
	    _resistance_array->setAt(indice,_feature);
	  }
	else
	  _resistance_array->setAt(indice,0);
      if(_iPot)
	if(_g->si_feature(*_it,_iPot)->r>=0)
	  {
	    float _feature=_g->si_feature(*_it,_iPot)->r;
	    _potential_array->setAt(indice,_feature);
	  }
	else
	  _potential_array->setAt(indice,0);    
    }
  
//--------------------------------------------------
// test de calcul de potentiel.
/*
  _flux_array=clcFlux();
  _potential_array=clcPotential(_flux_array);
  
  
  cout<<"--------------------------"<<endl<<"flux values"<<endl;
  for(int i=0;i<_nb_desc;i++)
  cout<<_flux_array->getAt(i)<<" | ";
  cout<<endl<<"------------------------"<<endl;
  
  cout<<"--------------------------"<<endl<<"potential values"<<endl;
  for(int i=0;i<_nb_desc;i++)
  cout<<_potential_array->getAt(i)<<" | ";
  cout<<endl<<"------------------------"<<endl;
  */
  
//-------------------------------------------------

  _isValid=true;
}



// precondition: pointers g, resistance, flux, potential must be non NULL

ElectricalModel:: ElectricalModel(MTG* g, VId root, RealArray* resistance, RealArray* flux, RealArray* potential, double base_pot)
{
  _isValid=false;

  assert(g);
  assert(resistance);
  assert(flux);
  assert(potential);


  _g=g;
  _id=root;
  _base_potential=base_pot;
  
  //give the descendants of id at the same scale
  _vlist=_g->si_descendants(_id);
  
  _nb_desc=_vlist->size();
  
  cout<<"number of descendants : "<< _nb_desc<< std::endl;
  
  //renseignement de la table vIdHTab
  VtxList::iterator _it;
  int i=0;
  for(_it=_vlist->begin();_it<_vlist->end();_it++)
    {
      _vIdHTab[*_it]=i;
      i++;
    }  
  

  if (resistance->getSize()==(uint32_t)_nb_desc && 
      flux->getSize()==(uint32_t)_nb_desc && 
      potential->getSize()==(uint32_t)_nb_desc) {

    _resistance_array=resistance;
    _flux_array=flux;
    _potential_array=potential;

    _isValid = true;

  }
  else {

    // Error message

  }

}


ElectricalModel::~ElectricalModel()
{

  if(_vlist)
    delete _vlist;
  if(_resistance_array)
    delete _resistance_array;
  if(_flux_array)
    delete _flux_array;
  if(_potential_array)
    delete _potential_array;
}

void ElectricalModel::computeEM()
{
  _flux_array=clcFlux();
  _potential_array=clcPotential(_flux_array);
  
/*  
  cout<<"--------------------------"<<endl<<"flux values"<<endl;
  for(int i=0;i<_nb_desc;i++)
  cout<<_flux_array->getAt(i)<<" | ";
  cout<<endl<<"------------------------"<<endl;
  
  cout<<"--------------------------"<<endl<<"potential values"<<endl;
  for(int i=0;i<_nb_desc;i++)
  cout<<_potential_array->getAt(i)<<" | ";
  cout<<endl<<"------------------------"<<endl;
*/
}

RealArray* ElectricalModel::clcFlux()
{
  //returned Array
  RealArray* _fluxArray=new RealArray(_nb_desc);
  int i=0;
  //for all vtx in vlist
  VtxList::iterator _it;
  for(_it=_vlist->begin();_it<_vlist->end();_it++)
    {
      //extract the extremities
      VtxList* extremities_list=_g->si_extremities(*_it);

      float _flux=0.0;

      //for all vtx in extremities
      VtxList::iterator _it_Extr;
      for(_it_Extr=extremities_list->begin();_it_Extr<extremities_list->end();_it_Extr++)
	{
	  //Flux=Transpiration*LeafArea
	  //int indice=_vIdHTab[*_it_Extr];
	  // _flux+=_fluxData.transp_array->getAt(indice)*_fluxData.leafArea_array->getAt(indice);
	  _flux+=_flux_array->getAt(vtxToIndex(*_it_Extr));
	}
      
      _fluxArray->setAt(i,_flux);

      i++;
      
      delete extremities_list;
    }
  return _fluxArray;
}

RealArray* ElectricalModel::clcPotential(RealArray* flux_array)
{
  //returned Array
  RealArray* _potentialArray=new RealArray(_nb_desc);

  int i=0;
  //for all vtx in vlist
  VtxList::iterator _it;
  for(_it=_vlist->begin();_it<_vlist->end();_it++)
    {
      //extract the Path between the current vtx and the base
      VtxList* path_list=_g->si_path(_id,*_it);
     
      float _pot=_base_potential;

      //for all vtx in the path
      VtxList::iterator _it_path;
      for(_it_path=path_list->begin();_it_path<path_list->end();_it_path++)
	{
	  int indice=_vIdHTab[*_it_path];
	  _pot-=flux_array->getAt(indice)*_resistance_array->getAt(indice);
	}

      _potentialArray->setAt(i,_pot);

      i++;
      
      delete path_list;
    }

  return _potentialArray;
}

ostream& ElectricalModel::displayOneLine(ostream& o) const 
{
  o << "Potential values computed ";

  return o;
}

ostream& ElectricalModel::display(ostream& o) const 
{
  o << endl <<"flux values : " << endl;
  for(int k=0;k<_nb_desc;k++)
      o<<_flux_array->getAt(k)<<" | ";
  o << endl <<endl;

  o << endl <<"potential values : " << endl;
  for(int k2=0;k2<_nb_desc;k2++)
      o << _potential_array->getAt(k2) << " | ";
  o << endl << endl;

  return o;
}
