#
# $Id: GNUmakefile,v 1.32 2002/09/27 08:34:10 greg Exp $
#
# /u/cajal/0/greg/src/libbasic/reech
#
# ETCDIR=/u/epidaure/2/epicode/make/

ETCDIR=../make
include ${ETCDIR}/GNUmakefile.vars # variables par defaut

CREATE_DIRS=TRUE
DO_NOT_CHECK_DISTANT_OBJS=TRUE
ALLWAYS_UPDATE_DEPEND=FALSE

CPPFLAGS += -D_$(MYCPU)_ -D_ANSI_ -UNO_PROTO

CC=gcc
# CFLAGS += -fbounds-checking

# templates pour le reechantillonage
include GNUmakefile.reech
# templates pour la morphologie mathematique
include GNUmakefile.morpho




FILES = convert.c \
	cspline.c \
	extrema.c \
	morpho.c \
	morphotools.c \
	recbuffer.c \
	recline.c \
	reech4x4.c \
	reech-def.c \
	regionalmax.c \
	watershed.c \
	zcross.c

HEADERS = convert.h \
	cspline.h \
	extrema.h \
	morpho.h \
	morphotools.h \
	recbuffer.h \
	recline.h \
	reech4x4.h \
	reech-def.h \
	regionalmax.h \
	typedefs.h \
	watershed.h \
	zcross.h

LIB=libbasic.a


rmtmp : 
	rm -f ${REECH_FILES} ${MORPHO_FILES}



INSTALLLIBDIR=${HOME}/${LIBDIR}
INSTALLHEADERSDIR=${HOME}/include

include ${ETCDIR}/GNUmakefile.rules 
