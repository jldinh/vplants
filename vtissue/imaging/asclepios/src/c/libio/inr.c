#include "inr.h"

#include <string.h>

/* Magic header for inrimages v4 */
#define INR4_MAGIC "#INRIMAGE-4#{"


/** Magic header for inrimages */
#define INR_MAGIC "#INR"

typedef struct stringListElementStruct {
  char *string;
  struct stringListElementStruct *next;
} stringListElement;
/* list element with a pointer on a string */

typedef struct {
  stringListElement *begin, *end;
} stringListHead;
/* string list descriptor */


static char *fgetns(char *str, int n, _image *im );
/* get a string from a file and discard the ending newline character
   if any */


static void addStringElement(stringListHead *strhead,
			     const char *str);
/* add a string element at the tail of given list */

static void concatStringElement(const stringListHead *strhead,
				const char *str);
/* concat given string at the last element of given list */


/* Writes the given inrimage header in an already opened file.*/
int _writeInrimageHeader(const _image *im, ENDIANNESS end) {
  unsigned int pos, i;
  char type[30], endianness[5], buf[257], scale[20];

  if(im->openMode != OM_CLOSE) {
    /* fix word kind */
    switch(im->wordKind) {

    case WK_FLOAT:
      sprintf(type, "float");
      scale[0] = '\0';
      break;

    case WK_FIXED:
      switch(im->sign) {
      case SGN_SIGNED:
	sprintf(type, "signed fixed");
	break;
      case SGN_UNSIGNED:
	sprintf(type, "unsigned fixed");
	break;
      default:
	return -1;
      }
      sprintf(scale, "SCALE=2**0\n");
      break;
      
    default:
      return -1;
    }
    
    switch(end) {
    case END_LITTLE:
      sprintf(endianness, "decm");
      break;
    case END_BIG:
      sprintf(endianness, "sun");
      break;
    default:
      /* fix architecture endianness */
      if( _getEndianness() == END_LITTLE)
	sprintf(endianness, "decm");
      else
	sprintf(endianness, "sun");
      break;
    }

    /* write header information */
    sprintf(buf, "%s\nXDIM=%i\nYDIM=%i\nZDIM=%i\nVDIM=%d\nTYPE=%s\nPIXSIZE=%i bits\n%sCPU=%s\nVX=%f\nVY=%f\nVZ=%f\n",
	    INR4_MAGIC, im->xdim, im->ydim, im->zdim, im->vdim,
	    type, im->wdim*8, scale, endianness, im->vx, im->vy, im->vz);

    if ( im->cx != 0 ) 
      sprintf(buf+strlen(buf), "XO=%d\n", im->cx );
    if ( im->cy != 0 ) 
      sprintf(buf+strlen(buf), "YO=%d\n", im->cy );
    if ( im->cz != 0 ) 
      sprintf(buf+strlen(buf), "ZO=%d\n", im->cz );
    if ( im->tx != 0.0 ) 
      sprintf(buf+strlen(buf), "TX=%f\n", im->tx );
    if ( im->ty != 0.0 ) 
      sprintf(buf+strlen(buf), "TY=%f\n", im->ty );
    if ( im->tz != 0.0 ) 
      sprintf(buf+strlen(buf), "TZ=%f\n", im->tz );

    if ( im->rx != 0.0 ) 
      sprintf(buf+strlen(buf), "RX=%f\n", im->rx );
    if ( im->ry != 0.0 ) 
      sprintf(buf+strlen(buf), "RY=%f\n", im->ry );
    if ( im->rz != 0.0 ) 
      sprintf(buf+strlen(buf), "RZ=%f\n", im->rz );


    pos = strlen(buf);  
    
    if(ImageIO_write(im, buf, strlen(buf)) == EOF) return -1;
    
    
    /* write user strings */
    if ( im->user != NULL ) {
      for(i = 0; i < im->nuser; i++) {
	if ( im->user[i] == NULL ) continue;
	pos += strlen(im->user[i]) + 2;
	if(ImageIO_write(im, "#", 1) == EOF) return -1;
	if(ImageIO_write(im, im->user[i], strlen(im->user[i])) == EOF) return -1;
	if(ImageIO_write(im, "\n", 1) == EOF) return -1;
      }
    }
    /* write end of header */
    pos = pos % 256;
    if(pos > 252) {
      for(i = pos; i < 256; i++)
	if(ImageIO_write(im, "\n", 1) != 1) return -1;
      pos = 0;
    }
    buf[0] = '\0';
    for(i = pos; i < 252; i++) strcat(buf, "\n");
    strcat(buf, "##}\n");
    
    if(ImageIO_write(im, buf, strlen(buf)) == EOF) return -1;
    else return 1;
  }

  else return -1;
}



/* Writes the given image body in an already opened file.*/
int _writeInrimageData(const _image *im) {
  unsigned long size, nbv, nwrt, i;
  unsigned int v;
  unsigned char **vp;
  
  if(im->openMode != OM_CLOSE) {

    /* scalar or interlaced vectors */
    if(im->vectMode != VM_NON_INTERLACED) {
      size = im->xdim * im->ydim * im->zdim * im->vdim * im->wdim;
      nwrt = ImageIO_write(im, im->data, size);
      if(nwrt != size) return -1;
      else return 1;
    }

    /* non interlaced vectors: interlace for saving */
    else {
      nbv = im->xdim * im->ydim * im->zdim;
      size = im->xdim * im->ydim * im->zdim * im->wdim;
      vp = (unsigned char **) ImageIO_alloc(im->vdim * sizeof(unsigned char *));
      for(v = 0; v < im->vdim; v++)
	vp[v] = (unsigned char *) im->data + v * size;
      for(i = 0; i < nbv; i++)
	for(v = 0; v < im->vdim; v++) {
	  if(ImageIO_write(im, (const void *) vp[v], im->wdim) != im->wdim)
	    return -1;
	  vp[v] += im->wdim;
	}
      ImageIO_free(vp);
      return 1;
    }
  }
  else return -1;
}




/* read header of an opened inrimage */
int readInrimageHeader(const char *fileName,_image *im) {
  char str[257];
  int n, nusr;
  stringListHead strl = { NULL, NULL };
  stringListElement *oel, *el;

  if(im->openMode != OM_CLOSE) {
    /* read image magic number */
    if(!fgetns(str, 257, im )) return -1;
    if(strcmp(str, INR4_MAGIC)) return -1;


    /* while read line does not begin with '#' or '\n', read line
       and decode field */
    if(!fgetns(str, 257, im)) return -1;

    while(str[0] != '#' && str[0] != '\0') {

      if(!strncmp(str, "XDIM=", 5)) {
	if(sscanf(str+5, "%i", &im->xdim) != 1) return -1;
      }
      else if(!strncmp(str, "YDIM=", 5)) {
	if(sscanf(str+5, "%i", &im->ydim) != 1) return -1;
      }
      else if(!strncmp(str, "ZDIM=", 5)) {
	if(sscanf(str+5, "%i", &im->zdim) != 1) return -1;
      }
      else if(!strncmp(str, "VDIM=", 5)) {
	if(sscanf(str+5, "%i", &im->vdim) != 1) return -1;
	if(im->vdim == 1) im->vectMode = VM_SCALAR;
	else im->vectMode = VM_INTERLACED;
      }
      else if(!strncmp(str, "VX=", 3)) {
	if(sscanf(str+3, "%lf", &im->vx) != 1) return -1;
      }
      else if(!strncmp(str, "VY=", 3)) {
	if(sscanf(str+3, "%lf", &im->vy) != 1) return -1;
      }
      else if(!strncmp(str, "VZ=", 3)) {
	if(sscanf(str+3, "%lf", &im->vz) != 1) return -1;
      }
      else if(!strncmp(str, "TYPE=", 5)) {
	if(!strncmp(str+5, "float", 5)) im->wordKind = WK_FLOAT;
	else {
	  if(!strncmp(str+5, "signed fixed", 12)) {
	    im->wordKind = WK_FIXED;
	    im->sign = SGN_SIGNED;
	  }
	  else if(!strncmp(str+5, "unsigned fixed", 14)) {
	    im->wordKind = WK_FIXED;
	    im->sign = SGN_UNSIGNED;
	  }
	  else return -1;
	}
      }
      /* before "sscanf(str+8, "%i %n", &im->wdim, &n) != 1"
	 was used. 
	 However the man said 
         ...
	 n      Nothing is expected; instead, the number of charac?
              ters consumed thus far from  the  input  is  stored
              through  the  next pointer, which must be a pointer
              to int.  This is not a conversion, although it  can
              be  suppressed  with  the  *  flag.  The C standard
              says: `Execution of a %n directive does not  incre?
              ment  the  assignment count returned at the comple?
              tion of execution' but  the  Corrigendum  seems  to
              contradict  this.  Probably  it is wise not to make
              any assumptions on the effect of %n conversions  on
              the return value.
	 ...
	 Thus I change it. It was yielding a RETURN_FAILURE with 
	 insight (GM).
      */
      else if(!strncmp(str, "PIXSIZE=", 8)) {
	if(sscanf(str+8, "%i", &im->wdim) != 1) return -1;
	if(im->wdim != 8 && im->wdim != 16 && im->wdim != 32 &&
	   im->wdim != 64) return -1;
	
	if ( im->wdim <= 9 ) {
	  if(strncmp(str+8+1, " bits", 5)) return -1;
	}
	else if ( im->wdim <= 99 ) {
	  if(strncmp(str+8+2, " bits", 5)) return -1;
	}
	else {
	  return -1;
	}

	im->wdim >>= 3;
      }
      else if(!strncmp(str, "SCALE=", 6)) ;
      else if(!strncmp(str, "CPU=", 4)) {
	if(!strncmp(str+4, "decm", 4)) im->endianness = END_LITTLE;
	else if(!strncmp(str+4, "alpha", 5)) im->endianness = END_LITTLE;
	else if(!strncmp(str+4, "pc", 2)) im->endianness = END_LITTLE;
	else if(!strncmp(str+4, "sun", 3)) im->endianness = END_BIG;
	else if(!strncmp(str+4, "sgi", 3)) im->endianness = END_BIG;
	else return -1;
      }

      else if(!strncmp(str, "XO=", 3)) {
	if(sscanf(str+3, "%d", &im->cx) != 1) return -1;
      }
      else if(!strncmp(str, "YO=", 3)) {
	if(sscanf(str+3, "%d", &im->cy) != 1) return -1;
      }
      else if(!strncmp(str, "ZO=", 3)) {
	if(sscanf(str+3, "%d", &im->cz) != 1) return -1;
      }

      else if(!strncmp(str, "TX=", 3)) {
	if(sscanf(str+3, "%f", &im->tx) != 1) return -1;
      }
      else if(!strncmp(str, "TY=", 3)) {
	if(sscanf(str+3, "%f", &im->ty) != 1) return -1;
      }
      else if(!strncmp(str, "TZ=", 3)) {
	if(sscanf(str+3, "%f", &im->tz) != 1) return -1;
      }
      else if(!strncmp(str, "RX=", 3)) {
	if(sscanf(str+3, "%f", &im->rx) != 1) return -1;
      }
      else if(!strncmp(str, "RY=", 3)) {
	if(sscanf(str+3, "%f", &im->ry) != 1) return -1;
      }
      else if(!strncmp(str, "RZ=", 3)) {
	if(sscanf(str+3, "%f", &im->rz) != 1) return -1;
      }

      if(!fgetns(str, 257, im)) return -1;
    }

    /* parse user strings */
    im->nuser = nusr = 0;
    while(str[0] == '#' && strncmp(str, "##}", 3)) {
      addStringElement(&strl, str + 1);
      while(strlen(str) == 256) {
	if(!fgetns(str, 257, im)) return -1;
	concatStringElement(&strl, str);
      }
      nusr++;
      if(!fgetns(str, 257, im)) return -1;      
    }
    
    /* go to end of header */
    while(strncmp(str, "##}", 3)) {
      if(!fgetns(str, 257, im)) return -1;
    }
    

    /* check header validity */
    if(im->xdim > 0 && im->ydim > 0 && im->zdim > 0 && im->vdim > 0 &&
       im->vx > 0.0 && im->vy > 0.0 && im->vz > 0.0 &&
       (im->wordKind == WK_FLOAT || (im->wordKind == WK_FIXED &&
				     im->sign != SGN_UNKNOWN)) &&
       im->endianness != END_UNKNOWN) {
      if(nusr > 0) {
	im->nuser = nusr;
	im->user = (char **) ImageIO_alloc(im->nuser * sizeof(char *));
	oel = NULL;
	for(el = strl.begin, n = 0; el != NULL; el = oel, n++) {
	  im->user[n] = el->string;
	  oel = el->next;
	  ImageIO_free(el);
	}
      }
      return 0;
    }
    else return -1;

  }
  else return -1;
}



/* add a string element at the tail of given list */
static void addStringElement(stringListHead *strhead, const char *str) {
  stringListElement *el;

  el = (stringListElement *) ImageIO_alloc(sizeof(stringListElement));
  /* was strdup(str); */
  el->string = ImageIO_alloc( strlen(str)+1);
  memcpy(el->string, str,  strlen(str)+1);
  el->next = NULL;
  if(strhead->begin == NULL)
    strhead->begin = strhead->end = el;
  else {
    strhead->end->next = el;
    strhead->end = el;
  }
}

/* get a string from a file and discard the ending newline character
   if any */
static char *fgetns(char *str, int n, _image *im ) {
  char *ret = NULL;
  int l;
  
  ret = ImageIO_gets( im, str, n );
  
  if(!ret) return NULL;

  l = strlen(str);
  if(l > 0 && str[l-1] == '\n') str[l-1] = '\0';
  return ret;
}

/* concat given string at the last element of given list */
static void concatStringElement(const stringListHead *strhead,
				const char *str) {
  stringListElement *el;

  el = strhead->end;
  el->string = (char *) realloc(el->string,
				strlen(el->string) + strlen(str) + 1);
  strcat(el->string, str);
}

int testInrimageHeader(char *magic,const char *name) {
  if (!strcmp(magic, INR_MAGIC))
    return 0;
  else 
    return -1;
}

int writeInrimage(char *name,_image *im) {
  int res;

  _openWriteImage( im, name );

  if(!im->fd) {
    fprintf(stderr, "writeInrimage: error: unable to open file \'%s\'\n", name );
    return ImageIO_OPENING;
  }

  res = _writeInrimageHeader(im, END_UNKNOWN);
  if (res < 0) {
    fprintf(stderr, "writeInrimage: error: unable to write header of \'%s\'\n",
	    name);
    ImageIO_close( im );
    im->fd = NULL;
    im->openMode = OM_CLOSE;
    return( res );
  }
  
  res = _writeInrimageData( im );
  if (res < 0) {
    fprintf(stderr, "writeInrimage: error: unable to write data of \'%s\'\n",
	    name);
    ImageIO_close( im );
    im->fd = NULL;
    im->openMode = OM_CLOSE;
    return( res );
  }

  ImageIO_close( im );
  im->fd = NULL;
  im->openMode = OM_CLOSE;

  return ( res );  
}

PTRIMAGE_FORMAT createInrimageFormat() {
  PTRIMAGE_FORMAT f=(PTRIMAGE_FORMAT) ImageIO_alloc(sizeof(IMAGE_FORMAT));

  f->testImageFormat=&testInrimageHeader;
  f->readImageHeader=&readInrimageHeader;
  f->writeImage=&writeInrimage;
  strcpy(f->fileExtension,".inr,.inr.gz,.gradient,.gradient.gz,.gradient_direction,.gradient_direction.gz");
  strcpy(f->realName,"Inrimage");
  return f;
}
