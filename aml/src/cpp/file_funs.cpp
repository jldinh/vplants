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
 *       $Id: file_funs.cpp 7393 2009-12-15 13:26:33Z moscardi $
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



#include "aml/file_funs.h"

#include "aml/erroraml.h"
#include "aml/parseraml.h"
#include "aml/fnode.h"
#include "aml/kernel_err.h"
#include "aml/kernel_funs.h"
#include "aml/global.h"

#include "aml/set.h"
#include "aml/array.h"
#include "aml/list.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <stdlib.h>
#include <errno.h>

#include <QtCore/qfile.h>
#include <QtCore/qdir.h>
#include <QtCore/qstringlist.h>
#if defined( __GNUC__ ) && ! defined(  __MINGW32__ )

#include <unistd.h>
#include <dirent.h>

#else

//#include <qfile.h>
//#include <qdir.h>
//#include <qstringlist.h>
#include "file_funs2.h"

#ifdef _WIN32
#include <io.h>
#include <direct.h>
#define access _access
#define F_OK 0
#define mkdir(a,b) _mkdir(a)
#endif

#endif


#include "tool/dirnames.h"
#include "tool/util_enviro.h"
#include "plantgl/gui/viewer/pglapplication.h"

VPTOOLS_USING_NAMESPACE
using namespace std;

#define  ERR_MSG_ARRAY          kernel_err_msgs_aml
#define  MODULE_NAME            "File"

/*  ------------------------------------------------------------------------ */

static AMObj F_Exists(const AMObjVector& args) {

    CHECKCONDVA(args.length() > 0,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Exists", 1));
    int len = args.length();
    int argth = 0;
    int mode = 0;
    string path;

  while (argth < len) {
      if (*(AMString*)(args[argth].val.p) == "Type") {
          if (args[argth+1].tag() != AMObjType::STRING){
            genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Exists", (argth+1)/2+1, "File or Directory");
            return AMObj(AMObjType::UNDEF);
          }
          if (*(AMString*)(args[argth+1].val.p) == "Directory") {
              mode += 1;
          }
          else if (*(AMString*)(args[argth+1].val.p) == "File") {
              mode += 2;
          }
          else {
              genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Exists", (argth+1)/2+1, "File or Directory");
          }
          argth++;
      }
      else if (args[argth].tag() == AMObjType::STRING) {
          path= string(((AMString*)(args[argth].val.p))->data());
      }
      argth++;
  }
  if(path.empty()){
      CHECKCONDVA(FALSE,
                  genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd), "Exists", 0));
      return AMObj(AMObjType::UNDEF);
  }
  if(!access(path.c_str(),F_OK)){
      if(mode == 0 || mode == 3)return AMObj(AMObjType::BOOL,TRUE);
      else {
#ifdef __GNUC__
                  struct stat * buf = new struct stat();
          if(stat(path.c_str(),buf) == -1){
            delete buf;
            return AMObj(AMObjType::BOOL,FALSE);
          }
          if( mode == 1 && S_ISDIR(buf->st_mode) == true){
            delete buf;
            return AMObj(AMObjType::BOOL,TRUE);
          }
          else if(S_ISREG(buf->st_mode) == true){
            delete buf;
            return AMObj(AMObjType::BOOL,TRUE);
          }
          delete buf;
#else
          QFileInfo fileinfo(path.c_str());
          if(!fileinfo.exists())return AMObj(AMObjType::BOOL,FALSE);
          else if ( mode == 1 && fileinfo.isDir() )return AMObj(AMObjType::BOOL,TRUE);
          else if ( mode == 2 && fileinfo.isFile() )return AMObj(AMObjType::BOOL,TRUE);
#endif
          return AMObj(AMObjType::BOOL,FALSE);
      }
  }
  else return AMObj(AMObjType::BOOL,FALSE);
}

/*  ------------------------------------------------------------------------ */

static AMObj F_Rm(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Rm", 1));

  if (args[0].tag() == AMObjType::STRING) {
      string arg(((AMString*)(args[0].val.p))->data());
#ifndef __GNUC__
          QDir path(arg.c_str());
          if(path.exists()){
                  QString name = path.dirName();
                  path.cdUp();
                  if(path.rmdir(name))
                        return AMObj(AMObjType::BOOL,TRUE);
                  else return AMObj(AMObjType::BOOL,FALSE);

          }
          else {
                if(QFile::remove(arg.c_str()))return AMObj(AMObjType::BOOL,TRUE);
                else return AMObj(AMObjType::BOOL,FALSE);

          }
#else
      if(!unlink(arg.c_str()))return AMObj(AMObjType::BOOL,TRUE);
      else {
          switch (errno) {
              case (EISDIR) :
                  AMLOUTPUT << arg.c_str() << " is a directory." << endl;
                  if(!rmdir(arg.c_str())) return AMObj(AMObjType::BOOL,TRUE);
                  else {
                      switch (errno) {
                          case (ENOMEM) :
                              AMLOUTPUT << "No memory available." << endl;
                              return AMObj(AMObjType::BOOL,FALSE);
                              break;
                          case (EISDIR) :
                              AMLOUTPUT << arg.c_str() << " is not a directory." << endl;
                              return AMObj(AMObjType::BOOL,FALSE);
                              break;
                          case (EBUSY) :
                              AMLOUTPUT << arg.c_str() << " is busy." << endl;
                              return AMObj(AMObjType::BOOL,FALSE);
                              break;
                          case (ENOTEMPTY) :
                              AMLOUTPUT << arg.c_str() << " is not empty." << endl;
                              return AMObj(AMObjType::BOOL,FALSE);
                              break;
                          case (EPERM) :
                          case (EACCES) :
                              AMLOUTPUT << "Unvalid access right." << endl;
                              return AMObj(AMObjType::BOOL,FALSE);
                              break;
                          default :
                              AMLOUTPUT << "Unvalid Filename." << endl;
                              return AMObj(AMObjType::BOOL,FALSE);
                              break;
                      }
                  }
                  break;
              case (ENOMEM) :
                  AMLOUTPUT << "No memory available." << endl;
                  return AMObj(AMObjType::BOOL,FALSE);
                  break;
              case (EPERM) :
              case (EACCES) :
                  AMLOUTPUT << "Unvalid access right." << endl;
                  return AMObj(AMObjType::BOOL,FALSE);
                  break;
              default :
                  AMLOUTPUT << "Unvalid Filename." << endl;
                  return AMObj(AMObjType::BOOL,FALSE);
                  break;
          }
      }
#endif
  }
  return AMObj(AMObjType::ERROR);
}

/*  ------------------------------------------------------------------------ */

static AMObj F_Cd(const AMObjVector& args) {

  CHECKCONDVA(args.length() <= 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Cd", 1));
  if(args.length() == 0){
      string p = getHome();
      if(chg_dir(p)){
          amobjTable()->remove(":CWD");
          amobjTable()->insert(":CWD",AMObj(AMObjType::STRING, new AMString(p.c_str())));
          return AMObj(AMObjType::BOOL,TRUE);
      }
  }
  else if (args[0].tag() == AMObjType::STRING) {
      string arg(((AMString*)(args[0].val.p))->data());
      string p = absolute_dirname(arg);
      if(chg_dir(p)){
          amobjTable()->remove(":CWD");
          amobjTable()->insert(":CWD",AMObj(AMObjType::STRING, new AMString(p.c_str())));
          return AMObj(AMObjType::BOOL,TRUE);
      }
      else return AMObj(AMObjType::BOOL,FALSE);

  }
  return AMObj(AMObjType::ERROR);
}

/*  ------------------------------------------------------------------------ */

static AMObj F_Mkdir(const AMObjVector& args) {

  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Mkdir", 1));

  if (args[0].tag() == AMObjType::STRING) {
      string arg(((AMString*)(args[0].val.p))->data());
      if(!mkdir(arg.c_str(), 0755))
          return AMObj(AMObjType::BOOL,TRUE);
      else return AMObj(AMObjType::BOOL,FALSE);
  }
  return AMObj(AMObjType::UNDEF);
}

/*  ------------------------------------------------------------------------ */

static AMObj F_Lsdir(const AMObjVector& args) {

    int len = args.length();
    int argth = 0;
    int mode = 0;
    string path(".");

    while (argth < len) {
        if (*(AMString*)(args[argth].val.p) == "Type" && argth+1 < len) {
          if (args[argth+1].tag() != AMObjType::STRING){
            genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Dir", (argth+1)/2+1, "File or Directory");
            return AMObj(AMObjType::UNDEF);
          }
          string flag = string((*(AMString*)(args[argth+1].val.p)).data());
          AMLOUTPUT << flag << endl;
          if (flag == "Directory") {
            mode += 1;
          }
          else if (flag == "File") {
            mode += 2;
          }
          else {
            genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Dir", (argth+1)/2+1, "File or Directory");
            return AMObj(AMObjType::UNDEF);
          }
          argth++;
        }
        else if (args[argth].tag() == AMObjType::STRING) {
            path= string(((AMString*)(args[argth].val.p))->data());
        }
        argth++;
    }
    path = absolute_dirname(path);

#if defined( __GNUC__ ) && ! defined(  __MINGW32__ )
    DIR      *dir;
    dirent   *file;
    dir = opendir( path.c_str() );
    Array* ret = new SLArray;
    if(!dir){
        AMLOUTPUT << "Cannot read directory " << path.c_str() << endl;
    }
    else {
        AMLOUTPUT << "Directory : " << path.c_str() << endl;
        while ( (file = readdir(dir)) ) {
            if(!(file->d_name[0] == '.' && (file->d_name[1] == '.' || file->d_name[1] == '\0' ))){
                struct stat * buf = new struct stat();
                stat(file->d_name,buf);
                if(mode == 0 ||
                   ( mode == 1 && S_ISDIR(buf->st_mode) == true) ||
                   ( mode == 2 && S_ISREG(buf->st_mode) == true) ){
                    (*ret) += AMObj(AMObjType::STRING,new AMString(file->d_name));
                    AMLOUTPUT << (S_ISDIR(buf->st_mode) == true ? "<DIRECTORY> : " : "<FILE>      : ")
                         << file->d_name << endl;
                }
            }
        }
        if ( closedir(dir) != 0 ) {
            AMLOUTPUT << "Cannot close directory " << path.c_str() << endl;
        }
    }
    return AMObj(AMObjType::ARRAY,ret);
#else
        QDir dir(path.c_str() );
        Array* ret = new SLArray;
    if(!dir.isReadable()){
                AMLOUTPUT << "Cannot read directory " << path.c_str() << endl;
    }
    else {
        AMLOUTPUT << "Directory : " << path.c_str() << endl;
        QStringList filenames = dir.entryList();
        uint32_t f_count = filenames.count();
        for(uint32_t i = 0 ; i < f_count ; i++  ) {
                QString filename =      filenames.at(i);
                QFileInfo file(dir.absolutePath() + '/' + filename);
            if(!(filename[0] == '.' && (filename[1] == '.' || filename[1] == '\0' )) ){
                if(mode == 0                      ||
                   ( mode == 1 && file.isDir()  ) ||
                   ( mode == 2 && file.isFile() )   ){
                    (*ret) += AMObj(AMObjType::STRING,new AMString(filename.toStdString()));
                    AMLOUTPUT << (file.isDir() == true ? "<DIRECTORY> : " : "<FILE>      : ")
                         << string( filename.toLatin1() ) << endl;
                }
            }
        }
        }
    return AMObj(AMObjType::ARRAY,ret);

#endif
}

/*  ------------------------------------------------------------------------ */

static AMObj F_Pwd(const AMObjVector& args) {
  CHECKCONDVA(args.length() == 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Pwd", 0));
  string p = absolute_dirname(".");
  amobjTable()->remove(":CWD");
  AMObj res(AMObjType::STRING, new AMString(p.c_str()));
  amobjTable()->insert(":CWD",res);
  return res;
}

/*  ------------------------------------------------------------------------ */

static AMObj F_SetAmapmodDir(const AMObjVector& args) {
  CHECKCONDVA(args.length() == 1,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "SetAmapmodDir", 1));
  if (args[0].tag() != AMObjType::STRING ){
    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "SetAmapmodDir", 0, "<STRING>");
    return AMObj(AMObjType::UNDEF);
  }
  string p = *((AMString*)(args[0].val.p));
 /* if (!exists(p)){
    AMLOUTPUT << "Directory " << p << " not exist." << endl;
    return AMObj(AMObjType::BOOL,FALSE);
  } */
  setAMAPmodDir(p);
  amobjTable()->remove(":AMAPMOD_DIR");
  AMObj res(AMObjType::STRING, new AMString(p.c_str()));
  amobjTable()->insert(":AMAPMOD_DIR",res);
  return AMObj(AMObjType::BOOL,TRUE);
}

/*  ------------------------------------------------------------------------ */

static AMObj F_Rename(const AMObjVector& args) {
  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Rename", 2));
  if (args[0].tag() != AMObjType::STRING ){
    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Rename", 0, "<STRING>");
    return AMObj(AMObjType::UNDEF);
  }
  if (args[1].tag() != AMObjType::STRING){
    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Rename", 1, "<STRING>");
    return AMObj(AMObjType::UNDEF);
  }
  if (!access((*(AMString*)(args[1].val.p)),F_OK)){
    AMLOUTPUT << "File " << (*(AMString*)(args[1].val.p)) << " already exist." << endl;
    return AMObj(AMObjType::BOOL,FALSE);
  }
  AMObjVector argsE(3);
  argsE[0] = args[0];
  argsE[1] = AMObj(AMObjType::STRING, new AMString("Type"));
  argsE[2] = AMObj(AMObjType::STRING, new AMString("File"));
  AMObj r = F_Exists(argsE);
  if((r.tag() == AMObjType::BOOL) && (r.val.b == TRUE)){
        if(!rename((*(AMString*)(args[0].val.p)),(*(AMString*)(args[1].val.p)))){
      AMLOUTPUT << "Renaming file succeed." << endl;
      return AMObj(AMObjType::BOOL,TRUE);
    }
    AMLOUTPUT << "Renaming file failed." << endl;
    return AMObj(AMObjType::BOOL,FALSE);
  }
  else {
    AMLOUTPUT << "File " << (*(AMString*)(args[0].val.p)) << " does not exist." << endl;
    return AMObj(AMObjType::BOOL,FALSE);
  }
}

/*  ------------------------------------------------------------------------ */

// #ifdef __GNUC__

static AMObj F_Copy(const AMObjVector& args) {
  CHECKCONDVA(args.length() == 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "Copy", 2));
  if (args[0].tag() != AMObjType::STRING ){
    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Copy", 0, "<STRING>");
    return AMObj(AMObjType::UNDEF);
  }
  if (args[1].tag() != AMObjType::STRING){
    genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "Copy", 1, "<STRING>");
    return AMObj(AMObjType::UNDEF);
  }
  if (!access((*(AMString*)(args[1].val.p)),F_OK)){
    AMLOUTPUT << "File " << (*(AMString*)(args[1].val.p)) << " already exist." << endl;
    return AMObj(AMObjType::BOOL,FALSE);
  }
  AMObjVector argsE(3);
  argsE[0] = args[0];
  argsE[1] = AMObj(AMObjType::STRING, new AMString("Type"));
  argsE[2] = AMObj(AMObjType::STRING, new AMString("File"));
  AMObj r = F_Exists(argsE);
  if(r.tag() == AMObjType::BOOL && r.val.b == TRUE){
    if(!copy((*(AMString*)(args[0].val.p)),(*(AMString*)(args[1].val.p)))){
      AMLOUTPUT << "Copying file succeed." << endl;
      return AMObj(AMObjType::BOOL,TRUE);
    }
    AMLOUTPUT << "Copying file failed." << endl;
    return AMObj(AMObjType::BOOL,FALSE);
  }
  else {
    AMLOUTPUT << "File " << (*(AMString*)(args[0].val.p)) << " does not exist." << endl;
    return AMObj(AMObjType::BOOL,FALSE);
  }
}

// #endif

/*  ------------------------------------------------------------------------ */

static AMObj F_FileHelp(const AMObjVector& args) {

//  FNode* func = NULL;
  RWCString  func_name;
  bool option = false;

  CHECKCONDVA(args.length() <= 2,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "FileHelp", 1));

  if(args.length() == 1){
    if (args[0].tag() == AMObjType::STRING) {
      func_name = RWCString((*(AMString*)(args[0].val.p)));
      option = true;
    }
    else if (args[0].tag() == AMObjType::FNODE) {
      func_name = ((FNode*) args[0].val.p)->name();
      option = true;
    }
    else AMLOUTPUT << "Found argument of type : " << args[0].tag.string().data() << endl;
  }
  else if(args.length() == 2){
    if (*(AMString*)(args[0].val.p) == "Function") {

      CHECKCONDVA(args[1].tag() ==AMObjType::FNODE,
                  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "FileHelp", 1, args[1].tag.string().data(), "FUNC"));

      func_name = ((FNode*) args[1].val.p)->name();
      option = true;
    }
  }

  AMLOUTPUT << "Help for File Module" << endl;
  if(option)
    AMLOUTPUT << "Functions : '" << func_name << '\'' << endl;
  else AMLOUTPUT << "Functions :" << endl;
  if(!option || func_name == "AMAPMOD_DIR"){
    AMLOUTPUT << " * AMAPMOD_DIR :" << endl;
    AMLOUTPUT << "   - Environmental variable for AMAPmod project location." << endl;
    AMLOUTPUT << "   - Type : STRING." << endl;
  }
  if(!option || func_name == ":Cd"){
    AMLOUTPUT << " * Cd(Dir) :" << endl;
    AMLOUTPUT << "   - Change Directory to Dir : " << endl;
    AMLOUTPUT << "   - Return True if success, else False." << endl;
  }
  if(!option || func_name == ":Copy"){
    AMLOUTPUT << " * Copy(Filename1,Filename2) :" << endl;
    AMLOUTPUT << "   - Copy Filename1 in Filename2." << endl;
    AMLOUTPUT << "   - Return True if success, else False." << endl;
  }
  if(!option || func_name == ":CWD"){
    AMLOUTPUT << " * CWD :" << endl;
    AMLOUTPUT << "   - Environmental variable for current working directory." << endl;
    AMLOUTPUT << "   - Type : STRING." << endl;
  }
  if(!option || func_name == ":Exists"){
    AMLOUTPUT << " * Exists(Filename,[Type->File|Directory]) :" << endl;
    AMLOUTPUT << "   - Test whether Filename exist: " << endl;
    AMLOUTPUT << "     - Filename must be of type Type. " << endl;
    AMLOUTPUT << "   - Return True if it exists, else False." << endl;
  }
  if(!option || func_name == ":FileHelp"){
    AMLOUTPUT << " * FileHelp([Function->Func]):" << endl;
    AMLOUTPUT << "   - Display Help about File Module or function Func." << endl;
    AMLOUTPUT << "   - Return Nothing." << endl;
  }
  if(!option || func_name == "HOME"){
    AMLOUTPUT << " * HOME :" << endl;
    AMLOUTPUT << "   - Environmental variable for user's home directory." << endl;
    AMLOUTPUT << "   - Type : STRING." << endl;
  }
  if(!option || func_name == ":Ls"|| func_name == ":Dir"){
    AMLOUTPUT << " * Ls([Dir],[Type->File|Directory]) | Dir([Dir],[Type->File|Directory]):" << endl;
    AMLOUTPUT << "   - List contents of current Directory of Dir ." << endl;
    AMLOUTPUT << "     - contents must be of type Type. " << endl;
    AMLOUTPUT << "   - Return Array of STRING." << endl;
  }
  if(!option || func_name == ":Mkdir"){
    AMLOUTPUT << " * Mkdir(Dir) :" << endl;
    AMLOUTPUT << "   - Create directory Dir." << endl;
    AMLOUTPUT << "   - Return True if success, else False." << endl;
  }
  if(!option || func_name == ":Pwd"){
    AMLOUTPUT << " * Pwd() :" << endl;
    AMLOUTPUT << "   - Display the absolute name of the current directory." << endl;
    AMLOUTPUT << "   - Return STRING." << endl;
  }
  if(!option || func_name == ":Rename"){
    AMLOUTPUT << " * Rename(Filename1,Filename2) :" << endl;
    AMLOUTPUT << "   - Rename Filename1 in Filename2." << endl;
    AMLOUTPUT << "   - Return True if success, else False." << endl;
  }
  if(!option || func_name == ":Rm"){
    AMLOUTPUT << " * Rm(Filename) :" << endl;
    AMLOUTPUT << "   - Rm Filename : " << endl;
    AMLOUTPUT << "   - Return True if success, else False." << endl;
  }
  return AMObj(AMObjType::VOID);
}

/*  ------------------------------------------------------------------------ */

void installFILEModule() {

  AMObjType type[10]; // max number of arguments
  AMObj var;
  RWCString varname;


  var = AMObj(AMObjType::STRING, new AMString(getAMAPmodDir().c_str()));
  varname = ":AMAPMOD_DIR";
  amobjTable()->insert(varname, var);


  var = AMObj(AMObjType::STRING, new AMString(getHome().c_str()));
  varname = ":HOME";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::STRING, new AMString(get_cwd().c_str()));
  varname = ":CWD";
  amobjTable()->insert(varname, var);

  var = AMObj(AMObjType::STRING, new AMString((QDir::rootPath()).toAscii().data()));
  varname = ":ROOTDIR";
  amobjTable()->insert(varname, var);

  /// Operation
  type[0] = AMObjType::STRING;
  installFNode("Exists", F_Exists, 1, type, AMObjType::BOOL);

  type[0] = AMObjType::STRING;
  installFNode("SetAmapmodDir", F_SetAmapmodDir, 1, type, AMObjType::BOOL);

  type[0] = AMObjType::STRING;
  installFNode("Cd", F_Cd, 1, type, AMObjType::BOOL);

  type[0] = AMObjType::STRING;
  installFNode("Rm", F_Rm, 1, type, AMObjType::BOOL);

  type[0] = AMObjType::STRING;
  installFNode("Mkdir", F_Mkdir, 1, type, AMObjType::BOOL);

  type[0] = AMObjType::STRING;
  installFNode("Dir", F_Lsdir, 1, type, AMObjType::BOOL);

  type[0] = AMObjType::STRING;
  installFNode("Ls", F_Lsdir, 1, type, AMObjType::ARRAY);

  type[0] = AMObjType::VOID;
  installFNode("Pwd", F_Pwd, 1, type, AMObjType::STRING);

  type[0] = AMObjType::STRING;
  type[1] = AMObjType::STRING;
  installFNode("Rename", F_Rename, 1, type, AMObjType::BOOL);

  type[0] = AMObjType::STRING;
  type[1] = AMObjType::STRING;
  installFNode("Copy", F_Copy, 1, type, AMObjType::BOOL);

  type[0] = AMObjType::VOID;
  type[1] = AMObjType::VOID;
  installFNode("FileHelp", F_FileHelp, 1, type, AMObjType::VOID);

}

