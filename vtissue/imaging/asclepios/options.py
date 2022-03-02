#scons parameters file
#use this file to pass custom parameter to SConstruct script
import platform

debug = True
warning=True
if platform.system() != "Windows":
    EXTRA_CPPDEFINES = ['-D_LINUX_']
    EXTRA_CCFLAGS=['-ansi', '-fsigned-char', '-fsigned-bitfields', '-Wall']
