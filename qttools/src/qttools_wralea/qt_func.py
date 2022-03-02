from PyQt4.QtGui import QTextEdit

def text_edit () :
	w = QTextEdit()
	w.setMinimumSize(400,600)
	w.setWindowTitle("display txt")
	w.show()
	return w,

def append_txt (viewer, txt) :
	viewer.append(str(txt) )
	return viewer
