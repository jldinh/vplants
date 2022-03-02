import openalea.lpy as lpy
import vafile_import as vafile


    
def empty_line(line):
    if len(line) == 0 : return True
    for c in line :
        if c not in ' \t': return False
    return True

def empty_end_line(txt,index):
    nbchar = len(txt)
    if nbchar >= index : return True
    for i in xrange(index,nbchar) :
        c = txt[i]
        if c in '\n': return True
        if c not in ' \t': return False
    return True

def find_code_limit(txt,index):
    nbchar = len(txt)
    begcode = index
    i = index
    nbparenthesis = 0
    while i < nbchar:
        if txt[i] == '{' : 
            nbparenthesis += 1
            if nbparenthesis == 1 : 
                begcode = i
        if txt[i] == '}' : 
            nbparenthesis -= 1
            if nbparenthesis <= 0 : break
        i += 1
    return begcode, i
    
def add_sharp_to_line(txt):
    result = '# '
    txt = txt[2:]
    result += '\n#'.join(txt.splitlines())
    return result
    
def translate_comments(txt):
    nxtcomment = -2
    nextendcomment = 0
    result = ''
    while nxtcomment != -1:
        nxtcomment = txt.find("/*",nextendcomment)
        if nxtcomment != -1:
            result += txt[nextendcomment:nxtcomment]
            nextendcomment = txt.find("*/",nxtcomment+2)
            nextendcomment += 2
            endline = txt.find("\n",nextendcomment)
            if empty_line(txt[nextendcomment:endline]):
                result += add_sharp_to_line(txt[nxtcomment:nextendcomment-2]) + txt[nextendcomment:endline]
                nextendcomment = endline
            else:
                # get the code of the end of the line before the comment
                result +=  txt[nextendcomment:endline] + add_sharp_to_line(txt[nxtcomment:nextendcomment -2])
                nextendcomment = endline
    result += txt[nextendcomment if nextendcomment >= 0 else 0:]
    return result
            

def convert_symbols(txt):
    result = txt.replace('&&',' and ')
    result = result.replace('||',' or ')
    result = result.replace('printf','print')
    return result

def convert_lstring(txt):
    return txt.replace('#','_')

    
def check_assignement(code):
    if len(code) >= 2 and code[:2] == 'if': return []
    if len(code) >= 5 and code[:5] == 'while': return []
    try :
        var, value = code.split('=')
    except:
        return []
    if value[0] == '=': return []
    if var[-1] in '!<>': return []
    var = var.strip()
    if var[0].isalpha() or var[0] == '_' and var.isalnum():
        return [var]
    else:
        return []
    
def translate_c_code(txt,indentation = 1):
    vars = []
    indent = '\t'*indentation
    txt = txt.strip()
    assert txt[0] == '{' and txt[-1] == '}'
    txt = txt[1:-1]
    commands = txt.split(';')
    commands = [ c.strip() for c in commands]
    commands = [ c for c in commands if len(c) > 0]    
    result = ''
    for command in commands:
        if '{' in command or '}' in command:
            if '}' in command:
                comparts = command.split('}')
                command = comparts[-1]
                comparts = comparts[:-1]
                for part in comparts:
                    part = part.strip()
                    if len(part) > 0:
                        result += indent + part +'\n'
                        vars += check_assignement(part)
                    indent = indent[:-1]
            if '{' in command:
                comparts = command.split('{')
                command = comparts[-1]
                comparts = comparts[:-1]
                for part in comparts:
                    result+= indent
                    if 'do' in part:
                        result += 'while True'
                        import warnings
                        warnings.warn('do command not supported for translation in line %s.' % lineno)
                    else:
                        part = part.strip()
                        result += part
                        vars += check_assignement(part)
                    result+= ':\n'
                    indent += '\t'
                command = command.strip()
                result+= indent + command +'\n'
                vars += check_assignement(command)
        else:
            vars += check_assignement(command)
            result += indent + command +'\n'
    return result, vars

def get_local_var(predecessor):
    c = lpy.LsysContext()
    c.options.setSelection('Optimization',0)
    c.makeCurrent()
    r = lpy.LsysRule()
    r.set(predecessor+' --> ')
    localvars = r.parameterNames()
    c.done()
    return localvars
    
def process_rule(predecessor,conditions,precondition,defs,withlineno = True):
    header = convert_lstring(predecessor) + ':\n'
    result = ''
    gvar = []
    if precondition:
        tcode, glvar = translate_c_code(precondition)
        result += tcode
        gvar += glvar
    indent = '\t'
    if conditions:
        result += indent + 'if '+conditions + ':\n'
        indent += '\t'
    if len(defs) == 1:
        postcondition, successor, prob, lineno = defs[0] 
        if prob:
            import warnings
            warnings.warn('Cannot take into account prob "%s" in line %s.' % (prob, lineno))
        if postcondition:
            tcode, glvar = translate_c_code(postcondition,len(indent))
            result += tcode
            gvar += glvar
        if withlineno:
            result += indent+'# see line '+str(lineno)+'\n'
        result += indent+'produce '+convert_lstring(successor)+'\n'
    else:
        nbrules = len(defs)
        assert len([pb for p,s,pb,l in defs if not pb is None]) ==  nbrules and "multiple successor with no probabilities"
        import warnings
        warnings.warn('Cannot only take into account probs of rules with same predecessor and condition.')
        if nbrules == 2 and defs[1][2] == '1-'+defs[0][2] : # Complementary rules
            result += indent+'from random import uniform\n'
            postcondition, successor, prob, lineno = defs[0]
            result += indent+'if uniform(0,1) < '+defs[1][2]+': '
            if withlineno:
                result += '# see line '+str(lineno)
            result += '\n'
            indent += '\t'
            if postcondition:
                result += translate_c_code(postcondition,len(indent))
            result += indent+'produce '+successor+'\n'
            result +=  indent[:-1]+'else: # see line '+str(lineno) + '\n'
            postcondition, successor, prob, lineno = defs[1]
            if postcondition:
                result += translate_c_code(postcondition,len(indent))
            result += indent+'produce '+convert_lstring(successor)+'\n'
            indent = indent[:-1]
            
        
        else:
            result += indent+'from openalea.lpy.cpfg_compat import select_successor_from_prob\n'
            result += indent+'successor = select_successor_from_prob(['+','.join([pb for p,s,pb,l in defs])+'])\n'
            for i in xrange(len(defs)) :
                postcondition, successor, prob, lineno = defs[i]             
                result += indent
                if i == 0: result +=  'if successor == '+str(i)+' : # see line '+str(lineno)+'\n'
                elif i != nbrules-1: result +=  'elif successor == '+str(i)+' : # see line '+str(lineno)+'\n'
                else: result +=  'else: # see line '+str(lineno)+'\n'
                indent += '\t'
                if postcondition:
                    result += translate_c_code(postcondition,len(indent))
                result += indent+'produce '+convert_lstring(successor)+'\n'
                indent = indent[:-1]
    gvdec = ''
    if len(gvar) > 0:
        localvars = get_local_var(predecessor)
        gvar = set(gvar).difference(localvars)
        if len(gvar) > 0:
            gvdec = '\tglobal '+','.join(gvar)+'\n'
    result = header + gvdec + result
    return result, gvar

class CurrentRule:
    def __init__(self):
        self.reset()
    def reset(self):
        self.predecessor = None
        self.precondition = None
        self.conditions = None
        self.defs = []
    def set(self,predecessor,precondition,conditions):
        self.predecessor = predecessor
        self.precondition = precondition
        self.conditions = conditions
    def append_succ(self,defs):
        self.defs.append(defs)
    def process(self):
        if self.empty(): return '', []
        result, gvar = process_rule(self.predecessor,self.conditions,self.precondition,self.defs)
        self.reset()
        return result, gvar
    def __eq__(self,values):
        predecessor, precondition, conditions = values
        return self.predecessor == predecessor and self.precondition == precondition and self.conditions == conditions
    def empty(self):
        return self.predecessor is None

    
def translate_l_code(txt, vlpyinitconfig = None):
    txt = convert_symbols(txt)
    txt = translate_comments(txt)
    allgvar = set()
    result = 'from openalea.lpy.cpfg_compat.func_compat import *\n'
    current_rule = CurrentRule()
    proddec = False
    proddecposition = None
    def process_current_rule(result, allgvar):
        lcode, lgvar = current_rule.process()
        if len(lgvar) > 0:
            allgvar = allgvar.union(set(lgvar))
        result += lcode
        return result, allgvar
    
    lines = txt.splitlines()
    lineno = 0
    while len(lines) > 0:
        lineno += 1
        line  = lines.pop(0)
        if empty_line(line) : 
            result += line +'\n'
            continue
        lineseg = line.split(' ',1)
        if len(lineseg) > 1:        
            fword, restofline = lineseg
        else:
            fword, restofline = line, ''
        if len(fword) > 0 and fword[0].isalpha() : 
            fword = fword[0].upper() + fword[1:]
        if fword == '#define': # define
            if line[-2:] == '\\\\':
                while len(lines) > 0 and restofline[-2:] == '\\\\':
                    nline = lines.pop(0)
                    lineno += 1
                    restofline = restofline[:-2] + nline[:-2].strip()
                
            headdef, restofdef = restofline.split(' ',1)
            if '(' in headdef:
                result += 'def ' + headdef + ' : return ' + restofdef + '\n'
            else:
                result += headdef + ' = ' + restofdef + '\n'
        elif fword == 'Lsystem:' : 
            result += '# ' + line + '\n'
        elif fword == 'Axiom:' : 
            result += 'Axiom: '
            if vlpyinitconfig:
                result += vafile.translate_view_init(vlpyinitconfig)
            result += convert_lstring(restofline) + '\n'
        elif fword == 'Seed:'  : 
            result += 'from random import seed\nseed(' + restofline + ')\n'
        elif fword == 'Derivation': 
            result, allgvar = process_current_rule(result, allgvar)
            result += line + '\n'
        elif fword == 'Ignore:': 
            result, allgvar = process_current_rule(result, allgvar)
            result += line + '\n'
        elif fword == 'Consider:': 
            result, allgvar = process_current_rule(result, allgvar)
            result += line + '\n'
        elif fword == 'Endlsystem': 
            result, allgvar = process_current_rule(result, allgvar)
            result += line + '\n'
        elif fword == 'Homomorphism': 
            result, allgvar = process_current_rule(result, allgvar)
            result += 'interpretation:\n'
        elif fword == 'Decomposition': 
            result, allgvar = process_current_rule(result, allgvar)
            result += 'decomposition:\n'
        elif fword == 'Maximum':  #suppose to be maximum depth
            result, allgvar = process_current_rule(result, allgvar)
            result += line + '\n'
        elif fword == 'Start:' or fword == 'StartEach:' or fword == 'End:' or fword == 'EndEach:': 
            be, ce = find_code_limit(restofline,0)
            code = restofline[be:ce+1]
            tcode, gvar = translate_c_code(code,1)
            if len(gvar) > 0:
                gvar = set(gvar)
                allgvar = allgvar.union(set(gvar))
            result += 'def '+ fword[:-1] +'():\n'
            if len(gvar) > 0:
                result += '\tglobal '+','.join(gvar)+'\n'
            result += tcode
        else:
            if line.strip()[0] == '#': # comment
                result += line + '\n'
            else: # rules are processed here
                if proddec == False:
                    proddecposition = len(result)
                    result += 'production:\n\n'
                    proddec = True
                # if next line is the following of the current rule
                while len(lines) > 0 and len(lines[0]) > 0 and lines[0][0] == '\t':
                    nline = lines.pop(0)
                    lineno += 1
                    line += nline.strip()
                try:
                    predecessor, successor = line.split('-->')
                except Exception, e:
                    print line
                    raise e
                if not ':' in predecessor and not ':' in successor: # simplest rules
                    result += convert_lstring(predecessor) + '-->' + convert_lstring(successor) + '\n'
                else:
                    prob = None
                    if ':' in successor :
                        successor, prob = successor.split(':')
                    if ':' in predecessor:
                        predecessor, conditions = predecessor.split(':')
                        predecessor = predecessor.strip()
                        conditions = conditions.strip()
                        precond = None
                        if conditions[0] == '{': # a pred condition computation exists
                            bprec, eprec = find_code_limit(conditions,0)
                            precond = conditions[bprec:eprec+1]
                            conditions = conditions[eprec+1:]
                        postcond = None
                        if conditions[-1] == '}': # a post condition computation exists
                            bpostc = conditions.index('{')
                            postcond = conditions[bpostc:]
                            conditions = conditions[:bpostc].strip()
                        if len(conditions) == 0 and postcond is None and not precond is None:
                            postcond, precond = precond, postcond
                    if current_rule.empty():
                        current_rule.set(predecessor, precond, conditions)
                        current_rule.append_succ([postcond, successor, prob,lineno])
                    elif current_rule == (predecessor, precond, conditions):
                        current_rule.append_succ([postcond, successor, prob,lineno]) # Concatenate
                    else:
                        result, allgvar = process_current_rule(result, allgvar)
                        current_rule.set(predecessor, precond, conditions)
                        current_rule.append_succ([postcond, successor, prob,lineno])
    if len(allgvar) > 0:
        gvardec =  '# declaration of global variables used in the model\n'
        gvardec += ','.join(allgvar) + ' = ' + ','.join([str(None) for i in xrange(len(allgvar))])+'\n\n'
        result = result[:proddecposition]+gvardec+result[proddecposition:]
        
    return result

import openalea.lpy.simu_environ as se
import openalea.lpy.cpfg_compat.data_import as di

def translate_obj(fname):
    import os
    from os.path import join, splitext, basename
    from openalea.lpy.gui.objectmanagers import get_managers
    if os.path.isdir(fname):
        project = fname
        files = os.listdir(project)
        infos = {}
        for f in files:
            ext = splitext(f)[1]
            infos[ext] = infos.get(ext,[])+[f]
        lfile = infos.get('.l')[0] # lsystem file
        afile = infos.get('.a') # animation file
        vfiles = infos.get('.v') # visualisation file
        sfiles = infos.get('.s') # surface file
        fsetfiles = infos.get('.fset') # functions file
        funcfiles = infos.get('.func') # functions file
        csetfiles = infos.get('.cset') # contours file
        mapfiles = infos.get('.map') # color file
        matfiles = infos.get('.mat') # material file
        descfile = 'description.txt' # description file
        if not descfile in files:  descfile = None
        
        if not lfile : return

        # read visual objects
        managers = get_managers()
        panels  = []
        
        # read surface file
        groupofpatches = {}
        if sfiles:
            for sfile in sfiles:
                sworkspace = splitext(basename(sfile))[0]
                surfaces = []
                for manager in managers.itervalues():
                    fname = join(project,sfile)
                    if manager.canImportData(fname):
                        try:
                            objects = manager.importData(fname)
                            surfaces += [(manager,i) for i in objects]
                            groupofpatches[sworkspace] = [i.name for i in objects]
                        except Exception, e:
                            import sys, traceback
                            exc_info = sys.exc_info()
                            traceback.print_exception(*exc_info)
                            print 'Cannot import file '+repr(sfile)
                        
                        break
                panels  += [({'name':sworkspace},surfaces)]
         
        # read func file
        if funcfiles:
            functions = []
            for funcfile in funcfiles:
                for manager in managers.itervalues():
                    fname = join(project,funcfile)
                    if manager.canImportData(fname):
                        try:
                            objects = manager.importData(fname)
                            functions += [(manager,i) for i in objects]
                        except Exception, e:
                            import sys, traceback
                            exc_info = sys.exc_info()
                            traceback.print_exception(*exc_info)
                            print 'Cannot import file '+repr(funcfile)
                        
                        break
            panels  += [({'name':'functions'},functions)]

        # read fset and cset file
        if fsetfiles or csetfiles:
            if fsetfiles is None: fsetfiles = []
            if csetfiles is None: csetfiles = []
            for fsetfile in fsetfiles+csetfiles:
                for manager in managers.itervalues():
                    fname = join(project,fsetfile)
                    if manager.canImportData(fname):
                        try:
                            objects = manager.importData(fname)
                            managedobjects = [(manager,i) for i in objects]
                            panels  += [({'name':basename(splitext(fn)[0])}, managedobjects)]
                        except Exception, e:
                            import sys, traceback
                            exc_info = sys.exc_info()
                            traceback.print_exception(*exc_info)
                            print 'Cannot import file '+repr(fsetfile)
                        
                        break
        
        # view file
        if vfiles:
            lpyvcode = '\n## View file settings ##\n'
            for vfile in vfiles:
                lpytvcode, vlpyinitconfig = vafile.translate_view_file(join(project,vfile),groupofpatches)
                lpyvcode += lpytvcode
        
        
        # read material
        l = lpy.LsysContext()
        materials = []
        if mapfiles: 
            for mapfile in mapfiles:
                materials += di.import_colormap(join(project,mapfile))
        if matfiles:  
            for matfile in matfiles:
                materials += di.import_materialmap(join(project,matfile))
        for i,mat in enumerate(materials):
            l.turtle.setMaterial(i,mat)
        nbMaterials = l.turtle.getColorListSize()
        if nbMaterials > len(materials):
            for i in xrange(nbMaterials-1,len(materials)-1,-1):
                l.turtle.removeColor(i)
        
        # read desciption
        if descfile:
            description = {'__description__' : open(join(project,descfile)).read() }
        else : description = None
        
        # translate lsystem code
        lpycode = translate_l_code(file(join(project,lfile)).read(),vlpyinitconfig)
        
        # add view file
        if vfiles:
            if lpycode.index('endlsystem') == -1:
                lpycode += '\nebdlsystem\n\n'
            lpycode += lpyvcode
        
        # translate environ
        init_txt = se.getInitialisationCode(l,credits = description, visualparameters=panels)
        return lpycode + init_txt
    else:
        return translate_l_code(file(fname).read())

def help():
    return 'Usage: cpfg2lpy project[.l] [output.lpy]\nHelp: This utility try to translate cpfg code and parameter in lpy. A simple cpfg lsystem file can be passed or an entire directory project.'
    
def main():
    import sys
    if len(sys.argv) < 2:
        print help()
        return
    lpycode = translate_obj(sys.argv[1])
    if len(sys.argv) == 3:
        output = file(sys.argv[2],'w')
        output.write(lpycode)
        output.close()
    else:
        print lpycode
    

if __name__ == '__main__':
    main()