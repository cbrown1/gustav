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

""" This form is intended to be useful for running n-alternative forced-choice 
    experiments, in which a subject chooses one of a number of alternatives. 
    Each alternative is represented as a box, with an identifying char in the 
    middle. You can change the color of the box, and also the border style to 
    provide stimulus timing or response feedback. There is also a prompt that 
    can be updated, shown and hidden, as well as notification boxes and title 
    and status bars as well that should offer enough flexibility to show 
    whatever information is needed at any given time during an experiment.

    Because this is a curses interface, a screenshot can be pasted right here in 
    the text, alas without color:


┌Gustav Speech!                        A speech experiment                              Subject 500┐
│                                                                                                  │
│┌Block Info─────────────────────────────────────────────────────────────────┐                     │
││ Condition 1, Block 1 of 24                                                │ 14:42:59  Playback  │
│└───────────────────────────────────────────────────────────────────────────┘                     │
│┌Trial Info──────────────────────────────────────────────────────────────────────────────────────┐│
││ Trial 2 of 3 | AW002.WAV; KW: 5                                                                ││
││ GLUE the SHEET to the DARK BLUE BACKGROUND.                                                    ││
│└────────────────────────────────────────────────────────────────────────────────────────────────┘│
│┌Current Block──────────────────────────────────┐┌Previous Block─────────────────────────────────┐│
││ Previous Trial: 3/5 (60%)                     ││                                               ││
││ This Block: 3/10 (30%)                        ││                                               ││
│└───────────────────────────────────────────────┘└───────────────────────────────────────────────┘│
│┌Block Variables────────────────────────────────┐┌Experiment Variables───────────────────────────┐│
││ SNR: 6                                        ││ Conditions: 1,2,3,4,5,6,7,8,9                 ││
││ Target: CUNY_F1                               ││ Record data: yes                              ││
││ Masker: IEEE_F1                               ││                                               ││
││                                               ││                                               ││
││                                               ││                                               ││
││                                               ││                                               ││
││                                               ││                                               ││
││                                               ││                                               ││
││                                               ││                                               ││
││                                               ││                                               ││
││                                               ││                                               ││
││                                               ││                                               ││
│└───────────────────────────────────────────────┘└───────────────────────────────────────────────┘│
└Press '/' to quit                         Trial 2 of 3                                Block 1 of 1┘


    You can instantiate the form with:

        from gustav.forms import nafc as theForm
        interface = theForm.Interface(alternatives=3)

    All of the text areas (Title left, center, right, status left, center, 
    right, notify left, right) are format-able in code with foreground and 
    background colors. You can set the text of any of them with something like:

        interface.update_Title_Left("A new title")

    but to optimize performance (all those chars!), the screen is not updated 
    until you request it. This can be done either with:

        interface.update()

    ...or while you are setting text with:

        interface.update_Status_Center("Some status text", redraw=True)

    For title and status text, set to "" to clear. Notify text works a little 
    different, with a little more control since it is intended to be used more 
    for moment-to-moment notifications. So, redraw is True by default when 
    setting notify text, and there are also functions to show or hide each:

        interface.show_Notify_Left(True)

    You can explicitly pass a bool, or leave blank to toggle.

    ## Lateralization-specific notes

    The main function will be:

        interface.set_marker_pos(pos=fpos, diffuse=fdiffuse)

    Both pos and diffuse are expected to be floats 0>=1. You can set both or 
    either. You can also show/hide the position bar and marker with:

        interface.show_Position_Bar()

    ...or just the marker:

        interface.show_Marker()

    See the main loop at the bottom of this file for more usage examples.

    ## Other notes

    This form has been confirmed to work in a number of common terminals, 
    including xfce4-terminal, gnome-terminal, qterminal, konsole, and 
    xterm. It may require the TERM var to be set for color support:

        env TERM=xterm-256color python3 speech.py

    It is working well on python 3.x. Much of the rendering is based on unicode 
    which is a mess in py2, and since py2 has reached end-of-life, not much work
    has gone into it...

    You can demo the interface by running it. In the demo, arrow keys will 
    control the marker and diffuse area, and some basic functionality is shown 
    off. 

"""

#from __future__ import unicode_literals
import os, sys
import curses
import threading
import time
import math

class Interface():
    def __init__(self):
        # Initialize text areas
        self.title_l_str = "Gustav Speech!"
        self.title_c_str = ""
        self.title_r_str = ""
#        self.notify_l_str = ""
#        self.notify_l_show = False
#        self.notify_r_str = ""
#        self.notify_r_show = False
#        self.notify_pad = True
#        self.notify_offset_v = 2                # Vertical offset of notifications from top of window
        self.status_l_str = "Press '/' to quit"
        self.status_c_str = ""
        self.status_r_str = ""

        self.keypress_wait = .005 # Sleep time in sec during keypress loop to avoid cpu race
                                  # Longer values are better for slower machines

        # Some stuff for rendering
        # Dict so you can specify colors in curses using standard xterm 256-color palette names.
        self.palette256 = {'Black': 0, 'Maroon': 1, 'Green': 2, 'Olive': 3, 'Navy': 4, 'Purple': 5, 'Teal': 6, 'Silver': 7, 'Grey': 8, 'Red': 9, 'Lime': 10, 'Yellow': 11, 'Blue': 12, 'Fuchsia': 13, 'Aqua': 14, 'White': 15, 'Grey0': 16, 'NavyBlue': 17, 'DarkBlue': 18, 'Blue3-1': 19, 'Blue3-2': 20, 'Blue1': 21, 'DarkGreen': 22, 'DeepSkyBlue4-1': 23, 'DeepSkyBlue4-2': 24, 'DeepSkyBlue4-3': 25, 'DodgerBlue3': 26, 'DodgerBlue2': 27, 'Green4': 28, 'SpringGreen4': 29, 'Turquoise4': 30, 'DeepSkyBlue3': 31, 'DeepSkyBlue3': 32, 'DodgerBlue1': 33, 'Green3': 34, 'SpringGreen3': 35, 'DarkCyan': 36, 'LightSeaGreen': 37, 'DeepSkyBlue2': 38, 'DeepSkyBlue1': 39, 'Green3': 40, 'SpringGreen3': 41, 'SpringGreen2': 42, 'Cyan3': 43, 'DarkTurquoise': 44, 'Turquoise2': 45, 'Green1': 46, 'SpringGreen2': 47, 'SpringGreen1': 48, 'MediumSpringGreen': 49, 'Cyan2': 50, 'Cyan1': 51, 'DarkRed': 52, 'DeepPink4': 53, 'Purple4': 54, 'Purple4': 55, 'Purple3': 56, 'BlueViolet': 57, 'Orange4': 58, 'Grey37': 59, 'MediumPurple4': 60, 'SlateBlue3': 61, 'SlateBlue3': 62, 'RoyalBlue1': 63, 'Chartreuse4': 64, 'DarkSeaGreen4': 65, 'PaleTurquoise4': 66, 'SteelBlue': 67, 'SteelBlue3': 68, 'CornflowerBlue': 69, 'Chartreuse3': 70, 'DarkSeaGreen4': 71, 'CadetBlue': 72, 'CadetBlue': 73, 'SkyBlue3': 74, 'SteelBlue1': 75, 'Chartreuse3': 76, 'PaleGreen3': 77, 'SeaGreen3': 78, 'Aquamarine3': 79, 'MediumTurquoise': 80, 'SteelBlue1': 81, 'Chartreuse2': 82, 'SeaGreen2': 83, 'SeaGreen1': 84, 'SeaGreen1': 85, 'Aquamarine1': 86, 'DarkSlateGray2': 87, 'DarkRed': 88, 'DeepPink4': 89, 'DarkMagenta': 90, 'DarkMagenta': 91, 'DarkViolet': 92, 'Purple': 93, 'Orange4': 94, 'LightPink4': 95, 'Plum4': 96, 'MediumPurple3': 97, 'MediumPurple3': 98, 'SlateBlue1': 99, 'Yellow4': 100, 'Wheat4': 101, 'Grey53': 102, 'LightSlateGrey': 103, 'MediumPurple': 104, 'LightSlateBlue': 105, 'Yellow4': 106, 'DarkOliveGreen3': 107, 'DarkSeaGreen': 108, 'LightSkyBlue3': 109, 'LightSkyBlue3': 110, 'SkyBlue2': 111, 'Chartreuse2': 112, 'DarkOliveGreen3': 113, 'PaleGreen3': 114, 'DarkSeaGreen3': 115, 'DarkSlateGray3': 116, 'SkyBlue1': 117, 'Chartreuse1': 118, 'LightGreen': 119, 'LightGreen': 120, 'PaleGreen1': 121, 'Aquamarine1': 122, 'DarkSlateGray1': 123, 'Red3': 124, 'DeepPink4': 125, 'MediumVioletRed': 126, 'Magenta3': 127, 'DarkViolet': 128, 'Purple': 129, 'DarkOrange3': 130, 'IndianRed': 131, 'HotPink3': 132, 'MediumOrchid3': 133, 'MediumOrchid': 134, 'MediumPurple2': 135, 'DarkGoldenrod': 136, 'LightSalmon3': 137, 'RosyBrown': 138, 'Grey63': 139, 'MediumPurple2': 140, 'MediumPurple1': 141, 'Gold3': 142, 'DarkKhaki': 143, 'NavajoWhite3': 144, 'Grey69': 145, 'LightSteelBlue3': 146, 'LightSteelBlue': 147, 'Yellow3': 148, 'DarkOliveGreen3': 149, 'DarkSeaGreen3': 150, 'DarkSeaGreen2': 151, 'LightCyan3': 152, 'LightSkyBlue1': 153, 'GreenYellow': 154, 'DarkOliveGreen2': 155, 'PaleGreen1': 156, 'DarkSeaGreen2': 157, 'DarkSeaGreen1': 158, 'PaleTurquoise1': 159, 'Red3': 160, 'DeepPink3': 161, 'DeepPink3': 162, 'Magenta3': 163, 'Magenta3': 164, 'Magenta2': 165, 'DarkOrange3': 166, 'IndianRed': 167, 'HotPink3': 168, 'HotPink2': 169, 'Orchid': 170, 'MediumOrchid1': 171, 'Orange3': 172, 'LightSalmon3': 173, 'LightPink3': 174, 'Pink3': 175, 'Plum3': 176, 'Violet': 177, 'Gold3': 178, 'LightGoldenrod3': 179, 'Tan': 180, 'MistyRose3': 181, 'Thistle3': 182, 'Plum2': 183, 'Yellow3': 184, 'Khaki3': 185, 'LightGoldenrod2-1': 186, 'LightYellow3': 187, 'Grey84': 188, 'LightSteelBlue1': 189, 'Yellow2': 190, 'DarkOliveGreen1': 191, 'DarkOliveGreen1': 192, 'DarkSeaGreen1': 193, 'Honeydew2': 194, 'LightCyan1': 195, 'Red1': 196, 'DeepPink2': 197, 'DeepPink1': 198, 'DeepPink1': 199, 'Magenta2': 200, 'Magenta1': 201, 'OrangeRed1': 202, 'IndianRed1': 203, 'IndianRed1': 204, 'HotPink': 205, 'HotPink': 206, 'MediumOrchid1': 207, 'DarkOrange': 208, 'Salmon1': 209, 'LightCoral': 210, 'PaleVioletRed1': 211, 'Orchid2': 212, 'Orchid1': 213, 'Orange1': 214, 'SandyBrown': 215, 'LightSalmon1': 216, 'LightPink1': 217, 'Pink1': 218, 'Plum1': 219, 'Gold1': 220, 'LightGoldenrod2-2': 221, 'LightGoldenrod2-3': 222, 'NavajoWhite1': 223, 'MistyRose1': 224, 'Thistle1': 225, 'Yellow1': 226, 'LightGoldenrod1': 227, 'Khaki1': 228, 'Wheat1': 229, 'Cornsilk1': 230, 'Grey100': 231, 'Grey3': 232, 'Grey7': 233, 'Grey11': 234, 'Grey15': 235, 'Grey19': 236, 'Grey23': 237, 'Grey27': 238, 'Grey30': 239, 'Grey35': 240, 'Grey39': 241, 'Grey42': 242, 'Grey46': 243, 'Grey50': 244, 'Grey54': 245, 'Grey58': 246, 'Grey62': 247, 'Grey66': 248, 'Grey70': 249, 'Grey74': 250, 'Grey78': 251, 'Grey82': 252, 'Grey85': 253, 'Grey89': 254, 'Grey93': 255, }
        # I'm sure there is a better way to do this, but I got tired of looking.
        self.glyphs = { 'blocks':
                            {
                             'block': "█",      # 
                             'block_hu': "▀",   # half up
                             'block_hd': "▄",   # half down
                             'block_hl': "▌",   # half left
                             'block_hr': "▐",   # half right
                             'block_qul': "▘",  # quarter upper left
                             'block_qur': "▝",  # quarter upper right
                             'block_qll;': "▖", # quarter lower left
                             'block_qlr': "▗",  # quarter lower right
                             },
                        'lines':
                           {'light':
                                {'line_h': "─",
                                 'line_hdd': "╌",
                                 'line_hdt': "┄",
                                 'line_hl': "╴",
                                 'line_hr': "╶",
                                 'line_v': "│",
                                 'line_vdd': "╎",
                                 'line_vdt': "┆",
                                 'line_vl': "╷",
                                 'line_vu': "╵",
                                 'corner_ul': "┌",
                                 'corner_ur': "┐",
                                 'corner_ll': "└",
                                 'corner_lr': "┘",
                                },
                            'heavy': 
                                {'line_h': "━",     # horizontal
                                 'line_hdd': "╍",   # horizontal dash double
                                 'line_hdt': "┅",   # horizontal dash triple
                                 'line_hl': "╸",    # horizontal left
                                 'line_hr': "╺",    # horizontal right
                                 'line_v': "┃",     # vertical
                                 'line_vdd': "╏",   # vertical dash double
                                 'line_vdt': "┇",   # vertical dash triple
                                 'line_vu': "╹",    # vertical upper
                                 'line_vl': "╻",    # vertical lower
                                 'corner_ul': "┏",  # corner upper left
                                 'corner_ur': "┓",  # corner upper right
                                 'corner_ll': "┗",  # corner lower left
                                 'corner_lr': "┛",  # corner lower right
                                },
                           'double':
                                {'line_h': "═",
                                 'line_v': "║",
                                 'corner_ul': "╔",
                                 'corner_ur': "╗",
                                 'corner_ll': "╚",
                                 'corner_lr': "╝",
                                },
                            },
                        }


        # Initialize curses stuff
        self.stdscr = curses.initscr()   # Return a window object representing the entire screen
        self.stdscr.keypad(True)         # Accept multibyte special keys (eg., curses.KEY_LEFT)
        self.stdscr.nodelay(True)        # Don't block waiting for input (must then block manually in a while loop)
        curses.cbreak()                  # Accept keypresses without having to hit enter
        curses.noecho()                  # Don't automatically echo keypresses to screen
        curses.curs_set(0)               # Hide the cursor
        curses.start_color()             # Initialize color

        self.color_default_fg =     self.palette256['Grey']
        self.color_default_bg =     self.palette256['Black']
        self.color_title_fg =       self.palette256['White']
        self.color_title_bg =       self.palette256['Grey']
        self.color_status_fg =      self.palette256['Grey74']
        self.color_status_bg =      self.palette256['Grey23']

        curses.init_pair(1,  self.color_default_fg,    self.color_default_bg)
        curses.init_pair(2,  self.color_title_fg,      self.color_title_bg)
        curses.init_pair(3,  self.color_status_fg,     self.color_status_bg)

        # A dict, so we can call colors by name
        self.cp = { 'default':       curses.color_pair(1),
                    'title':         curses.color_pair(2),
                    'status':        curses.color_pair(3),
                  }
        #####################################################################
        ## Begin Speech-specific stuff

        self.blockInfo_str = ""
        self.blockPrev_str = ""
        self.blockVars_str = ""
        self.trialInfo_str = ""
        self.blockCurr_str = ""
        self.expVars_str = ""
        self.blockInfo_lbl = "Block Info"
        self.blockPrev_lbl = "Previous Block"
        self.blockVars_lbl = "Block Variables"
        self.trialInfo_lbl = "Trial Info"
        self.blockCurr_lbl = "Current Block"
        self.expVars_lbl = "Experiment Variables"
        self.playing_str = " Playback "
        self.playing_show = False
        self.clock_str = "09:45:52"
        self.trialInfo_fmt_allcaps = curses.A_BOLD | curses.A_UNDERLINE

        curses.init_pair(4, self.palette256['White'], self.palette256['Black']) # Used for the playback win
        curses.init_pair(5, self.palette256['Grey'],  self.palette256['Black']) # Used for the playback win
        curses.init_pair(6, self.palette256['White'], self.palette256['Maroon']) # Used for the playback win
        curses.init_pair(7, self.palette256['Maroon'], self.palette256['Black']) # Used for the playback win

        self.white_cp = curses.color_pair(4)
        self.grey_cp = curses.color_pair(5)
        self.playing_cp = curses.color_pair(6)
        self.playing_edge_cp = curses.color_pair(7)

        # One feature is to highlight and underline words in all caps. If any of these chars are found in a word, do not highlight.
        self.allcaps_skip=list("`1234567890-=[]\\;',./'~!@#$%^&*()_+{}|:\"<>?")

        self.clock_timer = self.RepeatTimer(1, self.clock_callback)
        self.clock_timer.start()
 
        self.redraw()

    class RepeatTimer(threading.Timer):
        """A subclass of threading.timer that fires recursively

            Canceled with RepeatTimer.cancel()
        """
        def run(self):
            while not self.finished.wait(self.interval):
                self.function(*self.args, **self.kwargs)

    def clock_callback(self):
        self.clock_str = time.strftime("%T")
        self.stdscr.addstr(3,self.clock_x, self.clock_str, self.white_cp)

    def destroy(self):
        self.clock_timer.cancel()
        self.stdscr.nodelay(False)
        self.stdscr.keypad(False)
        curses.curs_set(1)
        curses.echo()
        curses.nocbreak()
        curses.endwin()


    def redraw(self):
        """Draw entire window

            Called when term is resized, or manually by user

        """
        self.win_height,self.win_width = self.stdscr.getmaxyx()
        
        glyph_blocks = self.glyphs['blocks']

        self.stdscr.erase()

        y = 2

        # Draw playing
        len_playing = len(self.playing_str)
        playing_x = self.win_width - 2 - len_playing
        if self.playing_show:
            self.stdscr.addstr(y,   playing_x, self.glyphs['blocks']['block_hd'] * len(self.playing_str), self.playing_edge_cp)
            self.stdscr.addstr(y+2, playing_x, self.glyphs['blocks']['block_hu'] * len(self.playing_str), self.playing_edge_cp)
            self.stdscr.addstr(y+1, playing_x, self.playing_str,                                          self.playing_cp | curses.A_BOLD)

        # Draw clock
        self.clock_x = playing_x - len(self.clock_str) - 1
        self.clock_callback()

        # Draw block info
        this_x = 1 #len_clock + 3 # Account for clock
        w = self.clock_x - this_x - 2
        h = 1
        self.rectangle(self.stdscr, y, this_x, y+2, this_x+w, self.grey_cp)
        self.stdscr.addstr(y, this_x+1, self.blockInfo_lbl[:w-2], self.grey_cp)
        self.stdscr.addstr(y+1, this_x+2, self.blockInfo_str[:w-2], self.white_cp)

        # Draw trial info
        this_x = 1
        w = self.win_width - 2
        y = y + 3
        h = 4
        self.rectangle(self.stdscr, y, this_x, y + h-1, this_x + w-1, self.grey_cp)
        self.stdscr.addstr(y, this_x+1, self.trialInfo_lbl[:w-2], self.grey_cp)
        
        this_y = y
        for line in self.trialInfo_str.split("\n"):

            this_line = line[:w-3]
            if self.trialInfo_fmt_allcaps is not None: # Apply format to words that are all caps
                if this_line and this_line[-1] in ['?', '.', '!']: # Strip off any string-final punctuation
                    punc = this_line[-1]
                    st = this_line[0:-1]
                else:
                    punc = None
                    st = this_line
                words = st.split()
                word_x = 0
                for word in words:
                    if word.upper() == word and not any(c in word for c in self.allcaps_skip):
                        self.stdscr.addstr(this_y+1, this_x+2+word_x, word, self.trialInfo_fmt_allcaps)
                    else:
                        self.stdscr.addstr(this_y+1, this_x+2+word_x, word)
                    word_x += len(word)+1 # +1 for the space
                if punc:
                    self.stdscr.addstr(this_y+1, this_x+2+word_x-1, punc)
            else:
                self.stdscr.addstr(this_y+1, this_x+2, line[:w-2], self.white_cp)
            this_y += 1

        # Draw trial score
        y = y + h
        this_x = 1
        h = 4
        w = (self.win_width // 2) - (self.win_width % 2) - 2
        self.rectangle(self.stdscr, y, this_x, y + h-1, this_x + w, self.grey_cp)
        self.stdscr.addstr(y, this_x + 1, self.blockCurr_lbl[:w-2], self.grey_cp)
        this_y = y
        for line in self.blockCurr_str.split("\n"):
            self.stdscr.addstr(this_y+1, this_x+2, line[:w-2], self.white_cp)
            this_y += 1

        # Draw block score
        this_x = (self.win_width // 2) - (self.win_width % 2)
        self.rectangle(self.stdscr, y, this_x, y + h-1, self.win_width - 2, self.grey_cp)
        self.stdscr.addstr(y, this_x + 1, self.blockPrev_lbl[:w-2], self.grey_cp)
        this_y = y
        for line in self.blockPrev_str.split("\n"):
            self.stdscr.addstr(this_y+1, this_x+2, line[:w-2], self.white_cp)
            this_y += 1

        # Draw block vars
        y = y + h
        this_x = 1
        h = self.win_height - y - 2
        w = (self.win_width // 2) - (self.win_width % 2) - 2
        self.rectangle(self.stdscr, y, this_x, y + h, this_x + w, self.grey_cp)
        self.stdscr.addstr(y, this_x + 1, self.blockVars_lbl[:w-2], self.grey_cp)
        this_y = y
        for line in self.blockVars_str.split("\n"):
            self.stdscr.addstr(this_y+1, this_x+2, line[:w-2], self.white_cp)
            this_y += 1

        # Draw experiment vars
        this_x = (self.win_width // 2) - (self.win_width % 2)
        self.rectangle(self.stdscr, y, this_x, y + h, self.win_width - 2, self.grey_cp)
        self.stdscr.addstr(y, this_x + 1, self.expVars_lbl[:w-2], self.grey_cp)
        this_y = y
        for line in self.expVars_str.split("\n"):
            self.stdscr.addstr(this_y+1, this_x+2, line[:w-2], self.white_cp)
            this_y += 1

        # Border
        self.stdscr.attron(self.grey_cp)
        self.stdscr.box()
        self.stdscr.attroff(self.grey_cp)

        # Title bar
        self.stdscr.addstr(0, 1, " " * (self.win_width-2), self.cp['title'])
        if self.title_l_str:
            self.stdscr.addstr(0, 1, self.title_l_str, curses.A_BOLD | self.cp['title'])
        if self.title_c_str:
            x = int((self.win_width // 2) - (len(self.title_c_str) // 2) - len(self.title_c_str) % 2) -1
            self.stdscr.addstr(0, x, self.title_c_str, curses.A_BOLD | self.cp['title'])
        if self.title_r_str:
            x = self.win_width - len(self.title_r_str) - 1
            self.stdscr.addstr(0, x, self.title_r_str, curses.A_BOLD | self.cp['title'])

        # Status bar
        self.stdscr.addstr(self.win_height-1, 1, " " * (self.win_width-2), self.cp['status'])
        if self.status_l_str:
            self.stdscr.addstr(self.win_height-1, 1, self.status_l_str, self.cp['status'])
        if self.status_c_str:
            x = int((self.win_width // 2) - (len(self.status_c_str) // 2) - len(self.status_c_str) % 2) -1
            self.stdscr.addstr(self.win_height-1, x, self.status_c_str, self.cp['status'])
        if self.status_r_str:
            x = self.win_width - len(self.status_r_str) - 1
            self.stdscr.addstr(self.win_height-1, x, self.status_r_str, self.cp['status'])


        self.stdscr.refresh()


    def rectangle(self, win, uly, ulx, lry, lrx, cp):
        """Draw a rectangle with corners at the provided upper-left
            and lower-right coordinates.

            https://stackoverflow.com/questions/52804155/extending-curses-rectangle-box-to-edge-of-terminal-in-python
        """
        win.attron(cp)
        win.vline(uly+1, ulx, curses.ACS_VLINE, lry - uly - 1)
        win.hline(uly, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
        win.hline(lry, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
        win.vline(uly+1, lrx, curses.ACS_VLINE, lry - uly - 1)
        win.addch(uly, ulx, curses.ACS_ULCORNER)
        win.addch(uly, lrx, curses.ACS_URCORNER)
        win.addch(lry, lrx, curses.ACS_LRCORNER)
        win.addch(lry, ulx, curses.ACS_LLCORNER)
        win.attroff(cp)


    def round_to(self, x, base):
        """Rounds x to the nearest base, which can be any float
        """
        recip = 1/float(base)
        return round(x * recip) / recip


    #########################################################################
    ## USER FACING FUNCTIONS BELOW

    def get_resp(self, timeout=None):
        """Wait modally for a keypress, returns the key as a char. 
            If you want to evaluate arrow keys etc, use ord:

                ret = get_resp()
                if ord(ret) == curses.KEY_LEFT:
                    # do something to the left

            If timeout is None, then block. If it is a float, wait at 
            least that many seconds, return None if no input.
        """

        try:
            key = curses.ERR
            waiting = True
            timeout_start = time.time()
            # Debugging:
            #loops = 0
            self.stdscr.timeout(10)
            curses.flushinp()
            while waiting:
                key = self.stdscr.getch()
                if key == curses.ERR: # Default wait response from curses; keep waiting
                    if (timeout is not None) and (time.time() >= timeout_start + timeout):
                        ret = None
                        waiting = False
                    time.sleep(self.keypress_wait) # Avoid cpu race while looping
                elif key == curses.KEY_RESIZE:
                    self.redraw()
                else:
                    # Something else: return key as char and let user evaluate
                    ret = chr(key)
                    waiting = False
                #loops += 1
                #self.update_Title_Left("Interface Loops: {:}".format(loops), redraw=True)
            return ret

        except:
            self.destroy()
            raise Exception("Error getting input")
    
    def update_Title_Left(self, s, redraw=False):
        """Update the text on the left side of the title bar

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.title_l_str = s
        if redraw: 
            self.redraw()

    def update_Title_Center(self, s, redraw=False):
        """Update the text in the center of the title bar

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.title_c_str = s
        if redraw: 
            self.redraw()

    def update_Title_Right(self, s, redraw=False):
        """Update the text on the right side of the title bar

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.title_r_str = s
        if redraw: 
            self.redraw()

    # def update_Notify_Left(self, s, show=None, redraw=False):
    #     """Update the notify text to the left of the face.

    #         show is a bool specifying whether to show the text,
    #         set to None to leave this param unchanged [default].
    #         show can also be set with show_Notify_Left.

    #         redraw is a bool specifying whether to redraw window. 
    #         A window redraw can also be set with update.
    #     """
    #     self.notify_l_str = s
    #     if show is not None:
    #         self.notify_l_show = show
    #     if redraw: 
    #         self.redraw()

    # def update_Notify_Right(self, s, show=None, redraw=False):
    #     """Update the notify text to the left of the face.

    #         show is a bool specifying whether to show the text,
    #         set to None to leave this param unchanged [default].
    #         show can also be set with show_Notify_Left.

    #         redraw is a bool specifying whether to redraw window. 
    #         A window redraw can also be set with update.
    #     """
    #     self.notify_r_str = s
    #     if show is not None:
    #         self.notify_r_show = show
    #     if redraw: 
    #         self.redraw()

    # def show_Notify_Left(self, show=None, redraw=True):
    #     """Show the left notify text

    #         If show==None, toggle. Otherwise show should be a bool.

    #         redraw is a bool specifying whether to redraw window. 
    #         A window redraw can also be set with update.
    #     """        
    #     if show is not None:
    #         self.notify_l_show = show
    #     else:
    #         self.notify_l_show = not self.notify_l_show

    #     if redraw: 
    #         self.redraw()

    # def show_Notify_Right(self, show=None, redraw=True):
    #     """Show the right notify text

    #         If show==None, toggle. Otherwise show should be a bool.

    #         redraw is a bool specifying whether to redraw window. 
    #         A window redraw can also be set with update.
    #     """        

    #     if show is not None:
    #         self.notify_r_show = show
    #     else:
    #         self.notify_r_show = not self.notify_r_show

    #     if redraw: 
    #         self.redraw()

    def update_Status_Left(self, s, redraw=False):
        """Update the text on the left side of the status bar

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.status_l_str = s
        if redraw: 
            self.redraw()

    def update_Status_Center(self, s, redraw=False):
        """Update the text in the center of the status bar

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.status_c_str = s
        if redraw: 
            self.redraw()

    def update_Status_Right(self, s, redraw=False):
        """Update the text on the right side of the status bar

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.status_r_str = s
        if redraw: 
            self.redraw()

    def update(self):
        self.redraw()

    ## Speech-specific user functions

    def update_Playing(self, s, show=True, redraw=False):
        """Update the text of the 'playing' prompt

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.playing_str = s
        self.playing_show = show

        if redraw: 
            self.redraw()


    def show_Playing(self, show=None, redraw=True):
        """Show the playing prompt

           If show==None, toggle show and force a redraw. Otherwise 
            show should be a bool.

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """        
        if show is not None:
            self.playing_show = show
            self.redraw()
        else:
            self.playing_show = not self.playing_show
            if redraw: 
                self.redraw()

    def update_Block_Info(self, s, redraw=False):
        """Update the Block Info text

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.blockInfo_str = s
        if redraw: 
            self.redraw()

    def update_Block_Prev(self, s, redraw=False):
        """Update the Block Score text

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.blockPrev_str = s
        if redraw: 
            self.redraw()

    def update_Block_Vars(self, s, redraw=False):
        """Update the Block Variables text

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.blockVars_str = s
        if redraw: 
            self.redraw()

    def update_Trial_Info(self, s, redraw=False):
        """Update the Trial_Info text

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.trialInfo_str = s
        if redraw: 
            self.redraw()

    def update_Block_Curr(self, s, redraw=False):
        """Update the Trial Score text

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.blockCurr_str = s
        if redraw: 
            self.redraw()

    def update_Exp_Vars(self, s, redraw=False):
        """Update the Experiment Variables text

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.expVars_str = s
        if redraw: 
            self.redraw()


if __name__ == "__main__":

    data = []
    # Initialize the interface
    interface = Interface()
    # Sentence info to display for the experimenter; filename, keywords possible, text
    # By default, All-caps words will be bold and underlined in the trialInfo win
    sentences = [
                ("AW001.WAV", "5", "The BIRCH CANOE SLID on the SMOOTH PLANKS."),
                ("AW002.WAV", "5", "GLUE the SHEET to the DARK BLUE BACKGROUND."),
                ("AW003.WAV", "5", "ITS EASY to TELL the DEPTH of a WELL."),
                ]
    # A list of responses to accept. 
    responses = list("012345") # There are 5 possible keywords in each sentence, so accept keys 0-5
    # Add some info to the interface
    interface.update_Title_Right("Subject {:}".format(500))
    interface.update_Title_Center("A speech experiment")
    interface.update_Status_Right("Block 1 of 1")
    interface.update_Block_Vars("SNR: 6\nTarget: CUNY_F1\nMasker: IEEE_F1")
    interface.update_Exp_Vars("Conditions: 1,2,3,4,5,6,7,8,9\nRecord data: yes")
    interface.update_Status_Center("Hit any key to begin", redraw=True)
    interface.update_Block_Info("Condition 1, Block 1 of 24")

    # Wait modally for any keypress to start. If 'q' then quit
    ret = interface.get_resp()
    interface.update_Status_Center("", redraw=True)
    if not ret in ['q', '/']: 
        run = True # run goes to false when user hits q, or trial == trials
        trial = 1  # The current trial
        trials = 3 # The total number of trials for the block
        kwc_t = 0  # Holds keywords correct for a trial
        kwp_t = 0  # Holds keywords possible for a trial
        kwc_b = 0  # Holds keywords correct for a block
        kwp_b = 0  # Holds keywords possible for a block
        while run:
            kwp_t = int(sentences[trial-1][1]) # Get the number of keywords possible for this trial
            kwp_b += kwp_t                     # Add it to keywords possible for the block
            interface.update_Status_Center("Trial {:} of {:}".format(trial, trials)) # Update trial number info
            trialInfo = "Trial {:} of {:} | {}; KW: {}\n{}".format(trial, trials, *sentences[trial-1])             # Build Trial info
            interface.update_Trial_Info(trialInfo, redraw=True)                  # Display trial info
            interface.show_Playing(True)  # Turn on 'Playback' display, simulating stimulus presentation
            time.sleep(2)                # Stimulus presentation would be here
            interface.show_Playing(False) # Turn off 'Playback'
            #interface.update_Status("Enter # or q to Quit") # Prompt user that we are waiting for input
            waiting = True # Waiting goes false when we get a good keypress (either q or a valid response)
            while waiting:
                key = interface.get_resp() # Wait modally for keypress
                if key in ['q', '/']: # If q, then quit. Break out of both the waiting loop, and the run loop
                    waiting = False
                    run = False
                elif key in responses:   # If it is a valid key (ie, found in responses), process
                        data.append(key) # Add it to list
                        kwc_t = int(key) # Grab it for display
                        kwc_b += kwc_t   # Add it to total keywords for the block
                        waiting = False  # We got a valid keypress, so exit waiting loop
                        if trial == trials: # If this was the last trial, exit run loop
                            run = False
            # Update score information
            interface.update_Block_Curr("Previous Trial: {}/{} ({:}%)\nThis Block: {}/{} ({:}%)".format(kwc_t, kwp_t, int((float(kwc_t) / kwp_t)*100),
                                                                                                     kwc_b, kwp_b, int((float(kwc_b) / kwp_b)*100)
                                                                                                    ))
            trial += 1
    interface.clock_timer.cancel()
    interface.show_Playing(True)
    interface.get_resp()

    interface.update_Status_Center("Experiment completed")
    interface.update_Status_Left("Hit any key to quit", redraw=True)
    ret = interface.get_resp()
    # We are done, clean up interface
    interface.destroy()
    # Do something with the data
    print("Responses: {:}".format(data))

