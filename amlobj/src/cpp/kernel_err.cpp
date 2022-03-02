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
 *       $Id: kernel_err.cpp 3259 2007-06-06 13:40:30Z dufourko $
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





const char* kernel_err_msgs_aml[] = {

  "operator %s: bad argument type %s: should be %s" ,                 		// K_OP_ARG_TYPE_ERR_sss = 0
  "operator %s: argument %d: bad argument type %s: should be %s" ,              // K_OP_ARG_TYPE_ERR_sdss 

  "iterator %s: bad argument type %s: should be %s" ,                 		// K_ITER_ARG_TYPE_ERR_sss 
  "iterator %s: argument %d: bad argument type %s: should be %s" ,              // K_ITER_ARG_TYPE_ERR_sdss
  "iterator %s: argument %d: should not contain the tied variable %s" ,		// K_ITER_SETDEF_ERR_sds,
  "iterator %s: an error occured at iteration step %d" ,			// K_ITER_EVAL_ERR_sd,

  "function %s: bad argument type %s: should be %s" ,			        // K_F_ARG_TYPE_ERR_sss
  "function %s: argument %d: bad argument type %s: should be %s" ,              // K_F_ARG_TYPE_ERR_sdss
  "function %s: argument %d: bad argument type %s: should not be %s" ,		// K_F_ARG_TYPE2_ERR_sdss
  "function %s: incompatible argument types %s and %s" ,		        // K_F_ARG_DIFFTYPES_ERR_sss
  "function %s: argument %d: incompatible argument types  %s and %s" ,		// K_F_ARG_DIFFTYPES_ERR_sdss

  "function %s: argument %d: bad option name" ,				        // K_OPTION_NAME_ERR_sd
  "function %s: argument %d: bad option name: should be %s" ,		        // K_OPTION_NAME_ERR_sds
  "function %s: argument %d: bad option value: should be %s", 			// K_OPTION_VALUE_ERR_sds
  "function %s: bad option values: %s", 					// K_OPTION_VALUES_ERR_ss
  "function %s: argument %d: bad option value: two options have incompatible values",  // K_OPTION_VALUES_INCOMPATIBLEERR_sd
 
  "function %s: argument %d: bad file format: should be %s" ,			// K_FILE_FORMAT_ERR_sds

  "constructor %s: argument %d: bad element type %s: all elements should have the same type" , // K_C_ELEM_TYPE_ERR_sds

  "function %s: bad number of arguments",				       	// K_NB_ARG_ERR_s 
  "function %s: bad number of arguments: function has no argument",   	       	// K_NO_ARG_ERR_s 
  "function %s: bad number of arguments: function has 1 mandatory argument", 	// K_SINGLE_ARG_ERR_s
  "function %s: bad number of arguments: function has %d mandatory arguments", 	// K_NB_ARG_ERR_sd
  "function %s: bad number of arguments: function has %s mandatory arguments", 	// K_NB_ARG_ERR_ss
  "function %s: bad number of arguments: function has %s mandatory arguments and possibly %d options", 	// K_NB_ARG_ERR_ssd
  "function %s: bad number of arguments: function may have any number of arguments except %s", 	// K_ANY_NB_ARG_ERR_ss

  "function %s: arguments have bad values: should be %s", 			// K_F_ARG_VALUE_ERR_ss
  "function %s: argument %d has a bad value: should be %s", 			// K_F_ARG_VALUE_ERR_sds
  "function %s: argument %d has a bad value: should not be %s", 		// K_F_ARG_VALUE_NEG_ERR_sds

  "function %s: cannot open %s in %s",						// K_F_FILE_ERR_sss
  "function %s: cannot be executed: %s",					// K_F_FUN_ERR_ss

  "Message Not Yet Implemented"							// K_NYI_ERR


};

