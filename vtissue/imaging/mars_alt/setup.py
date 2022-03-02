# -*- coding: utf-8 -*-
__revision__ = "$Id: $"


import sys
import os

from setuptools import setup, find_packages

# Reads the metainfo file
from openalea.deploy.metainfo import read_metainfo
metadata = read_metainfo('metainfo.ini', verbose=True)
for key,value in metadata.iteritems():
    exec("%s = '%s'" % (key, value))


pkg_root_dir = 'src'
pkgs = [ pkg for pkg in find_packages(pkg_root_dir) if namespace not in pkg]
top_pkgs = [pkg for pkg in pkgs if  len(pkg.split('.')) < 2]
packages = [ namespace + "." + pkg for pkg in pkgs]
package_dir = dict( [('',pkg_root_dir)] + [(namespace + "." + pkg, pkg_root_dir + "/" + pkg) for pkg in top_pkgs] )

setup_requires = ['openalea.deploy']

#install_requires = ["pylsm", "vplants.vtissuedata"]
install_requires = []

# web sites where to find eggs
dependency_links = ['http://openalea.gforge.inria.fr/pi']


###############################################################
# The following code block creates a thread that waits for    #
# user input. The user is asked if he wants to download       #
# the +700mb archive of data. If no anwser is given before 20 #
# seconds, the download is skipped.                           #
###############################################################
#X def check_data_installed():
#X     from os.path import dirname, join, exists
#X     direc = dirname(__file__)
#X     return exists(join(direc, "share", "plantB-data"))
#X
#X
#X import threading
#X import time
#X secondsBeforeNoDownload = 20
#X downloadData = None
#X
#X
#X def ask_user_if_download():
#X     global downloadData
#X     try:
#X         answer = raw_input()
#X         if len(answer)==0:
#X             downloadData = False
#X         else:
#X             fl = answer[0].lower()
#X             if fl in ["y", "n"]:
#X                 downloadData = fl == "y" or False
#X         threading.current_thread()._Thread__stop()
#X     except EOFError, e:
#X         downloadData = False
#X         threading.current_thread()._Thread__stop()
#X
#X
#X if not check_data_installed():
#X
#X     print "Do you want to download shared data (+700Mb)? (yes/no). Will skip in " + \
#X           str(secondsBeforeNoDownload) + " seconds."
#X     thInput = threading.Thread(target=ask_user_if_download)
#X     while secondsBeforeNoDownload > 0 and downloadData is None:
#X         if secondsBeforeNoDownload%5 == 0:
#X             print str(secondsBeforeNoDownload)+ " before skipping. \nDownload? (yes/no) > "
#X         if not thInput.is_alive():
#X             thInput.start()
#X         secondsBeforeNoDownload -= 1
#X         time.sleep(1)
#X     thInput._Thread__stop()
#X
#X
#X
#X
#X #############################################################
#X # If the user wants to download, the following code block   #
#X # creates a thread that downloads the archive and keeps the #
#X # user more or less informed about what is happening.       #
#X #############################################################
#X
#X from urllib import urlretrieve
#X import tarfile
#X from openalea.core.path import path
#X progress = 0.0
#X def report_hook(nbBlocks, szBlock, szFile):
#X     global progress
#X     progress = (nbBlocks*szBlock)/float(szFile)*100
#X
#X def py_files(members):
#X     for tarinfo in members:
#X         f = path(tarinfo)
#X         if '.svn' in f:
#X             continue
#X         elif f.basename().startswith('.'):
#X             continue
#X         else:
#X             yield tarinfo
#X
#X
#X def get_data_and_install(url):
#X     global downloadFinished
#X     fn, h = urlretrieve(url, reporthook=report_hook)
#X     downloadFinished = True
#X     tar = tarfile.open(fn, 'r:gz')
#X     for tarinfo in tar:
#X         print tarinfo.name, "is", tarinfo.size, "bytes in size and is",
#X         if tarinfo.isreg():
#X             print "a regular file."
#X         elif tarinfo.isdir():
#X             print "a directory."
#X         else:
#X             print "something else."
#X
#X     tar.extractall(path="share/.", members=py_files(tar))
#X     tar.close()
#X
#X previousProg = None
#X if downloadData is True:
#X     url = "ftp://ftp-sop.inria.fr/virtualplants/MARS-ALT/data/plantB-data.tar.gz"
#X     downloadFinished = False
#X     thDl = threading.Thread(target=get_data_and_install, args=(url,))
#X     while downloadFinished is False:
#X         if not thDl.is_alive():
#X             thDl.start()
#X         if previousProg != progress:
#X             print "downloading...", progress, "%"
#X             previousProg = progress
#X         time.sleep(10)
#X     print "Done downloading and installing data"





#(to be kept only if you contruct C/C++ binaries)

# To compile src of MARS-ALT

#build_prefix = "build-cmake"


###########
#
#		compile QT interfaces
#
###########

#rc_file = "src/vtissue/icons/icons.qrc"
#out_file = "src/vtissue/icons_rc.py"
#os.system("pyrcc4 -o %s %s" % (out_file,rc_file) )


# setup function call
#
if __name__ == '__main__':
    setup(
        # Meta data (no edition needed if you correctly defined the variables above)
        name=name,
        version=version,
        description=description,
        long_description=long_description,
        author=authors,
        author_email=authors_email,
        url=url,
        license=license,
        keywords = '',
        # package installation
        packages= packages,
        package_dir= package_dir,
        # Namespace packages creation by deploy
        namespace_packages = [namespace],
        create_namespaces = True,
        # tell setup not  tocreate a zip file but install the egg as a directory (recomended to be set to False)
        zip_safe= False,
        # Dependencies
        setup_requires = setup_requires,
        install_requires = install_requires,
        dependency_links = dependency_links,


        #cmake_scripts=['../src/CMakeLists.txt'],

        # Tell deploy where to find libs, includes and bins generated by cmake.
        # Used for MARS-ALT
        #lib_dirs = {'lib' : build_prefix+'/lib' },
        #bin_dirs = { 'bin' : build_prefix+'/bin' },

        share_dirs = { 'share' : 'share' },


        # Declare scripts and wralea as entry_points (extensions) of your package
        entry_points = {
            'wralea': [ 'vplants.mars_alt = vplants.mars_alt_wralea',
                        # 'vplants.mars_alt.demo = vplants.mars_alt_demo_wralea',
                        # 'vplants.mars_alt.demo.visualization = vplants.mars_alt_visualization_wralea',
                        # 'vplants.mars_alt.demo.reconstruction = vplants.mars_alt_reconstruction_wralea',
                        # 'vplants.mars_alt.demo.segmentation = vplants.mars_alt_segmentation_wralea',
                        # 'vplants.mars_alt.demo.alt = vplants.mars_alt_alt_wralea',
                        # 'vplants.mars_alt.demo.analysis = vplants.mars_alt_analysis_wralea',
                        # 'vplants.mars_alt.demo.structural_analysis = vplants.mars_alt_structural_analysis_wralea',
                        # 'vplants.mars_alt.nodes = vplants.mars_alt_nodes_wralea',
                        # 'vplants.mars_alt.macro = vplants.mars_alt_macro_wralea'
                        ]
            },
        )

