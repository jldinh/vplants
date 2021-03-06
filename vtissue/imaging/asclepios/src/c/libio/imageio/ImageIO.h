#ifndef IMAGEIO_H
#define IMAGEIO_H

#include <stdlib.h>
#include <stdio.h>



#ifdef NOZLIB
#undef ZLIB
#else
#define ZLIB
#endif

#ifdef ZLIB
#include <zlib.h>
/* see http://www.gzip.org/zlib/
   for details and documentation
*/
#endif



#if (defined(_LINUX_) || defined(_SOLARIS_))

/* should be declared in stdio.h
 */
extern int fileno( FILE *stream);
extern FILE *fdopen (int fildes, const char *mode);
/* should be declared in string.h
 */
#ifndef __cplusplus
extern char *strdup(const char *s);
extern int strncasecmp(const char *s1, const char *s2, size_t n);
#endif

#endif



#ifdef __cplusplus
extern "C" {
#endif


#ifndef LONGINT

#if (defined _ALPHA_ || (defined _SGI_ && (defined _64_ || defined _64_M4_ || defined _64_M3_)))
/* the 64-bits type on 64-bits platform (long int) */
#define LONGINT long  int
#else
#ifdef __GNUC__
/* the 64-bits type on 32-bits platform (long long int) */
#define LONGINT long long int
#else
/*#define LONGINT __int64 */
#define LONGINT long int
#endif
#endif

#endif








/** file open mode */
typedef enum {
  /** no file open */
  OM_CLOSE,
  /** file is stdin or stdout */
  OM_STD,
  /** file is gzipped */
#ifdef ZLIB
  OM_GZ,
#endif
  /** normal file */
  OM_FILE
} OPEN_MODE;


/** data mode */
typedef enum {
  /** data are binary */
  DM_BINARY,
  /** data are ascii */
  DM_ASCII
} DATA_MODE;


/** kind of image word */
typedef enum {
  /** fixed type */
  WK_FIXED,
  /** floating point */
  WK_FLOAT,
  /** unknown (uninitialized) */
  WK_UNKNOWN
} WORD_KIND;


/** image word sign */
typedef enum {
  /** signed */
  SGN_SIGNED,
  /** unsigned */
  SGN_UNSIGNED,
  /** unknown (uninitialized or floating point words) */
  SGN_UNKNOWN
} SIGN;


/** endianness */
typedef enum {
  /** Little endian processor */
  END_LITTLE,
  /** Big endian processor */
  END_BIG,
  /** Unknown endianness (unopenned file) */
  END_UNKNOWN
} ENDIANNESS;


/** inrimage vectorial storage mode */
typedef enum {
  /** interlaced vectors (i.e. x1, y1, z1, x2, y2, z2, x3, y3, z3, ...) */
  VM_INTERLACED,
  /** non interlaced vectors (i.e. x1, x2, x3, ..., y1, y2, y3, ..., z1, z2, z3...) */
  VM_NON_INTERLACED,
  /** scalar inrimage */
  VM_SCALAR
} VECTORIAL_MODE;



#ifdef ZLIB
typedef gzFile _ImageIO_file;
#else
typedef FILE*  _ImageIO_file;
#endif

#define IMAGE_FORMAT_NAME_LENGTH 100


struct point_image;

/** defines the type of function called to test if an image is of a given
    format. The first parameter is an array of char of size 5 (ends with
    character 0) that describes the first file character (magic string). The
    second parameter is the filename. The output value is >=0 if the image is
    of that given format and <0 otherwise */
typedef int (*TEST_IMAGE_FORMAT)(char *,const char *);
/** defines the type of function called to read an image or an image header
    from a file corresponding to a given format. The first parameter is the
    file name whereas the second parameter is an _image structure. Note that 
    the file has been already opened (the file descriptor fd is valid). 
    The output value is >0  if  the whole image has been read, it is 0 if 
    only the header has been read and it is  <0 otherwise */
typedef int (*READ_IMAGE_HEADER)(const char *, struct point_image *);
/** defines the type of function called to write an image to a file
    corresponding to a given format.  
    The first parameter is the full file name whereas the second parameter
    is an _image structure. 
    Note that the file has to be opened and closed in the function.
    The output value is >=0 if the whole image has been written
    correctly and it is <0 otherwise */
typedef int (*WRITE_IMAGE)(char *,struct point_image *);


/** Image Format descriptor */
typedef struct imformat {

  /** a pointer on a function that tests if an image is of a given format */
  TEST_IMAGE_FORMAT testImageFormat;

  /** a pointer on a function that reads the header of an image file */
  READ_IMAGE_HEADER readImageHeader;

  /** a pointer on a function that writes  image of a given
      format */
  WRITE_IMAGE writeImage;

  /* the file extension of format (including a dot ".": if several 
     extensions may be used, they should be separed with a 
     comma ".inr,.inr.gz" */
  char fileExtension[IMAGE_FORMAT_NAME_LENGTH];
  
  /** the usual name given to a format : for instance "inrimage", "gif" */
  char realName[IMAGE_FORMAT_NAME_LENGTH];
  /* pointer towards the next image format*/
  struct imformat *next;
} IMAGE_FORMAT, *PTRIMAGE_FORMAT;;

/** Image descriptor */
typedef struct point_image {
  /** Image x dimension (number of columns) */
  unsigned int xdim;
  /** Image y dimension (number of rows) */
  unsigned int ydim;
  /** Image z dimension (number of planes) */
  unsigned int zdim;
  /** Image vectorial dimension */
  unsigned int vdim;

  /** Image voxel size in x dimension */
  double vx;
  /** Image voxel size in y dimension */
  double vy;
  /** Image voxel size in z dimension */
  double vz;

  /** Image offset in x dimension */
  float tx;
  /** Image offset in y dimension */
  float ty;
  /** Image offset in z dimension */
  float tz;

  /** Image rotation vector in x dimension */
  float rx;
  /** Image rotation vector in y dimension */
  float ry;
  /** Image rotation vector in z dimension */
  float rz;

  /** Image center in x dimension */
  int cx;
  /** Image center in y dimension */
  int cy;
  /** Image center in z dimension */
  int cz;

  /** spm */
  float spm_offset;
  float spm_scale;

  /** Image data buffer */
  void *data;

  /** Image word size (in bytes) */
  unsigned int wdim;
  /** Image format to use for I/0. Should not be set by user */
  PTRIMAGE_FORMAT imageFormat;
  /** Data buffer vectors are interlaced or non interlaced */
  VECTORIAL_MODE vectMode;
  /** Image words kind */
  WORD_KIND wordKind;
  /** Image words sign */
  SIGN sign;

  /** User defined strings array. The user can use any internal purpose string.
      Each string is written at then end of header after a '#' character. */
  char **user;
  /** Number of user defined strings */
  unsigned int nuser;

  /** Image file descriptor */
  _ImageIO_file fd;


  /** Kind of image file descriptor */
  OPEN_MODE openMode;
  /** Written words endianness */
  ENDIANNESS endianness;
  /** Kind of image data encoding */
  DATA_MODE dataMode;

} _image;



/** Error codes */
#define ImageIO_NO_ERROR 0
#define ImageIO_UNKNOWN_TYPE -1
#define ImageIO_OPENING -2
#define ImageIO_READING_HEADER -3
#define ImageIO_READING_IMAGE -4
#define ImageIO_WRITING_HEADER -3
#define ImageIO_WRITING_IMAGE -4
#define ImageIO_WRITING_DATA  -5





/** Allocates and initializes an image descriptor */
_image *_initImage();

/** Free an image descriptor
    @param im image descriptor */
void _freeImage(_image *im);

/** creates an image descriptor from the given header information
    @param x image x dimension (number of columns)
    @param y image y dimension (number of rows)
    @param z image z dimension (number of planes)
    @param v image vectorial dimension
    @param vx image voxel size in x dimension
    @param vy image voxel size in y dimension
    @param vz image voxel size in z dimension
    @param w image word size in bytes
    @param wk image word kind
    @param sgn image word sign */
_image *_createImage(int x, int y, int z, int v,
		     float vx, float vy, float vz, int w,
		     WORD_KIND wk, SIGN sgn);


/** Reads an image from a file and returns an image descriptor or NULL if<br>
    reading failed.<br>
    Reads from stdin if image name is NULL.
    The image data field points to a xdim * ydim * zdim * vdim buffer
    containing voxels in order:
    (Z1, Y1, X1, V1) (Z1, Y1, X1, V2), ... , (Z1, Y1, X1, Vt),
    (Z1, Y1, X2, V1) ...         ...       , (Z1, Y1, X2, Vt),
    ...
    (Z1, Y1, Xn, V1) ...         ...       , (Z1, Y1, Xn, Vt),
    (Z1, Y2, X1, V1) ...         ...       , (Z1, Y2, X1, Vt),
    ...
    (Z2, Y1, X1, V1) ...         ...       , (Z2, Y1, X1, Vt),
    ...
                     ...         ...       , (Zl, Ym, Xn, Vt)

    Read the following format:
    Inrimage,
    GIF,
    IRIS,
    ANALYSE,
    PGM,
    PPM,
    BMP,
    GIS (CEA, IRISA, ENST 3D image format).
    
    See also:
    http://www.dcs.ed.ac.uk/home/mxr/gfx/2d-hi.html and
    http://www.gzip.org/zlib/
    

   @param name image file name or NULL for stdin */
_image* _readImage(const char *name);

/** Reads an image from a file and returns an image descriptor or NULL if<br>
    reading failed.<br>
    Reads from stdin if image name is NULL.
    If the image is vectorial, it is uninterlaced, i.e. the image data
    field points to a xdim * ydim * zdim * vdim buffer containing voxels
    in order:
     (V1, Z1, Y1, X1) (V1, Z1, Y1, X2), ... , (V1, Z1, Y1, Xn),
     (V1, Z1, Y2, X1) ...         ...       , (V1, Z1, Y2, Xn),
     ...
     (V1, Z1, Ym, X1) ...         ...       , (V1, Z1, Ym, Xn),
     (V1, Z2, Y1, X1) ...         ...       , (V1, Z2, Y1, Xn),
     ...
     (V2, Z1, Y1, X1) ...         ...       , (V2, Z1, Y1, Xn),
     ...
                      ...         ...       , (Vt, Zl, Ym, Xn)
   @param name image file name or NULL */
_image* _readNonInterlacedImage(const char *name);

/** Writes given image in file 'name'.<br>
    If name ends with '.gz', file is gzipped.<br>
    If name is NULL, image is sent to stdout.
    @param im image descriptor 
    @param name file name to store image or NULL */
int _writeImage(_image *im, const char *name);

/** Read one slice of given image whose header has already been read.<br>
    File descriptor is let at the beginning of next slice and closed<br>
    when end of file is encountered.<br>
    If data buffer is NULL, it is allocated for one slice only.<br>
    This funtion is dedicated to read huge inrimages.
    @param im image descriptor */
void _getNextSlice(_image *im);


/** adds a format in the list of image format. Test if all mandatory
    fields have been filled 
    @param format : an image format 
    @return -1 if it failed (missing information) and 0 if it succeeded */
int addImageFormat( PTRIMAGE_FORMAT format);


/** returns the first available image format */
PTRIMAGE_FORMAT firstImageFormat();

/** Reads header from an image file<br>
    If file is an inrimage, only header is read. Otherwise, whole image<br>
    is read and image file descriptor is closed.<br>
    If name is NULL, header is read from STDIN
    @param name image file name or NULL */
_image* _readImageHeader(const char *name);
_image *_readImageHeaderAndGetError( const char *name, int *error );

/** Reads body from an inrmage whose header has been read by
    _readImageHeader
    @param im image to read */
int _readImageData(_image *im);

/** Reads body from a vectorial inrimage whose header has been read by
    _readImageHeader. The image is uninterlaced
    (see _readNonInterlacedImage for details).
    @param im image descriptor*/
int _readNonInterlacedImageData(_image *im);

/** Reads body from a non-interlaced vectorial inrimage whose header has
    been read by _readImageHeader. The image buffer is interlaced.
    @param im image descriptor */
int _readNonInterlacedFileData(_image *im);




/** given an initialized file descriptor and a file name, open file
   from stdout (if name == NULL), a gziped pipe (if file is gziped)
   or a standard file otherwise.
   @param im initialized image descriptor
   @param name image file name */
void _openWriteImage(_image* im, const char *name) ;
   
/** open an image file from stdin (if name == NULL), from a pipe
   (piped with gzip if image was compressed) or from a standard file
   @param im initialized image descriptor
   @param name image file name */
void _openReadImage(_image *im, const char *name);

/** close an image file descriptor that was opened using _openImage
    @param im opened image descriptor */
void _closeImage(_image *im);


/** returns the endianness of the hardware architecture */
ENDIANNESS  _getEndianness(); 
/** initializes the list of  supported image formats */
void initSupportedFileFormat();
/** prints supported image formats */
void printSupportedFileFormat();
/** free the list of  supported image formats */
void removeSupportedFileFormat();


/** return image type in given file
    @param fileName image file name */
PTRIMAGE_FORMAT imageType(const char *fileName);


/** function prototype to allocate memory */
typedef void *(*ALLOCATION_FUNCTION)(size_t);

/** function prototype to free memory */
typedef void (*DEALLOCATION_FUNCTION)(void *);


/** set allocation and deallocation routines
    @param alloc new allocation routine
    @param del new deallocation routine */
void setImageIOAllocationRoutines(ALLOCATION_FUNCTION alloc,
				  DEALLOCATION_FUNCTION del);



/** call allocation routine */
void *ImageIO_alloc(size_t);
/** call deallocation routine */
void ImageIO_free(void *);

/** replaces fwrite function
    @param im image to write
    @param buf data buffer to write
    @param len buffer length */
size_t ImageIO_write(const _image *im, const void *buf, size_t len);


/** replaces fread function
    @param im image to read
    @param buf data buffer to read
    @param len buffer length */
size_t ImageIO_read(const _image *im, void *buf, size_t len);

/** replaces fgets function
 */
char *ImageIO_gets( const _image *im, char *str, int size );

/** replaces fseek function
 */
int ImageIO_seek( const _image *im, long offset, int whence );

/** replaces ferror function
 */
int ImageIO_error( const _image *im );

/** replaces fclose function
 */
int ImageIO_close( _image *im );





#ifdef __cplusplus
}
#endif

#endif
