================
Troubleshootings 
================

This is an up-to-date of known issue with MARS-ALT. If a unknown bugs in MARS-ALT is not found, please send `email <openalea-users@lists.gforge.inria.fr>`_ .

**Installation Issues**


**Installing on Mac OS X 10.6 "Snow Leopard"**

If you see the following error message when you build MIPS on Mac OS X::

    [  8%] Building CXX object StdPkgs/GuiPkg/Modules/CMakeFiles/tclModules.dir/Modules.o
    In file included from /Users/admin/Work/mips/mips_src/StdPkgs/GuiPkg/Modules/Modules.C:18:
    /Users/admin/Work/mips/mips_src/StdPkgs/GuiPkg/modules/togl.h:57:23: error: GL/gl.h: No such file or directory

Change the **OPENGL build options** in the CMake process. For that, type in your build shell: ::

    make edit_cache

When ccmake is running, press 't' to display all build options, and modify  **OPENGL build options** : ::

    OPENGL_INCLUDE_DIR		/usr/X11R6/include
    OPENGL_gl_LIBRARY		/usr/X11R6/lib/libGL.dylib
    OPENGL_glu_LIBRARY		/usr/X11R6/lib/libGLU.dylib

Configure [c], Generate [g] and re-build: ::

    make


**Installing on the Nef cluster**

If you have the following error message when you build on the Nef Cluster: ::

    Linking C shared library ../../../lib/libmipsZ.so
    /usr/bin/ld: CMakeFiles/mipsZ.dir/adler32.o: relocation R_X86_64_32 against `a local symbol' can not be used when making a shared object; recompile with -fPIC
    CMakeFiles/mipsZ.dir/adler32.o: could not read symbols: Bad value
    collect2: ld returned 1 exit status
    make[2]: *** [lib/libmipsZ.so] Error 1
    make[1]: *** [AuxPkgs/StdLibsPkg/Zlib/CMakeFiles/mipsZ.dir/all] Error 2
    make: *** [all] Error 2

Change the **CMAKE FLAGS build options** in the CMake process. For that, type in your build shell: ::

    make edit_cache

When ccmake is running, press 't' to display all build options, and modify  **CMAKE FLAGS build options** : ::

    CMAKE_CXX_FLAGS     -fPIC
    CMAKE_C_FLAGS       -fPIC

Configure [c], Generate [g] and re-build: ::

    make


**MARS-ALT Issues** 

**Running lsm2inr.py**

If you see the following error when you run : ::
    
    Traceback (most recent call last):
    File "lsm2inr.py", line 39, in <module>
      from openalea.vmanalysis import inrimage
    ImportError: No module named vmanalysis

Install `OpenAlea <http://openalea.gforge.inria.fr/dokuwiki/doku.php>`_ 

If you see the following error when you run : ::

    Traceback (most recent call last):
    File "lsm2inr.py", line 42, in <module>
      from pylsm import lsmreader
    ImportError: No module named pylsm

Install `PyLSM <http://www.freesbi.ch/en/pylsm>`_ 

**Running on Mac OS X 10.6 "Snow Leopard"**

If you see the following error when you run zviewer on Mac OS X: ::

    Segmentation fault 

Install Tcl-Tk 8.5 from the `sources <http://www.tcl.tk/software/tcltk/download.html>`_.

Download and Uncompress the sources.

Compiling Tcl 8.5 on Mac OS X has two steps: configure and make. ::

    cd tcl8.5.0/unix  # unix and not macosx
    ./configure --prefix=/Users/*your_username*/local/ --enable-framework --enable-threads
    make
    make test
    make install

Compiling Tk 8.5 on Mac OS X has the same steps than Tcl: configure and make. ::

    cd tk8.5.0/unix  # unix and not macosx
    ./configure --enable-threads --prefix=/Users/*your_username*/local/ --with-tcl=/Library/Frameworks/Tcl.framework/ --enable-framework --with-x
    make
    make test
    make install


Then change the **TCL-TK build options** in the CMake process. For that, type in your build shell: ::

    cd mips_build
    make edit_cache

When ccmake is running, press 't' to display all build options, and modify  **TCL-TK build options** : ::

    TCL_INCLUDE_PATH        /Library/Frameworks/Tcl.framework/Headers
    TCL_LIBRARY             /Library/Frameworks/Tcl.framework                                                                       
    TCL_TCLSH               /Users/username/local/bin/tclsh8.5                                                                    
    TK_INCLUDE_PATH         /Library/Frameworks/Tk.framework/Headers
    TK_LIBRARY              /Library/Frameworks/tk.framework


Configure [c], Generate [g] and re-build: ::

    make


**Running on Linux**

**cannot restore segment prot after reloc: Permission denied**

If you see the following error when you try to use MARS-ALT : ::

    cannot restore segment prot after reloc: Permission denied

This is likely due the the SE Linux setting being set to "enforcing".

**To Temporarily disable enforcement on a running system** ::

    /usr/sbin/setenforce 0

**To permanently disable enforcement during a system startup**

change "enforcing" to "disabled" in ''/etc/selinux/config'' and reboot.


**Aborted Error**

If you see the following error when you run zviewer on Linux : ::

    Aborted

It can be due to a bad link with the librairies of TK. 
Check the links: ::

    ls -la /usr/lib/libtk.so

If you see the following link : ::

    libtk.so -> libtk8.4.so

A solution can be to create a symbolic link to libtk8.5.so : ::

    rm /usr/lib/libtk.so
    ln -s /usr/lib/libtk8.5.so /usr/lib/libtk.so


**X Error of failed request**

If you see the following error when you run zviewer on Linux : ::

     X Error of failed request:  BadValue (integer parameter out of range for operation)
     Major opcode of failed request:  91 (X_QueryColors)
     Value in failed request:  0xff141312
     Serial number of failed request:  907
     Current serial number in output stream:  907

Check and insert your xorg.conf file in /etc/X11 : ::

     Section "Extensions"
          Option "Composite" "Disable"
     EndSection

That means that your graphical card doesn't manage the window draft.


**SuperBaloo Not Installed**

If Superbaloo is not installed, it means that **GMM++ is missing**.    

see `General Requirements <general_requirements.html>`_

Edit the **GMM build options** in the CMake process. For that, type in your build shell : ::

    cd mips_build
    make edit_cache

When ccmake is running, press 't' to display all build options, and modify  **GMM build options** : ::

    USE_GMM                          ON
    GMM_INCLUDE_DIR                  /usr/local/include
   
Configure [c], Generate [g] and re-build : ::
    make


**DefInverse Not Installed**

If DefInverse is not installed, it means that **USE_MTL build option is desactivated**.    

Edit the **USE_MTL build options** in the CMake process. For that, type in your build shell : ::

    cd mips_build
    make edit_cache

When ccmake is running, press 't' to display all build options, and modify  **USE_MTL build options** : ::

    USE_MTL                          ON

Configure [c], Generate [g] and re-build : ::

    make


**Running on Nef cluster**

**Permission denied (publickey)**

If you see the following error when you run :
* Script_5_Recalage_Rigide_Auto_sur_grille_1 
* or Script_6_Recalage_Rigide_Auto_sur_grille_2
* or Script_8_Recalage_Dense_Auto_sur_grille_1
* or Script_9_Recalage_Dense_Auto_sur_grille_2 ::

    Permission denied (publickey).
    lost connection

You have to edit the Script_5_Recalage_Rigide_Auto_sur_grille_1 with a text editor and add your username@ used on the cluster before nef.inria.fr: ::

    vim Script_5_Recalage_Rigide_Auto_sur_grille_1
    scp ScriptSubBaladin **username@** nef.inria.fr:~/tmpBaladin0/
    
Save and re-run the script.
