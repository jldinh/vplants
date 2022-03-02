/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): Ch. Godin (christophe.godin@cirad.fr)
 *
 *       $Source$
 *       $Id: array.cpp 17611 2014-10-17 13:20:41Z pradal $
 *
 *       Forum for AMAPmod developers    : amldevlp@cirad.fr
 *
 *  ----------------------------------------------------------------------------
 *
 *                      GNU General Public Licence
 *
 *       This program is free software; you can redistribute it and/or
 *       modify it under the terms of the GNU General Public License as
 *       published by the Free Software Foundation; either version 2 of
 *       the License, or (at your option) any later version.
 *
 *       This program is distributed in the hope that it will be useful,
 *       but WITHOUT ANY WARRANTY; without even the implied warranty of
 *       MERCHANTABILITY or FITNESS For A PARTICULAR PURPOSE. See the
 *       GNU General Public License for more details.
 *
 *       You should have received a copy of the GNU General Public
 *       License along with this program; see the file COPYING. If not,
 *       write to the Free Software Foundation, Inc., 59
 *       Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 *  ----------------------------------------------------------------------------
 */




#include <cstdio>
#include <cstdlib>
#include <fstream>

#include "tool/config.h"
#ifdef GNU_STL_EXTENSION
        #include <sstream>
#else
        #include <strstream>
#endif

// #include <values.h>
#ifdef SYSTEM_IS__IRIX
#include <values.h>
#else
#include <float.h>
#ifndef MINFLOAT
#define MINFLOAT FLT_MIN
#endif
#ifndef MAXFLOAT
#define MAXFLOAT FLT_MAX
#endif
#ifndef MAXDOUBLE
#define MAXDOUBLE DBL_MAX
#endif
#endif

#include "date.h"

#include "set.h"
#include "array.h"
//#include "parseraml.h"
//#include "kernel_funs.h"
#include "kernel_err.h"

// for white space characters
#include <ctype.h>

#include "gnuplot.h"
#include "tool/rw_locale.h"
#include "tool/dirnames.h"

using namespace std;

extern ostream& getAMLOutputStream();

#define  ERR_MSG_ARRAY          kernel_err_msgs_aml
#define  MODULE_NAME            "Kernel"

#define min(x,y) ((x<y)?(x):(y))
#define abs(x)   ((x>=0)?(x):(-(x)))

static const int DP_PLOT_SIZE = 100;

const char* Plot_prefix = "gnuplot_tmp_file";
const char* SYSTEMCHAR = ":"; // prefix of all system command names

ostream& Array::display(ostream& o, size_t maxbytes) const {

  if (!maxbytes) return displayOneLine(o);

  ArrayIter* pnext = iterator();
  ArrayIter& next = *pnext;

  if (maxbytes < 5) maxbytes = 5;

  int nbel = entries();

  // Computes the number of bytes allocated to one element

  int commas = ( nbel ) ? ( nbel - 1 ) : 0; // nb of commas used in the expression
  int fillchars = 5; // to account for chars : '[' '...' and ']'

  int reserved = fillchars + commas;
  int available = maxbytes - reserved;

  if (available < 0) available = 0;

  int elem_size = nbel?available/nbel:0;

#ifndef STL_EXTENSION

  char* tmp = new char[maxbytes+1];
  for (int h=0;h<=maxbytes;h++) tmp[h]=0;
  ostrstream os(tmp,maxbytes);
#else
  ostringstream os;
#endif

  o << "[" ;

  int first = TRUE;

  while(next()) {

    if (!first) os << ",";
    else first = FALSE;

    next.key().printValue(os, elem_size);

  }

  delete pnext;

  // cerr << "tmp       = " << tmp << endl;
  // cerr << "maxbytes = " << maxbytes << endl;

#ifndef STL_EXTENSION
  RWCString elemstg(tmp,min(strlen(tmp),maxbytes));
#else
  RWCString elemstg= string(os.str(),0,maxbytes);
#endif

  // cerr << "elemstg   = " << elemstg << endl;
  // cerr << "elemstg.ln= " << elemstg.length() << endl;

  if (elemstg.length() >= maxbytes-2) { // -2 for '[' and ']'

    if (maxbytes-fillchars >=0) {
      elemstg.remove(maxbytes-fillchars); // '[' "..." and ']'
    }
    elemstg.append("...");

  }

  o << elemstg;

  o << "]" ;

#ifndef STL_EXTENSION
  delete [] tmp;
#endif

  return o;

}



ostream& Array::displayOneLine(ostream& o) const {

  ArrayIter* pnext = iterator();
  ArrayIter& next = *pnext;

  o << "[" ;

  int first = TRUE;

  while(next()) {

    if (!first) o << ",";
    else first = FALSE;

    next.key().printValue(o);

  }

  delete pnext;

  o << "]" ;

  return o;

}

ostream& Array::displaySpreadSheet(ostream& o, int level = 0, const char* sep = " ") const {

  ArrayIter* pnext = iterator();
  ArrayIter& next = *pnext;

  int first = TRUE;

  level ++;

  if (entries()==0) {
    if (level != 1) o << endl << "#" << level <<  endl;
    o << "void"; // cas d'un tableau vide
  }

  while(next()) {

    if (!first) {
      if (surfaceType() != AMObjType::ARRAY) o << sep;
      if (next.key().tag == AMObjType::ARRAY) ((Array*)(next.key().val.p))->displaySpreadSheet(o);
      else {
	next.key().printValue(o);
	// next.key().printValue(cerr);
	// cerr << endl;
      }
    }
    else { // First element of an array
      first = FALSE;
      if (next.key().tag == AMObjType::ARRAY) ((Array*)(next.key().val.p))->displaySpreadSheet(o, level);
      else {
        if (level != 1) o << endl << "#" << level << endl;
        next.key().printValue(o);
	// next.key().printValue(cerr);
	// cerr << endl;
      }
    }

  }

  // o << " (" << nestedDepth() << ") " << flush;
  if (nestedDepth() == 1) o << endl;

  delete pnext;

  return o;

}

AmlBoolean Array::checkDefined() const {
  if (surfaceType() == AMObjType::ARRAY) {
    return ((Array*)(_an_element->val.p))->checkDefined();
  }
  else if (surfaceType() == AMObjType::SET) {
    return ((Set*)(_an_element->val.p))->checkDefined();
  }
  else if (surfaceType() == AMObjType::UNDEF) return FALSE;
  else return TRUE;
}


SLArray::SLArray(const VIdList* list) : Array() {

  VIdListIter next(*(VIdList*)list);

  while (next()) {

    if (!_an_element) _an_element = new AMObj(AMObjType::VTX,next.key());

    *this += AMObj(AMObjType::VTX,next.key());

  }

}


static AmlBoolean putToken(Array* thearray, RWCString token) {

  RWLocaleSnapshot french("fr");

  if (token.length() != 0) {

    long i;
    double d;
    char c = token(0);
    Date t;

    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) { // test whether it is a string

      *thearray += AMObj(AMObjType::STRING, new AMString(token.data()));

    }
    else if (token.contains(".")) {   // It might be a real number

      const char* stg = token.data();
      sscanf (stg,"%lf", &d);

      //if (french.stringToNum(token,&d)) {

        *thearray += AMObj(AMObjType::REAL, d);

        //{
        /*
      else {

        // Error

        cerr << "Error 2" << endl;
        return FALSE;

        }
        */

    }
    else if (token.contains("/")) {   // It might be a date

      if ((t = encodeDate(token.data(), DDMMYY)) != (unsigned long)LUNDEF) {

        *thearray += AMObj(AMObjType::DATE, (long) t);

      }
      else {

        // Error

        // cerr << "Error 3" << endl;
        return FALSE;

      }

    }
    else if (french.stringToNum(token, &i)) { // It might be an integer

      *thearray += AMObj(AMObjType::INTEGER, (int) i);

    }
    else {

      // Error

      // cerr << "Error 4" << endl;
      return FALSE;

    }

  }
  else { // token.length == 0

    // nothing

  }

  return TRUE;

}
// Renvoie un AMObj correspondant a un Array qui est lu dans le input stream.
// Le Array lu est un tableau multi-dimensionel dont les dimensions sont
// specifiees par level, dim, et dimarray :
// - dimmarray : est un tableau d'entiers definissant une suite de dimensions
//   allant de la plus macroscopique a la plus fine
// - dim : est la taille de dimarray (ces deux objets doivent etre coherents
//   a l'appel. Cette coherence n'est pas controlee dans la fonction
// - level : definit les dimensions du tableau que l'on veut calculer. C'est
// un index dans le tableau dimarray qui permet de ne considerer que des
// sous-tableaux d'un tableau complet ayant les dimensions de dimarray.
// ex: [[[1,2,3,4],[5,6,7,8],[9,10,11,12]],[13,14,15,16],[17,18,19,20],[21,22,23,24]]
// ce tableau est multidimensionel
// dim = 3
// dimarray = [2,3,4]
// si level = 3, les tableaux cherches dans l'entree auront des dimensions [2,3,4]
// si level = 2, les tableaux cherches dans l'entree auront des dimensions [3,4]
// si level = 1, les tableaux cherches dans l'entree auront des dimensions [4]
// (le niveau 1 est celui ou les donnees elementaires sont lues dans le fichier)
// les donnees elementaires doivent etre de type
// INT, REAL, STRING, ou DATE
// Sinon une erreur est generee.
// Une erreur est egalement generee si il manque des donnees pour completer
// toutes les dimensions

static AMObj getNextArray(istream& is, int level, int dim, const int* dimarray) {

  Array* thearray = new SLArray;
  AMObj tmp;

  assert(level>0 && level<=dim+1);

  if (level != 1) {

    // si level == dim, on est en train de construire le tableau le plus macroscopique.
    // => lecture jusqu'a la fin du fichier
    // sinon, la taille de la suite de valeurs a lire est determinee par
    // la derniere valeur du tableau dimarray, i.e. dimarray[dim-level]

    // On voit donc que l'on accede jamais a l'index du tableau dimarray
    // tel que level = dim+1, i.e. dim-level = dim-dim-1 = -1 qui serait
    // une erreur.

    int k = 0;

    while (level == dim+1 ? !is.eof() : !is.eof() && k<dimarray[dim-level] ) {

      k++;

      tmp = getNextArray(is, level-1, dim, dimarray);

      if (tmp.tag == AMObjType::ERROR) {

        delete thearray;

        return AMObj(AMObjType::ERROR);

      }
      else {

        assert(tmp.tag == AMObjType::ARRAY ||
               tmp.tag == AMObjType::UNDEF);

        if (tmp.tag == AMObjType::UNDEF) { // cas d'une lecture de trop apres un eof()

          // La fin du fichier a ete atteinte
          // C'est normal si on est sur la dimension la plus macroscopique
          // quelque soit k. On va sortir juste apres du while a cause du eof.

          if (level != dim+1) {

            // Si on recupere un AMObjType::UNDEF, c'est que on
            // est au tout debut de la saisie d'un sous tableau complet : exemple
            // [[[1,2,3],[1,2,3]],[[
            // c'est normal, seulement si k == 1 (on essaie de de lire un nouveau
            // sous tableau complet mais le fichier est termine et
            // on ne le savait pas avant de commencer a voulior lire le plus
            // petit element du sous-tableau complet)

            if (k == 1) {

              delete thearray;
              return tmp;

            }
            else {
              // il y a une erreur: on a rencontrer un eof au plus bas niveau alors
              // que la lecture du nombre d'elements de ce tableau n'etait
              // pas achevee

              delete thearray;
              return AMObj(AMObjType::ERROR);
            }

          }

        }
        else *thearray += tmp;

      }

    }

  }
  else {  // level == 1

    // Reads a terminal symbol: it must be either a string, a real, a date or an integer
    // and add it to the current array

    // dimarray[dim-1] token are read from the input stream

    // si dim == 1, on veut tracer un tableau monodimensionnel
    // => lecture jusqu'a la fin du fichier
    // sinon, la taille de la suite de valeurs a lire est determinee par
    // la derniere valeur du tableau dimarray, i.e. dimarray[dim-1]

    // donc pour dim == 2 (tableau a deux dimensions), on accede
    // a la dimension dimarray[2-2] = dimarray[0]. Le tableau dimarray
    // est effectivement constitue dans ce cas d'un seul element, specifiant
    // la valeur du nombre d'elements de la dimension la plus fine.

    RWCString token;

    int k = 0;
    while( (dim == 0 ? !is.eof() : !is.eof() && k < dimarray[dim-1])) {

      // cerr << "level = 1,  k = " << k << endl;
      k++;

      if (is.eof()) {

        // Error

        delete thearray;

        AMLOUTPUT << "Error EOF encountered prematurely." << endl;

        return AMObj(AMObjType::ERROR);

      }

      is >> token;

      // cerr << "<" << token << ">" << endl;

      if (is.eof() && k == 1) { // premier passage correspond a la fin de fichier
        delete thearray;
        return AMObj(AMObjType::UNDEF);
      }

      if (!putToken(thearray, token)) {

        delete thearray;
        return AMObj(AMObjType::ERROR);

      }


    }

  }

  return AMObj(AMObjType::ARRAY, thearray);

}

SLArray::SLArray(const char* filename, int dim, const int* dimarray) : Array() {

  ifstream in_file(filename);

  if (! in_file) {
    genAMLError(ERRORMSG(K_F_FILE_ERR_sss) , "Array", "input file", filename);
    _state = FALSE;
  }

  AMObj tmp = getNextArray(in_file, dim, dim-1, dimarray);

  if (tmp.tag() != AMObjType::ARRAY) {

    AMLOUTPUT << "Could not create the array." << endl;

    _state = FALSE;

  }
  else {

    Array* array = ((Array*)tmp.val.p);

    ArrayIter* pnext = array->iterator();
    ArrayIter& next = *pnext;

    int i = 0;
    while(next()) {

      *this += next.key();

      if (!_an_element || _an_element->tag == AMObjType::UNDEF) _an_element = &((*this)[i]);

      i++;

    }

    delete pnext;

    _state = TRUE;

  }
  in_file.close();

}

static AmlBoolean findOpenBracket(istream& is) {

  char c;

  while(! is.eof()) {

    c = is.get();

    // cerr << "c = " << c << endl;

    if (!isspace(c))
      if (c == '[') return TRUE;
      else return FALSE;

  }

  return FALSE; // no character [ has been found in the input stream


}

static RWCString getNextToken(istream& is) {

  char c;

  RWCString token;

  while(! is.eof()) {

    c = is.get();

    if (!isspace(c))
      if (c == ']') {
        is.putback(c);
        break;
      }
      else if (c == ',') {
        is.putback(c);
        break;
      }
      else token += RWCString(c);

  }

  return token;

}

static char getNextNWSChar(istream& is) {

  char c;

  while(! is.eof() ) {

    c = is.get();

    if (!isspace(c)) break;

  }

  return c;

}


// This function is called when an open bracket '['
// has just been read in the input stream and
// a new array has to be created (the function basically
// creates the new array, and then asks for
// retreiving the element list of the array.

// The array passed as an argument is the array to which
// elements have to be added by the function

static AmlBoolean getBracketedArray(istream& is, Array* thearray) {

  char c = getNextNWSChar(is); // reads the next non white space character from the input stream

  // cerr << "enter getBracketedArray : c = " << c << endl;

  if ( c == ']' ) return TRUE; // this is an empty array.
  else if ( c == '[' ) {

    is.putback(c); // it is put back to the input stream before calling getNextToken()

    RWCString token, result; // reads the input up to the next ',' or ']'.

    c = ',';

    // cerr << "\nDebut de la boucle sur les tableaux de tableaux" << endl;

    while( !is.eof() &&  c == ',') {

      if (!findOpenBracket(is)) {  // look for a '['

        return FALSE;

      }
      Array* a = new SLArray;
      AmlBoolean flag = getBracketedArray(is, a);

      if (!flag) {

        delete a;
        return FALSE;

      }
      else *thearray += AMObj(AMObjType::ARRAY, a);
      /*
      cerr << "-------" << endl;
      thearray->display (cerr);
      cerr << "\n-------" << endl;
      */
      c = getNextNWSChar(is); // reads the next non white space character from the input stream

    }

    // cerr << "\nFin de la boucle sur les tableaux de tableaux" << endl;

    if (!is.eof() && c != ']') {

      AMLOUTPUT << "Could not find a closing square bracket ']'." << endl;
      return FALSE;

    }

    return TRUE;

  }
  else {   // caracter c is supposed to belong to the first element of the array

    is.putback(c); // it is put back to the input stream before calling getNextToken()

    RWCString token; // reads the input up to the next ',' or ']'.

    c = ',';

    // cerr << "Debut tokens" << endl;

    while( !is.eof() &&  c == ',') {

      token = getNextToken(is);

      // cerr << "token = " << token << endl;

      if (!putToken(thearray, token)) {

        return FALSE;

      }

      c = getNextNWSChar(is); // reads the next non white space character from the input stream

    }
    /*
      cerr << "-------" << endl;
      thearray->display (cerr);
      cerr << "\n-------" << endl;
      */
    // cerr << "Fin tokens" << endl;


    if (c != ']') {

      AMLOUTPUT << "Could not find a closing square bracket ']'." << endl;
      return FALSE;

    }

    return TRUE;

  }

}


SLArray::SLArray(const char* filename) : Array() {

  ifstream in_file(filename);

  if (! in_file) {
    genAMLError(ERRORMSG(K_F_FILE_ERR_sss) , "Array", "input file", filename);
    _state = FALSE;
  }

  if (findOpenBracket(in_file)) {

    if (!getBracketedArray(in_file, this)) {

      AMLOUTPUT << "Could not create the array." << endl;

      _state = FALSE;

    }
    else _state = TRUE;

  }
  else {

    AMLOUTPUT << "Could not find any opening square bracket '[' in the file." << endl;

    _state = FALSE;

  }


  in_file.close();

}

SLArray::SLArray(const Array* array, const PFNode* pred, const AMObj* arg) {

  ArrayIter* pnext = array->iterator();
  ArrayIter& next = *pnext;

  AMObj obj(array->surfaceType());
  AMObjVector predarglist(pred->argNb());

  int k = 0;

  while(next()) {

    obj = next.key();

    for (register int j=0; j<pred->argNb(); j++) {

      if (pred->argRef(j) == -1) {
        predarglist[j] = obj;
      }
      else {
        predarglist[j] = arg[pred->argRef(j)];
      }

    }

    obj = (*(pred->fnode()))(predarglist);

    if (obj.tag() == AMObjType::ERROR) {

      genAMLError(ERRORMSG(K_ITER_EVAL_ERR_sd), (const char*)(pred->fnode()->name()), k+1);
      delete _an_element;
      _an_element = 0;
      _state = FALSE;
      break;

    }
    else if (obj.tag() != AMObjType::VOID) {
      if (!_an_element || _an_element->tag == AMObjType::UNDEF) _an_element = new AMObj(obj);
      if (_an_element->tag == obj.tag) AMObjList::insert(obj);
      else {

        genAMLError(ERRORMSG(K_ITER_EVAL_ERR_sd), (const char*)(pred->fnode()->name()), k+1);
        delete _an_element;
        _an_element = 0;
        _state = FALSE;
        break;

      }
    }

    k++;

  }

  delete pnext;

}


SLArray::SLArray(const Set* set) {

  assert(set != 0);

  SetIter* pnext = set->iterator();
  SetIter& next = *pnext;

  while(next()) {

    *this += next.key();

  }

  delete pnext;

}


AmlBoolean SLArray::contains(const AMObj& obj) const {

  return AMObjList::contains(obj);

}

AmlBoolean SLArray::contains(const Array& array) const {

  AmlBoolean result = TRUE;

  ArrayIter* pnext = array.iterator();
  ArrayIter& next = *pnext;

  while(next()) {

    if (!AMObjList::contains(next.key())) {
      result = FALSE;
      break;
    }

  }

  delete pnext;

  return result;

}

AmlBoolean SLArray::operator==(const Array& array) const {

  if (array.entries() != entries()) return FALSE;

  AmlBoolean result = TRUE;

  ArrayIter* pnext = iterator();
  ArrayIter* pnext2 = array.iterator();
  ArrayIter& next = *pnext;
  ArrayIter& next2 = *pnext2;

  while(next() && next2()) {

    if (next.key() != next2.key()) {
      result = FALSE;
      break;
    }

  }

  delete pnext;
  delete pnext2;

  return result;

}

Array& SLArray::operator+=(const AMObj& obj) {

  if (matchesArrayType(obj)) {
    AMObjList::insert(obj);
    if (!_an_element || _an_element->tag == AMObjType::UNDEF) _an_element = new AMObj(obj);
  }

  return *this;

}

Array& SLArray::operator-=(const AMObj& obj) {

  if (matchesArrayType(obj)) {
    AMObjList::remove(obj);
    if (!AMObjList::entries()) {
      delete _an_element;
      _an_element = 0;
    }
  }

  return *this;

}

Array& SLArray::operator+=(const Array* parray) {

  assert(parray);

  if (parray->anElement()) {

    ArrayIter* pnext = parray->iterator();
    ArrayIter& next = *pnext;

    if (!_an_element || _an_element->tag == AMObjType::UNDEF) _an_element = new AMObj(*(parray->anElement())); // if the current array is empty;

    while(next()) {

      AMObjList::insert(next.key());

    }

    delete pnext;
  }

  return *this;

}

void SLArray::remove(int start, int end) {

  assert(start>=0);
  assert(end>=start);
  assert(end<entries());

#ifdef RWOUT
  removeIn(start,end);
#else
  for (int i=start; i<=end; i++) {

    removeAt(i);

  }
#endif

  if (!AMObjList::entries()) {
    delete _an_element;
    _an_element = 0;
  }

}

void SLArray::insert(int index, const AMObj& val) {

  assert(index>=0);
  assert(index<entries());

  insertAt(index, val);

}


int SLArray::plotWrite(const char* prefix,
                       const char* title,
                       const char* xtitle,
                       const char* ytitle,
                       Array* titles,       // ARRAY(STRING)
                       const char* style,
                       int mode,
                       int xaxis,
                       double xoutset,
                       double xstep,
                       double xmin,
                       double xmax,
                       double ymin,
                       double ymax
                       ) const {

#ifndef STL_EXTENSION
  char *data_file_name , *file_name;
#else
  std::string data_string_name, string_name;
  const char *data_file_name , *file_name;
#endif

  register int i;

  int status = TRUE;
  AmlBoolean XMINFIXED = (xmin == -MAXDOUBLE) ? FALSE : TRUE;
  AmlBoolean XMAXFIXED = (xmax == MAXDOUBLE) ? FALSE : TRUE;
  AmlBoolean YMINFIXED = (ymin == -MAXDOUBLE) ? FALSE : TRUE;
  AmlBoolean YMAXFIXED = (ymax == MAXDOUBLE) ? FALSE : TRUE;

  int nb_curve = 1;
  int nested_level = 0;         // nb of nested arrays (at least 1)

  const AMObj* pelem = _an_element;

#ifndef STL_EXTENSION
  int name_size = strlen(prefix) + 10;
  data_file_name = new char[name_size+1];
  for (int h=0;h<=name_size;h++) data_file_name[h]=0;
#endif

  while (pelem &&  nested_level != -1) {

    nested_level++;

    if (pelem->tag == AMObjType::ARRAY) {
      pelem = ((Array*)(pelem->val.p))->anElement();
    }
    else
    if (pelem->tag == AMObjType::INTEGER || pelem->tag == AMObjType::DATE || pelem->tag == AMObjType::REAL) break;
    else nested_level = -1;     // ERROR

  }

  if (nested_level == 1) {      // the array is a series of yi values

    // creation du fichier de donnees
    // for (int h=0;h<=name_size;h++) data_file_name[h]=0;
#ifndef STL_EXTENSION
    ostrstream(data_file_name , name_size) << prefix << ".dat" << ends;

    ofstream datafile(data_file_name);
    if (!datafile) {

      cerr << "file error: cannot open file " << data_file_name << endl;
      delete data_file_name;
      return FALSE;

    }
#else
    ostringstream os;
    os << prefix << ".dat" << ends;
    data_string_name= os.str();
    data_file_name= data_string_name.c_str();
    ofstream datafile(data_file_name);
    if (!datafile.is_open()) {

      cerr << "file error: cannot open file " << data_file_name << endl;
      return FALSE;

    }
#endif

    ArrayIter* pnext = iterator();
    ArrayIter& next = *pnext;

    nb_curve = 1;
    double x = xoutset;

    while (next()) {

      if (next.key().tag != AMObjType::UNDEF) { // UNDEF values are discarded
        datafile << x << " ";               // x is printed
        next.key().printValue(datafile);    // y is printed

        if (!XMAXFIXED && (xmax == MAXDOUBLE || xmax < x)) xmax = x;
        if (!XMINFIXED && (xmin == -MAXDOUBLE || xmin > x)) xmin = x;

        if (next.key().tag == AMObjType::INTEGER || next.key().tag == AMObjType::DATE ) {

          double y = (double)next.key().val.i;

          if (!YMAXFIXED && (ymax == MAXDOUBLE || ymax < y)) ymax = y;
          if (!YMINFIXED && (ymin == -MAXDOUBLE || ymin > y)) ymin = y;

        }
        else if (next.key().tag == AMObjType::REAL) {

          if (!YMAXFIXED && (ymax == MAXDOUBLE || ymax < next.key().val.r)) ymax = next.key().val.r;
          if (!YMINFIXED && (ymin == -MAXDOUBLE || ymin > next.key().val.r)) ymin = next.key().val.r;

        }
        else {

          assert(FALSE);

        }

      }

      datafile << endl;

      x += xstep;

    }

    datafile << endl;

    delete pnext;

    datafile.close();

  }
  else  if (nested_level == 2) {

    if (mode == 0) { // the array is either a set of yi, zi, ... or xi, yi, zi, ...

      // creation du fichier de donnees
      //for (int h=0;h<=name_size;h++) data_file_name[h]=0;
#ifndef STL_EXTENSION
      ostrstream(data_file_name , name_size) << prefix << ".dat" << ends;
      ofstream datafile(data_file_name);

      if (!datafile) {

        cerr << "file error: cannot open file " << data_file_name << endl;
        delete data_file_name;
        return FALSE;

      }
#else
      ostringstream os;
      os << prefix << ".dat" << ends;
      data_string_name= os.str();
      data_file_name= data_string_name.c_str();
      ofstream datafile(data_file_name);

      if (!datafile.is_open()) {

        cerr << "file error: cannot open file " << data_file_name << endl;
        return FALSE;

      }

#endif

      nb_curve = 1;
      double x = xoutset;

      ArrayIter* pnextarray = iterator();
      ArrayIter& nextarray = *pnextarray;

      while (nextarray()) {

        if (nextarray.key().tag != AMObjType::UNDEF) {

          assert(nextarray.key().tag == AMObjType::ARRAY);

          Array* coord = (Array*)nextarray.key().val.p;

          ArrayIter* pnext = coord->iterator();
          ArrayIter& next = *pnext;

          int nbel = 0;

          if (coord->entries() > nb_curve) nb_curve = coord->entries();

          while (next()) {

            nbel++;

            if (nbel == 1) {

              datafile << endl;

              if (xaxis == 0) {

                if (!XMAXFIXED && (xmax == MAXDOUBLE || xmax < x)) xmax = x;
                if (!XMINFIXED && (xmin == -MAXDOUBLE || xmin > x)) xmin = x;

                datafile << x << " ";               // x is printed

                x += xstep;

              }

            }
            if (xaxis == nbel) {

              if (next.key().tag() == AMObjType::INTEGER) x = (double)next.key().val.i;
              else if (next.key().tag() == AMObjType::DATE) x = next.key().val.d;
              else if (next.key().tag() == AMObjType::REAL) x = next.key().val.r;
              else break; // bad value of x (AMObjType::UNDEF) skipped

              if (!XMAXFIXED && (xmax == MAXDOUBLE || xmax < x)) xmax = x;
              if (!XMINFIXED && (xmin == -MAXDOUBLE || xmin > x)) xmin = x;

              datafile << x << " ";                 // x is printed

              continue;
            }

            if (next.key().tag != AMObjType::UNDEF) { // UNDEF values are discarded

              next.key().printValue(datafile);    // y is printed
              datafile << " ";

              if (next.key().tag == AMObjType::INTEGER || next.key().tag == AMObjType::DATE) {

                double y = (double)next.key().val.i;

                if (!YMAXFIXED && (ymax == MAXDOUBLE || ymax < y)) ymax = y;
                if (!YMINFIXED && (ymin == -MAXDOUBLE || ymin > y)) ymin = y;

              }
              else if (next.key().tag == AMObjType::REAL) {

                if (!YMAXFIXED && (ymax == MAXDOUBLE || ymax < next.key().val.r)) ymax = next.key().val.r;
                if (!YMINFIXED && (ymin == -MAXDOUBLE || ymin > next.key().val.r)) ymin = next.key().val.r;

              }
              else {

                assert(FALSE);

              }

            }

          }

          delete pnext;

        }

      }

      datafile.close();

      delete pnextarray;

    }
    else {

      assert(mode == 1);

      nb_curve = 1;
      double x = xoutset;

      if (xaxis == 0) nb_curve = entries();
      else nb_curve = entries() - 1;

      ofstream* datafile = new ofstream[nb_curve];

      for (int n=0;n<nb_curve;n++) {

#ifndef STL_EXTENSION
        for (int h=0;h<=name_size;h++) data_file_name[h]=0;
        ostrstream(data_file_name , name_size) << prefix << n+1 << ".dat" << ends;
        datafile[n].open(data_file_name);

        if (!(datafile[n])) {

          cerr << "file error: cannot open file " << data_file_name << endl;
          delete data_file_name;
          return FALSE;

        }
#else
        ostringstream os;
	os << prefix << n+1 << ".dat" << ends;
	data_string_name= os.str();
	data_file_name= data_string_name.c_str();
        datafile[n].open(data_file_name);

        if (!(datafile[n])) {

          cerr << "file error: cannot open file " << data_file_name << endl;
          return FALSE;

        }

#endif
      }

      ArrayIter* pnextarray = iterator();
      ArrayIter& nextarray = *pnextarray;

      Array** pcurve = new Array*[nb_curve];
      int i = 0;
      int* curvesize = new int[nb_curve];
      int maxcurvesize = 0;

      Array* pxaxis;
      int xaxissize;

      int p = 0;

      while (nextarray()) {

        assert(nextarray.key().tag == AMObjType::ARRAY);

        if (p+1 != xaxis) {

          pcurve[i] = (Array*)nextarray.key().val.p;
          curvesize[i] = pcurve[i]->entries();
          if (curvesize[i] > maxcurvesize) maxcurvesize = curvesize[i];

          i++;

        }
        else { // xaxis == i+1

          pxaxis = (Array*)nextarray.key().val.p;
          xaxissize = pxaxis->entries();

        }

        p++;

      }

      if (xaxis == 0) xaxissize = maxcurvesize;


      for (int j=0; j<xaxissize; j++) {

        if (j==0) x -= xstep;

        if (xaxis == 0) {

          x += xstep;

          if (!XMAXFIXED && (xmax == MAXDOUBLE || xmax < x)) xmax = x;
          if (!XMINFIXED && (xmin == -MAXDOUBLE || xmin > x)) xmin = x;

        }
        else {

          if (pxaxis->at(j).tag == AMObjType::INTEGER) x = pxaxis->at(j).val.i;
          else if (pxaxis->at(j).tag == AMObjType::DATE) x = pxaxis->at(j).val.d;
          else if (pxaxis->at(j).tag == AMObjType::REAL) x = pxaxis->at(j).val.r;
          else x += xstep; // case x == Undef;

          if (!XMAXFIXED && (xmax == MAXDOUBLE || xmax < x)) xmax = x;
          if (!XMINFIXED && (xmin == -MAXDOUBLE || xmin > x)) xmin = x;

        }

        for (int k=0; k<nb_curve; k++) {

          if (j < curvesize[k]) {

            datafile[k] << x << " ";

            pcurve[k]->at(j).printValue(datafile[k]);

            if (pcurve[k]->at(j).tag == AMObjType::INTEGER  || pcurve[k]->at(j).tag == AMObjType::DATE) {

              double y = (double)pcurve[k]->at(j).val.i;

              if (!YMAXFIXED && (ymax == MAXDOUBLE || ymax < y)) ymax = y;
              if (!YMINFIXED && (ymin == -MAXDOUBLE || ymin > y)) ymin = y;

            }
            else if (pcurve[k]->at(j).tag == AMObjType::REAL) {

              if (!YMAXFIXED && (ymax == MAXDOUBLE || ymax < pcurve[k]->at(j).val.r)) ymax = pcurve[k]->at(j).val.r;
              if (!YMINFIXED && (ymin == -MAXDOUBLE || ymin > pcurve[k]->at(j).val.r)) ymin = pcurve[k]->at(j).val.r;

            }
            else {

              //assert(FALSE);

            }
          }

          datafile[k] << " ";

        }


        for(int d=0;d<nb_curve;d++) if (j < curvesize[d]-1) datafile[d] << endl;

      }

      delete [] pcurve;
      delete [] curvesize;

      for(int k=0 ;k<nb_curve;k++) datafile[k].close();

      delete [] datafile;

      delete pnextarray;

    }

  }
  else  if (nested_level == 3) { // the array is a set of curves [[x1,y1],[x2,y2],...], [[x'1,y'1],[x'2,y'2],...]

    // cerr << "On rentre dans nested_level == 3" << endl;

    ArrayIter* pcurvearray = iterator();
    ArrayIter& curvearray = *pcurvearray;

    nb_curve = 0;
    double x;
    double y;

    while (curvearray()) {

      if (curvearray.key().tag != AMObjType::UNDEF) {

        nb_curve++;

        // creation du fichier de donnees
        //for (int h=0;h<=name_size;h++) data_file_name[h]=0;
#ifndef STL_EXTENSION
        ostrstream(data_file_name , name_size) << prefix << nb_curve << ".dat" << ends;

        ofstream datafile(data_file_name);

        if (!datafile) {

          cerr << "file error: cannot open file " << data_file_name << endl;
          delete pcurvearray;
          delete data_file_name;
          return FALSE;

        }
#else
        ostringstream os;
	os << prefix << nb_curve << ".dat" << ends;
	data_string_name= os.str();
	data_file_name= data_string_name.c_str();
        ofstream datafile(data_file_name);

        if (!datafile) {

          cerr << "file error: cannot open file " << data_file_name << endl;
          delete pcurvearray;
          return FALSE;

        }

#endif
        assert(curvearray.key().tag == AMObjType::ARRAY);

        Array* coordarray = (Array*)curvearray.key().val.p;

        ArrayIter* pnextpoint = coordarray->iterator();
        ArrayIter& nextpoint = *pnextpoint;

        while(nextpoint()) {

          Array* point = (Array*)nextpoint.key().val.p;

          if (point->entries() != 2) cerr << "ERROR a point should have 2 coord" << endl;
          else {
            if (point->surfaceType() == AMObjType::INTEGER) {
              x = (double) point->at(0).val.i;
              y = (double) point->at(1).val.i;

            }
            else if (point->surfaceType() == AMObjType::DATE) {
              x = (double) point->at(0).val.d;
              y = (double) point->at(1).val.d;

            }
            else if (point->surfaceType() == AMObjType::REAL) {
              x = point->at(0).val.r;
              y = point->at(1).val.r;
            }
            else {

              status = FALSE;

              cerr << "Error: wrong data type, cannot be plotted" << endl;

            }

            if (!XMAXFIXED && (xmax == MAXDOUBLE || xmax < x)) xmax = x;
            if (!XMINFIXED && (xmin == -MAXDOUBLE || xmin > x)) xmin = x;
            if (!YMAXFIXED && (ymax == MAXDOUBLE || ymax < y)) ymax = y;
            if (!YMINFIXED && (ymin == -MAXDOUBLE || ymin > y)) ymin = y;

            datafile << x << " " << y << endl;              // x is printed

          }

        }

        delete pnextpoint;

        datafile.close();

      }

    }

    delete pcurvearray;

  }
  else {

    status = FALSE;

    cerr << "Error: wrong data type, cannot be plotted" << endl;

  }

  if (status) {

    // ecriture du fichier de commandes et du fichier d'impression

#ifndef STL_EXTENSION
    file_name = new char[name_size+1];
#endif
    //for (int h=0;h<=name_size;h++) file_name[h]=0;

    for (i = 0;i < 2;i++) {
#ifndef STL_EXTENSION
      switch (i) {
      case 0 :
        ostrstream(file_name , name_size) << prefix << ".plot" << ends;
        break;
      case 1 :
        ostrstream(file_name , name_size) << prefix << ".print" << ends;
        break;
      }
#else
      ostringstream os;
      switch (i) {
      case 0 :
	os << prefix << ".plot" << ends;
	string_name= os.str();
	file_name= string_name.c_str();
        break;
      case 1 :
	os << prefix << ".print" << ends;
	string_name= os.str();
	file_name= string_name.c_str();
        break;
      }
#endif

      ofstream out_file(file_name);

      if (i == 1) {
        out_file << "set terminal postscript" << endl;
#ifndef STL_EXTENSION
        ostrstream(file_name , name_size) << prefix << ".eps" << ends;
#else
        ostringstream os;
	os << prefix << ".eps" << ends;
	string_name= os.str();
	file_name= string_name.c_str();
#endif
        out_file << "set output \"" << file_name << "\"\n\n";
      }

      // out_file << "set noborder\n" << "set tics out\n"
      // << "set title";
      out_file << "set border 15 lw 0\n" << "set tics out\n" << "set xtics nomirror\n"
               << "set title";
      if (title) {
        out_file << " \"" << title << "\"";   // titre de la figure
      }
      out_file << "\nset xlabel";
      if (xtitle) {
        out_file << " \"" << xtitle << "\"";   // titre de la figure
      }
      out_file << "\nset ylabel";
      if (ytitle) {
        out_file << " \"" << ytitle << "\"";   // titre de la figure
      }

      out_file << "\n\n";

      ymax = ymax + abs(ymax-ymin)* 0.2; // not to superimpose titles and curves

      if (xmin == xmax) xmax++; // bug de gnuplot qui refuse [1,1] par exemple
      if (ymin == ymax) ymax++; // bug de gnuplot qui refuse [1,1] par exemple

      out_file << "plot [" << xmin << ":" << xmax << "] [" << ymin << ":" << ymax << "] ";

      if (xaxis == 0) {

        int test=nested_level == 3 || nested_level == 2 && mode == 1;

        for (register int j = 0;j < nb_curve;j++) { // nb_curve + xaxis
          //for (int h=0;h<=name_size;h++) data_file_name[h]=0;
          if (test) {
#ifndef STL_EXTENSION
            ostrstream(data_file_name , name_size) << prefix << j+1 << ".dat" << ends;
#else
	    ostringstream os;
	    os << prefix << j+1 << ".dat" << ends;
	    data_string_name= os.str();
	    data_file_name= data_string_name.c_str();
#endif
          }
          out_file << "\"" << data_file_name << "\" using " << xaxis+1 << ":" << ((test) ? 2 : j+2);
          if (titles && j<titles->entries()) out_file << " title \"" << *(AMString*)(titles->at(j).val.p) << "\"";
          else out_file << " title \"" << "\"";
          out_file << " with " << style;
          if (j < nb_curve - 1) {
            out_file << ",\\";
          }
          out_file << endl;
        }
      }
      else { // xaxis != 0

        int test = nested_level == 2 && mode == 1;

        if (!test) {
          int flag = FALSE;
          for (register int j = 0;j < nb_curve;j++) { // nb_curve + xaxis
            if (xaxis != j+1) {
              if (flag == TRUE) {
                out_file << ",";
              }
              out_file << "\\" << endl;
              flag = TRUE;
              out_file << "\"" << data_file_name << "\" using " << xaxis << ":" << j+1;
              if (titles && j<titles->entries()) out_file << " title \"" << *(AMString*)(titles->at(j).val.p)<< "\"";
              else out_file << " title \"" << "\"";
              out_file << " with " << style;
            }
          }
        }
        else {

          int flag = FALSE;
          for (register int j = 0;j < nb_curve;j++) { // nb_curve + xaxis
            //for (int h=0;h<=name_size;h++) data_file_name[h]=0;
#ifndef STL_EXTENSION
            ostrstream(data_file_name , name_size) << prefix << j+1 << ".dat" << ends;
#else
	    ostringstream os;
	    os << prefix << j+1 << ".dat" << ends;
	    data_string_name= os.str();
	    data_file_name= data_string_name.c_str();
#endif
            if (flag == TRUE) {
              out_file << ",";
            }
            out_file << "\\" << endl;
            flag = TRUE;
            out_file << "\"" << data_file_name << "\" using " << 1 << ":" << 2;
            if (titles && j<titles->entries()) out_file << " title \"" << *(AMString*)(titles->at(j).val.p)<< "\"";
            else out_file << " title \"" << "\"";
            out_file << " with " << style;
          }

        }
        out_file << endl;

      }


      if (i == 1) out_file << "\nset terminal x11" << endl;

      out_file << "\npause 0 \"End.\"" << endl;

      out_file.close();

    }

#ifndef STL_EXTENSION
    delete file_name;
#endif
  }

#ifndef STL_EXTENSION
  delete data_file_name;
#endif

  return status;

}


AMObj SLArray::plot(GP_window& window, const AMObjVector& args) const
{

  int argth = 1;
  int len = args.length();

  const char *title = "";
  const char *xtitle = "";
  const char *ytitle = "";

  char buffer[DP_PLOT_SIZE];

  ifstream in_file;

  Array* titles = 0;
  const char* style = "linespoints";
  int mode = 0;
  int xaxis = 0;

  double xoutset = 0;
  double xstep = 1;

  double xmin=-MAXDOUBLE , ymin=-MAXDOUBLE;
  double xmax=MAXDOUBLE , ymax=MAXDOUBLE;

  // argument obligatoire

  if (len > 0) {
    CHECKCONDVA(args[0].tag() == AMObjType::ARRAY,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , 1, args[0].tag.string().data(), "ARRAY"));

  }

  // argument optionnel

  while (argth < len) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , (argth+1)/2+1, args[argth].tag.string().data(), "OPTION"));

    assert(argth + 1 < len); // must contain at least two parameters : this is verified syntactically

    if (*(AMString*)(args[argth].val.p) == "XAxis") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT"));

      CHECKCONDVA(args[argth+1].val.i > 0,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "positive"));

      xaxis = args[argth+1].val.i;

    }
    else if (*(AMString*)(args[argth].val.p) == "XOutset") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER || args[argth+1].tag() ==AMObjType::REAL,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT or REAL"));

      if (args[argth+1].tag() ==AMObjType::INTEGER) xoutset = (double)args[argth+1].val.i;
      if (args[argth+1].tag() ==AMObjType::REAL) xoutset = args[argth+1].val.r;

    }
    else if (*(AMString*)(args[argth].val.p) == "XStep") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER || args[argth+1].tag() ==AMObjType::REAL,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT or REAL"));

      if (args[argth+1].tag() ==AMObjType::INTEGER) xstep = (double)args[argth+1].val.i;
      if (args[argth+1].tag() ==AMObjType::REAL) xstep = args[argth+1].val.r;

    }
    else if (*(AMString*)(args[argth].val.p) == "XMax") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER || args[argth+1].tag() ==AMObjType::REAL,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT or REAL"));

      if (args[argth+1].tag() ==AMObjType::INTEGER) xmax = (double)args[argth+1].val.i;
      if (args[argth+1].tag() ==AMObjType::REAL) xmax = args[argth+1].val.r;

    }
    else if (*(AMString*)(args[argth].val.p) == "XMin") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER || args[argth+1].tag() ==AMObjType::REAL,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT or REAL"));

      if (args[argth+1].tag() ==AMObjType::INTEGER) xmin = (double)args[argth+1].val.i;
      if (args[argth+1].tag() ==AMObjType::REAL) xmin = args[argth+1].val.r;

    }
    else if (*(AMString*)(args[argth].val.p) == "YMax") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER || args[argth+1].tag() ==AMObjType::REAL,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT or REAL"));

      if (args[argth+1].tag() ==AMObjType::INTEGER) ymax = (double)args[argth+1].val.i;
      if (args[argth+1].tag() ==AMObjType::REAL) ymax = args[argth+1].val.r;

    }
    else if (*(AMString*)(args[argth].val.p) == "YMin") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::INTEGER || args[argth+1].tag() ==AMObjType::REAL,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "INT or REAL"));

      if (args[argth+1].tag() ==AMObjType::INTEGER) ymin = (double)args[argth+1].val.i;
      if (args[argth+1].tag() ==AMObjType::REAL) ymin = args[argth+1].val.r;

    }
    else if (*(AMString*)(args[argth].val.p) == "Title") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      title = ((AMString*)(args[argth+1].val.p))->data();

    }
    else if (*(AMString*)(args[argth].val.p) == "XTitle") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      xtitle = ((AMString*)(args[argth+1].val.p))->data();

    }
    else if (*(AMString*)(args[argth].val.p) == "YTitle") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      ytitle = ((AMString*)(args[argth+1].val.p))->data();

    }
    else if (*(AMString*)(args[argth].val.p) == "Groups") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      if ( (*(AMString*)(args[argth+1].val.p)) == "Curves") mode = 1 ;
      else {
        if ( (*(AMString*)(args[argth+1].val.p)) == "Points") mode = 0 ;
        else {
        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "one of 'Curves' or 'Points'"));

        }
      }

    }
    else if (*(AMString*)(args[argth].val.p) == "Style") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      AMString stg = *(AMString*)(args[argth+1].val.p);
      style = stg.data();

      // allowed styles :
      // 'lines', 'points', 'linespoints', 'dots', 'impulses',
      // 'errorbars', 'steps', 'boxes' or 'boxerrorbars'
      if (stg != "lines" &&
          stg != "points" &&
          stg != "linespoints" &&
          stg != "dots" &&
          stg != "impulses" &&
          stg != "errorbars" &&
          stg != "steps" &&
          stg != "boxes" &&
          stg != "boxerrorbars" ) {

        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "Plot", (argth+1)/2+1, "one of 'lines', 'points', 'linespoints', 'dots', 'impulses', 'errorbars', 'steps', 'boxes' or 'boxerrorbars'"));


      }

    }
    else if (*(AMString*)(args[argth].val.p) == "SeriesTitle") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::ARRAY,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY(STRING)"));

      CHECKCONDVA(((Array*)(args[argth+1].val.p))->surfaceType() == AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Plot", (argth+1)/2+1, args[argth+1].tag.string().data(), "ARRAY(STRING)"));

      titles = (Array*)(args[argth+1].val.p);

    }
    else if (*(AMString*)(args[argth].val.p) == "Window") {
    }
    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "plot", (argth+1)/2+1));

    }

    argth += 2;

  }

  if (len > 0) {

    // destruction des fichiers Gnuplot courants

    //for (int h=0;h<DP_PLOT_SIZE;h++) buffer[h]=0;
#ifdef _WIN32
          if(VPTOOLS(exists)(string(Plot_prefix)+".plot")){
			std::string cmd = string("ERASE /F /Q ") + Plot_prefix + "*";
			system(cmd.c_str());
          }
#else
#ifndef STL_EXTENSION
    ostrstream(buffer , DP_PLOT_SIZE) << "rm -f " << Plot_prefix << "*" << ends;
    system(buffer);
#else
    ostringstream os;
    os << "rm -f " << Plot_prefix << "*" << ends;
    system(os.str().c_str());
    os.str("");
#endif
#endif

    // generation des fichiers Gnuplot

    if (!plotWrite(Plot_prefix , title, xtitle, ytitle, titles, style, mode, xaxis, xoutset, xstep, xmin, xmax, ymin, ymax)) {

      return AMObj(AMObjType::ERROR);

    }

    //for (int h=0;h<DP_PLOT_SIZE;h++) buffer[h]=0;
#ifndef _WIN32
#ifndef STL_EXTENSION
    ostrstream(buffer , DP_PLOT_SIZE) << "chmod 666 " << Plot_prefix << "*" << ends;
    system(buffer);
#else
    os << "chmod 666 " << Plot_prefix << "*" << ends;
    system(os.str().c_str());
    os.str("");

#endif
#endif
  }

// #ifndef GNU_STL_EXTENSION
//  ostrstream(prefix , DP_PLOT_SIZE) << Plot_prefix << ends;

//  ostrstream(buffer , DP_PLOT_SIZE) << prefix << ".plot" << ends;
/// Gnuplot port pb
//  in_file.open(buffer , ios::nocreate);
// option ios::nocreate is, in std, the default option
//  in_file.open(buffer);
// #else

  // prefix= Plot_prefix;
  string name= string( Plot_prefix )+".plot";
  in_file.open( name.c_str() );

// #endif

  if (in_file.fail()) {
    genAMLError(ERRORMSG(K_F_FILE_ERR_sss) , "Plot", "temporary file", name.c_str());
    return AMObj(AMObjType::ERROR);
  }

  in_file.close();

  window.session(Plot_prefix , AMLOUTPUT);

  return AMObj(AMObjType::VOID);

}


int Array::nestedDepth() const {

  int nested_level = 0;

  const AMObj* pelem = anElement();

  while (pelem && nested_level != -1) {

    nested_level++;

    if (pelem->tag == AMObjType::ARRAY) {
      pelem = ((Array*)(pelem->val.p))->anElement();
    }
    else break;

  }

  if (!pelem) nested_level++; // cas d'un tableau vide

  return nested_level;

}



int SLArray::saveWrite(const AMObj& array, const char* prefix) const {

#ifndef STL_EXTENSION
  char *data_file_name;
#else
  const char *data_file_name;
#endif
  int name_size = strlen(prefix) + 10;

  int status = TRUE;

  // ecriture du fichier de donnees

#ifndef STL_EXTENSION
  data_file_name = new char[name_size+1];
  for (int h=0;h<=name_size;h++) data_file_name[h]=0;
  ostrstream(data_file_name , name_size) << prefix << ends;
#else
  ostringstream os;
  os << prefix << ends;
  data_file_name= os.str().c_str();
#endif
  // Creer le fichier de donnees GNUPLOT
  //int status = plot_print(data_file_name);

  ofstream datafile(data_file_name);

  if (!datafile) {

    AMLOUTPUT << "file error: cannot open file " << data_file_name << endl;
#ifndef STL_EXTENSION
    delete data_file_name;
#endif
    return FALSE;

  }

  array.printValue(datafile);

  datafile.close();

  AMLOUTPUT << "object saved in " << data_file_name << endl;

#ifndef STL_EXTENSION
  delete data_file_name;
#endif
  return status;

}

AMObj SLArray::save(const AMObjVector& args) const {

  int argth = 2;
  int len = args.length();

  const char *fileprefix;
  int spreadsheetflag = FALSE;

  // 2 arguments obligatoires

  CHECKCONDVA(len >= 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Save" , 2));

  CHECKCONDVA(args[0].tag() == AMObjType::ARRAY,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , 1, args[0].tag.string().data(), "ARRAY"));

  CHECKCONDVA(args[1].tag() ==AMObjType::STRING,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Save", 2, args[1].tag.string().data(), "STRING"));

  fileprefix = ((AMString*)(args[1].val.p))->data();

  CHECKCONDVA(strlen(fileprefix) != 0,
              genAMLError(ERRORMSG(K_F_ARG_VALUE_NEG_ERR_sds), "Save", 2, "an empty string"));


  // argument optionnel

  while (argth < len) { // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , argth/2+2, args[argth].tag.string().data(), "OPTION"));

    assert(argth + 1 < len); // must contain at least two parameters : this is verified syntactically

    if (*(AMString*)(args[argth].val.p) == "Format") {

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Save", argth/2+2, args[argth+1].tag.string().data(), "STRING"));

      CHECKCONDVA(args[argth+1].tag() ==AMObjType::STRING,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "Save", (argth+1)/2+1, args[argth+1].tag.string().data(), "STRING"));

      AMString stg = *(AMString*)(args[argth+1].val.p);

      if (stg != "SpreadSheet" &&
          stg != "ASCII" ) {

        CHECKCONDVA(FALSE,
                    genAMLError(ERRORMSG(K_F_ARG_VALUE_ERR_sds), "Save", (argth+1)/2+1, "one of 'ASCII' or 'SpreadSheet'"));
      }
      spreadsheetflag = TRUE;

    }
    else {

      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Save", argth/2+2));

    }

    argth += 2;

  }

  if (len > 0) {

    if (spreadsheetflag) {
#ifndef STL_EXTENSION
      char* data_file_name;
#else
      const char* data_file_name;
#endif
      int name_size = strlen(fileprefix) + 10;

#ifndef STL_EXTENSION
      data_file_name = new char[name_size+1];
      for (int h=0;h<=name_size;h++) data_file_name[h]=0;
      ostrstream(data_file_name , name_size) << fileprefix << ends;
#else
      ostringstream os;
      os << fileprefix << ends;
      data_file_name=os.str().c_str();
#endif
      ofstream datafile(data_file_name);

      if (!datafile) {

        cerr << "file error: cannot open file " << data_file_name << endl;
#ifndef STL_EXTENSION
        delete data_file_name;
#endif
        return AMObj(AMObjType::ERROR);


      }

      ((Array*)args[0].val.p)->displaySpreadSheet(datafile);

      datafile.close();

      AMLOUTPUT << "object saved in " << data_file_name << endl;

#ifndef STL_EXTENSION
      delete data_file_name;
#endif
    }
    else if (!saveWrite(args[0], fileprefix)) {

      return AMObj(AMObjType::ERROR);

    }

  }

  return AMObj(AMObjType::VOID);

}
