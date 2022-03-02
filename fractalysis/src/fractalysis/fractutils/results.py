#! /usr/bin/env python
"""
:Authors:
  - Da SILVA David
:Organization: Virtual Plants
:Contact: david.da_silva:cirad.fr
:Version: 1.0
:Date: July 2005
"""

class ParamRes:
    """
    :Abstract: This module is dedicated to save the results obtained with one parameters set
    """
    def __init__(self, param, result):
        """
        Create a object containig the used parameters in one hand and the obtained results in the other.

        :Parameters:
          - `param`: Dictionnary containing all the used parameters formated as {*param name* : *param value*}
          - `result`: Dictionnary containing the results obtained with those parameters, formated as {*result name* : *result value*}

        :Types:
          - `param`: dictionnary
          - `result`: dictionnary
        """
        
        #self.plantename = plant
        self.param = param
        self.result = result

    def getParam(self, paramname):
        """
        :Parameters:
          - `paramname`: the dictionnary key of the wanted parameter

        :Types:
          - `paramname`: Any
        
        :Returns: the value of the given parameter name
        :Returntype: Any
        """
        if self.param.has_key(paramname):
            return self.param[paramname]
        else:
            raise "Param " + paramname + " does not exist."     

    def getResult(self, resultname):
        """
        :Parameters:
          - `resultname`: the dictionnary key of the wanted result

        :Types:
          - `resultname`: Any
        
        :Returns: the value of the given result name
        :Returntype: Any
        """
        
        if self.result.has_key(resultname):
            return self.result[resultname]
        else:
            raise "Result " + resultname + " does not exist."
        
    def testParamEq(self, param, value):
        """
        Test if the value of the given parameter is equal to the given value

        :Parameters:
          - `param`: the dictionnary key of the parameter to be tested
          - `value`: equality value to test

        :Types:
          - `param`: Any
          - `value`: Any

        :Returns: *True* if the parameter value is equal to the given value
        :Returntype: Boolean
        """
        if self.param.has_key(param):
            return self.param[param] == value
        else:
            raise "Parameter " + param + " does not exist."

    def testParamSup(self, param, value):
        """
        Test if the value of the given parameter is greater than the given value

        :Parameters:
          - `param`: the dictionnary key of the parameter to be tested
          - `value`: greater value to test

        :Types:
          - `param`: Any
          - `value`: Any

        :Returns: *True* if the parameter value is greater than the given value
        :Returntype: Boolean

        :note: If the tested parameter is the *shift*, each value [X,Y,Z] is tested and must be greater
        """
        if self.param.has_key(param):
            if param == 'shift':
                return self.param[param][0] >= value[0] and self.param[param][1] >= value[1] and self.param[param][2] >= value[2]
            else:
                return self.param[param] >= value
        else:
            raise "Parameter " + param + " does not exist."

    def testParamInf(self, param, value):
        """
        Test if the value of the given parameter is lesser than the given value

        :Parameters:
          - `param`: the dictionnary key of the parameter to be tested
          - `value`: equality value to test

        :Types:
          - `param`: Any
          - `value`: Any

        :Returns: *True* if the parameter value is equal to the given value
        :Returntype: Boolean
        
        :note: If the tested parameter is the *shift*, each value [X,Y,Z] is tested and must be greater
        """
        if self.param.has_key(param):
            if param == 'shift':
                return self.param[param][0] <= value[0] and self.param[param][1] <= value[1] and self.param[param][2] <= value[2]
            else:
                return self.param[param] <= value
        else:
            raise "Parameter " + param + " does not exist."


    def cout(self):
        """
        Print on the current display (screen) all the parameters and all the results of the instance.
        """
        print "Parameters : "
        for p in self.param.keys():
            print "%s : %s " %(p, self.param[p])

        print "Results : "
        for r in self.result.keys():
            print "%s : %s " %(r, self.result[r])
