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
  
#include <boost/python.hpp>
#include <plantgl/python/extract_widget.h>

#include <plantgl/algo/opengl/glskelrenderer.h>
#include <plantgl/algo/base/discretizer.h>
#include <plantgl/algo/base/skelcomputer.h>
#include <plantgl/algo/base/bboxcomputer.h>
#include <plantgl/algo/opengl/glbboxrenderer.h>
#include <plantgl/algo/opengl/glctrlptrenderer.h>
#include <plantgl/scenegraph/appearance/texture.h>

#include <QtOpenGL/qgl.h>

/* ----------------------------------------------------------------------- */

PGL_USING_NAMESPACE
using namespace boost::python;
#define bp boost::python

/* ----------------------------------------------------------------------- */

GLRenderer::RenderingMode get_rd_mode(GLRenderer * rd)
{ return rd->getRenderingMode();}

GLRenderer::SelectionId get_sel_mode(GLRenderer * rd)
{ return rd->getSelectionMode();}

/*
QGLWidget * get_fgl_mode(GLRenderer * rd)
{ return rd->getGLFrame();}
*/

void py_setGLFrame(GLRenderer * rd, boost::python::object widget){
	rd->setGLFrame(extract_widget<QGLWidget>(widget)());
}

void export_GLRenderer()
{
  scope glrenderer = class_< GLRenderer,bases< Action >,boost::noncopyable >
    ( "GLRenderer", init<Discretizer& >("GLRenderer(Discretizer d [, QGLWidget *]) An action which draws objects of type of Geometry or of type of Material to the current GL context."))
	.def("clear",&GLRenderer::clear)
    .def("beginSceneList",&GLRenderer::beginSceneList)
    .def("endSceneList",&GLRenderer::endSceneList)
    .def("clearSceneList",&GLRenderer::clearSceneList)
	.def("setGLFrame",&py_setGLFrame)
	.add_property("renderingMode",&get_rd_mode,&GLRenderer::setRenderingMode)
	.add_property("selectionMode",&get_sel_mode,&GLRenderer::setSelectionMode)
	// .add_property("frameGL",&get_fgl_mode,&GLRenderer::setGLFrame)
	 .def("getDiscretizer",&GLRenderer::getDiscretizer, return_internal_reference<>())
	 .def("setGLFrameFromId",&GLRenderer::setGLFrameFromId)
	 .def("registerTexture",&GLRenderer::registerTexture, (bp::arg("texture"),bp::arg("id"),bp::arg("erasePreviousIfExists")=true))
	 .def("getTextureId",&GLRenderer::getTextureId)
    ;

  enum_<GLRenderer::RenderingMode>("RenderingMode")
	  .value("Normal",GLRenderer::Normal)
	  .value("Selection",GLRenderer::Selection)
	  .value("DynamicPrimitive",GLRenderer::DynamicPrimitive)
	  .value("DynamicScene",GLRenderer::DynamicScene)
	  .value("Dynamic",GLRenderer::Dynamic)
	  .export_values()
	  ;

  enum_<GLRenderer::SelectionId>("SelectionId")
	  .value("ShapeId",GLRenderer::ShapeId)
	  .value("SceneObjectId",GLRenderer::SceneObjectId)
	  .export_values()
	  ;

}

void export_GLSkelRenderer()
{
	class_< GLSkelRenderer,bases< GLRenderer >,boost::noncopyable >
    ( "GLSkelRenderer", init<SkelComputer& >("GLSkelRenderer(SkelComputer s) An action which displays skeletons of shapes."))
	;
}

void export_GLBBoxRenderer()
{
	class_< GLBBoxRenderer,bases< GLRenderer >,boost::noncopyable >
    ( "GLBBoxRenderer", init<BBoxComputer& >("GLBBoxRenderer(BBoxComputer b) An action which displays bounding boxes of shapes."))
	;
}

AppearancePtr get_default_app() { return GLCtrlPointRenderer::DEFAULT_APPEARANCE; }
void set_default_app(AppearancePtr p) { GLCtrlPointRenderer::DEFAULT_APPEARANCE = p; }

void export_GLCtrlPointRenderer()
{
	class_< GLCtrlPointRenderer,bases< GLRenderer >,boost::noncopyable >
    ( "GLCtrlPointRenderer", init<Discretizer& >("GLCtrlPointRenderer(Discretizer d) An action which display the Control Points of Geometry objects."))
	.add_static_property("DEFAULT_APPEARANCE",&get_default_app,&set_default_app)
	;
}

/* ----------------------------------------------------------------------- */
