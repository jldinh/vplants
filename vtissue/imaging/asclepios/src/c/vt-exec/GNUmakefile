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

IFLAGS += -I../libvt/ -I../libbasic/
LDPATH += -L../libvt/lib/$(INTERNECPU)$(INTERNEOS) -L../libbasic/lib/$(INTERNECPU)$(INTERNEOS)
LDLIBS += -lvt -lbasic -lm

IFLAGS += -I../libio/
LDPATH += -L../libio/lib/$(INTERNECPU)$(INTERNEOS)
LDLIBS += -lio

CC=gcc
# CFLAGS += -fbounds-checking


EXECS = connexe \
	morpho \
	recfilters \
	reech3d \
	regionalmax \
	watershed \

LDLIBS += -lz

exec :
	$(MAKE) $(EXECS)

INSTALLBINDIR = $(HOME)/$(BINDIR)

include ${ETCDIR}/GNUmakefile.rules 
