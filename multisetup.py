"""Using of make_develop script"""
import os, sys


#a silly comment to trigger a compilation
try:
    from openalea.misc.multisetup import Multisetup
except ImportError:
    print 'Install OpenAlea.Misc first'
    try:
        sys.path.insert(0, os.path.join('..','openalea','misc', 'src', 'openalea', 'misc'))
        from multisetup import Multisetup
    except ImportError,e:
        print e


dirs = ['PlantGL',
        'tool',
        'stat_tool',
        'sequence_analysis',
        'amlobj',
        'mtg',
        'tree_matching',
        'aml',
        'tree_matching2',
        'fractalysis',
        'container',
        'newmtg',
        'WeberPenn',
        'lpy',
        #'tissue',
        'tree',
        'tree_statistic',
        #'pglviewer',
        #'mechanics',
        #'physics',
        #'svgdraw',
        'phyllotaxis_analysis',
        'aml2py',
        #'self_similarity',
]

def main():
    args = sys.argv[1:]
    if  len(args) == 1 and args[0] in ['-h', '--help']:
        Multisetup.help()
    else:
        mysetup = Multisetup(curdir='.', commands=args, packages=dirs)
        mysetup.run()


if __name__ == '__main__':
    main()

