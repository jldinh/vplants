/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       Copyright 2005-2008 UMR DAP 
 *
 *       File author(s): D. Da SILVA (david.da_silva@cirad.fr)
 *                       F. BOUDON (frederic.boudon@cirad.fr)
 *
 *       $Id: gridcomputer.cpp,v 1.4 2006/06/20 10:22:57 fboudon Exp $
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
// #define BCM_MAKEDLL

#include "fractalysis/engine/bcmCompute.h"
#include <cmath>
#include <cstring> // for memset
using namespace std;

//typedef vector<pair<Vector3,float> > FrPointList;
//typedef float *** FrGrid; //sert a rien ??

inline Vector3 getCenter(const Vector3& p1, const Vector3& p2, const Vector3& p3)
{ return (p1+p2+p3)/3; }

FrPointList * pointDiscretize(const ScenePtr& scene) //prend une scene et rend l'ensemble de point={centre de chaque triangle}
{
	FrPointList&  result = *(new FrPointList); // ???

	Tesselator t;
	TriangleSetPtr triangulation;
	for(Scene::const_iterator it = scene->getBegin(); it != scene->getEnd(); ++it) //pourquoi ++it ?
	{
		(*it)->apply(t);
		triangulation = t.getTriangulation();
		if (triangulation)
		{
			for(uint32_t itTriangle = 0; itTriangle < triangulation->getIndexList()->getSize(); ++itTriangle)
			{
				result.push_back(pair<Vector3,float>(getCenter( triangulation->getFacePointAt(itTriangle,0),
                                                                                triangulation->getFacePointAt(itTriangle,1),
                                                                                triangulation->getFacePointAt(itTriangle,2)
                                                                              ),
								    surface(triangulation->getFacePointAt(itTriangle,0),
                                                                            triangulation->getFacePointAt(itTriangle,1),
                                                                            triangulation->getFacePointAt(itTriangle,2)
                                                                          )
                                                                    )
                                              );
			}
		}
	}
	return &result;
}

pair<Vector3,Vector3> bbox(const FrPointList& points) //retourne les points min et max formant la bbox d'une liste de points
{
	Vector3 min = points[0].first , max = points[0].first;
	for(FrPointList::const_iterator itPoints = points.begin()+1; itPoints != points.end(); ++itPoints)
	{
		const Vector3& p = itPoints->first;
		if(min.x() > p.x()) min.x() = p.x();
		if(min.y() > p.y()) min.y() = p.y();
		if(min.z() > p.z()) min.z() = p.z();
		if(max.x() < p.x()) max.x() = p.x();
		if(max.y() < p.y()) max.y() = p.y();
		if(max.z() < p.z()) max.z() = p.z();
	}
	return pair<Vector3,Vector3>(min,max);

}

pair<Vector3,Vector3> bbox2(const ScenePtr& sc) // que fait cette bbox ?
{
    Discretizer d;
    BBoxComputer bbc( d );
    bbc.process(sc);
    Vector3 epsilon(0.01,0.01,0.01);
	if(!bbc.getBoundingBox())
	{
		std::cerr << "Error while computing bounding box." << std::endl;
	}
	return pair<Vector3,Vector3>(bbc.getBoundingBox()->getLowerLeftCorner()-epsilon,bbc.getBoundingBox()->getUpperRightCorner()+epsilon);

}


inline void gridIndex(const Vector3& point, const Vector3& step, int& i, int& j, int &k){
	i = floor(point.x() / step.x());
	j = floor(point.y() / step.y());
	k = floor(point.z() / step.z());
}

void scene2Grid( const FrPointList& points, 
				 const pair<Vector3,Vector3>& mbbox, int gridSize, 
				 int& intercepted, double& voxelSize  ) //calcul le nbr de voxel intercepte par une grille de taille gridsize
{
	Vector3 origin = mbbox.first;
	Vector3 step = (mbbox.second-mbbox.first) / gridSize;

	voxelSize = pow((double)step.x()*step.y()*step.z() , 1/3. );
	int gridSize3 = gridSize*gridSize*gridSize; // nbr de voxels

	int * gridData = new int[gridSize3+1]; // tableau de taille nbr de voxel + 1 ??
	memset(gridData,0,gridSize3*sizeof(int)); // ca sert a quoi ?

	int i,j,k;
	int gsize2 = gridSize*gridSize;
	int gsizem1 = gridSize-1;

	for(FrPointList::const_iterator itPoints = points.begin(); itPoints != points.end(); ++itPoints)
	{
		gridIndex( itPoints->first - origin, step, i, j, k );
		int index = min(i,gsizem1) * gsize2  + min(j,gsizem1) * gridSize + min(k,gsizem1) ; //calcul l'index du tableau en fonction de la position
		++gridData[index];
		// grid[index] += itPoints->second;

	}

	intercepted = 0;
	int * itGridData = gridData;// pourquoi une copie 
	for (int it= 0; it < gridSize3; ++it,++itGridData)
	{
		if(*itGridData > 0) ++intercepted; //si la case > 0 elle a ete intercepte
	}
	delete [] gridData;
}

pair<int,double> computeGrid(const ScenePtr& scene, int gridSize)
{
	FrPointList * points = pointDiscretize(scene); //recupere la liste de points a partir de la scene
	std::cerr << "Points computed" << std::endl;
	pair<Vector3,Vector3>  mbbox = bbox2(scene); //calcul la bbox de la liste de points
	std::cerr << "BBox computed" << std::endl;
	int intercepted =0;
	double voxelSize = 0;
	scene2Grid(*points,mbbox,gridSize,intercepted,voxelSize); //calcul le nbr de voxels intercepte
	delete points;
	return pair<int,double>(intercepted,voxelSize);
}


//typedef vector<pair<int,double> > FrResult; //vecteur de couple pour transformer en liste ?

FrResult computeGrids(const ScenePtr& scene, int maxGridSize)
{
	FrPointList * points = pointDiscretize(scene);
	std::cerr << "Points computed" << std::endl;
	pair<Vector3,Vector3>  mbbox = bbox2(scene);
	std::cerr << "BBox computed" << std::endl;
	FrResult results;
	int intercepted =0;
	double voxelSize = 0;
	for (int itGridSize = 2; itGridSize <= maxGridSize; ++itGridSize)
	{
		 
		scene2Grid(*points,mbbox,itGridSize,intercepted,voxelSize);
		results.push_back(pair<int,double>(intercepted,voxelSize));
		std::cerr << "Grid " << itGridSize << " computed : " << intercepted << " " << voxelSize << std::endl;
	}

	delete points;
	return results;
}


