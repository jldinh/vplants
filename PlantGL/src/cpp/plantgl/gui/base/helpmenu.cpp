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
 *                      GNU General Public license
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

#include <QtCore/qstring.h>
#include <QtGui/qmessagebox.h>
#include <QtGui/qapplication.h> 
#include <QtGui/qdesktopwidget.h> 
#include <QtGui/qlabel.h>
#include <QtGui/qpainter.h>

// #include <Qt3Support/q3listview.h> 
// #include <Qt3Support/q3textbrowser.h>
#include <QtGui/QTreeWidgetItem>
#include <QtGui/qtextbrowser.h>
#include <QtCore/qfile.h>
#include <QtCore/qfileinfo.h>
#include <QtCore/qtextstream.h>
#include <QtCore/qurl.h>
#include <QtGui/qevent.h>
#include <plantgl/tool/util_enviro.h>

/*  ------------------------------------------------------------------------ */


#include <QtGui/QStyle>
#include <QtGui/qstylefactory.h>


/*  ------------------------------------------------------------------------ */

#include "icons.h"

#include "helpmenu.h"
#include "info.h"
#include "qobjectbrowser.h"
#include "configuration.h"

#include <plantgl/scenegraph/pgl_version.h>

#include <plantgl/algo/codec/scne_scanner.h>
#include <plantgl/algo/codec/binaryprinter.h>
#include <plantgl/gui/viewer/geomscenegl.h>
#include <plantgl/tool/util_enviro.h>

PGL_USING_NAMESPACE
using namespace std;



static QString default_style_name;

ViewHelpMenu::ViewHelpMenu(QWidget * parent, QGLWidget * glwidget, const char * name) :
  QMenu(parent),
  __glwidget(glwidget)
{
	if(name) setObjectName(name);
	__about = new ViewAboutDialog(this,false);
	QObject::connect(__about,SIGNAL(licenseView()),this,SLOT(showLicense()));
	addAction( tr("What's &This?"), parent->parent() , SLOT(whatsThis()), Qt::Key_F1);
    addAction(QPixmap(ViewSysInfo::tools_logo),tr("&Help"),this,SLOT(showHelp()),Qt::SHIFT+Qt::Key_F1);
    addSeparator();
    addAction(QPixmap(ViewerIcon::getPixmap(ViewerIcon::flower)),tr("&About Viewer"),this,SLOT(showAbout()), Qt::CTRL+Qt::Key_F1);
    addAction(tr("&License"),this,SLOT(showLicense()));
    addAction(QPixmap(ViewSysInfo::qt_logo),tr("About &Qt"),this,SLOT(aboutQt()));
    // addAction(QPixmap(ViewSysInfo::qt_logo),tr("About &QGLViewer"),glwidget,SLOT(aboutQGLViewer()));
    addSeparator();
    addAction(QPixmap(ViewSysInfo::info_logo),tr("Technical Characteristics"),this,SLOT(generalInfo()));
    // addAction(QPixmap(ViewSysInfo::qt_logo),tr("Qt Hierarchy"),this,SLOT(qtbrowse()));
    addSeparator();
    __style = new QMenu(this);
	__style->setTitle(tr("Style"));
	addMenu(__style);
	QStringList styles = QStyleFactory::keys();
	QActionGroup * actiongroup = new QActionGroup(__style);
	actiongroup->setExclusive(true);
    QAction * action = NULL;
	for(uint k = 0 ; k < styles.size(); k++){
	  action = __style->addAction(styles[k]);
	  action->setCheckable(true);
	  actiongroup->addAction(action);
	  __ids.push_back( action );
	}
    __style->addSeparator();
    action = __style->addAction("Default");
	action->setCheckable(true);
	actiongroup->addAction(action);
	__ids.push_back( action );
	default_style_name = QApplication::style()->metaObject()->className();
    checkItem(__ids.size()-1);

    ViewerSettings settings;
    settings.beginGroup("WinStyle");
    QString stylename = settings.value("StyleName","Default").toString();
    settings.endGroup();
    setStyle(stylename);
	QObject::connect(__style,SIGNAL(triggered(QAction *)),this,SLOT(setStyleCorrespondingTo(QAction*)));
}


ViewHelpMenu::~ViewHelpMenu(){
#ifdef  PGL_DEBUG
  cout << "Help Menu deleted" << endl;
#endif
}

void ViewHelpMenu::endEvent()
{
  ViewerSettings settings;
  settings.beginGroup("WinStyle");
  settings.setValue("StyleName",getStyleName());
  settings.endGroup();
}

void 
ViewHelpMenu::setGLWidget(QGLWidget * glwidget)
{
  __glwidget = glwidget;
}

int ViewHelpMenu::getStyle() const {
    QStyle * style = QApplication::style();
    const QMetaObject * mo = style->metaObject();
	for(uint i = 0 ; i < __ids.size() ; i++){
		if((QStyleFactory::create(__ids[i]->text()))->metaObject() == mo)
			return i;
	}
	return -1;
}

QString ViewHelpMenu::getStyleName() const {
	for(uint i = 0 ; i < __ids.size() ; ++i)
		if(__ids[i]->isChecked()) return __ids[i]->text();
	return "Default";
}

int ViewHelpMenu::getStyleId(const QString& name) const {
    int id = QStyleFactory::keys().indexOf(name);
    if (id == -1) return __ids.size() -1;
    else return id;
}

void  
ViewHelpMenu::setStyleCorrespondingTo(QAction * action )
{
    setStyle(action->text());
}

void ViewHelpMenu::setStyle(const QString& name)
{ setStyle(getStyleId(name)); }

void  
ViewHelpMenu::setStyle(int i)
{
	if(i < 0 && i >= __ids.size())return;
    else if (i == __ids.size()-1) QApplication::setStyle( QStyleFactory::create(default_style_name) ); 
    else {
        QApplication::setStyle( QStyleFactory::create(QStyleFactory::keys()[i])); 
        qDebug((QString("Application.setStyle(") + (QStyleFactory::keys()[i]) +')').toAscii().data() ); 
    }
	if(i>= 0 && i <= __ids.size())checkItem(i);
}

void  
ViewHelpMenu::checkItem(int i)
{
  __ids[i]->setChecked(true);
}

void ViewHelpMenu::showHelp()
{
  const char* message ="<h3>How to use Viewer</h3><br>"
    "<p><b>Left button    :</b> Rotation <br>"
    "<b>Right button      :</b> Pan <br>"
    "<b>Middle button     :</b> Zoom <br>"
    "<b>Ctrl + Left click :</b> Pan <br>"
    "<b>Ctrl + Right click :</b> Zoom <br>"
    "<b>Alt + click        :</b> Light <br>"
    "<b>Shift + click     :</b> Selection <br>"
    "<b>x-move</b> -> Azimuth control <br>"
    "<b>y-move</b> -> Elevation control <br></p>";

  QMessageBox::information(this, tr("How to use Viewer"),tr(message));
}


void ViewHelpMenu::showAbout()
{  
  if(!__about)__about = new ViewAboutDialog(this,"About",false);
  __about->display(-1);
}

void ViewHelpMenu::showInit()
{  
  if(!__about)__about = new ViewAboutDialog(this,"About",false);
  __about->display(2000);
}

void ViewHelpMenu::showLicense()
{  
  QDialog b(this,Qt::Tool);
  b.setModal(true);
  QPixmap logo = ViewerIcon::getPixmap( "gnu.png");
  QLabel * llogo = new QLabel(&b);
  llogo->setGeometry(QRect(QPoint(0,0),logo.size()));
  llogo->setPixmap(logo);
  b.setMinimumSize(QSize(logo.width()*4,logo.height()));
  b.setWindowTitle("License");
  QTextBrowser * lictext = new QTextBrowser(&b);
  QFont f("Courrier", 8);
  lictext->setFont( f );
  lictext->setGeometry(QRect(logo.width(),0,logo.width()*3,logo.height()));
  // lictext->setHScrollBarMode(QScrollView::AlwaysOff);
  lictext->setLineWidth(0);
  /* QPalette pal = lictext->palette();
  QColorGroup c = pal.active();
  c.setColor(QColorGroup::Background,QColor(255,255,255));
  pal.setActive(c);
  lictext->setPalette(pal);*/
  QString copyright((TOOLS(getPlantGLDir())+"/share/plantgl/LICENSE").c_str());
  if(QFileInfo(copyright).exists() ) 
	  lictext->setSource(copyright);
  QSize s = qApp->desktop()->size();
  s = s - b.size();
  s /= 2;
  b.move(s.width(),s.height()); 
  b.exec();
}

void 
ViewHelpMenu::setInitText(const QString&t){
  if(!__about)__about = new ViewAboutDialog(this,"About",false);
  __about->setText(t);
}
void 
ViewHelpMenu::setInitText(const QString&t,int timeout)
{
  if(!__about)__about = new ViewAboutDialog(this,"About",false);
  __about->setText(t,timeout);
}


void
ViewHelpMenu::aboutQt()
{
 QMessageBox::aboutQt( this, tr("About Qt") );
}

void
ViewHelpMenu::qtbrowse()
{
  ViewQObjectBrowser a(this,"qtbrowse",TRUE);
  a.exec();
}

void
ViewHelpMenu::generalInfo()
{
  std::string text2 = getPGLVersionString();
  QString text;
  ViewSysInfo a (this,__glwidget,(tr("PlantGL Viewer")+" "+QString(text2.c_str())).toAscii(),true);
  QTreeWidgetItem * itemF = a.addItem(tr("PlantGL Library"));
  QTreeWidgetItem *item = new QTreeWidgetItem( itemF );
  item->setText( 0, tr( "Version" ) );
  item->setText( 1, QString(text2.c_str()) );
  item = new QTreeWidgetItem( itemF, item );
  item->setText( 0, tr( "Binary Format Version" ) );
  item->setText( 1, QString::number(BinaryPrinter::BINARY_FORMAT_VERSION) );
  item = new QTreeWidgetItem( itemF, item );
  item->setText( 0, tr( "Real Type Precision" ) );
#ifdef PGL_USE_DOUBLE
  text = "Double";
#else
  text = "Simple";
#endif
  item->setText( 1, text  );
  item = new QTreeWidgetItem( itemF, item );
  item->setText( 0, tr( "Using Threads" ) );
  if(ViewGeomSceneGL::useThread()) text = "True";
  else text = "False";
  item->setText( 1, tr( text.toAscii() ) );

  item = new QTreeWidgetItem( itemF, item );
  item->setText( 0, tr( "PGL Namespace" ) );
#ifndef PGL_NAMESPACE_NAME
  text = "False";
#else
  text = "True";
#endif
  item->setText( 1, tr( text.toAscii() ) );
  item = new QTreeWidgetItem( itemF, item );
  item->setText( 0, tr( "PGL Debug" ) );
#ifdef PGL_DEBUG
  text = "True";
#else
  text = "False";
#endif
  item->setText( 1, tr( text.toAscii() ) );
#ifdef _WIN32
  item = new QTreeWidgetItem( itemF, item );
  item->setText( 0, tr( "PGL DLLs" ) );
#ifdef VIEW_DLL
  text = "True";
#else
  text = "False";
#endif
  item->setText( 1, tr( text.toAscii() ) );
#endif
  item = new QTreeWidgetItem( itemF, item );
  item->setText( 0, tr( "Using Glut" ) );
#ifdef WITH_GLUT
  text = "True";
#else
  text = "False";
#endif
  item->setText( 1, tr( text.toAscii() ) );
  itemF = a.addItem(tr("Tools Library"));
  item = new QTreeWidgetItem( itemF );
  item->setText( 0, tr( "Tools Namespace" ) );
#ifndef TOOLS_NAMESPACE_NAME
  text = "False";
#else
  text = "True";
#endif
  item->setText( 1, tr( text.toAscii() ) );
  //itemF = a.addItem(tr("PlantGL"));
  //item = new QTreeWidgetItem( itemF );
  //item->setText( 0, tr( "Install Path" ) );
  //string p = TOOLS(getPlantGLDir());
  //if(!p.empty())item->setText( 1, QString(p.c_str()) );
  itemF = a.addItem(tr("Flex"));
  item = new QTreeWidgetItem( itemF );
  item->setText( 0, tr( "Version" ) );
  item->setText( 1, QString(lexerVersion().c_str())  );
  a.exec();
}





ViewAboutDialog::ViewAboutDialog ( QWidget * parent, 
								  const char * name, 
								  int timeout,
								  bool modal):
QDialog ( parent, Qt::Tool ), 
		__text(NULL),
	    __style(true),
		__license(false){
  if(name)setObjectName(name); 
  setModal(modal);
  __logo = ViewerIcon::getPixmap( "geomviewer.png");
  if(__logo.isNull()) {
    __style = false;
    __logo = ViewerIcon::getPixmap( ViewerIcon::plantlogo);
  }
  else {
    __logo2 = ViewerIcon::getPixmap( "geomviewer2.png");
  }
  setIconPixmap(__logo);
  __licenseRect = QRect(140,180,62,110);
  
  QString message =  "License : GNU General Public License (GPL).\n"
    "Developper : F. Boudon, C. Nouguier,\n"
    "C. Pradal, C. Godin -\n"
    "Virtual Plants Team - UMR AMAP\n"
    "N. Dones, B. Adam - UMR PIAF\n"
    "3D Models : F. Boudon, H. Sinoquet\n"
    "Y. Caraglio, F. Danjon";
  if(__style)setInfo(message,QRect(240,190,180,height()-210),7); 
  
  QString message2 =  "Version "+QString(getPGLVersionString().c_str())+
    "\nDate : " __DATE__;
  if(__style)setInfo(message2, QRect(20,220,95,40),7);
  else setInfo(message2, QRect(5,height()-45,80,40),6);

  if(__style){
    __text = new QLabel(this);
    QFont f("Courrier", 7);
    __text->setFont( f );
    __text->setGeometry(QRect(240,height()-25,260,15));

 /*   QPalette pal = __text->palette();
    QColorGroup c = pal.active();
    c.setColor(QColorGroup::Background,QColor(255,255,255));
    pal.setActive(c);
    __text->setPalette(pal); */

    __text->installEventFilter(this);
    QObject::connect(&__timer,SIGNAL(timeout()),__text,SLOT(clear()));
    setText("Initialization ...",800);
  }
};

ViewAboutDialog::~ViewAboutDialog(){}


void ViewAboutDialog::display(int timeout){
  if(timeout != -1)
	QTimer::singleShot(timeout,this,SLOT(hide()));
  show();
}


void ViewAboutDialog::setIconPixmap( const QPixmap & icon){
  QPalette palette;
  palette.setBrush(backgroundRole(), QBrush(icon));
  setPalette(palette);
  setMinimumSize(icon.size());
  setMaximumSize(icon.size());
  QSize s = qApp->desktop()->size();
  s = s - icon.size();
  s /= 2;
  move(s.width(),s.height()); 
}

void ViewAboutDialog::setInfo(const QString& text, QRect r,int s){
  QLabel * _text = new QLabel(this);
  QFont f("Courrier", s);
  _text->setFont( f );
  _text->setGeometry(r);

  /* QPalette pal = _text->palette();
  QColorGroup c = pal.active();
  c.setColor(QColorGroup::Background,QColor(255,255,255));
  pal.setActive(c);
  _text->setPalette(pal); */

  _text->setText(text);
  _text->installEventFilter(this);
}

void ViewAboutDialog::mousePressEvent ( QMouseEvent * e) {
  QPoint p = e->pos();
  if(__style && __licenseRect.contains(p))
	emit licenseView();
  else	if (e->button() ==  Qt::LeftButton) accept();
}

bool ViewAboutDialog::eventFilter( QObject *o, QEvent *e )
{
  if ( e->type() == QEvent::MouseButtonPress ) {
	accept();
  }
  if ( e->type() == QEvent::MouseMove ) { 
	QMouseEvent * m = (QMouseEvent *)e;
	changeLogo(m->pos());
	return QWidget::eventFilter( o, e );
  }
  return QWidget::eventFilter( o, e );    // standard event processing
}

void 
ViewAboutDialog::setText(const QString& t){
  if(__text){
   if(__timer.isActive())__timer.stop();
	__text->setText(t);
  }
}

void 
ViewAboutDialog::setText(const QString& t,int timeout){
  if(__text){
   if(__timer.isActive())__timer.stop();
	__text->setText(t);
	__timer.start(timeout);
  }
}

void 
ViewAboutDialog::clear(){
  if(__text){
   if(__timer.isActive())__timer.stop();
	__text->clear();
  }
}

void 
ViewAboutDialog::showEvent ( QShowEvent * )
{
  setMouseTracking(true);
}

void
ViewAboutDialog::hideEvent ( QHideEvent * )
{
  setMouseTracking(false);
}

void
ViewAboutDialog::mouseMoveEvent ( QMouseEvent * e )
{
	if (e->button() == Qt::NoButton) changeLogo(e->pos());
	else move(e->globalPos());
}

void
ViewAboutDialog::changeLogo(const QPoint& p)
{
  if(__style && !__logo2.isNull()){
//	qDebug("Point = ("+QString::number(p.x())+','+QString::number(p.x())+')');
	if(__license && !__licenseRect.contains(p)){
	  __license = false;
	  QPalette palette;
	  palette.setBrush(backgroundRole(), QBrush(__logo));
	  setPalette(palette);
	}
	else if(!__license && __licenseRect.contains(p)){
	  __license = true;
	  QPalette palette;
	  palette.setBrush(backgroundRole(), QBrush(__logo2));
	  setPalette(palette);
	}
  }
}
