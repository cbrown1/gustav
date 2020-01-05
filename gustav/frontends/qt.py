# -*- coding: utf-8 -*-

# Copyright (c) 2010-2020 Christopher Brown
#
# This file is part of gustav.
#
# gustav is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gustav is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gustav.  If not, see <http://www.gnu.org/licenses/>.
#
# Comments and/or additions are welcome. Send e-mail to: cbrown1@pitt.edu.
#


from PyQt4 import QtGui, QtCore
import sys
from copy import deepcopy
STDOUT = sys.stdout

name = 'qt'

def get_file(parent=None, title = 'Open File', default_dir = "", file_types = "All files types (*.*)"):
   """Opens a file dialog, returns file path as a string

       To specify filetypes, use the (qt) format:
       "Python or Plain Text Files (*.py *.txt);;All files (*.*)"
   """
   if QtGui.QApplication.startingUp():
       app = QtGui.QApplication([])
   sys.stdout = None # Avoid the "Redirecting output to win32trace
                     # remote collector" message from showing in stdout
   ret = QtGui.QFileDialog.getOpenFileName(parent, title, default_dir, file_types)
   sys.stdout = STDOUT
   return str(ret)

def get_folder(parent=None, title = 'Open Folder', default_dir = ""):
    """Opens a folder dialog, returns the path as a string
    """
    if QtGui.QApplication.startingUp():
        app = QtGui.QApplication([])
    sys.stdout = None
    ret = QtGui.QFileDialog.getExistingDirectory(parent, title, default_dir)
    sys.stdout = STDOUT
    return str(ret)

def get_input(parent=None, title = 'User Input', prompt = 'Enter a value:'):
    """Opens a simple prompt for user input, returns a string
    """
    if QtGui.QApplication.startingUp():
        app = QtGui.QApplication([])
    sys.stdout = None
    ret, ok = QtGui.QInputDialog.getText(parent, title, prompt)
    sys.stdout = STDOUT
    if ok:
        return str(ret)
    else:
        return ''

def get_item(parent=None, title = 'User Input', prompt = 'Choose One:', items = [], current = 0, editable = False):
    """Opens a simple prompt to choose an item from a list, returns a string
    """
    if QtGui.QApplication.startingUp():
        app = QtGui.QApplication([])
    sys.stdout = None
    ret, ok = QtGui.QInputDialog.getItem(parent, title, prompt, items, current, editable)
    sys.stdout = STDOUT
    if ok:
        return str(ret)
    else:
        return ''

def get_yesno(parent=None, title = 'User Input', prompt = 'Yes or No:'):
    """Opens a simple yes/no message box, returns a bool
    """
    if QtGui.QApplication.startingUp():
        app = QtGui.QApplication([])
    sys.stdout = None
    ret = QtGui.QMessageBox.question(parent, title, prompt, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    sys.stdout = STDOUT
    if ret == QtGui.QMessageBox.Yes:
        return True
    else:
        return False

def show_message(parent=None, title = 'Title', message = 'Message', msgtype = 'Information'):
    """Opens a simple message box

      msgtype = 'Information', 'Warning', or 'Critical'
    """
    if QtGui.QApplication.startingUp():
        app = QtGui.QApplication([])
    sys.stdout = None
    if msgtype == 'Information':
        QtGui.QMessageBox.information(parent, title, message)
    elif msgtype == 'Warning':
        QtGui.QMessageBox.warning(parent, title, message)
    elif msgtype == 'Critical':
        QtGui.QMessageBox.critical(parent, title, message)
    sys.stdout = STDOUT

