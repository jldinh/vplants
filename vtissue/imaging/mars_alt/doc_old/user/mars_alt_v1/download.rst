=========================
Download and Installation
=========================

The MARS-ALT components are developped on Linux platform. 

.. note:: The binaries are been compiled for Linux-FC12 platform.
 
          If you have an other distribution, you can use a `VirtualBox <http://www.virtualbox.org/>`_ or if you have an access to the SVN (for developpers), you can compile the code from `sources <install.html>`_.

* `General Requirements <general_requirements.html>`_

1. Download and Uncompress the binairies MIPS-MARS-ALT

`MARS-ALT for Linux <ftp://ftp-sop.inria.fr/virtualplants/MARS-ALT/downloads/>`_

2. Adjusting the Environment Variables**

In order to use MIPS-MARS-ALT for Linux, the PATH variables must be extended to locate all tools.

To set the PATH variable, type the following lines in your shell::
    
    echo "export PATH=WHERE_MARS-ALT_IS_UNCOMPRESSED/MarsAltFernandezSoftwareTools/bin:$PATH" >> ~/.bashrc
    echo "export LD_LIBRARY_PATH=WHERE_MARS-ALT_IS_UNCOMPRESSED/MarsAltFernandezSoftwareTools/lib:$LD_LIBRARY_PATH" >> ~/.bashrc
    echo "export YAV_SHELLS=WHERE_MARS-ALT_IS_UNCOMPRESSED/MarsAltFernandezSoftwareTools/shells" >> ~/.bashrc
    echo "export VTISSUEPATH=WHERE_MARS-ALT_IS_UNCOMPRESSED/MarsAltFernandezSoftwareTools/" >> ~/.bashrc 

If you are new to MARS-ALT, we suggest that you take a look at the tutorials to see MARS-ALT in action.

* `Tutorials <tutorial.html>`_

**Troubleshootings**

If you have any problems during or after the installation, see `Troubleshootings <troubleshootings.html>`_ page, where you may find some already known issues. If not present, post your question on `Mars-Alt Forum <https://gforge.inria.fr/forum/forum.php?forum_id=7376&group_id=79>`_ .
