from meshnode import *

def split_txt_rules(txt):
    def valid_buffer(buf):
        for i in buf:
            if i != '\n': return True
        return False
    rules = []
    buffer = ''
    for l in txt.split('\n'):
      if len(l) > 0:
        if l[0] == '\t' or l[0] == ' ':
            buffer += l + '\n'
        else:
            if valid_buffer(buffer):
                rules.append(buffer)
            if 'group' in l:
                rules.append(l+'\n')
                buffer = ''
            else:
                buffer = l +'\n'
    if valid_buffer(buffer):
        rules.append(buffer)
    return rules

class RuleKernel:
    def __init__(self,viewer,fname = None):
        self.rules  = [{ }]
        self.namespace = {"viewer":viewer,'SetGroup':self.set_group }
        if fname:
            txt = file(fname,'r').read()
            self.set(txt)
        self.tissuedb = None
        self.current_step = 0
        self.current_group = 0
        self.nbiterations  = None
    def set_group(self,group):
        print 'group:',group
        self.current_group = group
    def set(self,txt):
        header, rules = txt.split('rules:')
        exec(header,self.namespace,self.namespace)
        rules = split_txt_rules(rules)
        group = 0
        for i,r in enumerate(rules):
          header, code = r.split('\n',1)
          if 'group' in header:
              group = int(header.split()[1][:-1])
              if len(self.rules) <= group:
                for i in xrange(len(self.rules),group+1):
                    self.rules.append({})
          else:            
            pattern, signature = header.split('(',1)
            funcname = 'rule'+str(i)
            tcode = 'def '+funcname+'('+signature+'\n'+code
            exec(tcode,self.namespace,self.namespace)
            pattern = pattern.strip()
            self.add_rule(pattern,self.namespace[funcname],group)
    def add_rule(self, pattern, func,group = 0):
        self.rules[group][pattern] = func
    def init(self):
        self.set_group = 0
        self.tissuedb = self.namespace['init']()
        self.tissuedb.prop_to_update = {}
        self.nbiterations = self.namespace.get('nbiterations',None)
        self.current_step = 0
    def process(self, tissuedb):
        futuretissue = deepcopy(tissuedb)
        rules = self.rules[self.current_group]
        for n in get_buffered_nodes(tissuedb,futuretissue):
            try:
                label = n.label
                if rules.has_key(label):
                    rules[label](n)
            except AttributeError:
                pass
        return futuretissue
    # def process(self, tissuedb):
        # for n in get_cell_nodes(tissuedb):
            # if self.rules.has_key(n.label):
                # self.rules[n.label](n)
        # return tissuedb
    def step(self):
        if self.nbiterations is None or self.current_step < self.nbiterations:
            self.tissuedb = self.process(self.tissuedb)
            if 'EndEach' in self.namespace:
                self.namespace['EndEach'](self.current_step,self.tissuedb)
            self.current_step += 1
            if not self.nbiterations is None and self.current_step == self.nbiterations:
                if 'End' in self.namespace:
                   self.namespace['End'](self.tissuedb)
        else:
            self.init()
    def run(self):
        if self.current_step >= self.nbiterations:
            self.init()
        while self.current_step < self.nbiterations:
            self.step()


        