

/* ----------------------------------------------------------------------- */

#include <qlistview.h>
#include <qlabel.h>
#include <qtabwidget.h>
#include <qapplication.h>
#include <qthread.h>
#include <qpushbutton.h>
#include <qlineedit.h>
#include <qmultilineedit.h>

#include <iostream>
#include <strstream>

using namespace std;

#include "qt_aml.h"
#include "qaml.h"

/* ----------------------------------------------------------------------- */

int MAX_LENGTH = 10000;

QWaitCondition __wait;
QString input;
char * output;
std::ostrstream * outputstream;


class QOutputEvent : public QCustomEvent{
public:
	QOutputEvent() : QCustomEvent(18888) {};
};

/* ----------------------------------------------------------------------- */

QAml::QAml() :
QMainWindow(){
	__widget = new QAmlWidget(this);
	resize(860,580);
	__widget->ListObjects->clear();
	QObject::connect(__widget->ExecButton,SIGNAL(pressed()),this,SLOT(validateCommand()));
	QObject::connect(__widget->ShellCommand,SIGNAL(returnPressed()),this,SLOT(validateCommand()));
}

QAml::~QAml()
{
}


QAml::readOutput(){
	if(outputstream){
		if(output[0] != '\0'){
		 *outputstream << ends;
		 char * buff = new char [MAX_LENGTH];
		 buff = strncpy(buff,output,MAX_LENGTH);
		 QMultiLineEdit * shell = __widget->ShellEdit;
		 shell->append(QString(buff));
		 int nl = shell->numLines();
		 shell->setCursorPosition(nl,0);
		 delete buff;
		 outputstream->seekp(0);
	     output[0] = '\0'; 
		}
	}
}

QAml::validateCommand(){
	QMultiLineEdit * shell = __widget->ShellEdit;
	shell->append("AML> "+__widget->ShellCommand->text());
	int nl = shell->numLines();
    shell->setCursorPosition(nl,0);
	input = __widget->ShellCommand->text();
	__widget->ShellCommand->clear();
	__wait.wakeAll();
}


void QAml::resizeEvent( QResizeEvent * event){
  if(isVisible()){
    int x = event->size().width() - event->oldSize().width();
    int y = event->size().height() - event->oldSize().height();
	__widget->resize(__widget->size()+QSize(x,y));
    __widget->Prompt->move(__widget->Prompt->pos()+QPoint(0,y));
    __widget->ExecButton->move(__widget->ExecButton->pos()+QPoint(x,y));
    __widget->ShellCommand->move(__widget->ShellCommand->pos()+QPoint(0,y));
    __widget->ShellCommand->resize(__widget->ShellCommand->size()+QSize(x,0));

    __widget->FilesEditTab->resize(__widget->FilesEditTab->size()+QSize(x,y/2));
    __widget->FileEdit->resize(__widget->FileEdit->size()+QSize(x,y/2));
    __widget->ObjectsTab->resize(__widget->ObjectsTab->size()+QSize(0,y));

    __widget->ShellEdit->move(__widget->ShellEdit->pos()+QPoint(0,y/2));
    __widget->ShellEdit->resize(QSize(x+__widget->ShellEdit->width(),__widget->ExecButton->y()-__widget->ShellEdit->y()));

  }
}

void QAml::customEvent(QCustomEvent *e){
	if(e->type() == 18888)readOutput();
}


/* ----------------------------------------------------------------------- */


class AmlThread : public QThread {
	
public :
	AmlThread():QThread(),
    __appli(0),
    __aml(0){
		start();
	}

protected :

  /// Returning from this method will end execution of the thread.
  virtual void run(){
	  int argc = 0;
	  char ** argv = NULL;
	__appli = new QApplication(argc,argv);
	__aml = new QAml;
	__appli->setMainWidget(__aml);
    __aml->show();
    __appli->exec();
	__wait.wakeAll();
  }


public:

	QApplication * __appli;
	QAml * __aml;
};

AmlThread * AML = NULL;

/* ----------------------------------------------------------------------- */


std::ostream * qtOuput() {
	if(outputstream == NULL) {
		output = new char[MAX_LENGTH];
		outputstream = new std::ostrstream(output,MAX_LENGTH);
	}
	return outputstream;
}

bool qtInputLine(char * buff, int maxlength){
	if(AML == NULL){
		AML = new AmlThread;
	}
	else {
		QOutputEvent * e = new QOutputEvent;
		QThread::postEvent(AML->__aml,e);
	}
	if(AML != NULL && !(AML->running()))return false;
	__wait.wait();
	if(AML != NULL && !(AML->running()))return false;
	if(!input.isEmpty())
	   buff = strncpy (buff,input.latin1(),maxlength);
	return true;
}

/* ----------------------------------------------------------------------- */
