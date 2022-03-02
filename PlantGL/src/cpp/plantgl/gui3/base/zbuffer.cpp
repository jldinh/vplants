/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *                           UMR PIAF INRA-UBP Clermont-Ferrand
 *
 *       File author(s): C. Nouguier & F. Boudon
 *                       N. Dones & B. Adam
 *
 *       $Source$
 *       $Id: zbuffer.cpp 3334 2007-06-19 13:51:10Z boudon $
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


#include <plantgl/algo/opengl/util_gl.h>
#include <plantgl/tool/util_assert.h>
#include "zbuffer.h"

TOOLS_USING_NAMESPACE
PGL_USING_NAMESPACE

void ViewRayBuffer3::setAt(size_t i, size_t j, void * buffer, size_t size,const Vector3& position) { 
	RayHitList3& res = getAt(i,j) ;
	GLuint names, *ptr;
	ptr = (GLuint *) buffer;
	GLuint id;
	GLuint zmin;
	GLuint zmax;
	GLdouble zmin2;
	GLdouble zmax2;
	GLint viewport[4];
	GLdouble modelMatrix[16], projMatrix[16];
	glGetIntegerv(GL_VIEWPORT,viewport);
	glGetDoublev(GL_MODELVIEW_MATRIX,modelMatrix);
	glGetDoublev(GL_PROJECTION_MATRIX,projMatrix);
	GLdouble winx = viewport[2]/2;
	GLdouble winy = viewport[3]/2;
	GLdouble objx,objx2, objy,objy2, objzmin , objzmax;
//	int gluUnProject(winx,winy, winz, modelMatrix, projMatrix, viewport,
//                     objx,objy, objz);

	if(size > 0){
		for(size_t i = 0 ; i < size ; i++){
			names = *ptr;
			ptr++;
			zmin = (float)*ptr; zmin2 = (GLdouble)zmin /(GLdouble)ULONG_MAX ; ptr++;
			zmax = (float)*ptr; zmax2 = (GLdouble)zmax /(GLdouble)ULONG_MAX ;ptr++;
			id = *ptr;
			if( gluUnProject(winx,winy, zmin2, modelMatrix, projMatrix, viewport,
				&objx,&objy, &objzmin) == GL_TRUE  &&
				gluUnProject(winx,winy, zmax2, modelMatrix, projMatrix, viewport,
				&objx2,&objy2, &objzmax) == GL_TRUE  ){
				
				res.push_back(RayHit3(id,norm(Vector3(objx,objy,objzmin)-position),norm(Vector3(objx2,objy2,objzmax)-position)));
			}
			for(unsigned int j = 0 ; j < names ; j++)ptr++;
		}
	}
}

ViewRayPointHitBuffer3& ViewRayPointHitBuffer3::operator+=(const ViewRayPointHitBuffer3& buff)
{
  //arrays must have identical size
  int w = getRowsSize();
  int h = getColsSize();
  assert(buff.getRowsSize() == w && buff.getColsSize() == h && "Size of self and buff must be identical.");
  for(int r=0; r<h; ++r)
  {
      for(int c=0; c<w; ++c)
      {
        const RayPointHitList3& hitList = buff.getAt(r,c);
        if(!hitList.empty())
        {
		  RayPointHitList3& myhitList = getAt(r,c);
		  myhitList.insert(myhitList.end(),hitList.begin(),hitList.end());
        }
      }
  }
  return *this;
}

ViewRayPointHitBuffer3 ViewRayPointHitBuffer3::operator+(const ViewRayPointHitBuffer3& buff)const
{//arrays must have identical size
  ViewRayPointHitBuffer3 res (*this);
  res += buff;
  return res;
}


ViewZBuffer3* ViewZBuffer3::importglDepthBuffer(bool alldepth)
{	
	GLint viewport[4];
	glGetIntegerv(GL_VIEWPORT,viewport);
	int width = viewport[2];
	int height = viewport[3];
	ViewZBuffer3 * buffer = new ViewZBuffer3(height,width);

	
	float  * zvalues = new float[width*height];
	// std::cerr << "Read Depth Buffer ... ";
	glReadBuffer(GL_FRONT);
	glReadPixels(0,0,width,height,GL_DEPTH_COMPONENT, GL_FLOAT, zvalues);
	// std::cerr << "done." << std::endl;
	GLdouble modelMatrix[16], projMatrix[16];
	glGetDoublev(GL_MODELVIEW_MATRIX,modelMatrix);
	glGetDoublev(GL_PROJECTION_MATRIX,projMatrix);
	GLdouble objx, objy, objz;
	float  * iterzvalues = zvalues;
	// std::cerr << "Unproject Depth Buffer ... ";
	for(int i = 0; i < height; ++i){
		for (int j = 0; j < width; ++j){
			buffer->getAt(i,j).depth = *iterzvalues ;
			if( alldepth ||( 0 < *iterzvalues && *iterzvalues < 1) ){
				if( gluUnProject(j,i, (GLdouble)*iterzvalues, modelMatrix, projMatrix, viewport, &objx,&objy, &objz) == GL_TRUE ){
					buffer->getAt(i,j).pos = Vector3(objx,objy,objz);
				}
			}
			++iterzvalues;
		}
	}
	// std::cerr << "done." << std::endl;
	delete [] zvalues;
	return buffer;
}

ViewZBuffer3* ViewZBuffer3::importglZBuffer(bool alldepth)
{	
	ViewZBuffer3 * buffer = importglDepthBuffer(alldepth);
	int width = buffer->getRowsSize();
	int height = buffer->getColsSize();
	uchar  * colvalues = new uchar[4*width*height];
	// std::cerr << "Read Color Buffer ... ";
	glReadPixels(0,0,width,height,GL_RGBA, GL_UNSIGNED_BYTE, colvalues);
	// std::cerr << "done." << std::endl;
	uchar  * itercolvalues = colvalues;
	for(int i = 0; i < height; ++i){
		for (int j = 0; j < width; ++j){
			buffer->getAt(i,j).color = Color4(*itercolvalues,itercolvalues[1],
				                               itercolvalues[2],itercolvalues[3]);
			itercolvalues+=4;
		}
	}
	delete [] colvalues;

	return buffer;
}
