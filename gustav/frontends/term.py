# -*- coding: utf-8 -*-

# Copyright (c) 2010-2019 Christopher Brown
#
# This file is part of Gustav.
#
# Gustav is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Gustav is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Gustav.  If not, see <http://www.gnu.org/licenses/>.
#
# Comments and/or additions are welcome. Send e-mail to: cbrown1@pitt.edu.
#


import os, sys

try: input = raw_input
except: pass

name = 'term'

def get_file(parent=None, title = 'Open File', default_dir = "", file_types = ("All files (*.*)")):
    """Opens a file dialog, returns file path as a string

        To specify filetypes, use the (qt) format:
        "Python or Plain Text Files (*.py *.txt);;All files (*.*)"
    """

    getting_file = True
    while getting_file:
        ret = input("{} ({}): ".format(title, default_dir))
        if not os.path.exists(ret):
            print("File does not exist: {}".format(ret))
        elif not os.path.isfile(ret):
            print("Not a file: {}".format(ret))
        else:
            getting_file = False
    return ret


def get_folder(parent=None, title = 'Open Folder', default_dir = ""):
    """Opens a folder dialog, returns the path as a string
    """
    getting_folder = True
    while getting_folder:
        ret = input("{} ({}): ".format(title, default_dir))
        if not os.path.exists(ret):
            print("Path does not exist: {}".format(ret))
        elif not os.path.isdir(ret):
             print("Path is not a folder: {}".format(ret))
        else:
            getting_folder = False
    return ret

def get_item(parent=None, title = 'User Input', prompt = 'Choose One:', items = [], current = 0, editable = False):
    """Opens a simple prompt to choose an item from a list, returns a string
    """
    for ind, item in enumerate(items):
        print(" ",ind+1,". ", item)
    ret = input(prompt)
    if ret != '':
        ind = int(ret)-1
        if ind < len(items):
            return items[ind]
        else:
            return ""
    else:
        return ""


def get_yesno(parent=None, title = 'User Input', prompt = 'Yes or No:'):
    """Opens a simple yes/no message box, returns a bool
    """
    ret = input(prompt+" (Y/N): ")
    if ret.lower() == 'n':
        return False
    else:
        return True

def show_message(parent=None, title = 'Title', message = 'Message', msgtype = 'Information'):
    """Opens a simple message box

      msgtype = 'Information', 'Warning', or 'Critical'
    """
    if msgtype == 'Information':
        print(message)
    else:
        print(msgtype + ": "+ message)


def get_input(parent=None, title = 'User Input', prompt = 'Enter a value:'):
    """Opens a simple prompt for user input, returns a string
    """
    try:
        ret = input(prompt)
    except EOFError:
        ret = ''
    return ret

    
# System-specific functions
if os.name in ["posix"]: #, "mac"]:
    import termios
    TERMIOS = termios
    def get_char(parent=None, title = 'User Input', prompt = 'Enter a value:'):
        '''Returns a single character from standard input
        '''
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def clearscreen():
        """Clear the console.
        """
        os.system('tput clear')

elif os.name in ("nt", "dos", "ce"):
    from msvcrt import getch
    def get_char(parent=None, title = 'User Input', prompt = 'Enter a value:'):
        '''Returns a single character from standard input
        '''
        ch = getch()
        return ch

    def clearscreen():
        """Clear the console.
        """
        os.system('CLS')

elif os.name == "mac":
    def get_char(parent=None, title = 'User Input', prompt = 'Enter a value:'):
        '''Returns a single character from standard input [UNTESTED]
        '''
        import Carbon
        if Carbon.Evt.EventAvail(0x0008)[0]==0: # 0x0008 is the keyDownMask
            return ''
        else:
            (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)

    def clearscreen():
        """Clear the console.
        """
        os.system('tput clear')

