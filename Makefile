Executable=python multisetup.py
Project=vplants

main:
	
	@echo '============== $(Project) Makefile========================================='
	@echo 'This is a simple Makefile that calls the scritp make_develop.py '
	@echo 'This script has the following options: develop undevelop install or release'
	@echo '==========================================================================='

develop:
	$(Executable) develop

undevelop:
	$(Executable) undevelop 

nosetests:
	$(Executable) nosetests -p $(Project) -d .

bdist:
	$(Executable) bdist

bdist_egg:
	$(Executable) bdist_egg

sdist:
	$(Executable) sdist

 
install:
	$(Executable) install 

clean:
	$(Executable) clean

cleandoc:
	rm -r ./*/doc/html
	rm -r ./*/doc/latex
