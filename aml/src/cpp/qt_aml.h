

#ifndef __qt_aml_h__
#define __qt_aml_h__

/* ----------------------------------------------------------------------- */

#include <qmainwindow.h>
#include <iostream>

class QAmlWidget;


/* ----------------------------------------------------------------------- */

class QAml : public QMainWindow {
	Q_OBJECT

public :

	QAml();
	~QAml();

public slots :

	validateCommand();
	readOutput();

protected :

    virtual void resizeEvent( QResizeEvent * event); 
	virtual void customEvent(QCustomEvent *e);

	QAmlWidget * __widget;

};

/* ----------------------------------------------------------------------- */

std::ostream * qtOuput();
bool qtInputLine(char * buff, int maxlength);

/* ----------------------------------------------------------------------- */

#endif