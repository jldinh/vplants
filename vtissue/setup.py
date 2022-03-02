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


dirs = ['asclepios',
        'mars_alt',
        'tissue_analysis',
        ]

def main():
    args = sys.argv[1:]
    if  len(args) == 1 and args[0] in ['-h', '--help']:
        Multisetup.help()
    else:
        mysetup = Multisetup(curdir='./imaging/', commands=args, packages=dirs)
        mysetup.run()


if __name__ == '__main__':
    main()


