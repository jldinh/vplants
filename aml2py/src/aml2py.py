#############################################################################
#
#       aml2py: Write a Python script from an AML script
#       Copyright (C) 2004 Christophe Pradal, CIRAD
#
#       This program is free software; you can redistribute it and/or
#       modify it under the terms of the GNU General Public
#       License as published by the Free Software Foundation; either
#       version 2 of the License, or (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS For A PARTICULAR PURPOSE. See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public
#       License along with this program; see the file COPYING. If not,
#       write to the Free Software Foundation, Inc., 59
#       Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#############################################################################


import os
import re

from optparse import OptionParser


class Aml2Py:
    """
    Convert an aml file to a python file
    """
    
    kwds= { ' \s*And\s* ':' and ', ' \s*Or\s* ':' or ', ' \s*Not\s* ':' not ',
            '->':'=', r'(?<=[^r])("[^"]*\\[^"]*")' : r'r\\1'}#, r'^' : r'**'}

    re_func= r'([a-zA-Z_][a-zA-Z_0-9]*)\s*\(\s*_([a-zA-Z_][a-zA-Z_0-9]*)\s*\)\s*=\s*(.+)'
    re_assign= r'([a-zA-Z_][a-zA-Z_0-9]*)\s*=\s*(.+)'
    re_If= r'If\s*(.+)\s*Then \s*(.+)\s* Else \s*(.+)'
    re_Foreach= r'Foreach \s*(.+)\s* In \s*(.+)\s*:\s*(.+)'
    re_Switch= r'Switch \s*(.+)\s* Default\s*:(.+)'

    indent=' ' * 4
    
    def __init__(self,file):
        """ Aml2Py(open) """
        
        self.enter= False
        self.nivel= 0 # indentation nivel
        self.filename= file
        self.py= ["# Convert %s to python with aml2py\n" % file,
                  "try: ",
                  self.indent+"from openalea.aml import * ",
                  "except: ",
                  self.indent+"from amlPy import * " ]

        self._debug= False
        self.aml= []
        self.ml= [] # current multiline
        self.mc= False # multicomment state
        
    def run(self):
        """ run() -> bool

        Open an aml file.
        Parse each lines
        Write the result in a python file.
        """

        self.read()
        self.parse()
        return self.write()

    def read(self):
        """ read() -> Open and read an aml file. """

        ok= os.path.exists(self.filename)
        if ok:
            l= self.filename.split('.')
            if l[-1] != 'aml': ok= False

        if not ok:
            raise "%s is not a good aml file..."%self.filename

        file= open(self.filename, 'r')
        text= file.read()
        self.aml= text.splitlines()
        file.close()

    def write(self):
        """ write() -> None

        Create a python file with the same name but with an extenion .py"""

        l= self.filename.split('.')
        name= '.'.join(l[:-1])
        pyfile= name+'.py'
        i= 0
        while os.path.exists(pyfile):
            i+= 1
            pyfile= name + str(i) + '.py'

        f= open(pyfile,'w')

        # Add a \n after each lines
        f.writelines([ c+'\n' for c in self.py ])

        f.close()
        return os.path.abspath(pyfile)
      
    def parse(self):
        """ parse() -> None

        Parse the aml file and convert each exp into a python exp.
        """

        for l in self.aml:
            l= l.strip()
            if not l:
                self.py.append(l)
                continue

            if self.ml:
                self.Multiline(l)
                continue
            
            if self.mc:
                self.Multi_comment(l)
                continue

            if self._debug:
                if l[0] != '#':
                    self.py.append('# '+l) # add the AML expression to the python file

            self.Exp(l)

        # end of file
        #self.py.append('raw_input("Type enter to quit: ")')

    def If(self, s):
        """ If(string) -> bool

        If pred Then exp1 Else exp2 -> if pred: exp1 else: exp2
        """

        m= re.match(self.re_If,s)
        if not m: return False
        
        g= m.groups()
        # if pred: exp1 else: exp2
        pred, exp1, exp2= g[0], g[1], g[2]

        # check pred : if p then e1 else if p2 then e2 else e3
        i= pred.find('If')
        if i > -1:
            # todo
            
            re_If2= r'If\s*(.+?)\s*Then \s*(.+)'
            m= re.match(re_If2,s)
            if not m: return False
            g= m.groups()
            pred, suite= g[0], g[1]

            re_1= r'If\s*(.+?)\s*Then \s*(.+)\s* Else \s*(.+)\s* Else \s*(.+)\s*'
            re_2= r'\s*(.+)\s* Else If\s*(.+?)\s*Then \s*(.+)\s* Else \s*(.+)\s*'

            m= re.match(re_1,suite)
            g1= g2= []
            if m:
                g1= m.groups()
                exp1= 'If '+g1[0]+ ' Then '+g1[1]+ ' Else '+g1[2]
                exp2= g1[3]
            else:
                m= re.match(re_2,suite)
                if not m: return False
                g2= m.groups()
                exp2= 'If '+g2[1]+ ' Then '+g2[2]+ ' Else '+g2[3]
                exp1= g2[0]
            
        # write 'if pred:' with indentation
        ind= self.indent * self.nivel
        self.py.append( ind + 'if %s:' % pred )

        self.nivel+=1
        s1= self.Exp(exp1)

        self.py.append( ind + 'else:' )

        s2= self.Exp(exp2)

        self.nivel-= 1

        return s1 and s2


    def Foreach( self,s):
        """ Foreach(string) -> string

        Foreach x In set: exp -> [exp for x in set] 
        """

        m= re.match(self.re_Foreach,s)
        if not m: return False
        
        g= m.groups()
        # [exp for x in set] 
        x, set, exp= g[0], g[1], g[2]

        ind= self.indent * self.nivel
        str= '[ %s for %s in %s ]' % (exp,x,set)

        if self.enter:
            str= 'return ' + str

        str= ind + str
        
        self.py.append( ind + str )

        return True

    def Switch( self,s):
        """ Switch(string) -> bool

        Switch v Case v1 : e1 Case v2 : e2 Case ... Default ek
        """

        m= re.match(self.re_Switch,s)
        if not m: return False

        g= m.groups()
        # Complex ooups
        exp_cases, default = g[0], g[1]

        l= re.split(r'\s*Case\s*',exp_cases)
        exp= l[0]
        cases= l[1:]

        ind= self.indent * self.nivel
        var= 'switch_x= %s' % exp
        self.py.append( ind + var )

        begin= True
        for str in cases:
            l= re.split(r'\s*:\s*',str)
            if begin:
                si= 'if switch_x == %s:' % l[0]
            else:
                si= 'elif switch_x == %s:' % l[0]

            self.py.append( ind + si )

            si= ind+self.indent
            if self.enter: si+= 'return '
            self.py.append( si + l[1] )

        self.py.append( ind + 'else:' )
        si= ind+self.indent
        if self.enter: si+= 'return '
        self.py.append( si + default )

        return True
        
    def Comment(self,s):
        """ Convert an aml comment to python """

        if s[0] == '#':
            self.py.append( s )
            return True

        return False


    def Multi_comment(self,s):
        """ Convert a multi-line comment to python """
        
        if self.mc:
            self.py.append('# '+s)
            if s.find('#)') > -1:
                self.mc= False
        elif s.find('(#') > -1:
            self.mc= True
            self.py.append('# '+s)
        else:
            return False
        return True

    def Multiline(self,s):
        """ Convert a multi-line exp to a single string """

        if s[-1] == '\\': # AML multiline instruction
            self.ml.append( s[:-1].strip()+' ' )
            return True
        elif self.ml:
            s= ''.join(self.ml) +  s
            self.ml= []
            return self.Exp(s)
        else:
            return False
              

    def Function(self,s):
        """ Convert an amlfunction to Python """

        m= re.match(self.re_func,s)

        if m != None:
            groups= m.groups()
            f= 'def %s( _%s ):'%(groups[0],groups[1])
            self.py.append(f)
            self.nivel+= 1
            self.enter= True
            exp= groups[2]
            ok= self.Exp(exp)
            self.nivel-= 1
            self.enter= False
            self.py.append("")
            return ok
            
        return False

    def Assign(self,s):
        """ Convert an aml assignement to python """
        
        m= re.match(self.re_assign,s)

        if m != None:
            groups= m.groups()
            exp= groups[1]
            ok= self.Exp(exp)
            if ok:
                f= '%s= %s'%(groups[0],self.py[-1])
                self.py[-1]= f
            return ok
        return False

    def Substitute(self,s):
        """ Substitute all aml keywords to python.
        Return the string
        """

        for k in self.kwds:
            l= re.subn(r'%s'%k,r'%s'%self.kwds[k],s)
            if l[1]>0:
                s= l[0]

        l= re.subn(r'@([0-9]+)',r'[\1-1]',s)
        if l[1]>0:
            s= l[0]

        return s

    def Other(self,s):

        ind= self.indent * self.nivel
        if self.enter:
            s= 'return '+ s
        self.py.append(ind+s)
        
        
    def Exp(self,s):
        """ Convert an aml expression to python """

        if self.Multiline(s):
            return True
        if self.Multi_comment(s):
            return True
        if self.Comment(s):
            return True

        s= self.Substitute(s)
        
        if self.Function(s):
            return True
        if self.Assign(s):
            return True
        if self.If(s):
            return True
        if self.Switch(s):
            return True
        if self.Foreach(s):
            return True

        self.Other(s)

        return True



def aml2py(amlfile):
    """ aml2py(amlfile) -> Convert aml script to python script.

    amlfile: an input aml script
    pythonfile: the output python script
    """

    engine= Aml2Py(amlfile)
    pyfile = engine.run()
    return pyfile

def main():
    """ Main function to get user arguments. """

    usage = """
    %prog convert an aml script into a python script.

    %prog aml_file

    example: %prog tree.aml
    """

    parser = OptionParser(usage=usage)
    try:
        (opts, args)= parser.parse_args()
    except Exception,e:
        parser.print_usage()
        print "Error while parsing :", e
        raise e

    if (len(args) < 1 ):
        print "Provide an input aml file"
        parser.print_usage()
        return

    amlfile = args[0]

    pyfile = aml2py(amlfile)

    print '%s have been generated.'%pyfile


if __name__=="__main__":
    file= raw_input('Enter the AML filename: ')
    aml2py(file)
    raw_input('Fine: Type enter  ')
    

