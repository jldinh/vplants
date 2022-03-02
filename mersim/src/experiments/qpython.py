#!/usr/bin/env python

"""
qpython - an interactive Python shell

(C) David Boddie 2004

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import cmd, imp, os, string, sys, traceback, types

import threading

from qt import QApplication, QCustomEvent, QFileDialog, QFont, QHBoxLayout, \
               QInputDialog, QLineEdit, QMessageBox, QMouseEvent, QObject, \
               QPushButton, QPopupMenu, QStatusBar, QTextEdit, QThread, Qt, \
               QVBox, QVBoxLayout, QWidget, SIGNAL, SLOT, qApp

try:

    import qtext
    use_qtext = 1

except ImportError:

    use_qtext = 0


# Import the __future__ module to enable code using future language changes
# to be compiled interactively.

import __future__


# Define the application details.

appname = "qpython"
__version__ = "0.55"


# Set up tab completion
try:

    import readline, rlcompleter, __builtin__

except ImportError:

    tab_completion = 0

else:

    tab_completion = 1
    
    # For versions of Python earlier than Python 2.3, we need to provide
    # a Completer object that can scan namespaces other than __main__ and
    # __builtin__. We shall just use parts of the Python 2.3 Completer
    # class:
    
    class UserCompleter(rlcompleter.Completer):
    
        def __init__(self, namespace):
        
            self.use_main_ns = 0
            self.namespace = namespace
        
        def global_matches(self, text):
        
            import keyword
            matches = []
            n = len(text)
            for list in [keyword.kwlist,
                         __builtin__.__dict__,
                         self.namespace]:
                for word in list:
                    if word[:n] == text and word != "__builtins__":
                        matches.append(word)
            return matches
        
        def attr_matches(self, text):
        
            import re
            m = re.match(r"(\w+(\.\w+)*)\.(\w*)", text)
            if not m:
                return
            expr, attr = m.group(1, 3)
            
            object = eval(expr, self.namespace)
            
            words = dir(object)
            
            if hasattr(object,'__class__'):
            
                # Both modules and classes can have the __class__ attribute.
                
                if hasattr(object, '__module__'):
                
                    # Only classes have the __module__ attribute.
                    words.append('__class__')
                    words = words + self.get_class_members(object.__class__)
            
            matches = []
            n = len(attr)
            
            for word in words:
                if word[:n] == attr and word != "__builtins__":
                    matches.append("%s.%s" % (expr, word))
            return matches
        
        def get_class_members(self, klass):
            ret = dir(klass)
            if hasattr(klass,'__bases__'):
                for base in klass.__bases__:
                    ret = ret + self.get_class_members(base)
            return ret


# Define a start up message for the interpreter.

start_up = \
"""
%s %s

python:
  Type "help", "copyright", "credits" or "license" for more information.

qpython:
  Type "qpython_license" for license information specific to this environment.

""" % (appname, __version__)


class NoValueClass:

    pass

NoValue = NoValueClass()


class Traceback:

    def __init__(self, text):
    
        self.text = text


# Define an object to contain the license for khpython.
qpython_license = __doc__[1:]

# Define a docstring for the user module.
user_docstring = __doc__[1:string.find(__doc__, "\n", 1)]


# Define a function to obtain the class attributes for an instance.

adir_function = """
def adir(obj):

    if hasattr(obj, "__class__") and not hasattr(obj, "__bases__"):
    
        return obj.__class__.__dict__.keys()
    
    else:
    
        return []
"""

class Editor(QWidget):

    # Redefine the tr() function for this class.
    def tr(self, text):
    
        return qApp.translate("Editor", text)
    
    def __init__(self, environment):
    
        QWidget.__init__(self)
        
        self.environment = environment
        
        if use_qtext:
            self.text_edit = qtext.QextScintilla(self)
            self.text_edit.setLexer(qtext.QextScintillaLexerPython(self))
        else:
            self.text_edit = QTextEdit(self)
        
        font = QFont()
        font.setFamily("Courier")
        self.text_edit.setFont(font)
        
        self.run_button = QPushButton(self.tr("Run"), self)
        self.close_button = QPushButton(self.tr("Close"), self)
        
        self.status_bar = QStatusBar(self)
        
        self.connect(self.run_button, SIGNAL("clicked()"), self.run_script)
        self.connect(
            self.close_button, SIGNAL("clicked()"), self, SLOT("close()")
            )
        
        panel_layout = QHBoxLayout()
        panel_layout.addStretch(1)
        panel_layout.addWidget(self.run_button)
        panel_layout.addSpacing(4)
        panel_layout.addWidget(self.close_button)
        
        layout = QVBoxLayout(self)
        layout.addSpacing(4)
        layout.addWidget(self.text_edit, 1)
        layout.addSpacing(4)
        layout.addLayout(panel_layout)
        layout.addWidget(self.status_bar)
    
    def run_script(self):
    
        # Examine the text submitted.

        # Submit it to the user's running environment.
        try:

            # Retrieve a string value from the environment's execute method.
            text = str(self.text_edit.text())

            if text[-1:] != ["\n"]:

                text = text + "\n"

            value = self.environment.execute(text)

            if isinstance(value, Traceback):

                sys.stdout.write(value.text + "\n")
                last_line = filter(
                    lambda line: line != "", value.text.split("\n")
                    )[-1]

            elif value is not NoValue and value is not None:

                sys.stdout.write(repr(value) + "\n")
                last_line = repr(value).split("\n")[-1]
            
            else:
            
                last_line = "OK"
            
            self.status_bar.message(last_line, 2000)
        
        except SyntaxError:
        
            pass


class Environment:

    def __init__(self):
    
        # Import some modules to customise the environment.
        self.setup_environment()
        
        # Delayed code for execution.
        self.delayed = []
    
    def setup_environment(self):
    
        # Construct a module to use to contain Python executed by the
        # user.
        self.module = imp.new_module("__user__")
        
        # Add a docstring for this module.
        self.module.__doc__ = user_docstring
        
        # Copy the sys module into the user's environment.
        self.module.sys = sys
        
        # Define some functions for the user.
        
        # Introduce a function to return the class attributes of instance
        # objects.
        
        adir = compile(adir_function, "<setup_functions>", "exec")
        exec adir in self.module.__dict__
        
        # Set up tab completion in the user module.
        if tab_completion:
        
            readline.set_completer(
                UserCompleter(self.module.__dict__).complete
                )
            readline.parse_and_bind("tab: complete")
        
        # Set up an object containing qpython license information in the
        # user module.
        self.module.qpython_license = qpython_license
        #self.module.LICENSE = __doc__[1:]
    
    def execute(self, command_line, use_delayed = 1):
    
        if len(command_line) == 0:
        
            return NoValue
        
        if use_delayed:
        
            if command_line[0] in " \t":
            
                # Add the line to the list of delayed command lines.
                self.delayed.append(command_line)
                return NoValue
            
            if self.delayed != []:
            
                command_lines = "".join(self.delayed) + command_line
            
            else:
            
                command_lines = command_line
        
        try:
        
            value = eval(command_lines, self.module.__dict__)
            
            # Set the _ variable to the value returned.
            self.module._ = value
            
            if use_delayed:
            
                # The pending input was executed successfully so clear
                # the delayed command lines list.
                self.delayed = []
            
            return value
        
        except SyntaxError:
        
            # Catch Syntax Errors and pass them on for another attempt
            # to compile and execute them.
            pass
        
        except:
        
            # Catch all other errors and report them.
            
            if use_delayed:
            
                # Clear the delayed command line list.
                self.delayed = []
            
            return self.format_exc()
        
        
        # Try again with the exec command.
        
        # Construct a flags word for any features imported from the
        # __future__ module. Peculiarly, this has to be done because
        # the compile function appears not to be aware of any __future__
        # imports done from the command line.
        
        flags = 0
        user_values = filter(
            lambda x: isinstance(x, __future__._Feature),
            self.module.__dict__.values()
            )
        
        for value in __future__.__dict__.values():
        
            if isinstance(value, __future__._Feature):
            
                if value in user_values:
                
                    flags = flags | value.compiler_flag
        
        try:
        
            # Compile the code using the flags determined from the imported
            # features. The last parameter indicates that these flags should
            # be taken into account when compiling.
            
            code = compile(command_lines, "__user__", "exec", flags, 0)
            exec code in self.module.__dict__
            
            if use_delayed:
            
                # The pending input was executed successfully so clear
                # the delayed command lines list.
                self.delayed = []
            
            # No values are returned from the execution of code in this
            # manner unless we are using existing lines from the delayed
            # lines list.
            return NoValue
        
        except SyntaxError:
        
            msg = sys.exc_info()[1].msg
            #print encode(msg)
            
            if string.find( msg, "unexpected EOF while parsing" ) != -1:
            
                if use_delayed:
                
                    # Delay code for later execution.
                    self.delayed.append(command_line)
                
                return NoValue
            
            elif string.find(msg, "expected an indented block") != -1:

                # Only take this seriously if there is no preceding text
                # or if these last two lines have the same indentation.
                
                if use_delayed and self.delayed != [] and \
                    ( self.indentation(self.delayed[-1]) != \
                      self.indentation(command_line)          ):
                
                    # Keep the line for later if there is preceding text and
                    # the indentation has changed.
                    
                    self.delayed.append(command_line)
                    return NoValue
            
            # An actual Syntax Error.
            
            if use_delayed:
            
                # Clear the delayed command line list.
                self.delayed = []
            
            return self.format_exc()
        
        except:
        
            # Other errors are caught here.
            
            if use_delayed:
            
                # Clear the delayed command line list.
                self.delayed = []
            
            return self.format_exc()
    
    def format_exc(self):
    
        lines = map(
            lambda line: line,
            #traceback.format_exception_only(*(sys.exc_info()[:2]))
            traceback.format_exception(*(sys.exc_info()))
            )
        
        return Traceback("\n".join(lines))
    
    def indentation(self, s, tabsize = 4):
    
        l = 0
        
        for i in s:
        
            if i == " ":
                l = l + 1
            elif i == "\t":
                l = l + tabsize
            else:
                break
        
        return l


class GUIInterface(QObject):

    """GUIInterface(QObject)
    
    This class handles the interactions between a CommandLine object and an
    Environment object.
    
    gui = GUIInterface(finished_event, input_event, environment)
    
    The GUIInterface object is a subclass of QObject in order to allow
    executed Python code to access Qt classes.
    """
    
    def __init__(self, app, finished_event, input_event, environment):
    
        QObject.__init__(self)
        
        self.app = app
        
        # Record the environment object.
        self.environment = environment
        
        # Print a welcome message.
        self.add_output(start_up)
        
        self.finished_event = finished_event
        self.input_event = input_event
    
    def customEvent(self, event):
    
        """customEvent(self, event)
        
        Monitor the input from the command line.
        
        If the user asks the interpreter to exit, the finished event will be
        set. Therefore, we stop monitoring events and quit the application.
        
        If the input event is set then we can submit the user's input to the
        environment for compilation and execution, then display the result
        in the console. The input event is cleared afterwards to enable the
        command line to stop waiting, and read further input.
        """
        
        if event.type() != 99999:
        
            return
        
        if self.input_event.isSet():
        
            # Examine the text submitted.
            
            # Submit it to the user's running environment.
            try:
            
                # Retrieve a string value from the environment's execute method.
                value = self.environment.execute(
                    self.environment.input_string + "\n"
                    )
                
                if isinstance(value, Traceback):
                
                    self.add_output(value.text + "\n")
                
                elif value is not NoValue and value is not None:
                
                    self.add_output(repr(value) + "\n")
            
            except SyntaxError:
            
                pass
            
            # Clear the input event.
            self.input_event.clear()
        
        if self.finished_event.isSet():
        
            qApp.quit()
    
    def add_output(self, output):
    
        sys.stdout.write(output)


class CommandLine(QThread, cmd.Cmd):

    """CommandLine(QThread, cmd.Cmd)
    
    This class provides a command line for reading user input.
    
    command_line = CommandLine(environment, receiver, finished_event,
                               input_event)
    
    The environment must be an Environment object which will perform the
    compilation and execution of Python source code.
    
    The receiver is the GUI handling object which communicates with Qt's
    event loop.
    
    The exit, finished and input events should be threading.Event objects;
    these must also be passed in a consistent manner to a GUIInterface
    object.
    """
    
    def __init__(self, environment, receiver, finished_event, input_event):
    
        QThread.__init__(self)
        cmd.Cmd.__init__(self)
        
        # Record the environment object.
        self.environment = environment
        
        # Record the receiver of custom events.
        self.receiver = receiver
        
        self.finished_event = finished_event
        self.input_event = input_event
        
        # Set the prompt string.
        self.prompt = ">>> "
    
    def send_event(self):
    
        event = QCustomEvent(99999)
        self.postEvent(self.receiver, event)
    
    def onecmd(self, input_string):
    
        """stop = onecmd(self, input_string)
        
        Submit the input string to the Python execution environment for later
        execution, set the input event then wait for it to be cleared by the
        environment.
        """
        
        # Record the input string for later execution.
        self.environment.input_string = input_string
        
        # Set the input event so that the hidden object knows to
        # execute the code.
        self.input_event.set()
        self.send_event()
        
        # Wait until the previous input event has been processed.
        
        while not self.finished_event.isSet() and self.input_event.isSet():
        
            pass
    
    def preloop(self):
    
        """preloop(self)
        
        A reimplementation of the original preloop method. This prevents
        the CommandLine object from falling back on the original cmd.Cmd
        tab completion infrastructure.
        """
        pass
    
    def postcmd(self, line):
    
        """postcmd(self, line)
        
        Disply a prompt to reflect whether the environment is holding back
        source code for later execution. This makes multi line source code
        easier to see in the console.
        """
        
        if self.environment.delayed != []:
        
            self.prompt = "... "
        
        else:
        
            self.prompt = ">>> "
    
    def run(self, intro=None):
    
        """run(self, intro=None)
        
        Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.
        
        Don't interfere with the input string if the user input is terminated
        with a CTRL-D; raise an EOFError, if necessary, and catch the
        exception outside the processing loop.
        
        [Reimplemented using original code from the cmdloop method of
        the cmd.Cmd class.]
        """

        self.preloop()
        
        try:
        
            if intro is not None:
                self.intro = intro
            
            if self.intro:
                self.stdout.write(str(self.intro)+"\n")
            
            while not self.finished_event.isSet():
            
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                    
                        line = raw_input(self.prompt)
                    
                    else:
                    
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                        
                            raise EOFError, "end of input"
                        
                        else:
                        
                            line = line[:-1] # chop \n
                
                line = self.precmd(line)
                self.onecmd(line)
                self.postcmd(line)
        
        except (KeyboardInterrupt, EOFError):
        
            pass
        
        self.postloop()

    def postloop(self):
    
        """postloop(self)
        
        Sets the finished event to inform the GUI interface to stop the
        application's event loop.
        """
        
        if not self.finished_event.isSet():
        
            self.finished_event.set()
            self.send_event()


def main():

    # Find the path to this program.
    global app_path, app_file
    
    app_path, app_file = os.path.split(sys.argv[0])
    
    # If the working directory is not in the sys.path list then add it.
    
    pwd = os.getenv("PWD")
    
    if pwd != "" and pwd not in sys.path:
    
        sys.path.insert(0, pwd)
    
    app = QApplication(sys.argv)
    
    # Create an environment to run Python scripts in.
    environment = Environment()
    
    # Define a function to obtain an Editor instance.
    
    def editor():
    
        """Return and show an editor for Python code."""
        widget = Editor(environment)
        widget.show()
        return widget
    
    environment.module.editor = editor
    
    # The finished event is set when the command line exits.
    finished_event = threading.Event()
    
    # The input event is set when a new command line has been entered.
    input_event = threading.Event()
    
    # The GUI interface object checks whether the command line has finished
    # and, if so, exits the application.
    hidden = GUIInterface(app, finished_event, input_event, environment)
    
    # Create a thread to handle command line input and start it.
    command_line = CommandLine(
        environment, hidden, finished_event, input_event
        )
    
    command_line.start()
    
    # Wait for the Qt application to exit.
    result = app.exec_loop()
    
    print
    
    # Ask the command line thread to stop.
    if not command_line.finished():
    
        print "Stopping the command line thread..."
        command_line.wait()
        print "Exiting..."
    
    return result


if __name__ == "__main__":

    result = main()
    
    # Exit
    sys.exit(result)
