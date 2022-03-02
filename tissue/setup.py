"""This file (called setup.py) is a multisetup file (not setuptools)"""
import os, sys

try:
    from openalea.misc.multisetup import Multisetup
except ImportError:
    print 'Install OpenAlea.Misc first'
    try:
        sys.path.insert(0, os.path.join('..','openalea','misc', 'src', 'openalea', 'misc'))
        from multisetup import Multisetup
    except ImportError,e:
        print e


dirs = ['celltissue',
        'genepattern',
        'growth',
        'tissueedit',
        'tissueshape',
        'tissueview',
        'vmanalysis',
        'tissue_meta',
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

