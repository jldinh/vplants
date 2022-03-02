/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       V-Plants: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2014 CIRAD/INRA/Inria Virtual Plants
 *
 *       File author(s): Yann Guedon (yann.guedon@cirad.fr)
 *
 *       $Source$
 *       $Id: stat_module.h 16028 2014-03-07 16:08:38Z guedon $
 *
 *       Forum for V-Plants developers:
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



#ifndef STAT_MODULE_HEADER
#define STAT_MODULE_HEADER



const double STAT_FILTER_ROUNDNESS = 1.e-3;
const double STAT_MINIMUM_SPAN = 0.05;


enum STAT_ERRORLABEL {
  USED_OPTION_sd = KERNEL_ERR_OFFSET ,
  VIEW_POINT_sd ,
  VIEW_POINT_sds ,
  DETAIL_LEVEL_sddd ,
  STATE_PROFILE_TYPE_sds ,
  PLOTTING_MODE_sds ,
  INCOMPATIBLE_OPTIONS_s ,
  INCOMPATIBLE_OPTIONS_sss ,
  FORBIDDEN_OPTION_ss ,
  PARAMETER_VALUE_sd ,

  EMPTY_ARRAY_s ,
  ARRAY_ELEMENT_TYPE_sss ,
  ARRAY_ELEMENT_TYPE_1_sdss ,
  ARRAY_ELEMENT_TYPE_2_sdss ,
  ARRAY_ELEMENT_TYPE_sddss ,
  ARRAY_ELEMENT_TYPE_sdddss ,
  ARRAY_ELEMENT_VALUE_sd ,
  ARRAY_ELEMENT_VALUE_sdd ,
  ARRAY_ELEMENT_VALUE_sddd ,
  ARRAY_SIZE_sdd ,

  VECTOR_ARRAY_ELEMENT_TYPE_sdss ,
  VECTOR_ARRAY_ELEMENT_TYPE_sddss ,
  VECTOR_ARRAY_SIZE_sdd ,

  SEQUENCE_ARRAY_ELEMENT_TYPE_sdss ,
  SEQUENCE_ARRAY_ELEMENT_TYPE_sddss ,
  SEQUENCE_ARRAY_ELEMENT_TYPE_sdddss ,
  SEQUENCE_ARRAY_ELEMENT_VALUE_sddd ,
  SEQUENCE_ARRAY_SIZE_sddd ,

  PLOT_TYPE_sds ,

  VARIABLE_TYPE_sds ,

  STAT_MODULE_s ,
  STAT_TYPE_ss ,
  STAT_TYPE_sds ,
  STAT_TYPE_VECTOR_DISTANCE_sds ,
  STAT_MODEL_TYPE_sds ,
  STAT_MODEL_TYPE_DISTRIBUTION_sds ,
  STAT_DATA_TYPE_sds ,
  STAT_DATA_TYPE_FREQUENCY_DISTRIBUTION_sds ,
  STAT_DATA_TYPE_CORRELATION_sds ,
  STAT_DATA_TYPE_TIME_EVENTS_TOPS_sds ,
  ARG_sds ,
  ARGS_s ,
  ARG_VALUE_sd ,

  UNEVEN_NB_ARG_s ,
  INTER_EVENT_DISTRIBUTION_LOWER_BOUND_sd ,
  STOCHASTIC_PROCESS_TYPE_sds ,
  OBS_TIME_sddd ,
  SEQUENCE_FORMAT_sds ,
  MAX_POSITION_sd ,
  NB_VARIABLE_1_sd ,
  NB_VARIABLE_2_sd ,

  CLUSTERING_METHOD_sds ,
  ROUND_MODE_sds ,
  NB_CLASS_s ,
  VARIABLE_INDEX_1_sd ,
  VARIABLE_INDEX_2_sd ,
  FILTER_NORMALIZATION_sd ,
  MOVING_AVERAGE_OUTPUT_sds ,
  POINTWISE_AVERAGE_OUTPUT_sds ,

  MODEL_NAME_sd ,
  NB_DISTRIBUTION_sd ,
  NB_COMPONENT_sd ,
  DISTRIBUTION_NAME_sds ,
  FREQUENCY_DISTRIBUTION_NAME_sds ,
  INF_BOUND_STATUS_sds ,
  VARIANCE_FACTOR_sds ,
  ALGORITHM_NAME_sds ,
  PENALTY_TYPE_sds ,
  ESTIMATOR_NAME_sds ,
  SIDE_EFFECT_MANAGEMENT_TYPE_sds ,
  MEAN_COMPUTATION_METHOD_sds ,
  FUNCTION_NAME_sds ,
  MARKOV_CHAIN_TYPE_sds ,
  STRUCTURAL_PARAMETER_sds ,

  NB_FREQUENCY_DISTRIBUTION_s ,
  MISSING_TRANSPOSITION_OPTION_s ,
  MISSING_FILE_NAME_OPTION_s ,
  MISSING_ALIGNMENT_FILE_NAME_OPTION_s ,
  BEGIN_END_SPECIFICATION_sds ,
  INDEL_COST_SPECIFICATION_sds ,
  NB_MODEL_s ,
  CRITERION_NAME_sds ,
  TEST_TYPE_sds ,
  CORRELATION_COEFF_TYPE_sds ,
  NORMALIZATION_sds ,
  REGRESSION_METHOD_sds ,
  SPAN_sd ,
  CHANGE_POINT_MODEL_sds ,
  SEGMENTATION_OUTPUT_sds ,
  SEGMENTATION_OUTPUT_ss ,
  NB_SEGMENT_ESTIMATION_sds
};



/****************************************************************
 *
 *  Definition de la classe d'interface avec le langage
 */


struct STAT_model : public AMModel {

    StatInterface *pt;

    STAT_model(StatInterface *ipt) { pt = ipt; }
    ~STAT_model();

    std::ostream& displayOneLine(std::ostream &os) const;

    AMObj display(std::ostream &os , const AMObjVector &args) const;
    AMObj save(const AMObjVector &args) const;
    AMObj plot(GP_window &window , const AMObjVector &args) const;
};



#endif
