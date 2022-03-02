from pglviewer.ressources import compile_ui,compile_rc,make_menu

uiname=compile_ui("root.ui")
make_menu(uiname)
rcname=compile_rc("root.qrc")

