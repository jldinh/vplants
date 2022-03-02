#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""


.. module:: tops

.. topic:: tops.py summary

    A module dedicated to Tops objects

    :Code: buggy
    :Documentation: to be completed
    :Author: Thomas Cokelaer <Thomas.Cokelaer@sophia.inria.fr>
    :Revision: $Id: tops.py 9885 2010-11-06 18:19:34Z cokelaer $
    :Usage: >>> from openalea.sequence_analysis import tops


"""
__version__ = "$Id: tops.py 9885 2010-11-06 18:19:34Z cokelaer $"
import os
import openalea.stat_tool.interface as interface
from openalea.sequence_analysis._sequence_analysis import _Tops
from openalea.sequence_analysis._sequence_analysis import _Sequences

from openalea.sequence_analysis.enums import index_parameter_type_map

#import _sequence_analysis
from openalea.stat_tool import error

__all__ = ['Tops',
           '_Tops',
           'RemoveApicalInternodes']


# Extend dynamically class
interface.extend_class( _Tops, interface.StatInterface)

# Add methods to _Vectors


def Tops(*args, **kargs):
    """Construction of a set of sequences from multidimensional arrays of
    integers, from data generated by a renewal process or from an ASCII file.

    The data structure of type array(array(array(int))) should be constituted
    at the most internal level of arrays of constant size. If the optional
    argument IndexParameter is set at "Position" or "Time", the data
    structure of type array(array(array(int))) is constituted at the most
    internal level of arrays of size 1+n (index parameter, n variables attached
    to the explicit index parameter). If the optional argument IndexParameter
    is set at "Position", only the index parameter of the last array of size
    1+n is considered and the first component of successive elementary arrays
    (representing the index parameter) should be increasing. If the optional
    argument IndexParameter is set at "Time", the first component of successive
    elementary arrays should be strictly increasing.

    :Parameters:

    * array1 (array(array(int))): input data for univariate sequences
    * arrayn (array(array(array(int)))): input data for multivariate sequences,
    * timev (renewal_data), file_name (string).

    :Optional Parameters:

    * Identifiers (array(int)): explicit identifiers of sequences. This optional
      argument can only be used if the first argument is of type
      array(array(int/array(int))).
    * IndexParameter (string): type of the explicit index parameter: "Position"
      or "Time" (the default: implicit discrete index parameter starting at 0).
      This optional argument can only be used if the first argument is of type
      array(array(int/array(int))).

    :Returns:

    If the construction succeeds, an object of type sequences or
    discrete_sequences is returned, otherwise no object is returned. The
    returned object is of type discrete_sequences if all the variables are
    of type STATE, if the possible values for each variable are consecutive
    from 0 and if the number of possible values for each variable is <= 15.

    :Examples:

    .. doctest::
        :options: +SKIP
        
        >>> Tops(array1, Identifiers=[1, 8, 12])
        >>> Tops(arrayn, Identifiers=[1, 8, 12], IndexParameter="Position")
        >>> Tops(timev)
        >>> Tops(file_name)

    .. seealso::


        :class:`~openalea.stat_tool.output.Save`,
        :func:`~openalea.sequence_analysis.data_transform.AddAbsorbingRun`,
        :func:`~openalea.stat_tool.cluster.Cluster`,
        :func:`~openalea.sequence_analysis.data_transform.Cumulate`,
        :func:`~openalea.sequence_analysis.data_transform.Difference`,
        :func:`~openalea.sequence_analysis.data_transform.IndexParameterExtract`,
        :func:`~openalea.sequence_analysis.data_transform.LengthSelect`,
        :func:`~openalea.stat_tool.data_transform.Merge`,
        :func:`~openalea.stat_tool.data_transform.MergeVariable`,
        :func:`~openalea.sequence_analysis.data_transform.MovingAverage`,
        :func:`~openalea.sequence_analysis.data_transform.RecurrenceTimeSequences`,
        :func:`~openalea.sequence_analysis.data_transform.RemoveRun`,
        :func:`~openalea.sequence_analysis.data_transform.Reverse`,
        :func:`~openalea.sequence_analysis.data_transform.SegmentationExtract`,
        :func:`~openalea.stat_tool.data_transform.SelectIndividual`,
        :func:`~openalea.stat_tool.data_transform.SelectVariable`,
        :func:`~openalea.stat_tool.data_transform.Shift`,
        :func:`~openalea.stat_tool.cluster.Transcode`,
        :func:`~openalea.stat_tool.data_transform.ValueSelect`,
        :func:`~openalea.sequence_analysis.data_transform.VariableScaling`.
        :func:`~openalea.stat_tool.data_transform.ExtractHistogram`,
        :func:`~openalea.sequence_analysis.data_transform.ExtractVectors`,
        :func:`~openalea.sequence_analysis.correlation.ComputeCorrelation`,
        :func:`~openalea.sequence_analysis.correlation.ComputePartialAutoCorrelation`,
        :func:`~openalea.sequence_analysis.data_transform.ComputeSelfTransition`,
        :func:`~openalea.sequence_analysis.compare.Compare`,
        :func:`~openalea.sequence_analysis.estimate.Estimate`,
        :func:`ComputeStateTops`,
        :func:`~openalea.sequence_analysis.simulate.Simulate`.
    """
    error.CheckArgumentsLength(args, 1, 1)

    index_parameter = error.ParseKargs(kargs, "IndexParameter",
                                            "IMPLICIT_TYPE",
                                            index_parameter_type_map)

    Identifiers = error.ParseKargs(kargs, "Identifiers", None)


    if isinstance(args[0], str):
        #todo: add True, False instead or as well as Current, Old
        #todo: !!! OldFormat set to True does not work in CPP code
        OldFormat = error.ParseKargs(kargs, "Format", "Old",
                                 {"Current":False, "Old":True})
        filename = args[0]
        if os.path.isfile(filename):
            return _Tops(filename, OldFormat)
        else:
            raise IOError("bad file name")
    elif isinstance(args[0], _Sequences):
        raise NotImplemented
        #return _Tops(args[0])
    elif isinstance(args[0], list):
        error.CheckType([Identifiers], [list])
        if kargs.get("IndexParameter"):
            if Identifiers:
                return _Tops(args[0], Identifiers, index_parameter)
            else:
                return _Tops(args[0], range(0, len(args[0])), index_parameter)
        else:
            raise ValueError("wrong arguments ?")
    else:
        raise TypeError("""Expected a valid filename or a list of
         lists (e.g., [[1,0],[0,1]])""")



def RemoveApicalInternodes(obj, internode):
    """RemoveApicalInternodes

    Removal of the apical internodes of the parent shoot of a 'top'.

    :Usage:

    .. doctest::
        :options: +SKIP
        
        >>> RemoveApicalInternodes(top, nb_internode)

    :Arguments:

    * top (tops),
    * nb_internode (int): number of removed internodes.

    :Returned Object:

    If nb_internode >  0 and if the removed internodes do not bear offspring
    shoots, an object of type tops is returned, otherwise no object is returned.

    .. seealso::

        :func:`~openalea.stat_tool.data_transform.SelectIndividual`,
        :func:`~openalea.stat_tool.data_transform.Merge`,
        :func:`~openalea.sequence_analysis.data_transform.Reverse`.
    """
    error.CheckType([obj, internode], [_Tops, int])
    return obj.shift(internode)


