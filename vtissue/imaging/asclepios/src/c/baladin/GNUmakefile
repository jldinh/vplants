#
# $Id: GNUmakefile,v 1.19 2006/04/14 08:37:38 greg Exp $
#
# /u/cajal/0/greg/src/vt-exec
#

ETCDIR=../make
include ${ETCDIR}/GNUmakefile.vars # variables par defaut

CREATE_DIRS=TRUE
DO_NOT_CHECK_DISTANT_OBJS=TRUE
ALLWAYS_UPDATE_DEPEND=FALSE

CPPFLAGS += -D_$(MYCPU)_ -D_ANSI_ -UNO_PROTO

IFLAGS += -I../libbasic/
LDPATH += -L../libbasic/lib/$(INTERNECPU)$(INTERNEOS)
LDLIBS += -lbasic -lm

IFLAGS += -I../libio/
LDPATH += -L../libio/lib/$(INTERNECPU)$(INTERNEOS)
LDLIBS += -lio

CC=gcc
# CFLAGS += -fbounds-checking


EXECS = baladin

FILES = balimage.c \
	estimateur.c \
	initialisation.c \
	matrix.c \
	mesure.c \
	py_image.c \
	vecteur.c

LIB = libbaladin.a

LDLIBS += -lz

exec :
	$(MAKE) $(EXECS)

INSTALLBINDIR = $(HOME)/$(BINDIR)

include ${ETCDIR}/GNUmakefile.rules 
