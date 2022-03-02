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

/*! \file view_event.h
    \brief Definition of the viewer class events.
*/

#ifndef __view_event_h__
#define __view_event_h__

/* ----------------------------------------------------------------------- */

#include <QtCore/QEvent>
#include <QtGui/QColor>
#include <QtCore/qstringlist.h>
#include <vector>
#include "../gui_config.h"
#include <plantgl/math/util_vector.h>
#include "flags.h"

#ifdef QT_THREAD_SUPPORT
#include <QtCore/qthread.h>
#endif

TOOLS_USING(Vector3)

/* ----------------------------------------------------------------------- */

class VIEW_API ViewEvent : public QEvent {
public:
	enum Type {
		eFirstEvent = 10000,
		eNoneEvent = eFirstEvent,
		eFileChange,
		eImageSave,
		eRefresh,
		eGetSelection,
		eSetSelection,
		eWaitSelection,
		eGetRedrawPolicy,
		eSetRedrawPolicy,
		eShow,
		eEnd,
		eFullScreen,
		eGLFrameOnly,
		eShowMessage,
		eQuestion,
		eItemSelection,
		eFileSelection,
		eDoubleSelection,
		eAnimation,
		eBgColor,
		ePos,
		eGrid,
        eLightSet,
        eLightGet,
		eCameraSet,
		eCameraGet,
		eClippingPlaneActivate,
		eClippingPlaneSet,
		eRayBuff,
		eZBuff,
		eProjSize,
		eCameraProj,
		eSceneChange,
		eSetAborter,
		eLastEvent
	} ;




  ViewEvent(int type = eNoneEvent);

  virtual ~ViewEvent();

  bool sent_event;

};

struct void_ { typedef void_ type; };

#define ARGHOLDER(NUM) \
	template<typename T> class Arg##NUM##Holder { \
	public: \
	Arg##NUM##Holder(const T& v) : arg##NUM(v) {} \
	T arg##NUM; }; \
	template<> class Arg##NUM##Holder<void_> { };


ARGHOLDER(1)
ARGHOLDER(2)
ARGHOLDER(3)
ARGHOLDER(4)
ARGHOLDER(5)
ARGHOLDER(6)
ARGHOLDER(7)
ARGHOLDER(8)


template <int TEventType, typename ReturnType = int, typename Arg1 = void_, 
		  typename Arg2 = void_, typename Arg3 = void_, typename Arg4 = void_, 
		  typename Arg5 = void_, typename Arg6 = void_, typename Arg7 = void_, typename Arg8 = void_>
class TViewEvent : public ViewEvent, public Arg1Holder<Arg1>, public Arg2Holder<Arg2>, 
				   public Arg3Holder<Arg3>, public Arg4Holder<Arg4>, 
				   public Arg5Holder<Arg5>, public Arg6Holder<Arg6>, 
				   public Arg7Holder<Arg7>, public Arg8Holder<Arg8>  {
public:
	TViewEvent(ReturnType* _result, const Arg1& arg1,
			   const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5, 
			   const Arg6& arg6, const Arg7& arg7, 
			   const Arg8& arg8):
		ViewEvent(TEventType),  result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4),
		Arg5Holder<Arg5>(arg5), Arg6Holder<Arg6>(arg6),
		Arg7Holder<Arg7>(arg7), Arg8Holder<Arg8>(arg8){}

	TViewEvent(ReturnType* _result, const Arg1& arg1,
			   const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5, 
			   const Arg6& arg6, const Arg7& arg7):
		ViewEvent(TEventType),  result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4),
		Arg5Holder<Arg5>(arg5), Arg6Holder<Arg6>(arg6),
		Arg7Holder<Arg7>(arg7){}

	TViewEvent(ReturnType* _result, const Arg1& arg1,
			   const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5, const Arg6& arg6):
		ViewEvent(TEventType),  result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4),
		Arg5Holder<Arg5>(arg5), Arg6Holder<Arg6>(arg6){}

	TViewEvent(ReturnType* _result, const Arg1& arg1,
			   const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5):
		ViewEvent(TEventType),  result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4),
		Arg5Holder<Arg5>(arg5) {}

	TViewEvent(ReturnType* _result, const Arg1& arg1,
			   const Arg2& arg2,    const Arg3& arg3,
			   const Arg4& arg4):
		ViewEvent(TEventType),  result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4) {}

	TViewEvent(ReturnType* _result, const Arg1& arg1,
			   const Arg2& arg2,    const Arg3& arg3):
		ViewEvent(TEventType),result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3) {}

	TViewEvent(ReturnType* _result,  const Arg1& arg1,
			   const Arg2& arg2):
		ViewEvent(TEventType),result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2) {}

	TViewEvent(ReturnType* _result, const Arg1& arg1):
		ViewEvent(TEventType),result(_result),
		Arg1Holder<Arg1>(arg1){}

	TViewEvent(ReturnType* _result):
		ViewEvent(TEventType),result(_result) {}

        ReturnType * result;
};

template <int TEventType, typename Arg1 = void_, 
          typename Arg2 = void_, typename Arg3 = void_, 
		  typename Arg4 = void_, typename Arg5 = void_,
		  typename Arg6 = void_, typename Arg7 = void_,
		  typename Arg8 = void_>
class TPViewEvent : public ViewEvent, public Arg1Holder<Arg1>, 
				   public Arg2Holder<Arg2>, public Arg3Holder<Arg3>, 
				   public Arg4Holder<Arg4>, public Arg5Holder<Arg5>, 
				   public Arg6Holder<Arg6>, public Arg7Holder<Arg7>, 
				   public Arg8Holder<Arg8> {
public:
	TPViewEvent(const Arg1& arg1, const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5, const Arg6& arg6,
			   const Arg7& arg7, const Arg8& arg8):
		ViewEvent(TEventType),  Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4), Arg5Holder<Arg5>(arg5),
		Arg6Holder<Arg6>(arg6), Arg7Holder<Arg7>(arg7), Arg8Holder<Arg8>(arg8){}

	TPViewEvent(const Arg1& arg1, const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5, const Arg6& arg6,
			   const Arg7& arg7):
		ViewEvent(TEventType),  Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4), Arg5Holder<Arg5>(arg5),
		Arg6Holder<Arg6>(arg6), Arg7Holder<Arg7>(arg7){}

	TPViewEvent(const Arg1& arg1, const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5, const Arg6& arg6):
		ViewEvent(TEventType),  Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4), Arg5Holder<Arg5>(arg5),
		Arg6Holder<Arg6>(arg6){}

	TPViewEvent(const Arg1& arg1, const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5):
		ViewEvent(TEventType),  Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4), Arg5Holder<Arg5>(arg5) {}

	TPViewEvent(const Arg1& arg1, const Arg2& arg2, const Arg3& arg3, const Arg4& arg4):
		ViewEvent(TEventType),  Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4){}

	TPViewEvent(const Arg1& arg1, const Arg2& arg2, const Arg3& arg3):
		ViewEvent(TEventType), Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3) {}

	TPViewEvent(const Arg1& arg1, const Arg2& arg2):
		ViewEvent(TEventType), Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2){}

	TPViewEvent(const Arg1& arg1):
		ViewEvent(TEventType), Arg1Holder<Arg1>(arg1){}

	TPViewEvent():
		ViewEvent(TEventType) {}

};


/**
   \class ViewSceneChangeEvent
   \brief An event to pass to glframe for changing scene.

*/

/* ----------------------------------------------------------------------- */

class VIEW_API ViewGeomEvent : public ViewEvent {
public:
	enum GeomEventType {
		eFirstGeomEvent = ViewEvent::eLastEvent,
		eGetScene = eFirstGeomEvent,
		eProjList,
		eIntegratedProjList,
		eRayBuff2,
		eLastGeomEvent
	};

	ViewGeomEvent(int type):ViewEvent(type){}
	virtual ~ViewGeomEvent(){}

};


template <int TEventType, typename ReturnType = int, typename Arg1 = void_, 
		  typename Arg2 = void_, typename Arg3 = void_, typename Arg4 = void_, 
		  typename Arg5 = void_, typename Arg6 = void_, typename Arg7 = void_, typename Arg8 = void_>
class TViewGeomEvent : public ViewGeomEvent, public Arg1Holder<Arg1>, public Arg2Holder<Arg2>, 
				   public Arg3Holder<Arg3>, public Arg4Holder<Arg4>, 
				   public Arg5Holder<Arg5>, public Arg6Holder<Arg6>, 
				   public Arg7Holder<Arg7>, public Arg8Holder<Arg8>  {
public:
	TViewGeomEvent(ReturnType* _result, const Arg1& arg1,
			   const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5, 
			   const Arg6& arg6, const Arg7& arg7, 
			   const Arg8& arg8):
		ViewGeomEvent(TEventType),  result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4),
		Arg5Holder<Arg5>(arg5), Arg6Holder<Arg6>(arg6),
		Arg7Holder<Arg7>(arg7), Arg8Holder<Arg8>(arg8){}

	TViewGeomEvent(ReturnType* _result, const Arg1& arg1,
			   const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5, 
			   const Arg6& arg6, const Arg7& arg7):
		ViewGeomEvent(TEventType),  result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4),
		Arg5Holder<Arg5>(arg5), Arg6Holder<Arg6>(arg6),
		Arg7Holder<Arg7>(arg7){}

	TViewGeomEvent(ReturnType* _result, const Arg1& arg1,
			   const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5, const Arg6& arg6):
		ViewGeomEvent(TEventType),  result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4),
		Arg5Holder<Arg5>(arg5), Arg6Holder<Arg6>(arg6){}

	TViewGeomEvent(ReturnType* _result, const Arg1& arg1,
			   const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5):
		ViewGeomEvent(TEventType),  result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4),
		Arg5Holder<Arg5>(arg5) {}

	TViewGeomEvent(ReturnType* _result, const Arg1& arg1,
			   const Arg2& arg2,    const Arg3& arg3,
			   const Arg4& arg4):
		ViewGeomEvent(TEventType),  result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4) {}

	TViewGeomEvent(ReturnType* _result, const Arg1& arg1,
			   const Arg2& arg2,    const Arg3& arg3):
		ViewGeomEvent(TEventType),result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3) {}

	TViewGeomEvent(ReturnType* _result,  const Arg1& arg1,
			   const Arg2& arg2):
		ViewGeomEvent(TEventType),result(_result),
		Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2) {}

	TViewGeomEvent(ReturnType* _result, const Arg1& arg1):
		ViewGeomEvent(TEventType),result(_result),
		Arg1Holder<Arg1>(arg1){}

	TViewGeomEvent(ReturnType* _result):
		ViewGeomEvent(TEventType),result(_result) {}

        ReturnType * result;
};

template <int TEventType, typename Arg1 = void_, 
          typename Arg2 = void_, typename Arg3 = void_, 
		  typename Arg4 = void_, typename Arg5 = void_,
		  typename Arg6 = void_, typename Arg7 = void_,
		  typename Arg8 = void_>
class TPViewGeomEvent : public ViewGeomEvent, public Arg1Holder<Arg1>, 
				   public Arg2Holder<Arg2>, public Arg3Holder<Arg3>, 
				   public Arg4Holder<Arg4>, public Arg5Holder<Arg5>, 
				   public Arg6Holder<Arg6>, public Arg7Holder<Arg7>, 
				   public Arg8Holder<Arg8> {
public:
	TPViewGeomEvent(const Arg1& arg1, const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5, const Arg6& arg6,
			   const Arg7& arg7, const Arg8& arg8):
		ViewGeomEvent(TEventType),  Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4), Arg5Holder<Arg5>(arg5),
		Arg6Holder<Arg6>(arg6), Arg7Holder<Arg7>(arg7), Arg8Holder<Arg8>(arg8){}

	TPViewGeomEvent(const Arg1& arg1, const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5, const Arg6& arg6,
			   const Arg7& arg7):
		ViewGeomEvent(TEventType),  Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4), Arg5Holder<Arg5>(arg5),
		Arg6Holder<Arg6>(arg6), Arg7Holder<Arg7>(arg7){}

	TPViewGeomEvent(const Arg1& arg1, const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5, const Arg6& arg6):
		ViewGeomEvent(TEventType),  Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4), Arg5Holder<Arg5>(arg5),
		Arg6Holder<Arg6>(arg6){}

	TPViewGeomEvent(const Arg1& arg1, const Arg2& arg2, const Arg3& arg3,
			   const Arg4& arg4, const Arg5& arg5):
		ViewGeomEvent(TEventType),  Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4), Arg5Holder<Arg5>(arg5) {}

	TPViewGeomEvent(const Arg1& arg1, const Arg2& arg2, const Arg3& arg3, const Arg4& arg4):
		ViewGeomEvent(TEventType),  Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3), Arg4Holder<Arg4>(arg4){}

	TPViewGeomEvent(const Arg1& arg1, const Arg2& arg2, const Arg3& arg3):
		ViewGeomEvent(TEventType), Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2),
		Arg3Holder<Arg3>(arg3) {}

	TPViewGeomEvent(const Arg1& arg1, const Arg2& arg2):
		ViewGeomEvent(TEventType), Arg1Holder<Arg1>(arg1), Arg2Holder<Arg2>(arg2){}

	TPViewGeomEvent(const Arg1& arg1):
		ViewGeomEvent(TEventType), Arg1Holder<Arg1>(arg1){}

	TPViewGeomEvent():
		ViewGeomEvent(TEventType) {}

};


/* ----------------------------------------------------------------------- */

class VIEW_API ViewSceneChangeEvent : public ViewEvent {

  public :

  /// Constructor.
  ViewSceneChangeEvent(int type = 0);

  /// Destructor.
  ~ViewSceneChangeEvent();

  /// copy object.
  virtual ViewSceneChangeEvent * copy();

  const int& getSceneType() const;

protected:
  void setSceneType(const int& i);

private:

  int scene_type;
};

/* ----------------------------------------------------------------------- */


typedef TPViewEvent<ViewEvent::eFileChange,QString> ViewFileChangeEvent;
typedef TPViewEvent<ViewEvent::eImageSave,QString,QString,bool> ViewImageSaveEvent;
typedef TPViewEvent<ViewEvent::eRefresh> ViewRefreshEvent;
typedef TViewEvent<ViewEvent::eGetSelection,std::vector<uint_t> > ViewSelectRecoverEvent;
typedef TPViewEvent<ViewEvent::eSetSelection,std::vector<uint_t> > ViewSelectionSet;
typedef TViewEvent<ViewEvent::eWaitSelection,uint_t,QString> ViewWaitSelection;
typedef TPViewEvent<ViewEvent::eEnd> ViewEndEvent;
typedef TPViewEvent<ViewEvent::eShow> ViewShowEvent;
typedef TPViewEvent<ViewEvent::eFullScreen,bool> ViewFullScreenEvent;
typedef TPViewEvent<ViewEvent::eGLFrameOnly,bool> ViewGLFrameOnlyEvent;
typedef TPViewEvent<ViewEvent::eShowMessage,QString,int> ViewShowMessageEvent;
typedef TViewEvent<ViewEvent::eQuestion,int,QString,QString,QString,QString,QString> ViewQuestionEvent;
typedef TViewEvent<ViewEvent::eItemSelection,QString,QString,QString,QStringList,bool,bool *> ViewItemSelectionEvent;
typedef TViewEvent<ViewEvent::eDoubleSelection,double,QString,QString,double,double,double,bool *> ViewDoubleSelectionEvent;
typedef TViewEvent<ViewEvent::eFileSelection,QString,QString,QString,QString,bool,bool> ViewFileSelEvent;
typedef TPViewEvent<ViewEvent::eAnimation,eAnimationFlag> ViewAnimationEvent;
typedef TPViewEvent<ViewEvent::eBgColor,QColor> ViewBgColorEvent;
typedef TPViewEvent<ViewEvent::eGrid,bool,bool,bool,bool,int,int,int> ViewGridEvent;
typedef TPViewEvent<ViewEvent::eCameraSet,Vector3,Vector3,float,float,int> ViewCameraSetEvent;
typedef TViewEvent<ViewEvent::eCameraGet,Vector3,Vector3*,Vector3*> ViewCameraGetEvent;
typedef TPViewEvent<ViewEvent::eClippingPlaneActivate,int,bool> ViewCPActivateEvent;
typedef TPViewEvent<ViewEvent::eClippingPlaneSet,int,double,double,double,double> ViewCPSetEvent;
typedef TPViewEvent<ViewEvent::ePos,int,int,int,int,int> ViewPosEvent;
class ViewRayBuffer;
typedef TViewEvent<ViewEvent::eRayBuff,ViewRayBuffer *,Vector3,Vector3,Vector3,Vector3,int,int> ViewRayBuffEvent;
class ViewZBuffer;
typedef TViewEvent<ViewEvent::eZBuff,ViewZBuffer *> ViewZBuffEvent;
typedef TViewEvent<ViewEvent::eProjSize,double,int *,double *> ViewProjSizeEvent;
typedef TPViewEvent<ViewEvent::eCameraProj,bool> ViewCameraProjEvent;
typedef TPViewEvent<ViewEvent::eSetRedrawPolicy,bool> ViewSetRedrawEvent;
typedef bool (*DialogAborterFunc)();
typedef TPViewEvent<ViewEvent::eSetAborter,DialogAborterFunc> ViewSetAborterEvent;
typedef TViewEvent<ViewEvent::eGetRedrawPolicy,bool> ViewGetRedrawEvent;



/* ----------------------------------------------------------------------- */

class ViewLightSetEvent : public ViewEvent {

public :
    enum eLightAttribute {
        ePosition,
        eAmbient,
        eDiffuse,
        eSpecular,
        eActivation
    } ;

  /// Constructor.
  ViewLightSetEvent(const Vector3& pos,
                    QColor ambient,
                    QColor diffuse,
                    QColor specular,
                    bool activation,
                    eLightAttribute def);

  /// Destructor.
  ~ViewLightSetEvent();

  Vector3 position;
  QColor ambient;
  QColor diffuse;
  QColor specular;
  bool activation;
  eLightAttribute def;
};

/* ----------------------------------------------------------------------- */
class ViewLightGetEvent : public ViewEvent {

public :

  /// Constructor.
  ViewLightGetEvent(Vector3* pos = NULL,
                    QColor* ambient = NULL,
                    QColor* diffuse = NULL,
                    QColor* specular = NULL,
                    bool* activation = NULL,
                    ViewLightSetEvent::eLightAttribute def = ViewLightSetEvent::ePosition);

  /// Destructor.
  ~ViewLightGetEvent();

  Vector3* position;
  QColor* ambient;
  QColor* diffuse;
  QColor* specular;
  bool* activation;
  ViewLightSetEvent::eLightAttribute def;
};

/* ----------------------------------------------------------------------- */

/* ----------------------------------------------------------------------- */


/* ----------------------------------------------------------------------- */

#endif

