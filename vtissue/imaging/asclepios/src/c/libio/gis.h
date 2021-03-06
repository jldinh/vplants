#ifndef GIS_H
#define GIS_H


#include <imageio/ImageIO.h>


#ifdef __cplusplus
extern "C" {
#endif


/* read gis format header

   Format du fichier texte associe aux fichiers binaires (images)

exemple :
         512 512 100 2
	 -type U16
	 -dx 1. 
	 -dy 2.
	 -dz .5
	 -z2 5
         -ar SUN
	 -mod MR
         -txt image acquise sur SIGNA 1.5T au CHRU de Caen
         donnees brutes sans traitement  -endtxt
	
- la premi?re ligne comporte les dimensions de l'image, respectivement, le nombre de colonnes, de lignes, de coupes et de temps; ces deux, trois ou quatre entiers doivent ?tre strictement positifs et rester inf?rieurs ? 4096.

- les lignes suivantes comportent des champs indiques par des mots clefs:
			
   -type typespecifier

   U8 entier non sign? cod? sur 8 bit (unsigned char) 
   S8  entier sign? cod? sur 8 bit (signed char)
   U16  entier non sign? cod? sur 16 bit (unsigned short)
   S16  entier sign? cod? sur 16 bit (signed short)	
   U32  entier non sign? cod? sur 32 bit (unsigned int)
   S32  entier sign? cod? sur 32 bit (signed int)
   FLOAT  flottant simple pr?cision (float)
   DOUBLE  flottant double pr?cision (double)
			
   -dx double  (taille du voxel en x)
   -dy double  (taille du voxel en y)
   -dz double  (taille du voxel en z)
               (les tailles sont donnees en millimetres)
   -dt double  (taille du voxel en t)
               (taille donnee en secondes)

   (sp?cification d'un sous-volume)
   -x1 entier  	
   -x2 entier  	
   -y1 entier  
   -y2 entier  
   -z1 entier  
   -z2 entier  
   -ref nom x y z t   
        (origine d'un sous-volume : fichier correspondant a une
         sous-image de "nom")

   -ar architecture (string)
   -mod modalite (string) : MR, PET, fMR, etc.
   -dir plan de coupe (string) : sagittal, frontal, axial
   -min double (valeur physique correspondant au minimum des voxels)
   -max double (valeur physique correspondant au maximum des voxels)
   -ca x y z (3 entiers pour la position de CA)
   -cp x y z (3 entiers pour la position de CP)
   -ip a b c d (4 double pour les coefficients du plan inter-hemispherique
                equation de la forme ax+by+cz+d = 0)
   -td d1 d2 d3 d4 d5 d6 (6 entiers pour les distances au repere de
		Talairach, en voxels :
		d1 : Talairach anterior plane-CA distance
		d2 : Talairach posterior plane-CP distance
		d3 : Talairach left plane-IP distance
		d4 : Talairach right plane-IP distance
   		d5 : Talairach bottom plane-CACP distance
   		d6 : Talairach top plane-CACP distance
   -a age (entier)
   -s sexe (1/2)
   -l lateralite
   -txt texte libre (ascii)
   -endtxt (fin du texte)


   return:
   -1: error
   0: success
 */
int readGisHeader(const char* name,_image *im);


int testGisHeader(char *magic,const char *name);

/** creates an return the file format structure associated with the Gis file format */
PTRIMAGE_FORMAT createGisFormat();

/* 
   return:
   -1: error
    1: success
 */
int writeGis( char *basename, _image* im ) ;
/* 
   return:
   -1: error
    1: success
 */
int writeGisHeader( const _image* im ) ;


/* 
   return:
   -1: error
    1: success
 */
int writeGisData( const _image* im ) ;

#ifdef __cplusplus
}
#endif

#endif
