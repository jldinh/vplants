

#include <vt_names.h>

/*------- Definition des fonctions statiques ----------*/
#ifndef NO_PROTO
#else
#endif

/* Fonction d'initialisation de la structure vt_names.

   Les noms sont remplis avec des caracteres nuls. Les
   booleens sont mis a False.
*/

#if defined(_ANSI_)
void VT_Names( vt_names *n )
#else
void VT_Names( n )
vt_names *n;
#endif
{
    register int i;
    for (i=0; i<STRINGLENGTH; i++)
	n->in[i] = n->out[i] = n->ext[i] = '\0';
    n->inv = n->swap = False;
}

/* Fonction de copie d'un nom.

   Cette fonction copie name2 dans name1.
   Elle teste si les chaines sont non nulles,
   si la longueur de name2 est inferieure a
   STRINGLENGTH.

RETURN
   Elle renvoie 0 si la copie n'a pas pu se faire.
*/

#if defined(_ANSI_)
int VT_CopyName( char *name1 /* string containing the result of the copy */,
		char *name2 /* string to be copied */ )
#else
int VT_CopyName( name1, name2 )
char *name1; /* string containing the result of the copy */
char *name2; /* string to be copied */
#endif
{
    if ( (name1 == (char*)NULL) || (name2 == (char*)NULL) )
	return( 0 );
    if (VT_Strlen( name2 ) >= STRINGLENGTH)
	return( 0 );
    if (VT_Strlen( name2 ) <= 0)
	return( 1 );
    VT_Strncpy( name1, name2, (int)STRINGLENGTH );
    return( 1 );
}
