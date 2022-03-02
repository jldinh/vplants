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
 *       $Id: date.cpp 17611 2014-10-17 13:20:41Z pradal $
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




#include <cassert>
#include <cstdlib>
#include <cctype>
#include <cstring>

#include "tool/rw_locale.h"
#include "tool/rw_zone.h"
#include "tool/rw_date.h"
#include "tool/rw_time.h"
#include "tool/rw_tokenizer.h"

//#include <rw/locale.h>
//#include <rw/zone.h>
//#include <rw/rwdate.h>
//#include <rw/rwtime.h>
//#include <rw/ctoken.h>

#include "defs.h"
#include "date.h"

static RWLocale* pfrench = 0;
static RWZone* pzone = 0;

// Warning: this function can only be used for a date after 1/1/1970
// (cf the Unix lib: man ctime)
// lib RogueWave can do better difficult (impossible?) to output a date with a param format !

RWCString printDate(const RWTime& t,int type) {

  struct tm tmp;
  char buf[50];

  t.extract(&tmp); // fills the struct tm

  switch(type) {
  case DDMM:
    strftime(buf, 50, "%d/%m", &tmp);
    break;
  case DDMMYY:
    strftime(buf, 50, "%d/%m/%y", &tmp);
    break;
  case MMYY:
    strftime(buf, 50, "%m/%y", &tmp);
    break;
  case DDMMTIME:
    strftime(buf, 50, "%d/%m %H:%M", &tmp);
    break;
  case DDMMYYTIME:
    strftime(buf, 50, "%d/%m/%y %H:%M", &tmp);
    break;
  }
  return buf;

}


void installLocale() {

  pzone = new RWZoneSimple(RWZone::Europe, RWZone::WeEu);

  RWZone::locale(pzone); // sets the local as Europe for times

  pfrench = new RWLocaleSnapshot("fr");
  if(pfrench)
    {
    ((RWLocaleSnapshot*)pfrench)->dateOrder_ = RWLocaleSnapshot::DMY;              // for parsing correctly the dates

    RWLocale::global(pfrench);                     // sets French date and number formats as globals
    }
}

void removeLocale() {

  delete pzone;

  delete pfrench;

}

RWCString itorwcstring(long i) {

  assert(pfrench);

  return pfrench->asString(i);

}


static AmlBoolean onlyDigits(const char* stg) {
    register int i;
    for( i=0; i< strlen(stg); i++) if (!isdigit(stg[i])) return FALSE;
    return TRUE;
}

Date encodeDate(const char* stg, int type) {

  RWCString alpha(stg);

  AmlBoolean error = FALSE;

  unsigned int day = 1;         // default values
  unsigned int month = 1;
  unsigned int year = 90;

  unsigned int hour = 0;
  unsigned int minute = 0;
  unsigned int second = 0;

  switch(type) {

    case DDMM:
    {

      RWCTokenizer next1(alpha);
      RWCString date = next1();
      assert(!date.isNull());
      RWCString time = next1();
      if (!time.isNull()) {
        error = TRUE;
        break;
      }

      RWCTokenizer next(date);
      RWCString token;

      token = next("/");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) day = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next("/");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) month = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next("/");
      if (!token.isNull()) error = TRUE;

    }
      break;

    case DDMMYY:
    {

      RWCTokenizer next1(alpha);
      RWCString date = next1();
      assert(!date.isNull());
      RWCString time = next1();
      if (!time.isNull()) {
        error = TRUE;
        break;
      }

      RWCTokenizer next(date);
      RWCString token;

      token = next("/");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) day = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next("/");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) month = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next("/");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) year = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next("/");
      if (!token.isNull()) error = TRUE;

    }
    break;

    case MMYY:
    {

      RWCTokenizer next1(alpha);
      RWCString date = next1();
      assert(!date.isNull());
      RWCString time = next1();
      if (!time.isNull()) {
        error = TRUE;
        break;
      }

      RWCTokenizer next(date);
      RWCString token;

      token = next("/");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) month = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next("/");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) year = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next("/");
      if (!token.isNull()) error = TRUE;

    }
    break;

    case DDMMTIME:
    {
      RWCTokenizer next1(alpha);
      RWCString date = next1();
      assert(!date.isNull());
      RWCString time = next1();

      RWCTokenizer next(date);
      RWCString token;

      token = next("/");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) day = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next("/");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) month = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next("/");
      if (!token.isNull()) {
        error = TRUE;
        break;
      }

      RWCTokenizer next2(time);

      token = next2(":");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) hour = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next2(":");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) minute = atoi(token.data());
      else break;

      token = next2(":");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) second = atoi(token.data());
      else break;

      token = next2(":");
      if (!token.isNull()) error = TRUE;

    }
    break;

    case DDMMYYTIME:
    {

      RWCTokenizer next1(alpha);
      RWCString date = next1();
      assert(!date.isNull());
      RWCString time = next1();

      RWCTokenizer next(date);
      RWCString token;

      token = next("/");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) day = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next("/");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) month = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next("/");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) year = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next("/");
      if (!token.isNull()) {
        error = TRUE;
        break;
      }

      RWCTokenizer next2(time);

      token = next2(":");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) hour = atoi(token.data());
      else {
        error = TRUE;
        break;
      }

      token = next2(":");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) minute = atoi(token.data());
      else break;

      token = next2(":");
      if (!onlyDigits(token.data())) {
        error = TRUE;
        break;
      }
      if (!token.isNull()) second = atoi(token.data());
      else break;

      token = next2(":");
      if (!token.isNull()) error = TRUE;

    }
    break;

  }

  if (error == TRUE) {

    return (unsigned long)LUNDEF;

  }

  // cerr << "found : d=" << day << ", m=" << month << ", y=" << year << endl;
  // cerr << "found : H=" << hour << ", M=" << minute << ", s=" << second << endl;

  RWDate date(day, month, year);

  if (!date.isValid()) {

    return (unsigned long)LUNDEF;

  }

  RWTime time(date, hour, minute, second);

  if (!time.isValid()) {

    return (unsigned long)LUNDEF;

  }

  // cerr << endl << "date stored= " << printDate(time, type)
  // << "(code = " << time.seconds() << ", stored = " << (int) time.seconds() << ")" << endl;

  return time.seconds(); // number of seconds since 00:00:00 January, 1901 UTC

}

