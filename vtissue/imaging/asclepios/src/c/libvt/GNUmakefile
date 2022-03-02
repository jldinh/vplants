#
# $Id: GNUmakefile,v 1.9 2002/12/11 12:03:59 greg Exp $
#
# /u/cajal/0/greg/src/libvt/common
#
#

ETCDIR=../make/
include ${ETCDIR}/GNUmakefile.vars # variables par defaut

CREATE_DIRS=TRUE
DO_NOT_CHECK_DISTANT_OBJS=TRUE
ALLWAYS_UPDATE_DEPEND=FALSE

CPPFLAGS += -D_$(MYCPU)_ -D_ANSI_ -UNO_PROTO

IFLAGS += -I../libvt/ -I../libbasic/
# LDPATH += -L../libvt/lib/$(INTERNECPU)$(INTERNEOS) -L../libbasic/lib/$(INTERNECPU)$(INTERNEOS)
# LDLIBS += -lbasic -lm

IFLAGS += -I../libio/
# LDPATH += -L../libio/lib/$(INTERNECPU)$(INTERNEOS)
# LDLIBS += -lio

CC=gcc
# CFLAGS += -fbounds-checking


FILES = vt_3m.c \
	vt_bytes.c \
	vt_connexe.c \
	vt_copy.c \
	vt_error.c \
	vt_getval.c \
	vt_histo.c \
	vt_image.c \
	vt_inrimage.c \
	vt_morpho.c \
	vt_names.c \
	vt_reech.c \
	vt_seuil.c \
	vt_unix.c


HEADERS = vt_3m.h \
	vt_bytes.h \
	vt_common.h \
	vt_connexe.h \
	vt_copy.h \
	vt_error.h \
	vt_getval.h \
	vt_histo.h \
	vt_image.h \
	vt_inrimage.h \
	vt_morpho.h \
	vt_names.h \
	vt_reech.h \
	vt_seuil.h \
	vt_typedefs.h \
	vt_unix.h


LIB=libvt.a



IFLAGS += -I../libbasic
CPPFLAGS += -D_ANSI_ -UNO_PROTO


IFLAGS += -I../libio/
LDPATH += -L../libio/lib/$(INTERNECPU)$(INTERNEOS)
LDLIBS += -lio

#IFLAGS += -I/u/cajal/0/greg/include
#IFLAGS += -I.
EPIDAURE = /proj/epidaure/home/
#EPIDAURE2 = ${HOME}/NEWSRC-EPIDAURE
CPPFLAGS += -DLIBINRIMAGE
# CPPFLAGS += -DNOZLIB
# IFLAGS += -I${EPIDAURE2}/yav++/lib/libInrimage/src/
#IFLAGS += -I${HOME}/Mips/src/AuxPkgs/Baladin/Image
# IFLAGS += -I/user/greg/home/NEWSRC-EPIDAURE/yav++/lib/libInrimage/src/
# IFLAGS += -I${EPIDAURE}/include
# LDPATH += -L$(EPIDAURE2)/yav++/lib/libInrimage/src/$(LIBDIR)
#LDPATH += -L${HOME}/Mips/src/AuxPkgs/Baladin/Image/$(LIBDIR)
#LDPATH += -L$(EPIDAURE)/lib
#LDLIBS += -lio -lpng
LDLIBS += -lz



INSTALLLIBDIR = ${HOME}/${LIBDIR}
INSTALLHEADERSDIR = ${HOME}/include

include ${ETCDIR}/GNUmakefile.rules 
