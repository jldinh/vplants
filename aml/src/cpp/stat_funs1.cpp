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
 *       $Id: stat_funs1.cpp 16621 2014-05-21 09:41:26Z guedon $
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



#include <stdio.h>
#include <sys/types.h>
#include <iostream>
#include <fstream>
#include <sstream>

#include "tool/dirnames.h"

#include "stat_tool/stat_tools.h"
#include "stat_tool/distribution.h"
#include "stat_tool/discrete_mixture.h"
#include "stat_tool/convolution.h"
#include "stat_tool/compound.h"
#include "stat_tool/curves.h"
#include "stat_tool/markovian.h"
#include "stat_tool/vectors.h"
#include "stat_tool/mixture.h"
#include "stat_tool/regression.h"

#include "sequence_analysis/renewal.h"
#include "sequence_analysis/sequences.h"
#include "sequence_analysis/variable_order_markov.h"
#include "sequence_analysis/hidden_variable_order_markov.h"
#include "sequence_analysis/semi_markov.h"
#include "sequence_analysis/hidden_semi_markov.h"
#include "sequence_analysis/nonhomogeneous_markov.h"
#include "sequence_analysis/tops.h"

#include "aml/ammodel.h"
#include "aml/parseraml.h"
#include "aml/kernel_funs.h"
#include "aml/kernel_err.h"
#include "aml/amstring.h"
#include "aml/gnuplot.h"
#include "aml/array.h"

#include "aml/stat_module.h"


#define ERR_MSG_ARRAY STAT_err_msgs_aml
#define MODULE_NAME   "Statistics"


const char *STAT_err_msgs_aml[] = {
  "function %s: argument %d: option already used" ,
  "function %s: argument %d: bad view point" ,
  "function %s: argument %d: bad view point: should be %s" ,
  "function %s: argument %d: bad output detail level: should be %d or %d" ,
  "function %s: argument %d: bad state profile type: should be %s" ,
  "function %s: argument %d: bad plotting mode: should be %s" ,
  "function %s: incompatible options" ,
  "function %s: option %s incompatible with option %s" ,
  "function %s: forbidden option %s" ,
  "function %s: argument %d: bad parameter value" ,

  "function %s: empty array" ,
  "function %s: bad array element type %s: should be of type %s" ,
  "function %s: argument %d: bad array element type %s: should be of type %s" ,
  "function %s: bad array element %d type %s: should be of type %s" ,
  "function %s: argument %d: bad array element %d type %s: should be of type %s" ,
  "function %s: argument %d: array %d: bad array element %d type %s: should be of type %s" ,
  "function %s: bad array element value %d: should be positive" ,
  "function %s: argument %d: bad array element %d value: should be strictly positive" ,
  "function %s: argument %d: array %d: bad array element %d value: should be strictly positive" ,
  "function %s: argument %d: bad array size: should be %d" ,

  "function %s: vector %d: bad array element type %s: should be of type %s" ,
  "function %s: vector %d: variable %d: bad array element type %s: should be of type %s" ,
  "function %s: vector %d: bad array size: should be %d" ,

  "function %s: sequence %d: bad array element type %s: should be of type %s" ,
  "function %s: sequence %d: index %d: bad array element type %s: should be of type %s" ,
  "function %s: sequence %d: index %d: variable %d: bad array element type %s: should be of type %s" ,
  "function %s: sequence %d: index %d: variable %d: bad array element value: should be positive" ,
  "function %s: sequence %d: index %d: bad array size: should be %d" ,

  "function %s: argument %d: bad plot type: should be %s" ,

  "function %s: argument %d: bad variable type: should be %s" ,

  "function %s: error in STAT module" ,
  "function %s: bad argument type %s: should be a STAT module type" ,
  "function %s: argument %d: bad argument type %s: should be a STAT module type" ,
  "function %s: argument %d: bad argument type %s: should be a STAT module type except VECTOR_DISTANCE" ,
  "function %s: argument %d: bad argument type %s: should be a STAT module model type" ,
  "function %s: argument %d: bad argument type %s: should be a STAT module model type except DISTRIBUTION" ,
  "function %s: argument %d: bad argument type %s: should be a STAT module data type" ,
  "function %s: argument %d: bad argument type %s: should be a STAT module data type except FREQUENCY_DISTRIBUTION" ,
  "function %s: argument %d: bad argument type %s: should be a STAT module data type or CORRELATION" ,
  "function %s: argument %d: bad argument type %s: should be a STAT module data type except TIME_EVENTS, RENEWAL_DATA and TOPS" ,
  "function %s: argument %d: bad argument: should be %s" ,
  "function %s: bad arguments" ,
  "function %s: bad argument %d value: should be positive" ,

  "function %s: uneven number of arguments: should be even" ,
  "function %s: argument %d: bad inter-event distribution lower bound to the possible values: should be at least 1" ,
  "function %s: argument %d: bad stochastic process type: should be %s" ,
  "function %s: argument %d: bad observation time: should be between %d and %d" ,
  "function %s: argument %d: bad sequence format: should be %s" ,
  "function %s: argument %d: bad maximum position" ,
  "function %s: bad number of variables: should be between 1 and %d" ,
  "function %s: bad number of variables: should be %d" ,

  "function %s: argument %d: bad clustering method: should be %s" ,
  "function %s: argument %d: bad rounding mode: should be %s" ,
  "function %s: bad number of classes" ,
  "function %s: argument %d: bad variable index: should be strictly positive" ,
  "function %s: argument %d: bad variable index" ,
  "function %s: argument %d: bad filter normalization" ,
  "function %s: argument %d: bad moving average output: should be %s" ,
  "function %s: argument %d: bad pointwise average output: should be %s" ,

  "function %s: argument %d: bad model name" ,
  "function %s: bad number of distributions: should be between 2 and %d" ,
  "function %s: bad number of mixture components: should be between 2 and %d" ,
  "function %s: argument %d: bad distribution name: should be %s" ,
  "function %s: argument %d: bad histogram name: should be %s" ,
  "function %s: argument %d: bad inferior bound status: should be %s" ,
  "function %s: argument %d: bad variance factor: should be %s" ,
  "function %s: argument %d: bad algorithm name: should be %s" ,
  "function %s: argument %d: bad penalty type: should be %s" ,
  "function %s: argument %d: bad estimator name: should be %s" ,
  "function %s: argument %d: bad side effect management type: should be %s" ,
  "function %s: argument %d: bad mean computation method: should be %s" ,
  "function %s: argument %d: bad function name: should be %s" ,
  "function %s: argument %d: bad underlying Markov chain type: should be %s" ,
  "function %s: argument %d: bad structural parameter: should be %s" ,

  "function %s: bad number of frequency distributions" ,
  "function %s: missing Transposition option" ,
  "function %s: missing FileName option" ,
  "function %s: missing AlignmentFileName option" ,
  "function %s: argument %d: bad begin/end alignment specification: should be %s" ,
  "function %s: argument %d: bad indel cost specification: should be %s" ,
  "function %s: bad number of models" ,
  "function %s: argument %d: bad criterion name: should be %s" ,
  "function %s: argument %d: bad test type: should be %s" ,
  "function %s: argument %d: bad correlation coeefficient type: should be %s" ,
  "function %s: argument %d: bad normalization: should be %s" ,
  "function %s: argument %d: bad regression method: should be %s" ,
  "function %s: argument %d: bad span" ,
  "function %s: argument %d: bad change-point model: should be %s" ,
  "function %s: argument %d: bad segmentation output: should be %s" ,
  "function %s: bad segmentation output: should be %s" ,
  "function %s: argument %d: bad number of segments estimation: should be %s"
};


extern AMObj STAT_Distribution(const AMObjVector &args);
extern AMObj STAT_DiscreteMixture(const AMObjVector &args);
extern AMObj STAT_Convolution(const AMObjVector &args);
extern AMObj STAT_Compound(const AMObjVector &args);
extern AMObj STAT_FrequencyDistribution(const AMObjVector &args);
extern AMObj STAT_Histogram(const AMObjVector &args);  // pour compatibilite ascendante
extern AMObj STAT_Mixture(const AMObjVector &args);
extern AMObj STAT_Vectors(const AMObjVector &args);
extern AMObj STAT_VectorDistance(const AMObjVector &args);
extern AMObj STAT_Renewal(const AMObjVector &args);
extern AMObj STAT_TimeEvents(const AMObjVector &args);
extern AMObj STAT_RenewalData(const AMObjVector &args);
extern AMObj STAT_VariableOrderMarkov(const AMObjVector &args);
extern AMObj STAT_HiddenVariableOrderMarkov(const AMObjVector &args);
extern AMObj STAT_SemiMarkov(const AMObjVector &args);
extern AMObj STAT_HiddenSemiMarkov(const AMObjVector &args);
extern AMObj STAT_NonhomogeneousMarkov(const AMObjVector &args);
extern AMObj STAT_Sequences(const AMObjVector &args);
extern AMObj STAT_TopParameters(const AMObjVector &args);
extern AMObj STAT_Tops(const AMObjVector &args);
// extern AMObj STAT_Load(const AMObjVector &args);

extern AMObj STAT_ToDistribution(const AMObjVector &args);
extern AMObj STAT_ToFrequencyDistribution(const AMObjVector &args);
extern AMObj STAT_ToHistogram(const AMObjVector &args);  // pour compatibilite ascendante
extern AMObj STAT_ExtractDistribution(const AMObjVector &args);
extern AMObj STAT_ExtractFrequencyDistribution(const AMObjVector &args);
extern AMObj STAT_ExtractHistogram(const AMObjVector &args);  // pour compatibilite ascendante
extern AMObj STAT_ExtractVectors(const AMObjVector &args);
extern AMObj STAT_ExtractData(const AMObjVector &args);

extern AMObj STAT_Merge(const AMObjVector &args);
extern AMObj STAT_Shift(const AMObjVector &args);
extern AMObj STAT_Cluster(const AMObjVector &args);
extern AMObj STAT_Transcode(const AMObjVector &args);
extern AMObj STAT_ValueSelect(const AMObjVector &args);

extern AMObj STAT_VariableScaling(const AMObjVector &args);
extern AMObj STAT_Round(const AMObjVector &args);
extern AMObj STAT_SelectStep(const AMObjVector &args);
extern AMObj STAT_SelectIndividual(const AMObjVector &args);
extern AMObj STAT_SelectVariable(const AMObjVector &args);
extern AMObj STAT_MergeVariable(const AMObjVector &args);

extern AMObj STAT_NbEventSelect(const AMObjVector &args);
extern AMObj STAT_TimeScaling(const AMObjVector &args);
extern AMObj STAT_TimeSelect(const AMObjVector &args);

extern AMObj STAT_ShiftVariable(const AMObjVector &args);
extern AMObj STAT_LengthSelect(const AMObjVector &args);
extern AMObj STAT_RemoveRun(const AMObjVector &args);
extern AMObj STAT_Reverse(const AMObjVector &args);
extern AMObj STAT_RemoveIndexParameter(const AMObjVector &args);
extern AMObj STAT_ExplicitIndexParameter(const AMObjVector &args);
extern AMObj STAT_IndexParameterSelect(const AMObjVector &args);
extern AMObj STAT_IndexParameterExtract(const AMObjVector &args);
extern AMObj STAT_SegmentationExtract(const AMObjVector &args);
extern AMObj STAT_Cumulate(const AMObjVector &args);
extern AMObj STAT_Difference(const AMObjVector &args);
extern AMObj STAT_SequenceNormalization(const AMObjVector &args);
extern AMObj STAT_MovingAverage(const AMObjVector &args);
extern AMObj STAT_PointwiseAverage(const AMObjVector &args);
extern AMObj STAT_RecurrenceTimeSequences(const AMObjVector &args);
extern AMObj STAT_SojournTimeSequences(const AMObjVector &args);
extern AMObj STAT_TransformPosition(const AMObjVector &args);

extern AMObj STAT_Cross(const AMObjVector &args);
extern AMObj STAT_ComputeInitialRun(const AMObjVector &args);
extern AMObj STAT_AddAbsorbingRun(const AMObjVector &args);
extern AMObj STAT_ConsecutiveValues(const AMObjVector &args);
extern AMObj STAT_Split(const AMObjVector &args);

extern AMObj STAT_ToDistanceMatrix(const AMObjVector &args);
extern AMObj STAT_Symmetrize(const AMObjVector &args);
extern AMObj STAT_Unnormalize(const AMObjVector &args);

extern AMObj STAT_RemoveApicalInternodes(const AMObjVector &args);

extern AMObj STAT_Estimate(const AMObjVector &args);

extern AMObj STAT_Simulate(const AMObjVector &args);

extern AMObj STAT_Compare(const AMObjVector &args);
extern AMObj STAT_Clustering(const AMObjVector &args);

extern AMObj STAT_ComparisonTest(const AMObjVector &args);
extern AMObj STAT_Fit(const AMObjVector &args);

extern AMObj STAT_TruncateDistribution(const AMObjVector &args);

extern AMObj STAT_ComputeRankCorrelation(const AMObjVector &args);
extern AMObj STAT_ContingencyTable(const AMObjVector &args);
extern AMObj STAT_VarianceAnalysis(const AMObjVector &args);
extern AMObj STAT_Regression(const AMObjVector &args);

extern AMObj STAT_ComputeCorrelation(const AMObjVector &args);
extern AMObj STAT_ComputeWhiteNoiseCorrelation(const AMObjVector &args);
extern AMObj STAT_ComputePartialAutoCorrelation(const AMObjVector &args);

extern AMObj STAT_Segmentation(const AMObjVector &args);

extern AMObj STAT_ComputeSelfTransition(const AMObjVector &args);
extern AMObj STAT_TransitionCount(const AMObjVector &args);
extern AMObj STAT_WordCount(const AMObjVector &args);
extern AMObj STAT_LumpabilityTest(const AMObjVector &args);

extern AMObj STAT_Thresholding(const AMObjVector &args);
extern AMObj STAT_ComputeAutoCorrelation(const AMObjVector &args);
extern AMObj STAT_ComputeStateSequences(const AMObjVector &args);
extern AMObj STAT_BuildAuxiliaryVariable(const AMObjVector &args);



/*--------------------------------------------------------------*
 *
 *  Ecriture sur une ligne.
 *
 *--------------------------------------------------------------*/

ostream& GP_window::displayOneLine(ostream &os) const

{
#ifndef _WIN32
/// Gnuplot port pb
  if (son_id == DEFAULT_ID) {
    os << "inactive window";
  }
  else {
    os << "active window";
  }
#endif
  return os;
}


/*--------------------------------------------------------------*
 *
 *  Calcul du nombre d'arguments obligatoires
 *
 *--------------------------------------------------------------*/

int nb_required_computation(const AMObjVector &args)

{
  register int i;
  int nb_required = args.length();


  for (i = 0;i < args.length();i++) {
    if (args[i].tag() == AMObjType::OPTION) {
      nb_required = i;
      break;
    }
  }

  return nb_required;
}


/*--------------------------------------------------------------*
 *
 *  Destructeur de la classe STAT_model.
 *
 *--------------------------------------------------------------*/

STAT_model::~STAT_model()

{
  delete pt;
}


/*--------------------------------------------------------------*
 *
 *  Ecriture sur une ligne.
 *
 *--------------------------------------------------------------*/

ostream& STAT_model::displayOneLine(ostream &os) const

{
  return pt->line_write(os);
}


/*--------------------------------------------------------------*
 *
 *  Sortie ecran.
 *
 *--------------------------------------------------------------*/

AMObj STAT_model::display(ostream &os , const AMObjVector &args) const

{
  RWCString *pstr;
  char view_point = 'v' , format = 'c';
  bool status = true , view_point_option = false , detail_option = false ,
       format_option = false , segmentations_option = false , nb_segmentation_option = false ,
       state_sequences_option = false , nb_state_sequence_option = false ,
       output_option = false , exhaustive = false;
  register int i , j;
  int nb_required , segmentation = FORWARD_DYNAMIC_PROGRAMMING , nb_segmentation = NB_SEGMENTATION ,
      state_sequence = GENERALIZED_VITERBI , nb_state_sequence = NB_STATE_SEQUENCE , output;


  nb_required = nb_required_computation(args);

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
              (args.length() == nb_required + 8) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Display"));

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "ViewPoint") {
        switch (view_point_option) {

        case false : {
          view_point_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Data") {
              view_point = 'd';
            }
            else if (*pstr == "Survival") {
              view_point = 's';
            }
            else if (*pstr == "SegmentProfile") {
              view_point = 'q';
            }
            else if (*pstr == "StateProfile") {
              view_point = 'p';
            }
            else {
              status = false;
              genAMLError(ERRORMSG(VIEW_POINT_sds) , "Display" ,
                          nb_required + i + 1 , "Data or Survival or SegmentProfile or StateProfile");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Display" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Detail") {
        switch (detail_option) {

        case false : {
          detail_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            switch (args[nb_required + i * 2 + 1].val.i) {
            case 1 :
              exhaustive = false;
              break;
            case 2 :
              exhaustive = true;
              break;
            default :
              status = false;
              genAMLError(ERRORMSG(DETAIL_LEVEL_sddd) , "Display" ,
                          nb_required + i + 1 , 1 , 2);
              break;
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Display" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Format") {
        switch (format_option) {

        case false : {
          format_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Column") {
              format = 'c';
            }
            else if (*pstr == "Line") {
              format = 'l';
            }
            else {
              status = false;
              genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "Display" ,
                          nb_required + i + 1 , "Column or Line");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Display" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Segmentations") {
        switch (segmentations_option) {

        case false : {
          segmentations_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "DynamicProgramming") {
              segmentation = FORWARD_DYNAMIC_PROGRAMMING;
            }
            else if (*pstr == "ForwardBackwardSampling") {
              segmentation = FORWARD_BACKWARD_SAMPLING;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Display" ,
                          nb_required + i + 1 , "DynamicProgramming or ForwardBackwardSampling");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Display" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "NbSegmentation") {
        switch (nb_segmentation_option) {

        case false : {
          nb_segmentation_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            nb_segmentation = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Display" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "StateSequences") {
        switch (state_sequences_option) {

        case false : {
          state_sequences_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "GeneralizedViterbi") {
              state_sequence = GENERALIZED_VITERBI;
            }
            else if (*pstr == "ForwardBackwardSampling") {
              state_sequence = FORWARD_BACKWARD_SAMPLING;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Display" ,
                          nb_required + i + 1 , "GeneralizedViterbi or ForwardBackwardSampling");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Display" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "NbStateSequence") {
        switch (nb_state_sequence_option) {

        case false : {
          nb_state_sequence_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            nb_state_sequence = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Display" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Output") {
        switch (output_option) {

        case false : {
          output_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "ChangePoint") {
              output = CHANGE_POINT;
            }
            else if (*pstr == "Segment") {
              output = SEGMENT;
            }
            else if (*pstr == "State") {
              output = SSTATE;
            }
            else if (*pstr == "InState") {
              output = IN_STATE;
            }
            else if (*pstr == "OutState") {
              output = OUT_STATE;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(STATE_PROFILE_TYPE_sds) , "Display" ,
                          nb_required + i + 1 , "ChangePoint or Segment or State or InState or OutState");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Display" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Display" ,
                    nb_required + i + 1 , "ViewPoint or Detail or Format or Segmentations or NbSegmentation or StateSequences or NbStateSequence or Output");
      }
    }
  }

  if ((detail_option) && (view_point != 'v') && (view_point != 'd')) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Display");
  }
  if ((format_option) && (view_point != 'd')) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Display");
  }
  if (((segmentations_option) || (nb_segmentation_option)) && ((view_point != 'q') ||
       ((args[0].tag() != AMObjType::SEQUENCES) && (args[0].tag() != AMObjType::MARKOVIAN_SEQUENCES) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV_DATA)))) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Display");
  }
  if (((state_sequences_option) || (nb_state_sequence_option)) && ((view_point != 'p') ||
       ((args[0].tag() != AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) &&
        (args[0].tag() != AMObjType::HIDDEN_SEMI_MARKOV) &&
        (args[0].tag() != AMObjType::MARKOVIAN_SEQUENCES) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV_DATA)))) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Display");
  }
  if ((output_option) && ((view_point != 'q') ||
       ((args[0].tag() != AMObjType::SEQUENCES) && (args[0].tag() != AMObjType::MARKOVIAN_SEQUENCES) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV_DATA))) &&
      ((view_point != 'p') || ((args[0].tag() != AMObjType::HIDDEN_SEMI_MARKOV) &&
        (args[0].tag() != AMObjType::MARKOVIAN_SEQUENCES) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV_DATA)))) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Display");
  }

  switch (output_option) {

  case false : {
    switch (view_point) {
    case 'q' :
      output = SEGMENT;
      break;
    case 'p' :
      output = SSTATE;
      break;
    }
    break;
  }

  case true : {
    if (((view_point == 'q') && (output != CHANGE_POINT) && (output != SEGMENT)) ||
        ((view_point == 'p') && (output != STATE) && (output != IN_STATE) && (output != OUT_STATE))) {
      status = false;
      genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_sss) , "Display" , "ViewPoint" , "Output");
    }
    break;
  }
  }

  // argument obligatoire

  switch (view_point) {

  case 'v' : {
    CHECKCONDVA(nb_required == 1 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Display"));

    if ((args[0].tag() != AMObjType::DISTRIBUTION) && (args[0].tag() != AMObjType::FREQUENCY_DISTRIBUTION) &&
        (args[0].tag() != AMObjType::DISCRETE_MIXTURE) && (args[0].tag() != AMObjType::DISCRETE_MIXTURE_DATA) &&
        (args[0].tag() != AMObjType::CONVOLUTION) && (args[0].tag() != AMObjType::CONVOLUTION_DATA) &&
        (args[0].tag() != AMObjType::COMPOUND) && (args[0].tag() != AMObjType::COMPOUND_DATA) &&
        (args[0].tag() != AMObjType::MIXTURE) && (args[0].tag() != AMObjType::VECTORS) &&
        (args[0].tag() != AMObjType::MIXTURE_DATA) && (args[0].tag() != AMObjType::REGRESSION) &&
        (args[0].tag() != AMObjType::VECTOR_DISTANCE) && (args[0].tag() != AMObjType::RENEWAL) &&
        (args[0].tag() != AMObjType::TIME_EVENTS) && (args[0].tag() != AMObjType::RENEWAL_DATA) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV) &&
        (args[0].tag() != AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV) && (args[0].tag() != AMObjType::HIDDEN_SEMI_MARKOV) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV) &&
        (args[0].tag() != AMObjType::SEQUENCES) && (args[0].tag() != AMObjType::MARKOVIAN_SEQUENCES) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::CORRELATION) &&
        (args[0].tag() != AMObjType::DISTANCE_MATRIX) && (args[0].tag() != AMObjType::CLUSTERS) &&
        (args[0].tag() != AMObjType::TOP_PARAMETERS) && (args[0].tag() != AMObjType::TOPS)) {
      status = false;
      genAMLError(ERRORMSG(STAT_TYPE_sds) , "Display" , 1 , args[0].tag.string().data());
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    ((STAT_model*)args[0].val.p)->pt->ascii_write(os , exhaustive);
    break;
  }

  case 'd' : {
    CHECKCONDVA(nb_required == 1 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Display"));

    if ((args[0].tag() == AMObjType::VECTORS) || (args[0].tag() == AMObjType::MIXTURE_DATA)) {
      Vectors *vec;


      if (format_option) {
        status = false;
        genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Display");
      }

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }

      switch (args[0].tag()) {
      case AMObjType::VECTORS :
        vec = (Vectors*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::MIXTURE_DATA :
        vec = (MixtureData*)((STAT_model*)args[0].val.p)->pt;
        break;
      }

      vec->ascii_data_write(AMLOUTPUT , exhaustive);
    }

    else if ((args[0].tag() == AMObjType::SEQUENCES) || (args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
             (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) ||
             (args[0].tag() == AMObjType::SEMI_MARKOV_DATA) ||
             (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV_DATA) || (args[0].tag() == AMObjType::TOPS)) {
      Sequences *seq;


      switch (args[0].tag()) {
      case AMObjType::SEQUENCES :
        seq = (Sequences*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::MARKOVIAN_SEQUENCES :
        seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
        seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::SEMI_MARKOV_DATA :
        seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::NONHOMOGENEOUS_MARKOV_DATA :
        seq = (NonhomogeneousMarkovData*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::TOPS :
        seq = (Tops*)((STAT_model*)args[0].val.p)->pt;
        break;
      }

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }

      seq->ascii_data_write(AMLOUTPUT , format , exhaustive);
    }

    else {
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , 1 , args[0].tag.string().data() ,
                  "VECTORS or MIXTURE_DATA or SEQUENCES or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA or TOPS");
      return AMObj(AMObjType::ERROR);
    }
    break;
  }

  case 's' : {
    CHECKCONDVA(nb_required == 1 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Display"));

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    if ((args[0].tag() == AMObjType::DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE) ||
        (args[0].tag() == AMObjType::CONVOLUTION) || (args[0].tag() == AMObjType::COMPOUND)) {
      Distribution *dist;


      switch (args[0].tag()) {
      case AMObjType::DISTRIBUTION :
        dist = (Distribution*)((DiscreteParametricModel*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::DISCRETE_MIXTURE :
        dist = (Distribution*)((DiscreteMixture*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::CONVOLUTION :
        dist = (Distribution*)((Convolution*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::COMPOUND :
        dist = (Distribution*)((Compound*)((STAT_model*)args[0].val.p)->pt);
        break;
      }

      dist->survival_ascii_write(AMLOUTPUT);
    }

    else if ((args[0].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
             (args[0].tag() == AMObjType::CONVOLUTION_DATA) || (args[0].tag() == AMObjType::COMPOUND_DATA)) {
      FrequencyDistribution *histo;


      switch (args[0].tag()) {
      case AMObjType::FREQUENCY_DISTRIBUTION :
        histo = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::DISCRETE_MIXTURE_DATA :
        histo = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::CONVOLUTION_DATA :
        histo = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::COMPOUND_DATA :
        histo = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[0].val.p)->pt);
        break;
      }

      histo->survival_ascii_write(AMLOUTPUT);
    }

    else {
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , 1 , args[0].tag.string().data() ,
                  "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND or FREQUENCY_DISTRIBUTION or DISCRETE_MIXTURE_DATA or CONVOLUTION_DATA or COMPOUND_DATA");
      return AMObj(AMObjType::ERROR);
    }
    break;
  }

  case 'q' : {
    int nb_variable , *model_type;
    const Sequences *seq;
    StatError error;


    CHECKCONDVA(nb_required >= 4 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Display"));

    switch (args[0].tag()) {
    case AMObjType::SEQUENCES :
      seq = (Sequences*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::MARKOVIAN_SEQUENCES :
      seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
      seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::SEMI_MARKOV_DATA :
      seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
      break;
    default :
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , 1 , args[0].tag.string().data() ,
                  "SEQUENCES or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA");
      return AMObj(AMObjType::ERROR);
    }

    nb_variable = seq->get_nb_variable();

    model_type = new int[nb_variable];

    if (args[1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , 2 ,
                  args[1].tag.string().data() , "INT");
    }
    if (args[2].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , 3 ,
                  args[2].tag.string().data() , "INT");
    }

    for (i = 0;i < nb_variable;i++) {
      if (args[i + 3].tag() != AMObjType::STRING) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , i + 4 ,
                    args[i + 3].tag.string().data() , "STRING");
      }

      else {
        pstr = (AMString*)args[i + 3].val.p;

        if (i == 0) {
          if (*pstr == "Categorical") {
            model_type[i] = CATEGORICAL_CHANGE;
          }
          else if (*pstr == "MultivariateCategorical") {
            model_type[i] = MULTIVARIATE_CATEGORICAL_CHANGE;
          }
          else if (*pstr == "Poisson") {
            model_type[i] = POISSON_CHANGE;
          }
          else if (*pstr == "MultivariatePoisson") {
            model_type[i] = MULTIVARIATE_POISSON_CHANGE;
          }
          else if (*pstr == "Geometric") {
            model_type[i] = GEOMETRIC_0_CHANGE;
          }
          else if (*pstr == "ShiftedGeometric") {
            model_type[i] = GEOMETRIC_1_CHANGE;
          }
          else if (*pstr == "MultivariateGeometric") {
            model_type[i] = MULTIVARIATE_GEOMETRIC_0_CHANGE;
          }
          else if (*pstr == "Ordinal") {
            model_type[i] = ORDINAL_GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Gaussian") {
            model_type[i] = GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Mean") {
            model_type[i] = MEAN_CHANGE;
          }
          else if (*pstr == "Variance") {
            model_type[i] = VARIANCE_CHANGE;
          }
          else if (*pstr == "MeanVariance") {
            model_type[i] = MEAN_VARIANCE_CHANGE;
          }
          else if (*pstr == "LinearModel") {
            model_type[i] = LINEAR_MODEL_CHANGE;
          }
          else if (*pstr == "InterceptSlope") {
            model_type[i] = INTERCEPT_SLOPE_CHANGE;
          }
          else if (*pstr == "BayesianPoisson") {
            model_type[i] = BAYESIAN_POISSON_CHANGE;
          }
          else if (*pstr == "BayesianGaussian") {
            model_type[i] = BAYESIAN_GAUSSIAN_CHANGE;
          }
          else {
            status = false;
            genAMLError(ERRORMSG(CHANGE_POINT_MODEL_sds) , "Display" , i + 4 ,
                        "Categorical or Poisson or MultivariatePoisson or Geometric or ShiftedGeometric or MultivariateGeometric or Ordinal or Gaussian or Mean or Variance or MeanVariance or LinearModel or InterceptSlope");
          }

          if ((model_type[i] == MULTIVARIATE_CATEGORICAL_CHANGE) || (model_type[i] == MULTIVARIATE_POISSON_CHANGE) ||
              (model_type[i] == MULTIVARIATE_GEOMETRIC_0_CHANGE) || (model_type[i] == MEAN_CHANGE) ||
              (model_type[i] == MEAN_VARIANCE_CHANGE) || (model_type[i] == INTERCEPT_SLOPE_CHANGE)) {
            CHECKCONDVA(nb_required == 4 ,
                        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Display"));

            for (j = 1;j < nb_variable;j++) {
              model_type[j] = model_type[i];
            }
            break;
          }

          else {
            CHECKCONDVA(nb_required == nb_variable + 3 ,
                        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Display"));
          }
        }

        else {
          if (*pstr == "Categorical") {
            model_type[i] = CATEGORICAL_CHANGE;
          }
          else if (*pstr == "Poisson") {
            model_type[i] = POISSON_CHANGE;
          }
          else if (*pstr == "Geometric") {
            model_type[i] = GEOMETRIC_0_CHANGE;
          }
          else if (*pstr == "ShiftedGeometric") {
            model_type[i] = GEOMETRIC_1_CHANGE;
          }
          else if (*pstr == "Ordinal") {
            model_type[i] = ORDINAL_GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Gaussian") {
            model_type[i] = GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Variance") {
            model_type[i] = VARIANCE_CHANGE;
          }
          else if (*pstr == "LinearModel") {
            model_type[i] = LINEAR_MODEL_CHANGE;
          }
          else if (*pstr == "InterceptSlope") {
            model_type[i] = INTERCEPT_SLOPE_CHANGE;
          }
          else {
            status = false;
            genAMLError(ERRORMSG(CHANGE_POINT_MODEL_sds) , "Display" , i + 4 ,
                        "Categorical or Poisson or Geometric or ShiftedGeometric Ordinal or Gaussian or Variance or LinearModel or InterceptSlope");
          }
        }
      }
    }

    if (!status) {
      delete [] model_type;
      return AMObj(AMObjType::ERROR);
    }

    status = seq->segment_profile_write(error , AMLOUTPUT , args[1].val.i , args[2].val.i ,
                                        model_type , output , 'a' ,
                                        segmentation , nb_segmentation);
    delete [] model_type;

    if (!status) {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Display");
      return AMObj(AMObjType::ERROR);
    }
    break;
  }

  case 'p' : {
    StatError error;


    CHECKCONDVA(nb_required >= 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Display"));

    if (args[1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , 2 ,
                  args[1].tag.string().data() , "INT");
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    if (args[0].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) {
      CHECKCONDVA(nb_required == 2 ,
                  genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Display"));

      status = ((HiddenVariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt)->state_profile_ascii_write(error , AMLOUTPUT , args[1].val.i , state_sequence , nb_state_sequence);
    }

    else if (args[0].tag() == AMObjType::HIDDEN_SEMI_MARKOV) {
      CHECKCONDVA(nb_required == 2 ,
                  genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Display"));

      status = ((HiddenSemiMarkov*)((STAT_model*)args[0].val.p)->pt)->state_profile_ascii_write(error , AMLOUTPUT , args[1].val.i , output , state_sequence , nb_state_sequence);
    }

    else {
      const MarkovianSequences *seq;


      CHECKCONDVA(nb_required == 3 ,
                  genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Display"));

      switch (args[0].tag()) {
      case AMObjType::MARKOVIAN_SEQUENCES :
        seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
        seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::SEMI_MARKOV_DATA :
        seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::NONHOMOGENEOUS_MARKOV_DATA :
        seq = (NonhomogeneousMarkovData*)((STAT_model*)args[0].val.p)->pt;
        break;
      default :
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , 1 , args[0].tag.string().data() ,
                    "HIDDEN_VARIABLE_ORDER_MARKOV or HIDDEN_SEMI-MARKOV or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
        return AMObj(AMObjType::ERROR);
      }

      if (args[2].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) {
        status = ((HiddenVariableOrderMarkov*)((STAT_model*)args[2].val.p)->pt)->state_profile_write(error , AMLOUTPUT , *seq , args[1].val.i , 'a' , state_sequence , nb_state_sequence);
      }

      else if (args[2].tag() == AMObjType::HIDDEN_SEMI_MARKOV) {
        status = ((HiddenSemiMarkov*)((STAT_model*)args[2].val.p)->pt)->state_profile_write(error , AMLOUTPUT , *seq , args[1].val.i , output , 'a' , state_sequence , nb_state_sequence);
      }

      else {
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Display" , 3 , args[2].tag.string().data() ,
                    "HIDDEN_VARIABLE_ORDER_MARKOV or HIDDEN_SEMI-MARKOV");
        return AMObj(AMObjType::ERROR);
      }
    }

    if (!status) {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Display");
      return AMObj(AMObjType::ERROR);
    }
    break;
  }
  }

  return AMObj(AMObjType::VOID);
}


/*--------------------------------------------------------------*
 *
 *  Sortie fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_model::save(const AMObjVector &args) const

{
  RWCString *pstr , *format_pstr = NULL;
  char view_point = 'v' , format;
  bool status = true , view_point_option = false , detail_option = false ,
       format_option = false , segmentations_option = false , nb_segmentation_option = false ,
       state_sequences_option = false , nb_state_sequence_option = false ,
       output_option = false , exhaustive = false;
  register int i , j;
  int nb_required , format_index , segmentation = FORWARD_DYNAMIC_PROGRAMMING ,
      nb_segmentation = NB_SEGMENTATION , state_sequence = GENERALIZED_VITERBI ,
      nb_state_sequence = NB_STATE_SEQUENCE , output;
  StatError error;


  nb_required = nb_required_computation(args);

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
              (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Save"));

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "ViewPoint") {
        switch (view_point_option) {

        case false : {
          view_point_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Data") {
              view_point = 'd';
            }
            else if (*pstr == "Survival") {
              view_point = 's';
            }
            else if (*pstr == "SegmentProfile") {
              view_point = 'q';
            }
            else if (*pstr == "StateProfile") {
              view_point = 'p';
            }
            else {
              status = false;
              genAMLError(ERRORMSG(VIEW_POINT_sds) , "Save" ,
                          nb_required + i + 1 , "Data or Survival or SegmentProfile or StateProfile");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Save" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Detail") {
        switch (detail_option) {

        case false : {
          detail_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            switch (args[nb_required + i * 2 + 1].val.i) {
            case 1 :
              exhaustive = false;
              break;
            case 2 :
              exhaustive = true;
              break;
            default :
              status = false;
              genAMLError(ERRORMSG(DETAIL_LEVEL_sddd) , "Save" ,
                          nb_required + i + 1 , 1 , 2);
              break;
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Save" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Format") {
        switch (format_option) {

        case false : {
          format_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            format_pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            format_index = nb_required + i + 1;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Save" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Segmentations") {
        switch (segmentations_option) {

        case false : {
          segmentations_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "DynamicProgramming") {
              segmentation = FORWARD_DYNAMIC_PROGRAMMING;
            }
            else if (*pstr == "ForwardBackwardSampling") {
              segmentation = FORWARD_BACKWARD_SAMPLING;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Save" ,
                          nb_required + i + 1 , "DynamicProgramming or ForwardBackwardSampling");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Save" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "NbSegmentation") {
        switch (nb_segmentation_option) {

        case false : {
          nb_segmentation_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            nb_segmentation = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Save" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "StateSequences") {
        switch (state_sequences_option) {

        case false : {
          state_sequences_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "GeneralizedViterbi") {
              state_sequence = GENERALIZED_VITERBI;
            }
            else if (*pstr == "ForwardBackwardSampling") {
              state_sequence = FORWARD_BACKWARD_SAMPLING;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Save" ,
                          nb_required + i + 1 , "GeneralizedViterbi or ForwardBackwardSampling");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Save" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "NbStateSequence") {
        switch (nb_state_sequence_option) {

        case false : {
          nb_state_sequence_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            nb_state_sequence = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Save" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Output") {
        switch (output_option) {

        case false : {
          output_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "ChangePoint") {
              output = CHANGE_POINT;
            }
            else if (*pstr == "Segment") {
              output = SEGMENT;
            }
            else if (*pstr == "State") {
              output = SSTATE;
            }
            else if (*pstr == "InState") {
              output = IN_STATE;
            }
            else if (*pstr == "OutState") {
              output = OUT_STATE;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(STATE_PROFILE_TYPE_sds) , "Save" ,
                          nb_required + i + 1 , "ChangePoint or Segment or State or InState or OutState");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Save" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Save" ,
                    nb_required + i + 1 , "ViewPoint or Detail or Format or Segmentations or NbSegmentation or StateSequences or NbStateSequence or Output");
      }
    }
  }

  if ((detail_option) && (view_point != 'v') && (view_point != 'd')) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Save");
  }
  if (((segmentations_option) || (nb_segmentation_option)) && ((view_point != 'q') ||
       ((args[0].tag() != AMObjType::SEQUENCES) && (args[0].tag() != AMObjType::MARKOVIAN_SEQUENCES) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV_DATA)))) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Save");
  }
  if (((state_sequences_option) || (nb_state_sequence_option)) && ((view_point != 'p') ||
       ((args[0].tag() != AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) &&
        (args[0].tag() != AMObjType::HIDDEN_SEMI_MARKOV) &&
        (args[0].tag() != AMObjType::MARKOVIAN_SEQUENCES) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV_DATA)))) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Save");
  }
  if ((output_option) && ((view_point != 'q') ||
       ((args[0].tag() != AMObjType::SEQUENCES) && (args[0].tag() != AMObjType::MARKOVIAN_SEQUENCES) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV_DATA))) &&
      ((view_point != 'p') || ((args[0].tag() != AMObjType::HIDDEN_SEMI_MARKOV) &&
        (args[0].tag() != AMObjType::MARKOVIAN_SEQUENCES) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV_DATA)))) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Save");
  }

  switch (output_option) {

  case false : {
    switch (view_point) {
    case 'q' :
      output = SEGMENT;
      break;
    case 'p' :
      output = SSTATE;
      break;
    }
    break;
  }

  case true : {
    if (((view_point == 'q') && (output != CHANGE_POINT) && (output != SEGMENT)) ||
        ((view_point == 'p') && (output != STATE) && (output != IN_STATE) && (output != OUT_STATE))) {
      status = false;
      genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_sss) , "Save" , "ViewPoint" , "Output");
    }
    break;
  }
  }

  // arguments obligatoires

  if (args[1].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , 2 ,
                args[1].tag.string().data() , "STRING");
  }

  switch (view_point) {

  case 'v' : {
    CHECKCONDVA(nb_required == 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Save"));

    format = 'a';

    if (format_pstr) {
      if (*format_pstr == "ASCII") {
        format = 'a';
      }
      else if (*format_pstr == "SpreadSheet") {
        format = 's';
      }
      else if (*format_pstr == "Gnuplot") {
        format = 'g';
      }
      else {
        status = false;
        genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "Save" ,
                    format_index , "ASCII or SpreadSheet");
      }
    }

    if ((detail_option) && (format != 'a')) {
      status = false;
      genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Save");
    }

    if ((args[0].tag() != AMObjType::DISTRIBUTION) && (args[0].tag() != AMObjType::FREQUENCY_DISTRIBUTION) &&
        (args[0].tag() != AMObjType::DISCRETE_MIXTURE) && (args[0].tag() != AMObjType::DISCRETE_MIXTURE_DATA) &&
        (args[0].tag() != AMObjType::CONVOLUTION) && (args[0].tag() != AMObjType::CONVOLUTION_DATA) &&
        (args[0].tag() != AMObjType::COMPOUND) && (args[0].tag() != AMObjType::COMPOUND_DATA) &&
        (args[0].tag() != AMObjType::MIXTURE) && (args[0].tag() != AMObjType::VECTORS) &&
        (args[0].tag() != AMObjType::MIXTURE_DATA) && (args[0].tag() != AMObjType::REGRESSION) &&
        (args[0].tag() != AMObjType::RENEWAL) && (args[0].tag() != AMObjType::TIME_EVENTS) &&
        (args[0].tag() != AMObjType::RENEWAL_DATA) && (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV) &&
        (args[0].tag() != AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV) && (args[0].tag() != AMObjType::HIDDEN_SEMI_MARKOV) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV) && (args[0].tag() != AMObjType::SEQUENCES) &&
        (args[0].tag() != AMObjType::MARKOVIAN_SEQUENCES) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) && (args[0].tag() != AMObjType::SEMI_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::CORRELATION) && (args[0].tag() != AMObjType::DISTANCE_MATRIX) &&
        (args[0].tag() != AMObjType::CLUSTERS) && (args[0].tag() != AMObjType::TOP_PARAMETERS) &&
        (args[0].tag() != AMObjType::TOPS)) {
      status = false;
      genAMLError(ERRORMSG(STAT_TYPE_sds) , "Save" , 1 , args[0].tag.string().data());
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    switch (format) {
    case 'a' :
      status = ((STAT_model*)args[0].val.p)->pt->ascii_write(error , ((AMString*)args[1].val.p)->data() , exhaustive);
      break;
    case 's' :
      status = ((STAT_model*)args[0].val.p)->pt->spreadsheet_write(error , ((AMString*)args[1].val.p)->data());
      break;
    case 'g' :
      status = ((STAT_model*)args[0].val.p)->pt->plot_write(error , ((AMString*)args[1].val.p)->data());
      break;
    }
    break;
  }

  case 'd' : {
    CHECKCONDVA(nb_required == 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Save"));

    if ((args[0].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
        (args[0].tag() == AMObjType::CONVOLUTION_DATA) || (args[0].tag() == AMObjType::COMPOUND_DATA)) {
      FrequencyDistribution *histo;


      if ((detail_option) || (format_option)) {
        status = false;
        genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Save");
      }

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }

      switch (args[0].tag()) {
      case AMObjType::FREQUENCY_DISTRIBUTION :
        histo = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::DISCRETE_MIXTURE_DATA :
        histo = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::CONVOLUTION_DATA :
        histo = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::COMPOUND_DATA :
        histo = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[0].val.p)->pt);
        break;
      }

      status = histo->ascii_write(error , ((AMString*)args[1].val.p)->data());
    }

    else if ((args[0].tag() == AMObjType::VECTORS) || (args[0].tag() == AMObjType::MIXTURE_DATA)) {
      Vectors *vec;


      if (format_option) {
        status = false;
        genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Save");
      }

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }

      switch (args[0].tag()) {
      case AMObjType::VECTORS :
        vec = (Vectors*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::MIXTURE_DATA :
        vec = (MixtureData*)((STAT_model*)args[0].val.p)->pt;
        break;
      }

      status = vec->ascii_data_write(error , ((AMString*)args[1].val.p)->data() , exhaustive);
    }

    else if ((args[0].tag() == AMObjType::TIME_EVENTS) || (args[0].tag() == AMObjType::RENEWAL_DATA)) {
      TimeEvents *timev;


      if ((detail_option) || (format_option)) {
        status = false;
        genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Save");
      }

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }

      switch (args[0].tag()) {
      case AMObjType::TIME_EVENTS :
        timev = (TimeEvents*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::RENEWAL_DATA :
        timev = (RenewalData*)((STAT_model*)args[0].val.p)->pt;
        break;
      }

      status = timev->TimeEvents::ascii_write(error , ((AMString*)args[1].val.p)->data());
    }

    else if ((args[0].tag() == AMObjType::SEQUENCES) || (args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
             (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) ||
             (args[0].tag() == AMObjType::SEMI_MARKOV_DATA) ||
             (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV_DATA) || (args[0].tag() == AMObjType::TOPS)) {
      const Sequences *seq;


      format = 'c';

      if (format_pstr) {
        if (*format_pstr == "Column") {
          format = 'c';
        }
        else if (*format_pstr == "Vector") {
          format = 'v';
        }
        else if (*format_pstr == "Line") {
          format = 'l';
        }
        else if (*format_pstr == "Array") {
          format = 'a';
        }
        else if (*format_pstr == "PosteriorProbability") {
          format = 'p';
        }
        else {
          status = false;
          genAMLError(ERRORMSG(SEQUENCE_FORMAT_sds) , "Save" ,
                      format_index , "Column or Line");
        }
      }

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }

      switch (args[0].tag()) {
      case AMObjType::SEQUENCES :
        seq = (Sequences*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::MARKOVIAN_SEQUENCES :
        seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
        seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::SEMI_MARKOV_DATA :
        seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::NONHOMOGENEOUS_MARKOV_DATA :
        seq = (NonhomogeneousMarkovData*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::TOPS :
        seq = (Tops*)((STAT_model*)args[0].val.p)->pt;
        break;
      }

      status = seq->ascii_data_write(error , ((AMString*)args[1].val.p)->data() ,
                                     format , exhaustive);
    }

    else {
      genAMLError(ERRORMSG(STAT_DATA_TYPE_sds) , "Save" , 1 , args[0].tag.string().data());
      return AMObj(AMObjType::ERROR);
    }
    break;
  }

  case 's' : {
    CHECKCONDVA(nb_required == 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Save"));

    format = 'a';

    if (format_pstr) {
      if (*format_pstr == "ASCII") {
        format = 'a';
      }
      else if (*format_pstr == "SpreadSheet") {
        format = 's';
      }
      else if (*format_pstr == "Gnuplot") {
        format = 'g';
      }
      else {
        status = false;
        genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "Save" ,
                    format_index , "ASCII or SpreadSheet");
      }
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    if ((args[0].tag() == AMObjType::DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE) ||
        (args[0].tag() == AMObjType::CONVOLUTION) || (args[0].tag() == AMObjType::COMPOUND)) {
      Distribution *dist;


      switch (args[0].tag()) {
      case AMObjType::DISTRIBUTION :
        dist = (Distribution*)((DiscreteParametricModel*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::DISCRETE_MIXTURE :
        dist = (Distribution*)((DiscreteMixture*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::CONVOLUTION :
        dist = (Distribution*)((Convolution*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::COMPOUND :
        dist = (Distribution*)((Compound*)((STAT_model*)args[0].val.p)->pt);
        break;
      }

      switch (format) {
      case 'a' :
        status = dist->survival_ascii_write(error , ((AMString*)args[1].val.p)->data());
        break;
      case 's' :
        status = dist->survival_spreadsheet_write(error , ((AMString*)args[1].val.p)->data());
        break;
      case 'g' :
        status = dist->survival_plot_write(error , ((AMString*)args[1].val.p)->data());
        break;
      }
    }

    else if ((args[0].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
             (args[0].tag() == AMObjType::CONVOLUTION_DATA) || (args[0].tag() == AMObjType::COMPOUND_DATA)) {
      FrequencyDistribution *histo;


      switch (args[0].tag()) {
      case AMObjType::FREQUENCY_DISTRIBUTION :
        histo = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::DISCRETE_MIXTURE_DATA :
        histo = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::CONVOLUTION_DATA :
        histo = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[0].val.p)->pt);
        break;
      case AMObjType::COMPOUND_DATA :
        histo = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[0].val.p)->pt);
        break;
      }

      switch (format) {
      case 'a' :
        status = histo->survival_ascii_write(error , ((AMString*)args[1].val.p)->data());
        break;
      case 's' :
        status = histo->survival_spreadsheet_write(error , ((AMString*)args[1].val.p)->data());
        break;
      case 'g' :
        status = histo->survival_plot_write(error , ((AMString*)args[1].val.p)->data());
        break;
      }
    }

    else {
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , 1 , args[0].tag.string().data() ,
                  "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND or FREQUENCY_DISTRIBUTION or DISCRETE_MIXTURE_DATA or CONVOLUTION_DATA or COMPOUND_DATA");
      return AMObj(AMObjType::ERROR);
    }
    break;
  }

  case 'q' : {
    int nb_variable , *model_type;
    const Sequences *seq;
    StatError error;


    CHECKCONDVA(nb_required >= 5 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Save"));

    switch (args[0].tag()) {
    case AMObjType::SEQUENCES :
      seq = (Sequences*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::MARKOVIAN_SEQUENCES :
      seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
      seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::SEMI_MARKOV_DATA :
      seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
      break;
    default :
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , 1 , args[0].tag.string().data() ,
                  "SEQUENCES or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA");
      return AMObj(AMObjType::ERROR);
    }

    nb_variable = seq->get_nb_variable();

    model_type = new int[nb_variable];

    if (args[2].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , 3 ,
                  args[2].tag.string().data() , "INT");
    }
    if (args[3].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , 4 ,
                  args[3].tag.string().data() , "INT");
    }

    for (i = 0;i < nb_variable;i++) {
      if (args[i + 4].tag() != AMObjType::STRING) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , i + 5 ,
                    args[i + 4].tag.string().data() , "STRING");
      }

      else {
        pstr = (AMString*)args[i + 4].val.p;

        if (i == 0) {
          if (*pstr == "Categorical") {
            model_type[i] = CATEGORICAL_CHANGE;
          }
          else if (*pstr == "MultivariateCategorical") {
            model_type[i] = MULTIVARIATE_CATEGORICAL_CHANGE;
          }
          else if (*pstr == "Poisson") {
            model_type[i] = POISSON_CHANGE;
          }
          else if (*pstr == "MultivariatePoisson") {
            model_type[i] = MULTIVARIATE_POISSON_CHANGE;
          }
          else if (*pstr == "Geometric") {
            model_type[i] = GEOMETRIC_0_CHANGE;
          }
          else if (*pstr == "ShiftedGeometric") {
            model_type[i] = GEOMETRIC_1_CHANGE;
          }
          else if (*pstr == "MultivariateGeometric") {
            model_type[i] = MULTIVARIATE_GEOMETRIC_0_CHANGE;
          }
          else if (*pstr == "Ordinal") {
            model_type[i] = ORDINAL_GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Gaussian") {
            model_type[i] = GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Mean") {
            model_type[i] = MEAN_CHANGE;
          }
          else if (*pstr == "Variance") {
            model_type[i] = VARIANCE_CHANGE;
          }
          else if (*pstr == "MeanVariance") {
            model_type[i] = MEAN_VARIANCE_CHANGE;
          }
          else if (*pstr == "LinearModel") {
            model_type[i] = LINEAR_MODEL_CHANGE;
          }
          else if (*pstr == "InterceptSlope") {
            model_type[i] = INTERCEPT_SLOPE_CHANGE;
          }
          else if (*pstr == "BayesianPoisson") {
            model_type[i] = BAYESIAN_POISSON_CHANGE;
          }
          else if (*pstr == "BayesianGaussian") {
            model_type[i] = BAYESIAN_GAUSSIAN_CHANGE;
          }
          else {
            status = false;
            genAMLError(ERRORMSG(CHANGE_POINT_MODEL_sds) , "Save" , i + 5 ,
                        "Categorical or Poisson or MultivariatePoisson or Geometric or ShiftedGeometric or MultivariateGeometric or Ordinal or Gaussian or Mean or Variance or MeanVariance or LinearModel or InterceptSlope");
          }

          if ((model_type[i] == MULTIVARIATE_CATEGORICAL_CHANGE) || (model_type[i] == MULTIVARIATE_POISSON_CHANGE) ||
              (model_type[i] == MULTIVARIATE_GEOMETRIC_0_CHANGE) || (model_type[i] == MEAN_CHANGE) ||
              (model_type[i] == MEAN_VARIANCE_CHANGE) || (model_type[i] == INTERCEPT_SLOPE_CHANGE)) {
            CHECKCONDVA(nb_required == 5 ,
                        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Save"));

            for (j = 1;j < nb_variable;j++) {
              model_type[j] = model_type[i];
            }
            break;
          }

          else {
            CHECKCONDVA(nb_required == nb_variable + 4 ,
                        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Save"));
          }
        }

        else {
          if (*pstr == "Categorical") {
            model_type[i] = CATEGORICAL_CHANGE;
          }
          else if (*pstr == "Poisson") {
            model_type[i] = POISSON_CHANGE;
          }
          else if (*pstr == "Geometric") {
            model_type[i] = GEOMETRIC_0_CHANGE;
          }
          else if (*pstr == "ShiftedGeometric") {
            model_type[i] = GEOMETRIC_1_CHANGE;
          }
          else if (*pstr == "Ordinal") {
            model_type[i] = ORDINAL_GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Gaussian") {
            model_type[i] = GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Variance") {
            model_type[i] = VARIANCE_CHANGE;
          }
          else if (*pstr == "LinearModel") {
            model_type[i] = LINEAR_MODEL_CHANGE;
          }
          else if (*pstr == "InterceptSlope") {
            model_type[i] = INTERCEPT_SLOPE_CHANGE;
          }
          else {
            status = false;
            genAMLError(ERRORMSG(CHANGE_POINT_MODEL_sds) , "Save" , i + 5 ,
                        "Categorical or Poisson or Geometric or ShiftedGeometric or Ordinal or Gaussian or Variance or LinearModel or InterceptSlope");
          }
        }
      }
    }

    format = 'a';

    if (format_pstr) {
      if (*format_pstr == "ASCII") {
        format = 'a';
      }
      else if (*format_pstr == "SpreadSheet") {
        format = 's';
      }
      else {
        status = false;
        genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "Save" ,
                    format_index , "ASCII or SpreadSheet");
      }
    }

    if (!status) {
      delete [] model_type;
      return AMObj(AMObjType::ERROR);
    }

    status = seq->segment_profile_write(error , ((AMString*)args[1].val.p)->data() ,
                                        args[2].val.i , args[3].val.i , model_type ,
                                        output , format , segmentation , nb_segmentation);
    delete [] model_type;

    if (!status) {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Save");
      return AMObj(AMObjType::ERROR);
    }
    break;
  }

  case 'p' : {
    CHECKCONDVA(nb_required >= 3 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Save"));

    if (args[2].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , 3 ,
                  args[2].tag.string().data() , "INT");
    }

    format = 'a';

    if (format_pstr) {
      if (*format_pstr == "ASCII") {
        format = 'a';
      }
      else if (*format_pstr == "SpreadSheet") {
        format = 's';
      }
      else {
        status = false;
        genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "Save" ,
                    format_index , "ASCII or SpreadSheet");
      }
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    if (args[0].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) {
      CHECKCONDVA(nb_required == 3 ,
                  genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Save"));

      status = ((HiddenVariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt)->state_profile_write(error , ((AMString*)args[1].val.p)->data() , args[2].val.i , format , state_sequence , nb_state_sequence);
    }

    else if (args[0].tag() == AMObjType::HIDDEN_SEMI_MARKOV) {
      CHECKCONDVA(nb_required == 3 ,
                  genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Save"));

      status = ((HiddenSemiMarkov*)((STAT_model*)args[0].val.p)->pt)->state_profile_write(error , ((AMString*)args[1].val.p)->data() , args[2].val.i , output , format , state_sequence , nb_state_sequence);
    }

    else {
      const MarkovianSequences *seq;


      CHECKCONDVA(nb_required == 4 ,
                  genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Save"));

      switch (args[0].tag()) {
      case AMObjType::MARKOVIAN_SEQUENCES :
        seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
        seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::SEMI_MARKOV_DATA :
        seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
        break;
      case AMObjType::NONHOMOGENEOUS_MARKOV_DATA :
        seq = (NonhomogeneousMarkovData*)((STAT_model*)args[0].val.p)->pt;
        break;
      default :
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , 1 , args[0].tag.string().data() ,
                    "HIDDEN_VARIABLE_ORDER_MARKOV or HIDDEN_SEMI-MARKOV or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
        return AMObj(AMObjType::ERROR);
      }

      if (args[3].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) {
        status = ((HiddenVariableOrderMarkov*)((STAT_model*)args[3].val.p)->pt)->state_profile_write(error , ((AMString*)args[1].val.p)->data() , *seq , args[2].val.i , format , state_sequence , nb_state_sequence);
      }

      else if (args[3].tag() == AMObjType::HIDDEN_SEMI_MARKOV) {
        status = ((HiddenSemiMarkov*)((STAT_model*)args[3].val.p)->pt)->state_profile_write(error , ((AMString*)args[1].val.p)->data() , *seq , args[2].val.i , output , format , state_sequence , nb_state_sequence);
      }

      else {
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Save" , 4 , args[3].tag.string().data() ,
                    "HIDDEN_VARIABLE_ORDER_MARKOV or HIDDEN_SEMI-MARKOV");
        return AMObj(AMObjType::ERROR);
      }
    }
    break;
  }
  }

  if (status) {
    return AMObj(AMObjType::VOID);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Save");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Sortie Gnuplot.
 *
 *--------------------------------------------------------------*/

AMObj STAT_model::plot(GP_window &window , const AMObjVector &args) const

{
  RWCString *pstr;
  char view_point = 'v' , *title = NULL;
  bool status = true , data = false , survival = false , config = false , mode = false ,
       window_option = false , mode_option = false , view_point_option = false ,
       title_option = false , output_option = false;
  register int i , j;
  int nb_required , nb_object = 0 , variable , type , output;
  const Distribution **pdist;
  const HiddenVariableOrderMarkov *hmarkov;
  const HiddenSemiMarkov *hsmarkov;
  const FrequencyDistribution **phisto;
  const MarkovianSequences *seq;
  ifstream in_file;
  StatError error;


  CHECKCONDVA(args[0].tag() != AMObjType::VECTOR_DISTANCE ,
              genAMLError(ERRORMSG(STAT_TYPE_VECTOR_DISTANCE_sds) , "Plot" , 1 ,
                          args[0].tag.string().data()));

  pdist = NULL;
  phisto = NULL;

  nb_required = nb_required_computation(args);

  // arguments obligatoires

  if (nb_required >= 1) {
    if ((args[0].tag() == AMObjType::DISTRIBUTION) || (args[0].tag() == AMObjType::FREQUENCY_DISTRIBUTION) ||
        (args[0].tag() == AMObjType::DISCRETE_MIXTURE) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
        (args[0].tag() == AMObjType::CONVOLUTION) || (args[0].tag() == AMObjType::CONVOLUTION_DATA) ||
        (args[0].tag() == AMObjType::COMPOUND) || (args[0].tag() == AMObjType::COMPOUND_DATA)) {
      nb_object = nb_required;
      if (nb_object == 1) {
        survival = true;
      }

      else {
        if ((args[0].tag() == AMObjType::DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE) ||
            (args[0].tag() == AMObjType::CONVOLUTION) || (args[0].tag() == AMObjType::COMPOUND)) {
          pdist = new const Distribution*[nb_required];

          switch (args[0].tag()) {
          case AMObjType::DISTRIBUTION :
            pdist[0] = (Distribution*)((DiscreteParametricModel*)((STAT_model*)args[0].val.p)->pt);
            break;
          case AMObjType::DISCRETE_MIXTURE :
            pdist[0] = (Distribution*)((DiscreteMixture*)((STAT_model*)args[0].val.p)->pt);
            break;
          case AMObjType::CONVOLUTION :
            pdist[0] = (Distribution*)((Convolution*)((STAT_model*)args[0].val.p)->pt);
            break;
          case AMObjType::COMPOUND :
            pdist[0] = (Distribution*)((Compound*)((STAT_model*)args[0].val.p)->pt);
            break;
          }

          for (i = 1;i < nb_required;i++) {
            switch (args[i].tag()) {
            case AMObjType::DISTRIBUTION :
              pdist[i] = (Distribution*)((DiscreteParametricModel*)((STAT_model*)args[i].val.p)->pt);
              break;
            case AMObjType::DISCRETE_MIXTURE :
              pdist[i] = (Distribution*)((DiscreteMixture*)((STAT_model*)args[i].val.p)->pt);
              break;
            case AMObjType::CONVOLUTION :
              pdist[i] = (Distribution*)((Convolution*)((STAT_model*)args[i].val.p)->pt);
              break;
            case AMObjType::COMPOUND :
              pdist[i] = (Distribution*)((Compound*)((STAT_model*)args[i].val.p)->pt);
              break;
            default :
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , i + 1 , args[i].tag.string().data() ,
                          "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
            }
          }
        }

        else if ((args[0].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
                 (args[0].tag() == AMObjType::CONVOLUTION_DATA) || (args[0].tag() == AMObjType::COMPOUND_DATA)) {
          phisto = new const FrequencyDistribution*[nb_required];

          switch (args[0].tag()) {
          case AMObjType::FREQUENCY_DISTRIBUTION :
            phisto[0] = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[0].val.p)->pt);
            break;
          case AMObjType::DISCRETE_MIXTURE_DATA :
            phisto[0] = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[0].val.p)->pt);
            break;
          case AMObjType::CONVOLUTION_DATA :
            phisto[0] = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[0].val.p)->pt);
            break;
          case AMObjType::COMPOUND_DATA :
            phisto[0] = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[0].val.p)->pt);
            break;
          }

          for (i = 1;i < nb_required;i++) {
            switch (args[i].tag()) {
            case AMObjType::FREQUENCY_DISTRIBUTION :
              phisto[i] = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[i].val.p)->pt);
              break;
            case AMObjType::DISCRETE_MIXTURE_DATA :
              phisto[i] = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[i].val.p)->pt);
              break;
            case AMObjType::CONVOLUTION_DATA :
              phisto[i] = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[i].val.p)->pt);
              break;
            case AMObjType::COMPOUND_DATA :
              phisto[i] = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[i].val.p)->pt);
              break;
            default :
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , i + 1 , args[i].tag.string().data() ,
                          "FREQUENCY_DISTRIBUTION or DISCRETE_MIXTURE_DATA or CONVOLUTION_DATA or COMPOUND_DATA");
            }
          }
        }
      }
    }

    else if ((args[0].tag() == AMObjType::REGRESSION) || (args[0].tag() == AMObjType::RENEWAL) ||
             (args[0].tag() == AMObjType::TIME_EVENTS) || (args[0].tag() == AMObjType::RENEWAL_DATA) ||
             (args[0].tag() == AMObjType::CORRELATION) || (args[0].tag() == AMObjType::DISTANCE_MATRIX) ||
             (args[0].tag() == AMObjType::CLUSTERS) || (args[0].tag() == AMObjType::TOP_PARAMETERS) ||
             (args[0].tag() == AMObjType::TOPS)) {
      if (nb_required != 1) {
        status = false;
        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot");
      }
      else {
        nb_object = 1;
        if (args[0].tag() == AMObjType::TOPS) {
          data = true;
        }
      }
    }

    else if ((args[0].tag() == AMObjType::SEQUENCES) && (nb_required == 1)) {
      nb_object = 1;
      data = true;
    }

    else if ((args[0].tag() == AMObjType::MIXTURE) || (args[0].tag() == AMObjType::VECTORS) ||
             (args[0].tag() == AMObjType::MIXTURE_DATA)) {
      if (nb_required > 2) {
        status = false;
        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot");
      }
      else {
        nb_object = 1;
      }
    }

    else if (((args[0].tag() == AMObjType::SEQUENCES) || (args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
              (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) || (args[0].tag() == AMObjType::SEMI_MARKOV_DATA)) && (nb_required >= 4)) {
      nb_object = 1;
    }

    else if ((args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV) ||
             (args[0].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) ||
             (args[0].tag() == AMObjType::SEMI_MARKOV) || (args[0].tag() == AMObjType::HIDDEN_SEMI_MARKOV) ||
             (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV) ||
             (args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
             (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) ||
             (args[0].tag() == AMObjType::SEMI_MARKOV_DATA) ||
             (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV_DATA)) {
      if (nb_required > 3) {
        status = false;
        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot");
      }

      else {
        nb_object = 1;
        if ((nb_required == nb_object) && ((args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
             (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) ||
             (args[0].tag() == AMObjType::SEMI_MARKOV_DATA) ||
             (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV_DATA))) {
          data = true;
        }

        if ((nb_required >= nb_object + 1) && ((args[0].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) ||
             (args[0].tag() == AMObjType::HIDDEN_SEMI_MARKOV) || (args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
             (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) ||
             (args[0].tag() == AMObjType::SEMI_MARKOV_DATA)) && (args[1].tag() == AMObjType::INTEGER)) {
          config = true;
        }
      }
    }

    else if (nb_required > 2) {
      status = false;
      genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot");
    }

    if (((nb_required == nb_object + 1) || (nb_required == nb_object + 2)) && (!config)) {
      if (args[nb_object].tag() == AMObjType::STRING) {
        if (nb_required == nb_object + 1) {
          if (args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) {
            variable = 1;
          }
          else {
            variable = 0;
          }
        }

        pstr = (AMString*)args[nb_object].val.p;
        if ((nb_required == nb_object + 1) && (*pstr == "SelfTransition")) {
          type = 0;
        }
        else if ((nb_required == nb_object + 2) && (*pstr == "Observation")) {
          type = 0;
        }
        else if (*pstr == "Intensity") {
          type = 1;
        }
        else if (*pstr == "FirstOccurrence") {
          type = 2;
        }
        else if (*pstr == "Recurrence") {
          type = 3;
        }
        else if (*pstr == "Sojourn") {
          type = 4;
        }
        else if (*pstr == "Counting") {
          type = 5;
        }

        else {
          status = false;

          switch (nb_required - nb_object) {
          case 1 :
            genAMLError(ERRORMSG(PLOT_TYPE_sds) , "Plot" , nb_object + 1 ,
                        "SelfTransition or Intensity or FirstOccurrence or Recurrence or Sojourn or Counting");
            break;
          case 2 :
            genAMLError(ERRORMSG(PLOT_TYPE_sds) , "Plot" , nb_object + 1 ,
                        "Observation or Intensity or FirstOccurrence or Recurrence or Sojourn or Counting");
            break;
          }
        }
      }

      else if (args[nb_object].tag() != AMObjType::INTEGER) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , nb_object + 1 ,
                    args[nb_object].tag.string().data() , "INT or STRING");
      }

      if (args[nb_required - 1].tag() == AMObjType::INTEGER) {
        variable = args[nb_required - 1].val.i;
      }
      else if (nb_required == nb_object + 2) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , nb_object + 2 ,
                    args[nb_object + 1].tag.string().data() , "INT");
      }
    }
  }

  if (nb_object == 0) {
    if ((args.length() != nb_required) && (args.length() != nb_required + 2) &&
        (args.length() != nb_required + 4)) {
      status = false;
      genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot");
    }
  }
  else {
    if ((args.length() != nb_required) && (args.length() != nb_required + 2) &&
        (args.length() != nb_required + 4) && (args.length() != nb_required + 6) &&
        (args.length() != nb_required + 8)) {
      status = false;
      genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot");
    }
  }

  if (!status) {
    delete [] pdist;
    delete [] phisto;
    return AMObj(AMObjType::ERROR);
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "Window") {
        switch (window_option) {

        case false : {
          window_option = true;
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Plot" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Mode") {
        switch (mode_option) {

        case false : {
          mode_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Blocking") {
              mode = false;
            }
            else if (*pstr == "NonBlocking") {
              mode = true;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(PLOTTING_MODE_sds) , "Plot" ,
                          nb_required + i + 1 , "Blocking or NonBlocking");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Plot" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "ViewPoint") {
        switch (view_point_option) {

        case false : {
          view_point_option = true;

          if (nb_object == 0) {
            status = false;
            genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Plot" , "ViewPoint");
          }

          else {
            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Data") {
                view_point = 'd';
                if (!data) {
                  status = false;
                  genAMLError(ERRORMSG(VIEW_POINT_sd) , "Plot" , nb_required + i + 1);
                }
              }
              else if (*pstr == "Survival") {
                view_point = 's';
                if (!survival) {
                  status = false;
                  genAMLError(ERRORMSG(VIEW_POINT_sd) , "Plot" , nb_required + i + 1);
                }
              }
              else if (*pstr == "SegmentProfile") {
                view_point = 'q';
              }
              else if (*pstr == "StateProfile") {
                view_point = 'p';
                if (!config) {
                  status = false;
                  genAMLError(ERRORMSG(VIEW_POINT_sd) , "Plot" , nb_required + i + 1);
                }
              }
              else {
                status = false;
                genAMLError(ERRORMSG(VIEW_POINT_sds) , "Plot" ,
                            nb_required + i + 1 , "Data or Survival or SegmentProfile or StateProfile");
              }
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Plot" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Title") {
        switch (title_option) {

        case false : {
          title_option = true;

          if (nb_object == 0) {
            status = false;
            genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Plot" , "Title");
          }

          else {
            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              title = (char*)((AMString*)args[nb_required + i * 2 + 1].val.p)->data();
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Plot" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Output") {
        switch (output_option) {

        case false : {
          output_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "ChangePoint") {
              output = CHANGE_POINT;
            }
            else if (*pstr == "Segment") {
              output = SEGMENT;
            }
            else if (*pstr == "State") {
              output = SSTATE;
            }
            else if (*pstr == "InState") {
              output = IN_STATE;
            }
            else if (*pstr == "OutState") {
              output = OUT_STATE;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(STATE_PROFILE_TYPE_sds) , "Plot" ,
                          nb_required + i + 1 , "ChangePoint or Segment or State or InState or OutState");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Plot" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        if (nb_object == 0) {
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Plot" ,
                      nb_required + i + 1 , "Window or Mode");
        }
        else {
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Plot" ,
                      nb_required + i + 1 , "Window or Mode or ViewPoint or Title or Output");
        }
      }
    }
  }

  if ((output_option) && ((view_point != 'q') ||
       ((args[0].tag() != AMObjType::SEQUENCES) && (args[0].tag() != AMObjType::MARKOVIAN_SEQUENCES) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV_DATA))) &&
      ((view_point != 'p') || ((args[0].tag() != AMObjType::HIDDEN_SEMI_MARKOV) &&
        (args[0].tag() != AMObjType::MARKOVIAN_SEQUENCES) &&
        (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::SEMI_MARKOV_DATA) &&
        (args[0].tag() != AMObjType::NONHOMOGENEOUS_MARKOV_DATA)))) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "Plot");
  }

  switch (output_option) {

  case false : {
    switch (view_point) {
    case 'q' :
      output = SEGMENT;
      break;
    case 'p' :
      output = SSTATE;
      break;
    }
    break;
  }

  case true : {
    if (((view_point == 'q') && (output != CHANGE_POINT) && (output != SEGMENT)) ||
        ((view_point == 'p') && (output != STATE) && (output != IN_STATE) && (output != OUT_STATE))) {
      status = false;
      genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_sss) , "Plot" , "ViewPoint" , "Output");
    }
    break;
  }
  }

  if ((config) && (view_point != 'p') && ((args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
       (args[0].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) || (args[0].tag() == AMObjType::HIDDEN_SEMI_MARKOV) ||
       (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) || (args[0].tag() == AMObjType::SEMI_MARKOV_DATA))) {
    variable = args[1].val.i;

    switch (args[0].tag()) {

    case AMObjType::MARKOVIAN_SEQUENCES : {
      seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
      if ((variable <= seq->get_nb_variable()) && (seq->get_characteristics(variable - 1))) {
        status = false;
        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot");
      }
      break;
    }

    case AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV : {
      hmarkov = (HiddenVariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt;
      if ((variable <= hmarkov->get_nb_output_process()) &&
          (hmarkov->get_categorical_process(variable - 1))) {
        status = false;
        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot");
      }
      break;
    }

    case AMObjType::HIDDEN_SEMI_MARKOV : {
      hsmarkov = (HiddenSemiMarkov*)((STAT_model*)args[0].val.p)->pt;
      if ((variable <= hsmarkov->get_nb_output_process()) &&
          (hsmarkov->get_categorical_process(variable - 1))) {
        status = false;
        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot");
      }
      break;
    }

    case AMObjType::VARIABLE_ORDER_MARKOV_DATA : {
      seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
      if ((variable < seq->get_nb_variable()) && (seq->get_characteristics(variable))) {
        status = false;
        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot");
      }
      break;
    }

    case AMObjType::SEMI_MARKOV_DATA : {
      seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
      if ((variable < seq->get_nb_variable()) && (seq->get_characteristics(variable))) {
        status = false;
        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot");
      }
      break;
    }
    }
  }

  if (!status) {
    delete [] pdist;
    delete [] phisto;
    return AMObj(AMObjType::ERROR);
  }

  if (nb_object > 0) {

//  cpl
    window.end_old_session();
//  cpl

    // destruction des fichiers Gnuplot courants

#   ifdef _WIN32
    if(VPTOOLS(exists)(string(Plot_prefix) + string(".plot"))) {
      string buffer = string("ERASE /F /Q ") + Plot_prefix + "*";
      if (system(buffer.c_str()) == -1) {
        aml_system_error(AMLOUTPUT , "ERASE");
      }
    }
#   else
    {
      ostringstream buffer;
      buffer << "rm -f " << Plot_prefix << "*";
      if (system((buffer.str()).c_str()) == -1) {
        aml_system_error(AMLOUTPUT , "rm");
      }
    }
#   endif

    // generation des fichiers Gnuplot

    if (nb_object == 1) {
      switch (view_point) {

      case 'v' : {
        ((STAT_model*)args[0].val.p)->pt->plot_write(error , Plot_prefix , title);
        break;
      }

      case 'd' : {
        Sequences *seq;


        switch (args[0].tag()) {
        case AMObjType::SEQUENCES :
          seq = (Sequences*)((STAT_model*)args[0].val.p)->pt;
          break;
        case AMObjType::MARKOVIAN_SEQUENCES :
          seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
          break;
        case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
          seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
          break;
        case AMObjType::SEMI_MARKOV_DATA :
          seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
          break;
        case AMObjType::NONHOMOGENEOUS_MARKOV_DATA :
          seq = (NonhomogeneousMarkovData*)((STAT_model*)args[0].val.p)->pt;
          break;
        case AMObjType::TOPS :
          seq = (Tops*)((STAT_model*)args[0].val.p)->pt;
          break;
        }

        status = seq->plot_data_write(error , Plot_prefix , title);
        break;
      }

      case 's' : {
        if ((args[0].tag() == AMObjType::DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE) ||
            (args[0].tag() == AMObjType::CONVOLUTION) || (args[0].tag() == AMObjType::COMPOUND)) {
          const Distribution *dist;


          switch (args[0].tag()) {
          case AMObjType::DISTRIBUTION :
            dist = (Distribution*)((DiscreteParametricModel*)((STAT_model*)args[0].val.p)->pt);
            break;
          case AMObjType::DISCRETE_MIXTURE :
            dist = (Distribution*)((DiscreteMixture*)((STAT_model*)args[0].val.p)->pt);
            break;
          case AMObjType::CONVOLUTION :
            dist = (Distribution*)((Convolution*)((STAT_model*)args[0].val.p)->pt);
            break;
          case AMObjType::COMPOUND :
            dist = (Distribution*)((Compound*)((STAT_model*)args[0].val.p)->pt);
            break;
          }

          status = dist->survival_plot_write(error , Plot_prefix , title);
        }

        else if ((args[0].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
                 (args[0].tag() == AMObjType::CONVOLUTION_DATA) || (args[0].tag() == AMObjType::COMPOUND_DATA)) {
          const FrequencyDistribution *histo;


          switch (args[0].tag()) {
          case AMObjType::FREQUENCY_DISTRIBUTION :
            histo = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[0].val.p)->pt);
            break;
          case AMObjType::DISCRETE_MIXTURE_DATA :
            histo = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[0].val.p)->pt);
            break;
          case AMObjType::CONVOLUTION_DATA :
            histo = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[0].val.p)->pt);
            break;
          case AMObjType::COMPOUND_DATA :
            histo = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[0].val.p)->pt);
            break;
          }

          status = histo->survival_plot_write(error , Plot_prefix , title);
        }

        if (!status) {
          AMLOUTPUT << "\n" << error;
          genAMLError(ERRORMSG(STAT_MODULE_s) , "Plot");
          return AMObj(AMObjType::ERROR);
        }
        break;
      }

      case 'q' : {
        int nb_variable , *model_type;
        const Sequences *seq;


        switch (args[0].tag()) {
        case AMObjType::SEQUENCES :
          seq = (Sequences*)((STAT_model*)args[0].val.p)->pt;
          break;
        case AMObjType::MARKOVIAN_SEQUENCES :
          seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
          break;
        case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
          seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
          break;
        case AMObjType::SEMI_MARKOV_DATA :
          seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
          break;
        default :
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , 1 , args[0].tag.string().data() ,
                      "SEQUENCES or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA");
          return AMObj(AMObjType::ERROR);
        }

        nb_variable = seq->get_nb_variable();

        model_type = new int[nb_variable];

        if (args[1].tag() != AMObjType::INTEGER) {
          status = false;
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , 2 ,
                      args[1].tag.string().data() , "INT");
        }
        if (args[2].tag() != AMObjType::INTEGER) {
          status = false;
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , 3 ,
                      args[2].tag.string().data() , "INT");
        }

        for (i = 0;i < nb_variable;i++) {
          if (args[i + 3].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , i + 4 ,
                        args[i + 3].tag.string().data() , "STRING");
          }

          else {
            pstr = (AMString*)args[i + 3].val.p;

            if (i == 0) {
              if (*pstr == "Categorical") {
                model_type[i] = CATEGORICAL_CHANGE;
              }
              else if (*pstr == "MultivariateCategorical") {
                model_type[i] = MULTIVARIATE_CATEGORICAL_CHANGE;
              }
              else if (*pstr == "Poisson") {
                model_type[i] = POISSON_CHANGE;
              }
              else if (*pstr == "MultivariatePoisson") {
                model_type[i] = MULTIVARIATE_POISSON_CHANGE;
              }
              else if (*pstr == "Geometric") {
                model_type[i] = GEOMETRIC_0_CHANGE;
              }
              else if (*pstr == "ShiftedGeometric") {
                model_type[i] = GEOMETRIC_1_CHANGE;
              }
              else if (*pstr == "MultivariateGeometric") {
                model_type[i] = MULTIVARIATE_GEOMETRIC_0_CHANGE;
              }
              else if (*pstr == "Ordinal") {
                model_type[i] = ORDINAL_GAUSSIAN_CHANGE;
              }
              else if (*pstr == "Gaussian") {
                model_type[i] = GAUSSIAN_CHANGE;
              }
              else if (*pstr == "Mean") {
                model_type[i] = MEAN_CHANGE;
              }
              else if (*pstr == "Variance") {
                model_type[i] = VARIANCE_CHANGE;
              }
              else if (*pstr == "MeanVariance") {
                model_type[i] = MEAN_VARIANCE_CHANGE;
              }
              else if (*pstr == "LinearModel") {
                model_type[i] = LINEAR_MODEL_CHANGE;
              }
              else if (*pstr == "InterceptSlope") {
                model_type[i] = INTERCEPT_SLOPE_CHANGE;
              }
              else if (*pstr == "BayesianPoisson") {
                model_type[i] = BAYESIAN_POISSON_CHANGE;
              }
              else if (*pstr == "BayesianGaussian") {
                model_type[i] = BAYESIAN_GAUSSIAN_CHANGE;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(CHANGE_POINT_MODEL_sds) , "Plot" , i + 4 ,
                            "Categorical or Poisson or MultivariatePoisson or Geometric or ShiftedGeometric or MultivariateGeometric or Ordinal or Gaussian or Mean or Variance or MeanVariance or LinearModel or InterceptSlope");
              }

              if ((model_type[i] == MULTIVARIATE_CATEGORICAL_CHANGE) || (model_type[i] == MULTIVARIATE_POISSON_CHANGE) ||
                  (model_type[i] == MULTIVARIATE_GEOMETRIC_0_CHANGE) || (model_type[i] == MEAN_CHANGE) ||
                  (model_type[i] == MEAN_VARIANCE_CHANGE) || (model_type[i] == INTERCEPT_SLOPE_CHANGE)) {
                CHECKCONDVA(nb_required == 4 ,
                            genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot"));

                for (j = 1;j < nb_variable;j++) {
                  model_type[j] = model_type[i];
                }
                break;
              }

              else {
                CHECKCONDVA(nb_required == nb_variable + 3 ,
                            genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot"));
              }
            }

            else {
              if (*pstr == "Categorical") {
                model_type[i] = CATEGORICAL_CHANGE;
              }
              else if (*pstr == "Poisson") {
                model_type[i] = POISSON_CHANGE;
              }
              else if (*pstr == "Geometric") {
                model_type[i] = GEOMETRIC_0_CHANGE;
              }
              else if (*pstr == "ShiftedGeometric") {
                model_type[i] = GEOMETRIC_1_CHANGE;
              }
              else if (*pstr == "Ordinal") {
                model_type[i] = ORDINAL_GAUSSIAN_CHANGE;
              }
              else if (*pstr == "Gaussian") {
                model_type[i] = GAUSSIAN_CHANGE;
              }
              else if (*pstr == "Variance") {
                model_type[i] = VARIANCE_CHANGE;
              }
              else if (*pstr == "LinearModel") {
                model_type[i] = LINEAR_MODEL_CHANGE;
              }
              else if (*pstr == "InterceptSlope") {
                model_type[i] = INTERCEPT_SLOPE_CHANGE;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(CHANGE_POINT_MODEL_sds) , "Plot" , i + 4 ,
                            "Categorical or Poisson or Geometric or ShiftedGeometric or Ordinal or Gaussian or Variance or LinearModel or InterceptSlope");
              }
            }
          }
        }

        if (!status) {
          delete [] model_type;
          return AMObj(AMObjType::ERROR);
        }

        status = seq->segment_profile_plot_write(error , Plot_prefix , args[1].val.i ,
                                                 args[2].val.i , model_type , output , title);
        delete [] model_type;

        if (status) {
          nb_object = nb_required;
        }
        else {
          AMLOUTPUT << "\n" << error;
          genAMLError(ERRORMSG(STAT_MODULE_s) , "Plot");
          return AMObj(AMObjType::ERROR);
        }
        break;
      }

      case 'p' : {
        if (args[0].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) {
          CHECKCONDVA(nb_required == 2 ,
                      genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot"));

          status = ((HiddenVariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt)->state_profile_plot_write(error , Plot_prefix , args[1].val.i , title);
        }

        else if (args[0].tag() == AMObjType::HIDDEN_SEMI_MARKOV) {
          CHECKCONDVA(nb_required == 2 ,
                      genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot"));

          status = ((HiddenSemiMarkov*)((STAT_model*)args[0].val.p)->pt)->state_profile_plot_write(error , Plot_prefix , args[1].val.i , output , title);
        }

        else {
          const MarkovianSequences *seq;


          CHECKCONDVA(nb_required == 3 ,
                      genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Plot"));

          switch (args[0].tag()) {
          case AMObjType::MARKOVIAN_SEQUENCES :
            seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
            break;
          case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
            seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
            break;
          case AMObjType::SEMI_MARKOV_DATA :
            seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
            break;
          case AMObjType::NONHOMOGENEOUS_MARKOV_DATA :
            seq = (NonhomogeneousMarkovData*)((STAT_model*)args[0].val.p)->pt;
            break;
          default :
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , 1 , args[0].tag.string().data() ,
                        "HIDDEN_VARIABLE_ORDER_MARKOV or HIDDEN_SEMI-MARKOV or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
            return AMObj(AMObjType::ERROR);
          }

          if (args[2].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) {
            status = ((HiddenVariableOrderMarkov*)((STAT_model*)args[2].val.p)->pt)->state_profile_plot_write(error , Plot_prefix , *seq , args[1].val.i , title);
          }

          else if (args[2].tag() == AMObjType::HIDDEN_SEMI_MARKOV) {
            status = ((HiddenSemiMarkov*)((STAT_model*)args[2].val.p)->pt)->state_profile_plot_write(error , Plot_prefix , *seq , args[1].val.i , output , title);
          }

          else {
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Plot" , 3 , args[2].tag.string().data() ,
                        "HIDDEN_VARIABLE_ORDER_MARKOV or HIDDEN_SEMI-MARKOV");
            return AMObj(AMObjType::ERROR);
          }
        }

        if (status) {
          nb_object = nb_required;
        }
        else {
          AMLOUTPUT << "\n" << error;
          genAMLError(ERRORMSG(STAT_MODULE_s) , "Plot");
          return AMObj(AMObjType::ERROR);
        }
        break;
      }
      }
    }

    else {
      if ((args[0].tag() == AMObjType::DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE) ||
          (args[0].tag() == AMObjType::CONVOLUTION) || (args[0].tag() == AMObjType::COMPOUND)) {
        status = pdist[0]->plot_write(error , Plot_prefix , nb_object - 1 , pdist + 1 , title);
        delete [] pdist;
      }

      else if ((args[0].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
               (args[0].tag() == AMObjType::CONVOLUTION_DATA) || (args[0].tag() == AMObjType::COMPOUND_DATA)) {
        status = phisto[0]->plot_write(error , Plot_prefix , nb_object - 1 , phisto + 1 , title);
        delete [] phisto;
      }

      if (!status) {
        AMLOUTPUT << "\n" << error;
        genAMLError(ERRORMSG(STAT_MODULE_s) , "Plot");
        return AMObj(AMObjType::ERROR);
      }
    }

#   ifndef _WIN32
    {
      ostringstream buffer;
      buffer << "chmod 666 " << Plot_prefix << "*" << ends;
      if (system((buffer.str()).c_str()) == -1) {
        aml_system_error(AMLOUTPUT , "chmod");
      }
    }
#   endif

  }

  {
    ostringstream buffer , prefix;

    switch (nb_required - nb_object) {

    case 0 : {
      prefix << Plot_prefix;
      break;
    }

    case 1 : {
      switch (args[nb_object].tag()) {
      case AMObjType::INTEGER :
        prefix << Plot_prefix << variable;
        break;
      case AMObjType::STRING :
        prefix << Plot_prefix << variable << type;
        break;
      }
      break;
    }

    case 2 : {
      prefix << Plot_prefix << variable << type;
      break;
    }
    }

    buffer << prefix.str() << ".plot";

//    Gnuplot port pb
//    in_file.open((buffer.str()).c_str() , ios::nocreate);

    in_file.open((buffer.str()).c_str());
    if (in_file.fail() != 0) {
      genAMLError(ERRORMSG(ARGS_s) , "Plot");
      return AMObj(AMObjType::ERROR);
    }
    window.session((prefix.str()).c_str() , AMLOUTPUT , mode);
  }

  return AMObj(AMObjType::VOID);
}


/*--------------------------------------------------------------*
 *
 *  Sauvegarde dans un fichier au format MTG de sequences.
 *
 *--------------------------------------------------------------*/

AMObj STAT_SaveMTG(const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true;
  register int i;
  int nb_variable , *type;
  const MarkovianSequences *seq;
  StatError error;


  CHECKCONDVA(args.length() >= 3 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "SaveMTG"));

  switch (args[0].tag()) {
  case AMObjType::MARKOVIAN_SEQUENCES :
    seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
    seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::SEMI_MARKOV_DATA :
    seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::NONHOMOGENEOUS_MARKOV_DATA :
    seq = (NonhomogeneousMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  default :
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "SaveMTG" , 1 , args[0].tag.string().data() ,
                "MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
    break;
  }

  if (args[1].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "SaveMTG" , 2 ,
                args[1].tag.string().data() , "STRING");
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  nb_variable = seq->get_nb_variable();

  CHECKCONDVA(args.length() == 2 + nb_variable ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "SaveMTG" , 2 + nb_variable));

  type = new int[nb_variable];

  for (i = 0;i < nb_variable;i++) {
    if (args[2 + i].tag() != AMObjType::STRING) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "SaveMTG" , 3 + i ,
                  args[2 + i].tag.string().data() , "STRING");
    }

    else {
      pstr = (AMString*)args[2 + i].val.p;
      if ((*pstr == "SYMBOLIC") || (*pstr == "S")) {
        type[i] = SYMBOLIC;
      }
      else if ((*pstr == "NUMERIC") || (*pstr == "N")) {
        type[i] = NUMERIC;
      }
      else {
        status = false;
        genAMLError(ERRORMSG(VARIABLE_TYPE_sds) , "SaveMTG" , 3 + i ,
                    "SYMBOLIC(S) or NUMERIC(N)");
      }
    }
  }

  if (!status) {
    delete [] type;
    return AMObj(AMObjType::ERROR);
  }

  status = seq->mtg_write(error , ((AMString*)args[1].val.p)->data() , type);
  delete [] type;

  if (status) {
    return AMObj(AMObjType::VOID);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "SaveMTG");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 * Installation.
 *
 *--------------------------------------------------------------*/

void installSTATModule()

{
  AMObjType type[10];


  type[0] = AMObjType::ANY;
  type[1] = AMObjType::STRING;
  type[2] = AMObjType::STRING;
  installFNode("SaveMTG" , STAT_SaveMTG , 3 , type , AMObjType::VOID);

  type[0] = AMObjType::ANY;
  installFNode("Distribution" , STAT_Distribution , 1 , type , AMObjType::DISTRIBUTION);

  type[0] = AMObjType::ANY;
  installFNode("DiscreteMixture" , STAT_DiscreteMixture , 1 , type , AMObjType::DISCRETE_MIXTURE);

  type[0] = AMObjType::ANY;
  installFNode("Convolution" , STAT_Convolution , 1 , type , AMObjType::CONVOLUTION);

  type[0] = AMObjType::ANY;
  installFNode("Compound" , STAT_Compound , 1 , type , AMObjType::COMPOUND);

  type[0] = AMObjType::ANY;
  installFNode("FrequencyDistribution" , STAT_FrequencyDistribution , 1 , type , AMObjType::FREQUENCY_DISTRIBUTION);

  type[0] = AMObjType::ANY;  // pour compatibilite ascendante
  installFNode("Histogram" , STAT_Histogram , 1 , type , AMObjType::FREQUENCY_DISTRIBUTION);

  type[0] = AMObjType::STRING;
  installFNode("Mixture" , STAT_Mixture , 1 , type , AMObjType::MIXTURE);

  type[0] = AMObjType::ANY;
  installFNode("Vectors" , STAT_Vectors , 1 , type , AMObjType::VECTORS);

  type[0] = AMObjType::ANY;
  installFNode("VectorDistance" , STAT_VectorDistance , 1 , type , AMObjType::VECTOR_DISTANCE);

  type[0] = AMObjType::ANY;
  installFNode("Renewal" , STAT_Renewal , 1 , type , AMObjType::RENEWAL);

  type[0] = AMObjType::ANY;
  installFNode("TimeEvents" , STAT_TimeEvents , 1 , type , AMObjType::TIME_EVENTS);

  type[0] = AMObjType::SEQUENCES;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::INTEGER;
  installFNode("RenewalData" , STAT_RenewalData , 3 , type , AMObjType::RENEWAL_DATA);

  type[0] = AMObjType::STRING;
  installFNode("VariableOrderMarkov" , STAT_VariableOrderMarkov , 1 , type , AMObjType::VARIABLE_ORDER_MARKOV);

  type[0] = AMObjType::STRING;
  installFNode("HiddenVariableOrderMarkov" , STAT_HiddenVariableOrderMarkov , 1 , type , AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV);

  type[0] = AMObjType::STRING;
  installFNode("SemiMarkov" , STAT_SemiMarkov , 1 , type , AMObjType::SEMI_MARKOV);

  type[0] = AMObjType::STRING;
  installFNode("HiddenSemiMarkov" , STAT_HiddenSemiMarkov , 1 , type , AMObjType::HIDDEN_SEMI_MARKOV);

  type[0] = AMObjType::STRING;
  installFNode("NonhomogeneousMarkov" , STAT_NonhomogeneousMarkov , 1 , type , AMObjType::NONHOMOGENEOUS_MARKOV);

  type[0] = AMObjType::ANY;
  installFNode("Sequences" , STAT_Sequences , 1 , type , AMObjType::MARKOVIAN_SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("TopParameters" , STAT_TopParameters , 1 , type , AMObjType::TOP_PARAMETERS);

  type[0] = AMObjType::ANY;
  installFNode("Tops" , STAT_Tops , 1 , type , AMObjType::TOPS);

//  type[0] = AMObjType::STRING;
//  installFNode("Load" , STAT_Load , 1 , type , AMObjType::DISTRIBUTION);

  type[0] = AMObjType::FREQUENCY_DISTRIBUTION;
  installFNode("ToDistribution" , STAT_ToDistribution , 1 , type , AMObjType::DISTRIBUTION);

  type[0] = AMObjType::DISTRIBUTION;
  installFNode("ToFrequencyDistribution" , STAT_ToFrequencyDistribution , 1 , type , AMObjType::FREQUENCY_DISTRIBUTION);

  type[0] = AMObjType::DISTRIBUTION;  // pour compatibilite ascendante
  installFNode("ToHistogram" , STAT_ToHistogram , 1 , type , AMObjType::FREQUENCY_DISTRIBUTION);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("ExtractDistribution" , STAT_ExtractDistribution , 2 , type , AMObjType::DISTRIBUTION);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("ExtractFrequencyDistribution" , STAT_ExtractFrequencyDistribution , 2 , type , AMObjType::FREQUENCY_DISTRIBUTION);

  type[0] = AMObjType::ANY;  // pour compatibilite ascendante
  type[1] = AMObjType::ANY;
  installFNode("ExtractHistogram" , STAT_ExtractHistogram , 2 , type , AMObjType::FREQUENCY_DISTRIBUTION);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("ExtractVectors" , STAT_ExtractVectors , 2 , type , AMObjType::VECTORS);

  type[0] = AMObjType::ANY;
  installFNode("ExtractData" , STAT_ExtractData , 1 , type , AMObjType::DISCRETE_MIXTURE_DATA);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("Merge" , STAT_Merge , 2 , type , AMObjType::FREQUENCY_DISTRIBUTION);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("Shift" , STAT_Shift , 2 , type , AMObjType::FREQUENCY_DISTRIBUTION);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::STRING;
  type[2] = AMObjType::ANY;
  installFNode("Cluster" , STAT_Cluster , 3 , type , AMObjType::FREQUENCY_DISTRIBUTION);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("Transcode" , STAT_Transcode , 2 , type , AMObjType::FREQUENCY_DISTRIBUTION);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("ValueSelect" , STAT_ValueSelect , 2 , type , AMObjType::FREQUENCY_DISTRIBUTION);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("VariableScaling" , STAT_VariableScaling , 2 , type , AMObjType::VECTORS);

  type[0] = AMObjType::ANY;
  installFNode("Round" , STAT_Round , 1 , type , AMObjType::VECTORS);

  type[0] = AMObjType::ANY;
  installFNode("SelectStep" , STAT_SelectStep , 1 , type , AMObjType::VECTORS);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("SelectIndividual" , STAT_SelectIndividual , 2 , type , AMObjType::VECTORS);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("SelectVariable" , STAT_SelectVariable , 2 , type , AMObjType::VECTORS);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("MergeVariable" , STAT_MergeVariable , 2 , type , AMObjType::VECTORS);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::INTEGER;
  installFNode("NbEventSelect" , STAT_NbEventSelect , 3 , type , AMObjType::TIME_EVENTS);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("TimeScaling" , STAT_TimeScaling , 2 , type , AMObjType::TIME_EVENTS);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::INTEGER;
  installFNode("TimeSelect" , STAT_TimeSelect , 3 , type , AMObjType::TIME_EVENTS);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::INTEGER;
  installFNode("ShiftVariable" , STAT_ShiftVariable , 3 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::INTEGER;
  installFNode("LengthSelect" , STAT_LengthSelect , 3 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::ANY;
  installFNode("RemoveRun" , STAT_RemoveRun , 3 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("Reverse" , STAT_Reverse , 1 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("RemoveIndexParameter" , STAT_RemoveIndexParameter , 1 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("ExplicitIndexParameter" , STAT_ExplicitIndexParameter , 1 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("IndexParameterSelect" , STAT_IndexParameterSelect , 2 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("IndexParameterExtract" , STAT_IndexParameterExtract , 2 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::INTEGER;
  type[3] = AMObjType::STRING;
  installFNode("SegmentationExtract" , STAT_SegmentationExtract , 4 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("Cumulate" , STAT_Cumulate , 1 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("Difference" , STAT_Difference , 1 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("SequenceNormalization" , STAT_SequenceNormalization , 1 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("MovingAverage" , STAT_MovingAverage , 2 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("PointwiseAverage" , STAT_PointwiseAverage , 1 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("RecurrenceTimeSequences" , STAT_RecurrenceTimeSequences , 2 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("SojournTimeSequences" , STAT_SojournTimeSequences , 1 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::SEQUENCES;
  type[1] = AMObjType::INTEGER;
  installFNode("TransformPosition" , STAT_TransformPosition , 2 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("Cross" , STAT_Cross , 1 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("ComputeInitialRun" , STAT_ComputeInitialRun , 1 , type , AMObjType::MARKOVIAN_SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("AddAbsorbingRun" , STAT_AddAbsorbingRun , 1 , type , AMObjType::MARKOVIAN_SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("ConsecutiveValues" , STAT_ConsecutiveValues , 1 , type , AMObjType::MARKOVIAN_SEQUENCES);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("Split" , STAT_Split , 2 , type , AMObjType::MARKOVIAN_SEQUENCES);

  type[0] = AMObjType::CLUSTERS;
  installFNode("ToDistanceMatrix" , STAT_ToDistanceMatrix , 1 , type , AMObjType::DISTANCE_MATRIX);

  type[0] = AMObjType::DISTANCE_MATRIX;
  installFNode("Symmetrize" , STAT_Symmetrize , 1 , type , AMObjType::DISTANCE_MATRIX);

  type[0] = AMObjType::DISTANCE_MATRIX;
  installFNode("Unnormalize" , STAT_Unnormalize , 1 , type , AMObjType::DISTANCE_MATRIX);

  type[0] = AMObjType::TOPS;
  type[1] = AMObjType::INTEGER;
  installFNode("RemoveApicalInternodes" , STAT_RemoveApicalInternodes , 2 , type , AMObjType::TOPS);

  type[0] = AMObjType::ANY;
  installFNode("Estimate" , STAT_Estimate , 1 , type , AMObjType::DISTRIBUTION);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("Simulate" , STAT_Simulate , 2 , type , AMObjType::FREQUENCY_DISTRIBUTION);

  type[0] = AMObjType::ANY;
  installFNode("Compare" , STAT_Compare , 1 , type , AMObjType::VOID);

  type[0] = AMObjType::DISTANCE_MATRIX;
  type[1] = AMObjType::STRING;
  installFNode("Clustering" , STAT_Clustering , 2 , type , AMObjType::CLUSTERS);

  type[0] = AMObjType::STRING;
  type[1] = AMObjType::ANY;
  type[2] = AMObjType::ANY;
  installFNode("ComparisonTest" , STAT_ComparisonTest , 3 , type , AMObjType::VOID);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::DISTRIBUTION;
  installFNode("Fit" , STAT_Fit , 2 , type , AMObjType::DISTRIBUTION);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("TruncateDistribution" , STAT_TruncateDistribution , 2 , type , AMObjType::DISTRIBUTION);

  type[0] = AMObjType::VECTORS;
  installFNode("ComputeRankCorrelation" , STAT_ComputeRankCorrelation , 1 , type , AMObjType::VOID);

  type[0] = AMObjType::VECTORS;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::INTEGER;
  installFNode("ContingencyTable" , STAT_ContingencyTable , 3 , type , AMObjType::VOID);

  type[0] = AMObjType::VECTORS;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::INTEGER;
  installFNode("VarianceAnalysis" , STAT_VarianceAnalysis , 3 , type , AMObjType::VOID);

  type[0] = AMObjType::VECTORS;
  type[1] = AMObjType::STRING;
  installFNode("Regression" , STAT_Regression , 2 , type , AMObjType::VOID);

  type[0] = AMObjType::ANY;
  installFNode("ComputeCorrelation" , STAT_ComputeCorrelation , 1 , type , AMObjType::CORRELATION);

  type[0] = AMObjType::CORRELATION;
  type[1] = AMObjType::ANY;
  installFNode("ComputeWhiteNoiseCorrelation" , STAT_ComputeWhiteNoiseCorrelation , 2 , type , AMObjType::VOID);

  type[0] = AMObjType::ANY;
  installFNode("ComputePartialAutoCorrelation" , STAT_ComputePartialAutoCorrelation , 1 , type , AMObjType::CORRELATION);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::ANY;
  installFNode("Segmentation" , STAT_Segmentation , 3 , type , AMObjType::SEQUENCES);

  type[0] = AMObjType::ANY;
  installFNode("ComputeSelfTransition" , STAT_ComputeSelfTransition , 1 , type , AMObjType::VOID);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("TransitionCount" , STAT_TransitionCount , 2 , type , AMObjType::VOID);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("WordCount" , STAT_WordCount , 2 , type , AMObjType::VOID);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  type[2] = AMObjType::INTEGER;
  installFNode("LumpabilityTest" , STAT_LumpabilityTest , 3 , type , AMObjType::VOID);

  type[0] = AMObjType::ANY;
  installFNode("Thresholding" , STAT_Thresholding , 1 , type , AMObjType::VARIABLE_ORDER_MARKOV);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::INTEGER;
  installFNode("ComputeAutoCorrelation" , STAT_ComputeAutoCorrelation , 2 , type , AMObjType::CORRELATION);

  type[0] = AMObjType::ANY;
  type[1] = AMObjType::ANY;
  installFNode("ComputeStateSequences" , STAT_ComputeStateSequences , 2 , type , AMObjType::VARIABLE_ORDER_MARKOV_DATA);

  type[0] = AMObjType::ANY;
  installFNode("BuildAuxiliaryVariable" , STAT_BuildAuxiliaryVariable , 1 , type , AMObjType::MARKOVIAN_SEQUENCES);
}
