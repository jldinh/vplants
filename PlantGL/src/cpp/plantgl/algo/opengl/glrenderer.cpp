/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: The Plant Graphic Library
 *
 *       Copyright 1995-2007 UMR CIRAD/INRIA/INRA DAP 
 *
 *       File author(s): F. Boudon et al.
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




#include "glrenderer.h"
#include <plantgl/algo/base/discretizer.h>

#include <plantgl/pgl_appearance.h>
#include <plantgl/pgl_geometry.h>
#include <plantgl/pgl_transformation.h>
#include <plantgl/pgl_scene.h>

#include <plantgl/scenegraph/container/indexarray.h>
#include "util_appegl.h"
#include <plantgl/scenegraph/container/pointarray.h>
#include <plantgl/scenegraph/container/geometryarray2.h>
#include <plantgl/math/util_math.h>

#include <QtOpenGL/QGLWidget>
#include <QtGui/QImage>
#include <QtGui/QFont>

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE

// #define GEOM_DLDEBUG
// #define WITH_VERTEXARRAY
// #define WITH_GPU_PRIMITIVE


/* ----------------------------------------------------------------------- */

  

#define GEOM_GLRENDERER_CHECK_CACHE(geom) \
  GLuint _displaylist = 0; \
  if(!geom->unique()){ \
	if(__compil == 0){ \
	  if(check(geom->getId(),_displaylist)) return true; \
	}  \
	else if(call(geom->getId()))return true; \
  } \
  

#define GEOM_GLRENDERER_UPDATE_CACHE(geom) \
  if(__compil == 0 && !geom->unique()) update(geom->getId(),_displaylist); \

#define GEOM_GLRENDERER_CHECK_APPEARANCE(app) \
  if (__appearance.get() == app) return true;

#define GEOM_GLRENDERER_UPDATE_APPEARANCE(app) \
  __appearance = AppearancePtr(app);

template<class T>
bool GLRenderer::discretize_and_render(T * geom){
  GEOM_ASSERT(geom); 
  GEOM_GLRENDERER_CHECK_CACHE(geom);
  if(__appearance && __appearance->isTexture())
      __discretizer.computeTexCoord(true);
  else __discretizer.computeTexCoord(false);
  bool b=geom->apply(__discretizer); 
  if( b && (b=(__discretizer.getDiscretization()))){ 
      b=__discretizer.getDiscretization()->apply(*this);
  } 
  GEOM_GLRENDERER_UPDATE_CACHE(geom);
  return b; 
}

#define GEOM_GLRENDERER_DISCRETIZE_RENDER(geom) \
  return discretize_and_render(geom); \


#define BEGIN_LINE_WIDTH(obj) \
  if(!obj->isWidthToDefault()){ \
    glPushAttrib (GL_LINE_BIT); \
    int globalwidth = 1; \
	glGetIntegerv(GL_LINE_WIDTH,&globalwidth); \
	glLineWidth(float(obj->getWidth()+globalwidth-1)); \
  } \

#define END_LINE_WIDTH(obj) if(!obj->isWidthToDefault()){ glPopAttrib(); }

/* ----------------------------------------------------------------------- */


GLRenderer::GLRenderer( Discretizer& discretizer, QGLWidget * glframe ) :
  Action(),
  __scenecache(0),
  __discretizer(discretizer),
  __appearance(),
  __Mode(Normal),
  __selectMode(ShapeId),
  __compil(0),
  __glframe(glframe),
  __currentdisplaylist(false)
{
}


GLRenderer::~GLRenderer( )
{
  clear();
}

Discretizer&
GLRenderer::getDiscretizer( )
{
  return __discretizer;
}

void 
GLRenderer::setSelectionMode(SelectionId m)
{
  __selectMode = m;
}

const 
GLRenderer::SelectionId GLRenderer::getSelectionMode() const
{
  return __selectMode;
}

bool GLRenderer::setGLFrameFromId(uint_t wid)
{
    QWidget * widget = QWidget::find(WId(wid));
    if (!widget) return false;
#ifdef Q_CC_MSVC
    // By default qmake do not compile project with rtti information when
    // using msvc. So do a static cast
    QGLWidget * glwidget = static_cast<QGLWidget *>(widget);
#else
    QGLWidget * glwidget = dynamic_cast<QGLWidget *>(widget);
#endif
    if (!glwidget) return false;
    setGLFrame(glwidget);
    return true;
}

void GLRenderer::clear( )
{
#ifdef GEOM_DLDEBUG
  printf("clear cache\n");
#endif
  for (Cache<GLuint>::Iterator _it = __cache.begin();
       _it != __cache.end();
       _it++){
    if (_it->second) glDeleteLists(_it->second,1);
  }
  __cache.clear();
  if(__scenecache !=0){
    glDeleteLists(__scenecache,1);
    __scenecache = 0;
  }
  for (Cache<GLuint>::Iterator _it2 = __cachetexture.begin();
       _it2 != __cachetexture.end();
       _it2++){
    if (_it2->second) glDeleteTextures(1,&(_it2->second));
  }
  __cachetexture.clear();
  __currentdisplaylist = false;
  if(__compil != -1)__compil = 0;
}


bool GLRenderer::check(uint_t id, GLuint& displaylist){
  if(__Mode != DynamicPrimitive){ 
	Cache<GLuint>::Iterator _it = __cache.find(id); 
	if (_it != __cache.end()) { 
	  displaylist = _it->second;
	  glCallList(displaylist); 
#ifdef GEOM_DLDEBUG
	  printf("Call Display List %i\n",displaylist);
#endif
	  assert( glGetError()==GL_NO_ERROR); 
	  return true; 
	} 
	else { 
      displaylist = 0;
	  if(!__currentdisplaylist){
		displaylist = glGenLists(1); 
		if(displaylist != 0){
		  glNewList(displaylist,GL_COMPILE_AND_EXECUTE);
#ifdef GEOM_DLDEBUG
		  printf("Debut Display List %i\n",displaylist);
#endif
		  __currentdisplaylist = true;
		}
		assert( glGetError() == GL_NO_ERROR /* Creation */); 
	  } 
	} 
  }
  return false;
}

bool GLRenderer::call(uint_t id){
  if(__Mode != DynamicPrimitive){ 
	Cache<GLuint>::Iterator _it = __cache.find(id); 
	if (_it != __cache.end()) { 
	  glCallList(_it->second); 
#ifdef GEOM_DLDEBUG
	  printf("Call Display List %i\n",_it->second);
#endif
	  assert( glGetError()==GL_NO_ERROR); 
	  return true; 
	} 
  } 
  return false;
}

void GLRenderer::update(uint_t id, GLuint displaylist){
  if(__Mode != DynamicPrimitive && displaylist != 0 && __currentdisplaylist){ 
#ifdef GEOM_DLDEBUG
	  printf("End Display List %i for obj %i\n",displaylist,id);
#endif
	  glEndList(); 
	  __cache.insert(id,displaylist); 
	  assert( glGetError( ) == GL_NO_ERROR); 
	  __currentdisplaylist = false;
  }
}

void GLRenderer::registerTexture(ImageTexture * texture, GLuint id, bool erasePreviousIfExists)
{ 
  Cache<GLuint>::Iterator it = __cachetexture.find(texture->getId());
  if(it != __cachetexture.end()){
    GLuint oldid = it->second;
	if(erasePreviousIfExists)glDeleteTextures(1,&(it->second));
	it->second = id;
  }
  else {
	  __cachetexture.insert(texture->getId(),id);
  }
}


GLuint GLRenderer::getTextureId(ImageTexture * texture)
{
  Cache<GLuint>::Iterator it = __cachetexture.find(texture->getId());
  if(it != __cachetexture.end()) return it->second;
  else return 0;
}

/* ----------------------------------------------------------------------- */
void
GLRenderer::setRenderingMode(RenderingMode mode)
{
  if(__Mode != mode){
    if(!(__Mode & DynamicPrimitive) && (mode & DynamicPrimitive)){
      clear();
    }
    if(!(__Mode & Dynamic) && (mode & DynamicScene)){
      clearSceneList();
    }
    if(mode &  DynamicPrimitive)__compil = -1;
	else if(__compil == -1)__compil = 0;
    __Mode = mode;
  }
}

const GLRenderer::RenderingMode& GLRenderer::getRenderingMode() const{
	return __Mode;
}

bool
GLRenderer::beginSceneList()
{
  if(__Mode == Normal){
    if(__compil == 0 || __compil == 1 || __compil == -1){
      return true;
    }
	else {
	  if(!__scenecache ){
		__scenecache = glGenLists(1);
		if(__scenecache != 0){
		  glNewList(__scenecache,GL_COMPILE_AND_EXECUTE); 
#ifdef GEOM_DLDEBUG
		  printf("Debut Scene DisplayList\n");
#endif
		}
#ifdef GEOM_DLDEBUG
		else printf("Failed to create global display list");
#endif
		return true;
	  }
	  else {
#ifdef GEOM_DLDEBUG
		printf("Call Scene DisplayList\n");
#endif
		glCallList(__scenecache);
		return false;
      }
	}
  }
  else return true;
}

void
GLRenderer::endSceneList()
{
  if(__compil >= 2 && 
	 __scenecache != 0 && 
	 __Mode == Normal){
#ifdef GEOM_DLDEBUG
	printf("Fin Scene DisplayList\n");
#endif
    glEndList();
  }
}

void
GLRenderer::clearSceneList()
{
  if(__scenecache){
    glDeleteLists(__scenecache,1);
    __scenecache = 0;
    __compil = 2;
  }
}


bool GLRenderer::beginProcess(){
  if(__Mode == Selection){
    glInitNames();
  }
  else {
#ifdef GEOM_DLDEBUG
	if(__compil == 0)printf("** Compile Geometry\n");
	else if(__compil == 1)printf("** Compile Shape\n");
	else if(__compil == 2)printf("** Compile Scene\n");
#endif
  }
  return true;
}


bool GLRenderer::endProcess(){
  if(__compil != -1 && __compil < 3) {
#ifdef GEOM_DLDEBUG
	if(__compil == 0)printf("** Compiled Geometry\n");
	else if(__compil == 1)printf("** Compiled Shape\n");
	else if(__compil == 2)printf("** Compiled Scene : %i\n",__scenecache);
#endif
    __compil+=2;
  }
  glDisable( GL_TEXTURE_2D );
  glBindTexture(GL_TEXTURE_2D, 0);
  __appearance = AppearancePtr();
  // __discretizer.computeTexCoord(false);
  return true;
}

/* ----------------------------------------------------------------------- */
bool GLRenderer::process(Shape * geomshape)
{
  GEOM_ASSERT(geomshape);
  processAppereance(geomshape);
  return processGeometry(geomshape);
}

bool GLRenderer::processAppereance(Shape * geomshape){
  GEOM_ASSERT(geomshape);
  if(geomshape->appearance){
    return geomshape->appearance->apply(*this);
  }
  else return Material::DEFAULT_MATERIAL->apply(*this);
}

bool GLRenderer::processGeometry(Shape * geomshape){
  GEOM_ASSERT(geomshape);
  if(__Mode & Dynamic)return geomshape->geometry->apply(*this);

  if(__Mode == Selection){
      if(__selectMode == ShapeId && geomshape->getId()!=Shape::NOID){
      glPushName(GLuint(geomshape->getId()));
    }
    else {
      glPushName(GLuint(geomshape->SceneObject::getId()));
    }
  }

  // if(__compil == 0) return Shape->geometry->apply(*this);

  assert( glGetError() == GL_NO_ERROR);

/*  GLuint _displayList = 0;
  if(__compil == 1){
	if(check(Shape->SceneObject::getId(),_displayList)){
      if(__Mode == Selection)glPopName();
	  return true;
	}
	else {*/
      geomshape->geometry->apply(*this);
	  //update(Shape->SceneObject::getId(),_displayList);
      if(__Mode == Selection)glPopName();
	  return true;
/*	}
  }
  else {
	if(!call(Shape->SceneObject::getId()))Shape->geometry->apply(*this);
    if(__Mode == Selection)glPopName();
	return true;
  }*/
}

/* ----------------------------------------------------------------------- */

bool GLRenderer::process(Inline * geomInline) {
    GEOM_ASSERT(geomInline);
    if(geomInline->getScene()){
		if(__Mode == Selection){
			glPushName(GLuint(geomInline->getId()));
		}
        if(!geomInline->isTranslationToDefault() || !geomInline->isScaleToDefault()){
            glPushMatrix();
            const Vector3 _trans =geomInline->getTranslation();
            glGeomTranslate(_trans);
            const Vector3 _scale = geomInline->getScale();
            glGeomScale(_scale);
        }
        bool _result = true;
        for (Scene::iterator _i = geomInline->getScene()->begin();
             _i != geomInline->getScene()->end();
             _i++) {
            if (! (*_i)->applyAppearanceFirst(*this)) _result = false;
        };
        if(!geomInline->isTranslationToDefault() || !geomInline->isScaleToDefault()){
            glPopMatrix();
        }
        if(__Mode == Selection)glPopName();

        assert(glGetError() == GL_NO_ERROR);
        return _result;
    }
    else return false;
}

/* ----------------------------------------------------------------------- */

bool GLRenderer::process( AmapSymbol * amapSymbol ) {
  GEOM_ASSERT(amapSymbol);
  GEOM_GLRENDERER_CHECK_CACHE(amapSymbol);

  const IndexArrayPtr& _indexList = amapSymbol->getIndexList();

  glFrontFace(amapSymbol->getCCW() ? GL_CCW : GL_CW);
  bool tex = __appearance && __appearance->isTexture() && amapSymbol->hasTexCoordList();
  bool color = amapSymbol->hasColorList();
  bool colorV = amapSymbol->getColorPerVertex();

  if(__appearance && 
	 __appearance->isTexture() && 
	 !amapSymbol->hasTexCoordList()){
	glEnable(GL_TEXTURE_GEN_S);
	glEnable(GL_TEXTURE_GEN_T);
  }
  amapSymbol->checkNormalList();

#ifndef WITH_VERTEXARRAY
  uint_t _sizei = _indexList->size();
  GLfloat _rgba[4];
  for (uint_t _i = 0; _i < _sizei; _i++) {
    glBegin(GL_POLYGON);
	if ( color && !colorV) { 
          const Color4& _ambient = amapSymbol->getColorAt( _i );
          _rgba[0] = (GLfloat)_ambient.getRedClamped();
          _rgba[1] = (GLfloat)_ambient.getGreenClamped();
          _rgba[2] = (GLfloat)_ambient.getBlueClamped();
          _rgba[3] = 1.0f-( GLfloat )_ambient.getAlphaClamped();
          glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT,_rgba);
          glColor4fv(_rgba);
	}

    const Index& _index = _indexList->getAt(_i);
    uint_t _sizej = _index.size();
    for (uint_t _j = 0; _j < _sizej; _j++){
      glGeomNormal(amapSymbol->getFaceNormalAt(_i,_j));
      if(tex){
		Vector3& tex = amapSymbol->getFaceTexCoord3At(_i,_j);
		glTexCoord2d(tex.y(),tex.z());
	  }
	  else if ( color && colorV)
        {
          const Color4& _ambient = amapSymbol->getFaceColorAt( _i, _j );
          _rgba[0] = (GLfloat)_ambient.getRedClamped();
          _rgba[1] = (GLfloat)_ambient.getGreenClamped();
          _rgba[2] = (GLfloat)_ambient.getBlueClamped();
          _rgba[3] = 1.0f-( GLfloat )_ambient.getAlphaClamped();
          glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT,_rgba);
          glColor4fv(_rgba);
        }
      glGeomVertex(amapSymbol->getFacePointAt(_i,_j));
    }
    glEnd();
  };
#else

  glEnableClientState(GL_VERTEX_ARRAY);
  real_t * vertices = amapSymbol->getPointList()->data();
  glVertexPointer( 3, GL_GEOM_REAL,0,vertices);

  real_t * normals = amapSymbol->getNormalList()->data();
  glEnableClientState(GL_NORMAL_ARRAY);
  glNormalPointer( GL_GEOM_REAL,0,normals);

  real_t * texCoord = NULL;
  if(tex){
	texCoord = amapSymbol->getTexCoordList()->data();
	glEnableClientState(GL_TEXTURE_COORD_ARRAY);
	glTexCoordPointer( 2, GL_GEOM_REAL, sizeof(real_t) ,&texCoord[1]);
  }

  for(IndexArray::const_iterator it = amapSymbol->getIndexList()->begin();
      it != amapSymbol->getIndexList()->end(); it++)
    {
      glDrawElements( GL_POLYGON, it->size() , GL_UNSIGNED_INT, ( const GLvoid* )( &*( it->begin() ) ));
    }

  glDisableClientState(GL_VERTEX_ARRAY);
  glDisableClientState(GL_NORMAL_ARRAY);
  glDisableClientState(GL_TEXTURE_COORD_ARRAY);
  delete [] vertices;
  delete [] normals;
  if(texCoord)delete [] texCoord;

#endif
  if(__appearance && 
	 __appearance->isTexture() && 
	 !amapSymbol->hasTexCoordList()){
	glDisable(GL_TEXTURE_GEN_S);
	glDisable(GL_TEXTURE_GEN_T);
  }

  GEOM_GLRENDERER_UPDATE_CACHE(amapSymbol);
  return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( AsymmetricHull * asymmetricHull ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(asymmetricHull);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( AxisRotated * axisRotated ) {
  GEOM_ASSERT(axisRotated);
  GEOM_GLRENDERER_CHECK_CACHE(axisRotated);

  const Vector3& _axis = axisRotated->getAxis();
  const real_t& _angle = axisRotated->getAngle();

  glPushMatrix();
  glGeomRadRotate(_axis,_angle);
  axisRotated->getGeometry()->apply(*this);
  glPopMatrix();

  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  GEOM_GLRENDERER_UPDATE_CACHE(axisRotated);
  return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( BezierCurve * bezierCurve ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(bezierCurve);
}

/* ----------------------------------------------------------------------- */


bool GLRenderer::process( BezierPatch * bezierPatch ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(bezierPatch);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Box * box ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(box);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Cone * cone ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(cone);
}


/* ----------------------------------------------------------------------- */

#ifdef WITH_GPU_PRIMITIVE
#include "gpu_primitives/GPU_cylinder.h"
using namespace GPU_PRIMITIVES;
#endif

bool GLRenderer::process( Cylinder * cylinder ) {
#ifndef WITH_GPU_PRIMITIVE
  GEOM_GLRENDERER_DISCRETIZE_RENDER(cylinder);
#else
  GEOM_ASSERT(cylinder);
  GPU_cylinder c;
  if(c.gpu_begin()){
	GEOM_GL_ERROR_FROM(NULL);
	c.gpu_float(cylinder->getRadius());
	GEOM_GL_ERROR_FROM(NULL);
	c.gpu_vec3f(0,0,cylinder->getHeight());
	GEOM_GL_ERROR_FROM(NULL);
	c.gpu_point3f(0,0,0);
	GEOM_GL_ERROR_FROM(NULL);
	c.gpu_end();
	GEOM_GL_ERROR_FROM(NULL);
	return true;
  }
  else {
	GEOM_GLRENDERER_DISCRETIZE_RENDER(cylinder);
  }
#endif
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( ElevationGrid * elevationGrid ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(elevationGrid);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( EulerRotated * eulerRotated ) {
  GEOM_ASSERT(eulerRotated);
  GEOM_GLRENDERER_CHECK_CACHE(eulerRotated);

  glPushMatrix();
  glGeomRadEulerRotateZYX(eulerRotated->getAzimuth(),
						  eulerRotated->getElevation(),
						  eulerRotated->getRoll() );
  eulerRotated->getGeometry()->apply(*this);
  glPopMatrix();

  GEOM_GLRENDERER_UPDATE_CACHE(eulerRotated);
  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( ExtrudedHull * extrudedHull ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(extrudedHull);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( FaceSet * faceSet ) {
  GEOM_ASSERT(faceSet);
  GEOM_GLRENDERER_CHECK_CACHE(faceSet);

  glFrontFace(faceSet->getCCW() ? GL_CCW : GL_CW);
  const IndexArrayPtr& _indexList = faceSet->getIndexList();
  bool normalV = faceSet->getNormalPerVertex();
  bool tex = __appearance && __appearance->isTexture() && faceSet->hasTexCoordList();
  bool color = faceSet->hasColorList();
  bool colorV = faceSet->getColorPerVertex();

  if(__appearance && 
	 __appearance->isTexture() && 
	 !faceSet->hasTexCoordList()){
	glEnable(GL_TEXTURE_GEN_S);
	glEnable(GL_TEXTURE_GEN_T);
  }
  faceSet->checkNormalList();

#ifndef WITH_VERTEXARRAY
  uint_t _sizei = _indexList->size();
  GLfloat _rgba[4];
  for (uint_t _i = 0; _i < _sizei; _i++) {
    glBegin(GL_POLYGON);
    if (!normalV)glGeomNormal(faceSet->getNormalAt(_i));
	if ( color && !colorV) { 
          const Color4& _ambient = faceSet->getColorAt( _i );
          _rgba[0] = (GLfloat)_ambient.getRedClamped();
          _rgba[1] = (GLfloat)_ambient.getGreenClamped();
          _rgba[2] = (GLfloat)_ambient.getBlueClamped();
          _rgba[3] = 1.0f-( GLfloat )_ambient.getAlphaClamped();
          glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT,_rgba);
          glColor4fv(_rgba);
	}

    const Index& _index = _indexList->getAt(_i);
    uint_t _sizej = _index.size();
    for (uint_t _j = 0; _j < _sizej; _j++){
      if (normalV)glGeomNormal(faceSet->getFaceNormalAt(_i,_j));
	  if(tex)glGeomTexCoord(faceSet->getFaceTexCoordAt(_i,_j));
	  else if ( color && colorV)
        {
          const Color4& _ambient = faceSet->getFaceColorAt( _i, _j );
          _rgba[0] = (GLfloat)_ambient.getRedClamped();
          _rgba[1] = (GLfloat)_ambient.getGreenClamped();
          _rgba[2] = (GLfloat)_ambient.getBlueClamped();
          _rgba[3] = 1.0f-( GLfloat )_ambient.getAlphaClamped();
          glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT,_rgba);
          glColor4fv(_rgba);
        }
      glGeomVertex(faceSet->getFacePointAt(_i,_j));
    }
    glEnd();
  };
#else

  glEnableClientState(GL_VERTEX_ARRAY);
  real_t * vertices = faceSet->getPointList()->data();
  glVertexPointer( 3, GL_GEOM_REAL,0,vertices);

  faceSet->checkNormalList();
  real_t * normals = NULL;
  if (normalV) {
	normals = faceSet->getNormalList()->data();
	glEnableClientState(GL_NORMAL_ARRAY);
	glNormalPointer( GL_GEOM_REAL,0,normals);
  }

  real_t * texCoord = NULL;
  if(tex){
	texCoord = faceSet->getTexCoordList()->data();
	glEnableClientState(GL_TEXTURE_COORD_ARRAY);
	glTexCoordPointer( 2, GL_GEOM_REAL,0,texCoord);
  }

  size_t _i = 0;
  for(IndexArray::const_iterator it = faceSet->getIndexList()->begin();
      it != faceSet->getIndexList()->end(); it++)
    {
      if(!normalV)
        glGeomNormal(faceSet->getNormalAt(_i));
      _i++;
      glDrawElements( GL_POLYGON, it->size() , GL_UNSIGNED_INT, ( const GLvoid* )( &*( it->begin() )) );
    }

  glDisableClientState(GL_VERTEX_ARRAY);
  glDisableClientState(GL_NORMAL_ARRAY);
  glDisableClientState(GL_TEXTURE_COORD_ARRAY);
  delete [] vertices;
  if(normals)delete [] normals;
  if(texCoord)delete [] texCoord;

#endif
  if(__appearance && 
	 __appearance->isTexture() && 
	 !faceSet->hasTexCoordList()){
	glDisable(GL_TEXTURE_GEN_S);
	glDisable(GL_TEXTURE_GEN_T);
  }

  GEOM_GLRENDERER_UPDATE_CACHE(faceSet);
  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Frustum * frustum ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(frustum);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process(Extrusion * extrusion ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(extrusion);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Group * group ) {
  GEOM_ASSERT(group);
  GEOM_GLRENDERER_CHECK_CACHE(group);

  group->getGeometryList()->apply(*this);

  GEOM_GLRENDERER_UPDATE_CACHE(group);

  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( IFS * ifs ) {
  GEOM_ASSERT(ifs);
  GEOM_GLRENDERER_CHECK_CACHE(ifs);

  ITPtr transfos;
  transfos= dynamic_pointer_cast<IT>( ifs->getTransformation() );
  GEOM_ASSERT(transfos);
  const Matrix4ArrayPtr& matrixList= transfos->getAllTransfo();
  GEOM_ASSERT(matrixList);

  Matrix4Array::const_iterator matrix= matrixList->begin();
  while( matrix != matrixList->end() )
    {
    glPushMatrix();
    glGeomMultMatrix(*matrix);
    ifs->getGeometry()->apply(*this);
    glPopMatrix();
    matrix++;
    }

  GEOM_GLRENDERER_UPDATE_CACHE(ifs);

  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Material * material ) {
  GEOM_ASSERT(material);
  GEOM_GLRENDERER_CHECK_APPEARANCE(material);

  glDisable( GL_TEXTURE_2D );
  glBindTexture(GL_TEXTURE_2D, 0);

  GLfloat _rgba[4];
  const Color3& _ambient = material->getAmbient();
  _rgba[0] = (GLfloat)_ambient.getRedClamped();
  _rgba[1] = (GLfloat)_ambient.getGreenClamped();
  _rgba[2] = (GLfloat)_ambient.getBlueClamped();
  _rgba[3] = 1.0f-material->getTransparency();
  glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT,_rgba);

  const real_t& _diffuse = material->getDiffuse();
  _rgba[0] *= _diffuse;
  _rgba[1] *= _diffuse;
  _rgba[2] *= _diffuse;
  glMaterialfv(GL_FRONT_AND_BACK,GL_DIFFUSE,_rgba);

 /// We set the current color in the case of disabling the lighting
  glColor4fv(_rgba);

  const Color3& _specular = material->getSpecular();
  _rgba[0] = (GLfloat)_specular.getRedClamped();
  _rgba[1] = (GLfloat)_specular.getGreenClamped();
  _rgba[2] = (GLfloat)_specular.getBlueClamped();
  glMaterialfv(GL_FRONT_AND_BACK,GL_SPECULAR,_rgba);

  const Color3& _emission = material->getEmission();
  _rgba[0] = (GLfloat)_emission.getRedClamped();
  _rgba[1] = (GLfloat)_emission.getGreenClamped();
  _rgba[2] = (GLfloat)_emission.getBlueClamped();
  glMaterialfv(GL_FRONT_AND_BACK,GL_EMISSION,_rgba);

  glMaterialf(GL_FRONT_AND_BACK,GL_SHININESS,material->getShininess());

  GEOM_GLRENDERER_UPDATE_APPEARANCE(material);

  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */
bool GLRenderer::process( ImageTexture * texture ) {
  GEOM_ASSERT(texture);

  Cache<GLuint>::Iterator it = __cachetexture.find(texture->getId());
  if(it != __cachetexture.end()){
	//  printf("bind texture : %i\n", it->second);
    glEnable( GL_TEXTURE_2D );
    glBindTexture(GL_TEXTURE_2D, it->second);
  }
  else {
	QImage img;
	if(img.load(texture->getFilename().c_str())){
      bool notUsingMipmap = (!texture->getMipmaping()) && isPowerOfTwo(img.width()) && isPowerOfTwo(img.height());
      glEnable( GL_TEXTURE_2D );
	  img = QGLWidget::convertToGLFormat(img);
	  GLuint id;
	  glGenTextures(1, &id);
	  if (id !=0){
	  glBindTexture(GL_TEXTURE_2D, id);

//	  glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE  );
//	  glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL  );
//	  glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_BLEND  );
	  glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE  );

	  glTexParameterf( GL_TEXTURE_2D, 
					   GL_TEXTURE_WRAP_S, 
					   texture->getRepeatS() ? GL_REPEAT : GL_CLAMP);

	  glTexParameterf( GL_TEXTURE_2D, 
					   GL_TEXTURE_WRAP_T, 
					   texture->getRepeatT() ? GL_REPEAT : GL_CLAMP);

	  glTexParameterf( GL_TEXTURE_2D, 
					   GL_TEXTURE_MAG_FILTER, 
					   GL_LINEAR );

      if(notUsingMipmap){
	    glTexParameterf( GL_TEXTURE_2D, 
		                 GL_TEXTURE_MIN_FILTER, 
			    	     GL_LINEAR );

	    glTexImage2D( GL_TEXTURE_2D, 0, 4, img.width(), img.height(), 0,
		    GL_RGBA, GL_UNSIGNED_BYTE, img.bits() );
      }
      else{
	    glTexParameterf( GL_TEXTURE_2D, 
		                 GL_TEXTURE_MIN_FILTER, 
			    	     GL_LINEAR_MIPMAP_NEAREST );

	    gluBuild2DMipmaps( GL_TEXTURE_2D, 4, img.width(), img.height(),
		                     GL_RGBA, GL_UNSIGNED_BYTE, img.bits() );
      }
	  // printf("gen texture : %i\n",id);
	  // registerTexture(texture,id);
  	  __cachetexture.insert(texture->getId(),id);

	  }
	}
  }

  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */

bool GLRenderer::process( Texture2D * texture ) {
  GEOM_ASSERT(texture);
  GEOM_GLRENDERER_CHECK_APPEARANCE(texture);

  if(texture->getImage()){
	  // load image
	  texture->getImage()->apply(*this);

	  // apply texture transformation
	  if(texture->getTransformation())
			texture->getTransformation()->apply(*this);
	  else {
		// Set Texture transformation to Id if no transformation is specified
		glMatrixMode(GL_TEXTURE);
		glLoadIdentity();
		glMatrixMode(GL_MODELVIEW);
	  }
  }
  GEOM_GLRENDERER_UPDATE_APPEARANCE(texture);

  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}

/* ----------------------------------------------------------------------- */

bool GLRenderer::process( Texture2DTransformation * texturetransfo ) {
  GEOM_ASSERT(texturetransfo);

  glMatrixMode(GL_TEXTURE);
  glLoadIdentity();

  if (!texturetransfo->isTranslationToDefault()){
	  Vector2& value = texturetransfo->getTranslation();
	  glGeomTranslate(value.x(),value.y(),0.0);
  }

  if (!texturetransfo->isRotationAngleToDefault()){
	  Vector2& rotationCenter = texturetransfo->getRotationCenter();
	  glGeomTranslate(rotationCenter.x(),rotationCenter.y(),0.0);

	  real_t& value = texturetransfo->getRotationAngle();
	  glGeomRadRotate(0,0,1,value);

	  glGeomTranslate(-rotationCenter.x(),-rotationCenter.y(),0.0);
  }

  if (!texturetransfo->isScaleToDefault()){
	  Vector2& value = texturetransfo->getScale();
	  glGeomScale(value.x(),value.y(),1.0);
  }

  glMatrixMode(GL_MODELVIEW);
  return true;
}

/* ----------------------------------------------------------------------- */


bool GLRenderer::process( MonoSpectral * monoSpectral ) {
  GEOM_ASSERT(monoSpectral);

  GEOM_GLRENDERER_CHECK_APPEARANCE(monoSpectral);

  glDisable( GL_TEXTURE_2D );
  glBindTexture(GL_TEXTURE_2D, 0);

  GLfloat _rgba[4];
  _rgba[0] = (GLfloat)monoSpectral->getReflectance();
  _rgba[1] = (GLfloat)monoSpectral->getReflectance();
  _rgba[2] = (GLfloat)monoSpectral->getReflectance();
  _rgba[3] = (GLfloat)monoSpectral->getTransmittance();
  glMaterialfv(GL_FRONT_AND_BACK,GL_DIFFUSE,_rgba);

 /// We set the current color in the case of disabling the lighting
  glColor4fv(_rgba);

  GEOM_GLRENDERER_UPDATE_APPEARANCE(monoSpectral);

  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( MultiSpectral * multiSpectral ) {
  GEOM_ASSERT(multiSpectral);

  GEOM_GLRENDERER_CHECK_APPEARANCE(multiSpectral);

  glDisable( GL_TEXTURE_2D );
  glBindTexture(GL_TEXTURE_2D, 0);

  GLfloat _rgba[4];
  const Index3& _filter = multiSpectral->getFilter();
  _rgba[0] = (GLfloat)multiSpectral->getReflectanceAt(_filter.getAt(0));
  _rgba[1] = (GLfloat)multiSpectral->getReflectanceAt(_filter.getAt(1));
  _rgba[2] = (GLfloat)multiSpectral->getReflectanceAt(_filter.getAt(2));
  _rgba[3] = ((GLfloat)multiSpectral->getTransmittanceAt(_filter.getAt(0)) +
              (GLfloat)multiSpectral->getTransmittanceAt(_filter.getAt(1)) +
              (GLfloat)multiSpectral->getTransmittanceAt(_filter.getAt(2))) / 3;
  glMaterialfv(GL_FRONT_AND_BACK,GL_DIFFUSE,_rgba);

 /// We set the current color in the case of disabling the lighting
  glColor4fv(_rgba);

  GEOM_GLRENDERER_UPDATE_APPEARANCE(multiSpectral);

  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( NurbsCurve * nurbsCurve ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(nurbsCurve);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( NurbsPatch * nurbsPatch ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(nurbsPatch);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Oriented * oriented ) {
  GEOM_ASSERT(oriented);
  GEOM_GLRENDERER_CHECK_CACHE(oriented);

  glPushMatrix();
  Matrix4TransformationPtr _basis;
  _basis= dynamic_pointer_cast<Matrix4Transformation>(oriented->getTransformation());
  GEOM_ASSERT(_basis);
  glGeomMultMatrix(_basis->getMatrix());
  oriented->getGeometry()->apply(*this);
  glPopMatrix();

  GEOM_GLRENDERER_UPDATE_CACHE(oriented);
  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Paraboloid * paraboloid ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(paraboloid);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( PointSet * pointSet ) {
  GEOM_ASSERT(pointSet);
  GEOM_GLRENDERER_CHECK_CACHE(pointSet);

  glPushAttrib (GL_LIGHTING_BIT);
  glDisable(GL_LIGHTING);

  if(!pointSet->isWidthToDefault()){ 
    glPushAttrib (GL_POINT_BIT); 
    int globalwidth = 1; 
	glGetIntegerv(GL_POINT_SIZE,&globalwidth); 
	glPointSize(float(pointSet->getWidth()+globalwidth-1)); 
  } 

  const Point3ArrayPtr& points = pointSet->getPointList();
  if (!points) return false;
  bool color = pointSet->hasColorList() && 
			 (pointSet->getColorList()->size() == points->size());

#ifndef WITH_VERTEXARRAY
  Color4Array::const_iterator _itCol;
  if(color) _itCol = pointSet->getColorList()->begin();
  GLfloat _rgba[4];
  glBegin(GL_POINTS);
  for (Point3Array::const_iterator _i = points->begin();
       _i != points->end();
	   _i++){
		if(color){ 
          const Color4& _ambient = *_itCol;
          _rgba[0] = (GLfloat)_ambient.getRedClamped();
          _rgba[1] = (GLfloat)_ambient.getGreenClamped();
          _rgba[2] = (GLfloat)_ambient.getBlueClamped();
          _rgba[3] = 1.0f-( GLfloat )_ambient.getAlphaClamped();
          glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT,_rgba);
          glColor4fv(_rgba);
		  ++_itCol; 
		}
		glGeomVertex(*_i);
  }
  glEnd();
#else
  glEnableClientState(GL_VERTEX_ARRAY);
  real_t * vertices = points->data();
  glVertexPointer( 3, GL_GEOM_REAL,0,vertices);
  if( color ) {
    glEnableClientState( GL_COLOR_ARRAY );
    glColorPointer( 4, GL_UNSIGNED_BYTE, 4*sizeof( uchar_t ), points->getColorList()->toUcharArray() );
  }  
  glDrawArrays(GL_POINTS, 0 , points->size() );
  glDisableClientState(GL_VERTEX_ARRAY);
  delete [] vertices;
#endif

  if(!pointSet->isWidthToDefault()){ glPopAttrib(); }
  glPopAttrib();

  GEOM_GLRENDERER_UPDATE_CACHE(pointSet);
  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */

bool GLRenderer::process( PGL(Polyline) * polyline ) {
  GEOM_ASSERT(polyline);
  GEOM_GLRENDERER_CHECK_CACHE(polyline);

  glPushAttrib (GL_LIGHTING_BIT);
  glDisable(GL_LIGHTING);

  BEGIN_LINE_WIDTH(polyline)
	
  const Point3ArrayPtr& points = polyline->getPointList();
  bool color = polyline->hasColorList() && 
			 (polyline->getColorList()->size() == points->size());

#ifndef WITH_VERTEXARRAY
  Color4Array::const_iterator _itCol;
  if(color) _itCol = polyline->getColorList()->begin();
  GLfloat _rgba[4];
  glBegin(GL_LINE_STRIP);
  for (Point3Array::const_iterator _i = points->begin();
       _i != points->end();
	   _i++){
		if(color){ 
          const Color4& _ambient = *_itCol;
          _rgba[0] = (GLfloat)_ambient.getRedClamped();
          _rgba[1] = (GLfloat)_ambient.getGreenClamped();
          _rgba[2] = (GLfloat)_ambient.getBlueClamped();
          _rgba[3] = 1.0f-( GLfloat )_ambient.getAlphaClamped();
          glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT,_rgba);
          glColor4fv(_rgba);
		  ++_itCol; 
		}
		glGeomVertex((*_i));
  }
  glEnd();
#else
  glEnableClientState(GL_VERTEX_ARRAY);
  real_t * vertices = points->data();
  glVertexPointer( 3, GL_GEOM_REAL,0,vertices);
  if( color ) {
    glEnableClientState( GL_COLOR_ARRAY );
    glColorPointer( 4, GL_UNSIGNED_BYTE, 4*sizeof( uchar_t ), polyline->getColorList()->toUcharArray() );
  }  
  glDrawArrays(GL_LINE_STRIP, 0 , points->size() );
  glDisableClientState(GL_VERTEX_ARRAY);
  delete [] vertices;
#endif
  
  END_LINE_WIDTH(polyline)
  glPopAttrib();

  GEOM_GLRENDERER_UPDATE_CACHE(polyline);
  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */




bool GLRenderer::process( QuadSet * quadSet ) {
  GEOM_ASSERT(quadSet);
  GEOM_GLRENDERER_CHECK_CACHE(quadSet);

  glFrontFace(quadSet->getCCW() ? GL_CCW : GL_CW);
  bool normalV = quadSet->getNormalPerVertex();
  bool tex = __appearance && __appearance->isTexture() && quadSet->hasTexCoordList();
  bool color = quadSet->hasColorList();
  bool colorV = quadSet->getColorPerVertex();

  if(__appearance && 
	 __appearance->isTexture() && 
	 !quadSet->hasTexCoordList()){
	glEnable(GL_TEXTURE_GEN_S);
	glEnable(GL_TEXTURE_GEN_T);
  }

  quadSet->checkNormalList();
#ifndef WITH_VERTEXARRAY
  glBegin(GL_QUADS);
  uint_t _size = quadSet->getIndexListSize();
  GLfloat _rgba[4];
  for (uint_t _i = 0; _i < _size; _i++) {
    if (!normalV)glGeomNormal(quadSet->getNormalAt(_i));
	if ( color && !colorV) { 
          const Color4& _ambient = quadSet->getColorAt( _i );
          _rgba[0] = (GLfloat)_ambient.getRedClamped();
          _rgba[1] = (GLfloat)_ambient.getGreenClamped();
          _rgba[2] = (GLfloat)_ambient.getBlueClamped();
          _rgba[3] = 1.0f-( GLfloat )_ambient.getAlphaClamped();
          glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT,_rgba);
          glColor4fv(_rgba);
	}
	for (uint_t _j = 0; _j < 4; _j++) {
	  if (normalV) glGeomNormal(quadSet->getFaceNormalAt(_i,_j));
	  if(tex)glGeomTexCoord(quadSet->getFaceTexCoordAt(_i,_j));
      else if ( color && colorV)
        {
          const Color4& _ambient = quadSet->getFaceColorAt( _i, _j );
          _rgba[0] = (GLfloat)_ambient.getRedClamped();
          _rgba[1] = (GLfloat)_ambient.getGreenClamped();
          _rgba[2] = (GLfloat)_ambient.getBlueClamped();
          _rgba[3] = 1.0f-( GLfloat )_ambient.getAlphaClamped();
          glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT,_rgba);
          glColor4fv(_rgba);
        }
	  glGeomVertex(quadSet->getFacePointAt(_i,_j));
	}
  };
  glEnd();
#else

  glEnableClientState(GL_VERTEX_ARRAY);
  real_t * vertices = quadSet->getPointList()->data();
  glVertexPointer( 3, GL_GEOM_REAL,0,vertices);

  real_t * normals = NULL;
  if (normalV) {
	normals = quadSet->getNormalList()->data();
	glEnableClientState(GL_NORMAL_ARRAY);
	glNormalPointer( GL_GEOM_REAL,0,normals);
  }

  real_t * texCoord = NULL;
  uchar_t * colorCoord = NULL;
  if(tex){
	texCoord = quadSet->getTexCoordList()->data();
	glEnableClientState(GL_TEXTURE_COORD_ARRAY);
	glTexCoordPointer( 2, GL_GEOM_REAL,0,texCoord);
  }
  else if( color ) {
    glEnableClientState( GL_COLOR_ARRAY );
    glColorPointer( 4, GL_UNSIGNED_BYTE, 4*sizeof( uchar_t ), quadSet->getColorList()->toUcharArray() );
  }

  if (normalV){
	size_t si = quadSet->getIndexList()->size();
	uint_t * indices = quadSet->getIndexList()->data();
	glDrawElements(	GL_QUADS, 4*si , GL_UNSIGNED_INT, indices);
	delete [] indices;
  }
  else {
	size_t _i = 0;
	for(Index4Array::const_iterator it = quadSet->getIndexList()->begin();
	it != quadSet->getIndexList()->end(); it++){
		  glGeomNormal(quadSet->getNormalAt(_i));_i++;
		  glDrawElements(	GL_QUADS, 4 , GL_UNSIGNED_INT, it->begin());
	 }

  }

  glDisableClientState(GL_VERTEX_ARRAY);
  glDisableClientState(GL_NORMAL_ARRAY);
  glDisableClientState(GL_TEXTURE_COORD_ARRAY);
  glDisableClientState(GL_COLOR_ARRAY);
  delete [] vertices;
  if(normals)delete [] normals;
  if(texCoord)delete [] texCoord;
  if( colorCoord ) delete [] colorCoord;

#endif
  if(__appearance && 
	 __appearance->isTexture() && 
	 !quadSet->hasTexCoordList()){
	glDisable(GL_TEXTURE_GEN_S);
	glDisable(GL_TEXTURE_GEN_T);
  }

  GEOM_GLRENDERER_UPDATE_CACHE(quadSet);
  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Revolution * revolution )
{
  GEOM_GLRENDERER_DISCRETIZE_RENDER(revolution);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Swung * swung )
{
  GEOM_GLRENDERER_DISCRETIZE_RENDER(swung);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Scaled * scaled ) {
  GEOM_ASSERT(scaled);
  GEOM_GLRENDERER_CHECK_CACHE(scaled);
  glPushMatrix();
  glGeomScale(scaled->getScale());
  scaled->getGeometry()->apply(*this);
  glPopMatrix();

  GEOM_GLRENDERER_UPDATE_CACHE(scaled);
  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( ScreenProjected * scp ) {
	GEOM_ASSERT(scp);
    if(__Mode == Selection) {
        return true;
    } 
	GEOM_GLRENDERER_CHECK_CACHE(scp);
	real_t heigthscale = 1.0;
    if(__glframe!= NULL && scp->getKeepAspectRatio()){
		heigthscale = float(__glframe->height()) / float(__glframe->width());
    }

	glMatrixMode(GL_PROJECTION);
	glPushMatrix();
	glLoadIdentity();
	glOrtho(-1, 1,-heigthscale, heigthscale, 1, -1);
	glMatrixMode(GL_MODELVIEW);
	glPushMatrix();
    glLoadIdentity();

    bool lighting = glIsEnabled(GL_LIGHTING);
    if (lighting){
        glPushAttrib(GL_LIGHTING_BIT);
        glGeomLightPosition(GL_LIGHT0,Vector3(0,0,-1));
        glGeomLightDirection(GL_LIGHT0,Vector3(0,0,1));
    }

	scp->getGeometry()->apply(*this);
  
    if (lighting) glPopAttrib();
	glMatrixMode(GL_PROJECTION);
	glPopMatrix();
	glMatrixMode(GL_MODELVIEW);
	glPopMatrix();


    GEOM_GLRENDERER_UPDATE_CACHE(scp);
    GEOM_ASSERT(glGetError() == GL_NO_ERROR);
    return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Sphere * sphere ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(sphere);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Tapered * tapered ) {
  GEOM_ASSERT(tapered);
  GEOM_GLRENDERER_CHECK_CACHE(tapered);

  PrimitivePtr _primitive = tapered->getPrimitive();
  if(_primitive->apply(__discretizer)){
      ExplicitModelPtr _explicit = __discretizer.getDiscretization();

      Transformation3DPtr _taper(tapered->getTransformation());
      ExplicitModelPtr _tExplicit = _explicit->transform(_taper);
      _tExplicit->apply(*this);

      GEOM_GLRENDERER_UPDATE_CACHE(tapered);
      return true;
  }
  else return false;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Translated * translated ) {
  GEOM_ASSERT(translated);
  GEOM_GLRENDERER_CHECK_CACHE(translated);

  glPushMatrix();
  glGeomTranslate(translated->getTranslation());
  translated->getGeometry()->apply(*this);
  glPopMatrix();

  GEOM_GLRENDERER_UPDATE_CACHE(translated);
  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */
#include <iostream>
using namespace std;

bool GLRenderer::process( TriangleSet * triangleSet ) {
  GEOM_ASSERT(triangleSet);
  GEOM_GLRENDERER_CHECK_CACHE(triangleSet);

  bool normalV = triangleSet->getNormalPerVertex();
  bool tex = __appearance && __appearance->isTexture() && triangleSet->hasTexCoordList();
  bool color = triangleSet->hasColorList();
  bool colorV = triangleSet->getColorPerVertex();

  glFrontFace(triangleSet->getCCW() ? GL_CCW : GL_CW);
  if(__appearance && __appearance->isTexture() && !triangleSet->hasTexCoordList())
    {
      glEnable(GL_TEXTURE_GEN_S);
      glEnable(GL_TEXTURE_GEN_T);
    }
  else if( color )
    {
      glDisable( GL_TEXTURE_2D );
      glBindTexture(GL_TEXTURE_2D, 0);
    }

  triangleSet->checkNormalList();

#ifndef WITH_VERTEXARRAY
  glBegin(GL_TRIANGLES);
  uint_t _size = triangleSet->getIndexListSize();
  GLfloat _rgba[4];
  for (uint_t _i = 0; _i < _size; _i++) {
    if (!normalV)
      glGeomNormal(triangleSet->getNormalAt(_i));
	if ( color && !colorV) { 
          const Color4& _ambient = triangleSet->getColorAt( _i );
          _rgba[0] = (GLfloat)_ambient.getRedClamped();
          _rgba[1] = (GLfloat)_ambient.getGreenClamped();
          _rgba[2] = (GLfloat)_ambient.getBlueClamped();
          _rgba[3] = 1.0f-( GLfloat )_ambient.getAlphaClamped();
          glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT,_rgba);
          glColor4fv(_rgba);
	}
    for (uint_t _j = 0; _j < 3; _j++) {
      if (normalV)
        glGeomNormal(triangleSet->getFaceNormalAt(_i,_j));
      if(tex)
        glGeomTexCoord(triangleSet->getFaceTexCoordAt(_i,_j));
      else if ( color  && colorV)
        {
          const Color4& _ambient = triangleSet->getFaceColorAt( _i, _j );
          _rgba[0] = (GLfloat)_ambient.getRedClamped();
          _rgba[1] = (GLfloat)_ambient.getGreenClamped();
          _rgba[2] = (GLfloat)_ambient.getBlueClamped();
          _rgba[3] = 1.0f-( GLfloat )_ambient.getAlphaClamped();
          glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT,_rgba);
          glColor4fv(_rgba);
        }
      glGeomVertex(triangleSet->getFacePointAt(_i,_j));
    }
  };
  glEnd();
#else

  glEnableClientState(GL_VERTEX_ARRAY);
  real_t * vertices = triangleSet->getPointList()->data();
  glVertexPointer( 3, GL_GEOM_REAL,0,vertices);
  size_t si = triangleSet->getIndexList()->size();

  real_t * normals = NULL;
  if (normalV) {
	normals = triangleSet->getNormalList()->data();
	glEnableClientState(GL_NORMAL_ARRAY);
	glNormalPointer( GL_GEOM_REAL,0,normals);
  }

  real_t * texCoord = NULL;
  uchar_t * colorCoord = NULL;
  if(tex){
	texCoord = triangleSet->getTexCoordList()->data();
	glEnableClientState(GL_TEXTURE_COORD_ARRAY);
	glTexCoordPointer( 2, GL_GEOM_REAL,0,texCoord);
  } 
  else if( color ) {
    glEnableClientState( GL_COLOR_ARRAY );
    glColorPointer( 4, GL_UNSIGNED_BYTE, 4*sizeof( uchar_t ), triangleSet->getColorList()->toUcharArray() );
  }

  if (normalV){
	uint_t * indices = triangleSet->getIndexList()->data();
	glDrawElements(	GL_TRIANGLES, 3*si , GL_UNSIGNED_INT, indices);
	delete [] indices;
  }
  else {
	size_t _i = 0;
	for(Index3Array::const_iterator it = triangleSet->getIndexList()->begin();
	it != triangleSet->getIndexList()->end(); it++){
		  glGeomNormal(triangleSet->getNormalAt(_i));_i++;
		  glDrawElements(	GL_TRIANGLES, 3 , GL_UNSIGNED_INT, it->begin());
		  }

  }

  glDisableClientState(GL_VERTEX_ARRAY);
  glDisableClientState(GL_NORMAL_ARRAY);
  glDisableClientState(GL_TEXTURE_COORD_ARRAY);
  glDisableClientState(GL_COLOR_ARRAY);
  delete [] vertices;
  if(normals) delete [] normals;
  if(texCoord) delete [] texCoord;
  if( colorCoord ) delete [] colorCoord;
#endif

  if(__appearance && __appearance->isTexture() && !triangleSet->hasTexCoordList()){
	glDisable(GL_TEXTURE_GEN_S);
	glDisable(GL_TEXTURE_GEN_T);
  }

  GEOM_GLRENDERER_UPDATE_CACHE(triangleSet);
  GEOM_ASSERT(glGetError() == GL_NO_ERROR);
  return true;
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( BezierCurve2D * bezierCurve ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(bezierCurve);
}

/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Disc * disc ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(disc);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( NurbsCurve2D * nurbsCurve ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(nurbsCurve);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( PointSet2D * pointSet ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(pointSet);
}


/* ----------------------------------------------------------------------- */


bool GLRenderer::process( Polyline2D * polyline ) {
  GEOM_GLRENDERER_DISCRETIZE_RENDER(polyline);
}


/* ----------------------------------------------------------------------- */

#if QT_VERSION >= 300

bool GLRenderer::process( Text * text ) {
  GEOM_ASSERT(text);
  if(__Mode == Selection) {
        return true;
  } 
  else {
      glPushAttrib(GL_LIGHTING_BIT);
      glDisable(GL_LIGHTING);
      if(!text->getString().empty()){
    	QFont f;
    	if(text->getFontStyle()){
    	  const FontPtr& font = text->getFontStyle();
    	  if(!font->getFamily().empty())
    		  f.setFamily(font->getFamily().c_str());
    	  f.setPointSize(font->getSize());
    	  f.setBold(font->getBold()),
    	  f.setItalic(font->getItalic());
    	}
    	else {
    	  f.setPointSize(Font::DEFAULT_SIZE);
    	}
    	if(__glframe!= NULL){
    		if (text->getScreenCoordinates()) {
    			glMatrixMode(GL_PROJECTION);
    			glPushMatrix();
    			glLoadIdentity();
    			glOrtho(0,100,0,100,0,-100);
    			glMatrixMode(GL_MODELVIEW);
    			glPushMatrix();
    			glLoadIdentity();
    		}

    		const Vector3& position = text->getPosition();
    		__glframe->renderText(position.x(),position.y(),position.z(),QString(text->getString().c_str()),f);

    		if (text->getScreenCoordinates()) {
    			glMatrixMode(GL_PROJECTION);
    			glPopMatrix();
    			glMatrixMode(GL_MODELVIEW);
    			glPopMatrix();
    		}

    	}
      }
      glPopAttrib();
  }
  return true;
}

#else

bool GLRenderer::process( Text * text ) {
  GEOM_ASSERT(text);
  return true;
}

#endif


/* ----------------------------------------------------------------------- */

bool GLRenderer::process( Font * font ) {
  GEOM_ASSERT(font);
  return true;
}

/* ----------------------------------------------------------------------- */
