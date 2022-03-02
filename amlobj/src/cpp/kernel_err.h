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
 *       $Id: kernel_err.h 3259 2007-06-06 13:40:30Z dufourko $
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




#ifndef KERNEL_ERR_HEADER
#define KERNEL_ERR_HEADER

#define FAILCOND(x)       !(x)
#define AMLOUTPUT         getAMLOutputStream()
#define AMLCOMMENT(s)     AMLOUTPUT << std::endl << (s) << std::endl


#define ERRORMSG(i)       __FILE__,__LINE__,MODULE_NAME,\
                          (((i)<KERNEL_ERR_OFFSET)?kernel_err_msgs_aml[i]:ERR_MSG_ARRAY[(i-KERNEL_ERR_OFFSET)<0?0:i-KERNEL_ERR_OFFSET])
#define GENERRORMSG(i)    genAMLError(ERRORMSG(i))              /* the message does not contain parameters */
#define CHECKCOND(x,i)    if (FAILCOND(x)) {GENERRORMSG(i); return AMObj(AMObjType::ERROR);}
#define CHECKCONDVA(x,i)  if (FAILCOND(x)) {i; return AMObj(AMObjType::ERROR);}

#define CHECKDEFINECOND(x,s) if (FAILCOND(x)) {/*AMLCOMMENT(s);*/ return AMObj(AMObjType::UNDEF);}

extern const char* kernel_err_messages_aml[];
extern const char* kernel_err_types_aml[];

// This function creates an AMLErrorItem with the desired error message
extern void genAMLError(const char* file, int line, const char* module_name, const char* msg ...);

#define  KERNEL_ERR_OFFSET      1000            /* Max number of error messages in the Kernel */

extern const char* kernel_err_msgs_aml[];
enum  K_ERRORLABEL {

  K_OP_ARG_TYPE_ERR_sss = 0,
  K_OP_ARG_TYPE_ERR_sdss,
  K_ITER_ARG_TYPE_ERR_sss,
  K_ITER_ARG_TYPE_ERR_sdss,
  K_ITER_SETDEF_ERR_sds,
  K_ITER_EVAL_ERR_sd,
  K_F_ARG_TYPE_ERR_sss,
  K_F_ARG_TYPE_ERR_sdss,
  K_F_ARG_TYPE2_ERR_sdss,
  K_F_ARG_DIFFTYPES_ERR_sss,
  K_F_ARG_DIFFTYPES_ERR_sdss,

  K_OPTION_NAME_ERR_sd,
  K_OPTION_NAME_ERR_sds,
  K_OPTION_VALUE_ERR_sds,
  K_OPTION_VALUES_ERR_ss,
  K_OPTION_VALUES_INCOMPATIBLE_ERR_sd,
  K_FILE_FORMAT_ERR_sds,
  K_C_ELEM_TYPE_ERR_sds,
  K_NB_ARG_ERR_s,
  K_NO_ARG_ERR_s,
  K_SINGLE_ARG_ERR_s,
  K_NB_ARG_ERR_sd,
  K_NB_ARG_ERR_ss,
  K_NB_ARG_ERR_ssd,
  K_ANY_NB_ARG_ERR_ss,
  K_F_ARG_VALUE_ERR_ss,
  K_F_ARG_VALUE_ERR_sds,
  K_F_ARG_VALUE_NEG_ERR_sds,
  K_F_FILE_ERR_sss,
  K_F_FUN_ERR_ss,
  K_NYI_ERR

};

#endif
