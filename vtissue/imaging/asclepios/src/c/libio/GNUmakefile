ETCDIR=../make
include ${ETCDIR}/GNUmakefile.vars # variables par defaut

CREATE_DIRS=TRUE
DO_NOT_CHECK_DISTANT_OBJS=TRUE
ALLWAYS_UPDATE_DEPEND=FALSE

CPPFLAGS += -D_$(MYCPU)_ -D_ANSI_ -UNO_PROTO

CC=gcc

FILES = analyze.c \
	bmp.c \
	bmpendian.c \
	bmpread.c \
	gif.c \
	gis.c \
	ImageIO.c \
	inr.c \
	iris.c \
	mincio.c \
	pnm.c

HEADERS = analyze.h \
	bmpendian.h \
	bmp.h \
	bmpread.h \
	bmptypes.h \
	gif.h \
	gis.h \
	inr.h \
	iris.h \
	mincio.h \
	pnm.h


LIB = libio.a

exec :
	$(MAKE) $(EXECS)

INSTALLBINDIR = $(HOME)/$(BINDIR)
INSTALLHEADERSDIR = ${HOME}/include

include ${ETCDIR}/GNUmakefile.rules 
