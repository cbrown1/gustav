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

""" This form is intended to be useful for running lateralization experiments, 
    in which a subject indicates a lateral position inside the head by moving 
    a marker along a position bar. There is also a diffuseness parameter as 
    well, which draws a colored area in the position bar that is centered on 
    the marker. 

    Because this is a curses interface, a screenshot can be pasted right here in 
    the text, alas without color:

┌Title Bar Left                          Title Bar Center                           Title Bar Right┐
│                                                                                                  │
│                                   ▄▄▄▄▀▀▀▀▀▀▀▀▀╏▀▀▀▀▀▀▀▀▀▄▄▄▄                                    │
│                             ▄▄▄▀▀▀             ╏             ▀▀▀▄▄▄                              │
│ Left Notify Area        ▄▄▀▀            ▄▄▄████╏████▄▄▄            ▀▀▄▄        Right Notify Area │
│   is centered         ▄▀            ▄▄█████████╏█████████▄▄            ▀▄         is centered    │
│  and Multi-line  ┌───────█───────────────────────────────────────────────────┐   and Multi-line  │
│                  └───────█───────────────────────────────────────────────────┘                   │
│                    ▞       ▗███████████████████╏███████████████████▖       ▚                     │
│                    ▌      ▗████████████████████╏████████████████████▖      ▐                     │
│                   ▞  ╭──╮███████████▛▘  ▝▜█████╏█████▛▘  ▝▜███████████╭──╮  ▚                    │
│                   ▌┌─┤  │███████████      █████╏█████      ███████████│  ├─┐▐                    │
│                  ▐ │ │  │███████████      █████╏█████      ███████████│  │ │ ▌                   │
│                  ▐┌┤ │  │███████████▙    ▟█████╏█████▙    ▟███████████│  │ ├┐▌                   │
│                  ▐││ │  │██████████████████████╏██████████████████████│  │ ││▌                   │
│                  ▐││ │  │██████████████████████╏██████████████████████│  │ ││▌                   │
│                   └┤ │  │██████████████████████╏██████████████████████│  │ ├┘                    │
│                    │ │  │███  ▀████████████████╏████████████████▀  ███│  │ │                     │
│                    └─┤  │███    ▀██████████████╏██████████████▀    ███│  ├─┘                     │
│                      ╰──╯███▄     ▀▀▀██████████╏██████████▀▀▀     ▄███╰──╯                       │
│                           ███▄          ▀▀▀████╏████▀▀▀          ▄███                            │
│                            ████▄               ╏               ▄████                             │
│                             ▝████▄             ╏             ▄████▘                              │
│                               ▝█████▄▄         ╏         ▄▄█████▘                                │
│                                  ▝▀█████▄▄▄▄   ╏   ▄▄▄▄█████▀▘                                   │
│                                      ▀▀████████╏████████▀▀                                       │
│                                                                                                  │
└Status Bar Left                        Status Bar Center                          Status Bar Right┘

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

        env TERM=xterm-256color python3 lateralization.py

    It is working well on python 3.x. Much of the rendering is based on unicode 
    which is a mess in py2, and since py2 has reached end-of-life, not much work
    has gone into it...

    You can demo the interface by running it. In the demo, arrow keys will 
    control the marker and diffuse area, and some basic functionality is shown 
    off. 

    Consider using a joystick as input. A two-joystick gamepad will allow 
    independent and intuitive control over marker and diffuse areas. If you 
    are on linux, the gamepad package works very well to do this:

        https://github.com/cbrown1/gamepad

"""

#from __future__ import unicode_literals
import os, sys
import curses
import time
import math

class Interface():
    def __init__(self):
        # Initialize text areas
        self.title_l_str = "Gustav Lat!"
        self.title_c_str = ""
        self.title_r_str = ""
        self.notify_l_str = ""
        self.notify_l_show = False
        self.notify_r_str = ""
        self.notify_r_show = False
        self.notify_pad = True
        self.notify_offset_v = 2                # Vertical offset of notifications from top of window
        self.status_l_str = ""
        self.status_c_str = "Press '/' to quit"
        self.status_r_str = ""

        self.keypress_wait = .005 # Sleep time in sec during keypress loop to avoid cpu race
                                  # Longer values are better for slower machines

        # Some stuff for rendering
        # Dict so you can specify colors in curses using standard xterm 256-color palette names.
        self.palette256 = {'Black': 0, 'Maroon': 1, 'Green': 2, 'Olive': 3, 'Navy': 4, 'Purple': 5, 'Teal': 6, 'Silver': 7, 'Grey': 8, 'Red': 9, 'Lime': 10, 'Yellow': 11, 'Blue': 12, 'Fuchsia': 13, 'Aqua': 14, 'White': 15, 'Grey0': 16, 'NavyBlue': 17, 'DarkBlue': 18, 'Blue3': 19, 'Blue3': 20, 'Blue1': 21, 'DarkGreen': 22, 'DeepSkyBlue4': 23, 'DeepSkyBlue4': 24, 'DeepSkyBlue4': 25, 'DodgerBlue3': 26, 'DodgerBlue2': 27, 'Green4': 28, 'SpringGreen4': 29, 'Turquoise4': 30, 'DeepSkyBlue3': 31, 'DeepSkyBlue3': 32, 'DodgerBlue1': 33, 'Green3': 34, 'SpringGreen3': 35, 'DarkCyan': 36, 'LightSeaGreen': 37, 'DeepSkyBlue2': 38, 'DeepSkyBlue1': 39, 'Green3': 40, 'SpringGreen3': 41, 'SpringGreen2': 42, 'Cyan3': 43, 'DarkTurquoise': 44, 'Turquoise2': 45, 'Green1': 46, 'SpringGreen2': 47, 'SpringGreen1': 48, 'MediumSpringGreen': 49, 'Cyan2': 50, 'Cyan1': 51, 'DarkRed': 52, 'DeepPink4': 53, 'Purple4': 54, 'Purple4': 55, 'Purple3': 56, 'BlueViolet': 57, 'Orange4': 58, 'Grey37': 59, 'MediumPurple4': 60, 'SlateBlue3': 61, 'SlateBlue3': 62, 'RoyalBlue1': 63, 'Chartreuse4': 64, 'DarkSeaGreen4': 65, 'PaleTurquoise4': 66, 'SteelBlue': 67, 'SteelBlue3': 68, 'CornflowerBlue': 69, 'Chartreuse3': 70, 'DarkSeaGreen4': 71, 'CadetBlue': 72, 'CadetBlue': 73, 'SkyBlue3': 74, 'SteelBlue1': 75, 'Chartreuse3': 76, 'PaleGreen3': 77, 'SeaGreen3': 78, 'Aquamarine3': 79, 'MediumTurquoise': 80, 'SteelBlue1': 81, 'Chartreuse2': 82, 'SeaGreen2': 83, 'SeaGreen1': 84, 'SeaGreen1': 85, 'Aquamarine1': 86, 'DarkSlateGray2': 87, 'DarkRed': 88, 'DeepPink4': 89, 'DarkMagenta': 90, 'DarkMagenta': 91, 'DarkViolet': 92, 'Purple': 93, 'Orange4': 94, 'LightPink4': 95, 'Plum4': 96, 'MediumPurple3': 97, 'MediumPurple3': 98, 'SlateBlue1': 99, 'Yellow4': 100, 'Wheat4': 101, 'Grey53': 102, 'LightSlateGrey': 103, 'MediumPurple': 104, 'LightSlateBlue': 105, 'Yellow4': 106, 'DarkOliveGreen3': 107, 'DarkSeaGreen': 108, 'LightSkyBlue3': 109, 'LightSkyBlue3': 110, 'SkyBlue2': 111, 'Chartreuse2': 112, 'DarkOliveGreen3': 113, 'PaleGreen3': 114, 'DarkSeaGreen3': 115, 'DarkSlateGray3': 116, 'SkyBlue1': 117, 'Chartreuse1': 118, 'LightGreen': 119, 'LightGreen': 120, 'PaleGreen1': 121, 'Aquamarine1': 122, 'DarkSlateGray1': 123, 'Red3': 124, 'DeepPink4': 125, 'MediumVioletRed': 126, 'Magenta3': 127, 'DarkViolet': 128, 'Purple': 129, 'DarkOrange3': 130, 'IndianRed': 131, 'HotPink3': 132, 'MediumOrchid3': 133, 'MediumOrchid': 134, 'MediumPurple2': 135, 'DarkGoldenrod': 136, 'LightSalmon3': 137, 'RosyBrown': 138, 'Grey63': 139, 'MediumPurple2': 140, 'MediumPurple1': 141, 'Gold3': 142, 'DarkKhaki': 143, 'NavajoWhite3': 144, 'Grey69': 145, 'LightSteelBlue3': 146, 'LightSteelBlue': 147, 'Yellow3': 148, 'DarkOliveGreen3': 149, 'DarkSeaGreen3': 150, 'DarkSeaGreen2': 151, 'LightCyan3': 152, 'LightSkyBlue1': 153, 'GreenYellow': 154, 'DarkOliveGreen2': 155, 'PaleGreen1': 156, 'DarkSeaGreen2': 157, 'DarkSeaGreen1': 158, 'PaleTurquoise1': 159, 'Red3': 160, 'DeepPink3': 161, 'DeepPink3': 162, 'Magenta3': 163, 'Magenta3': 164, 'Magenta2': 165, 'DarkOrange3': 166, 'IndianRed': 167, 'HotPink3': 168, 'HotPink2': 169, 'Orchid': 170, 'MediumOrchid1': 171, 'Orange3': 172, 'LightSalmon3': 173, 'LightPink3': 174, 'Pink3': 175, 'Plum3': 176, 'Violet': 177, 'Gold3': 178, 'LightGoldenrod3': 179, 'Tan': 180, 'MistyRose3': 181, 'Thistle3': 182, 'Plum2': 183, 'Yellow3': 184, 'Khaki3': 185, 'LightGoldenrod2': 186, 'LightYellow3': 187, 'Grey84': 188, 'LightSteelBlue1': 189, 'Yellow2': 190, 'DarkOliveGreen1': 191, 'DarkOliveGreen1': 192, 'DarkSeaGreen1': 193, 'Honeydew2': 194, 'LightCyan1': 195, 'Red1': 196, 'DeepPink2': 197, 'DeepPink1': 198, 'DeepPink1': 199, 'Magenta2': 200, 'Magenta1': 201, 'OrangeRed1': 202, 'IndianRed1': 203, 'IndianRed1': 204, 'HotPink': 205, 'HotPink': 206, 'MediumOrchid1': 207, 'DarkOrange': 208, 'Salmon1': 209, 'LightCoral': 210, 'PaleVioletRed1': 211, 'Orchid2': 212, 'Orchid1': 213, 'Orange1': 214, 'SandyBrown': 215, 'LightSalmon1': 216, 'LightPink1': 217, 'Pink1': 218, 'Plum1': 219, 'Gold1': 220, 'LightGoldenrod2': 221, 'LightGoldenrod2': 222, 'NavajoWhite1': 223, 'MistyRose1': 224, 'Thistle1': 225, 'Yellow1': 226, 'LightGoldenrod1': 227, 'Khaki1': 228, 'Wheat1': 229, 'Cornsilk1': 230, 'Grey100': 231, 'Grey3': 232, 'Grey7': 233, 'Grey11': 234, 'Grey15': 235, 'Grey19': 236, 'Grey23': 237, 'Grey27': 238, 'Grey30': 239, 'Grey35': 240, 'Grey39': 241, 'Grey42': 242, 'Grey46': 243, 'Grey50': 244, 'Grey54': 245, 'Grey58': 246, 'Grey62': 247, 'Grey66': 248, 'Grey70': 249, 'Grey74': 250, 'Grey78': 251, 'Grey82': 252, 'Grey85': 253, 'Grey89': 254, 'Grey93': 255, }
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
                            {'heavy': 
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
                           'light':
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
        # When drawing lines, use either 'heavy' or 'light' weight (see above)
        self.line_weight = 'heavy'

        # Initialize curses stuff
        self.stdscr = curses.initscr()   # Return a window object representing the entire screen
        self.stdscr.keypad(True)         # Accept multibyte special keys (eg., curses.KEY_LEFT)
        self.stdscr.nodelay(True)        # Don't block waiting for input (must then block manually in a while loop)
        curses.cbreak()                  # Accept keypresses without having to hit enter
        curses.noecho()                  # Don't automatically echo keypresses to screen
        curses.curs_set(0)               # Hide the cursor
        curses.start_color()             # Initialize color

        #####################################################################
        ## Begin lateralization-specific stuff
        self.pos = 0                            # Marker position, 0>=1
        self.diffuse = 0                        # Diffuseness, 0>=1
        self.posbar_show = True                 # Whether to show the position bar
        self.posbar_offset_v = 5                # Vertical offset of position bar from top of face

        self.marker_show = False
        # Diffuse area cannot be interpolated, so it can sometimes become slightly misaligned or asymmetrical
        # relative to marker. To address this, marker_interp has three possible values:
        # 
        # True: Always interpolate marker. Smoother marker movement, but diffuse area may become slightly misaligned
        # False: Never interpolate marker. Marker movement is not quite as smooth, but diffuse area is always aligned
        # None: Only interpolate when diffuse is 0
        self.marker_interp = None

        # Centering line
        self.vline_show = True

        # This face is 24 rows high, which means the interface will look best in a term 
        # with at least 28 rows (titlebar + padding + statusbar + padding)
        self.face = """
                ▄▄▄▄▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▄▄▄▄
          ▄▄▄▀▀▀                         ▀▀▀▄▄▄
       ▄▀▀            ▄▄▄███████▄▄▄            ▀▀▄
     ▄▀           ▄▄█████████████████▄▄           ▀▄
    ▞         ▄▄█████████████████████████▄▄         ▚
   ▞       ▗▄███████████████████████████████▄▖       ▚
  ▞      ▗█████████████████████████████████████▖      ▚
  ▌     ▗███████████████████████████████████████▖     ▐
 ▞  ╭──╮██████████▛▘  ▝▜█████████▛▘  ▝▜██████████╭──╮  ▚
 ▌┌─┤  │██████████      █████████      ██████████│  ├─┐▐
▐ │ │  │██████████      █████████      ██████████│  │ │ ▌
▐┌┤ │  │██████████▙    ▟█████████▙    ▟██████████│  │ ├┐▌
▐││ │  │█████████████████████████████████████████│  │ ││▌
▐││ │  │█████████████████████████████████████████│  │ ││▌
 └┤ │  │█████████████████████████████████████████│  │ ├┘
  │ │  │██  ▀███████████████████████████████▀  ██│  │ │
  └─┤  │██    ▀███████████████████████████▀    ██│  ├─┘
    ╰──╯██▄     ▀▀▀███████████████████▀▀▀     ▄██╰──╯
        ███▄          ▀▀▀███████▀▀▀          ▄███
         ████▄                             ▄████
          ▝████▄                         ▄████▘
            ▝█████▄▄                 ▄▄█████▘
               ▝▀█████▄▄▄▄     ▄▄▄▄█████▀▘
                   ▀▀███████████████▀▀

""" #.encode('utf-8').decode('utf-8')

        self.face_width = 0
        this_face_lines = self.face.strip("\n").split("\n")
        self.face_lines = []
        for line in this_face_lines:
            if len(line)>0:
                self.face_width = max(self.face_width, len(line))
                self.face_lines.append(line)
        self.face_height = len(self.face_lines)

        # Set colors
        self.color_default_fg =     self.palette256['Grey']
        self.color_default_bg =     self.palette256['Black']
        self.color_posbar_fg =      self.palette256['Grey74']
        self.color_posbar_bg =      self.palette256['Black']
        self.color_posbar_marker =  self.palette256['DeepSkyBlue4']
        self.color_posbar_diffuse = self.palette256['DodgerBlue1']
        self.color_title_fg =       self.palette256['White']
        self.color_title_bg =       self.palette256['Grey']
        self.color_status_fg =      self.palette256['Grey74']
        self.color_status_bg =      self.palette256['Grey23']
        self.color_notify_ul_fg =   self.palette256['White']
        self.color_notify_ul_bg =   self.palette256['DarkGreen']
        self.color_notify_ur_fg =   self.palette256['White']
        self.color_notify_ur_bg =   self.palette256['DarkRed']
        self.color_notify_ll_fg =   self.palette256['White']
        self.color_notify_ll_bg =   self.palette256['DarkGreen']
        self.color_notify_lr_fg =   self.palette256['White']
        self.color_notify_lr_bg =   self.palette256['DarkRed']
        self.color_face_fg =        self.palette256['LightGoldenrod1']
        self.color_face_bg =        self.palette256['Black']
        self.color_vline_fg =       self.palette256['White']
        self.color_vline_bg =       self.palette256['Black']

        # Create curses fg/bg color pairs
        curses.init_pair(1, self.color_default_fg,     self.color_default_bg)
        curses.init_pair(2, self.color_title_fg,       self.color_title_bg)
        curses.init_pair(3, self.color_status_fg,      self.color_status_bg)
        curses.init_pair(4, self.color_notify_ul_fg,   self.color_notify_ul_bg)
        curses.init_pair(5, self.color_notify_ur_fg,   self.color_notify_ur_bg)
        curses.init_pair(6, self.color_notify_ul_bg,   self.color_default_bg) # Used for padding
        curses.init_pair(7, self.color_notify_ur_bg,   self.color_default_bg)
        curses.init_pair(8, self.color_notify_ll_fg,   self.color_notify_ll_bg)
        curses.init_pair(9, self.color_notify_lr_fg,   self.color_notify_lr_bg)
        curses.init_pair(10, self.color_notify_ll_bg,   self.color_default_bg)
        curses.init_pair(11, self.color_notify_lr_bg,   self.color_default_bg)
        curses.init_pair(12, self.color_face_fg,        self.color_face_bg)
        curses.init_pair(13, self.color_posbar_fg,      self.color_posbar_bg)
        curses.init_pair(14, self.color_posbar_marker, self.color_posbar_bg)
        curses.init_pair(15, self.color_posbar_marker, self.color_posbar_diffuse)
        curses.init_pair(16, self.color_posbar_fg,     self.color_posbar_diffuse)
        curses.init_pair(17,self.color_vline_fg,       self.color_vline_bg)

        # A dict, so we can call colors by name
        self.cp = { 'default':       curses.color_pair(1),
                    'title':         curses.color_pair(2),
                    'status':        curses.color_pair(3),
                    'notify_ul':     curses.color_pair(4),
                    'notify_ur':     curses.color_pair(5),
                    'notify_ul_pad': curses.color_pair(6),
                    'notify_ur_pad': curses.color_pair(7),
                    'notify_ll':     curses.color_pair(8),
                    'notify_lr':     curses.color_pair(9),
                    'notify_ll_pad': curses.color_pair(10),
                    'notify_lr_pad': curses.color_pair(11),
                    'face':          curses.color_pair(12),
                    'posbar_m-d-':   curses.color_pair(13),
                    'posbar_m+d-':   curses.color_pair(14),
                    'posbar_m+d+':   curses.color_pair(15),
                    'posbar_m-d+':   curses.color_pair(16),
                    'vline':         curses.color_pair(17),
                    }

        self.redraw()


    def destroy(self):
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
        
        glyph_lines = self.glyphs['lines'][self.line_weight]
        glyph_blocks = self.glyphs['blocks']

        # Compute position of face
        if self.win_width > self.face_width:
            # Window is wider than face
            pad_w = int((self.win_width // 2) - (self.face_width // 2) - self.face_width % 2)   # How much window space to skip to center text
            len_w = self.face_width                                                             # How much text can fit in window
            crop_w = 0                                                                          # How much text to skip so it fits
        else:
            # Face is wider than window
            pad_w = 0
            len_w = self.win_width
            crop_w = int((self.face_width // 2) - (self.win_width // 2) - self.face_width % 2)

        # Compute vertical align
        if self.win_height > self.face_height:
            # Window is taller than face
            pad_h = int((self.win_height // 2) - (self.face_height // 2) - self.face_height % 2)
            len_h = self.face_height
            crop_h = 0
        else:
            # Face is taller than window
            pad_h = 0
            len_h = self.win_height
            crop_h = int((self.face_height // 2) - (self.win_height // 2) - (self.face_height % 2))

        self.stdscr.erase()

        # Draw face
        for ii in range(len_h):
            face_line = self.face_lines[crop_h + ii]
            cropped_face_line = face_line[crop_w:crop_w+len_w]
            self.stdscr.addstr(pad_h + ii, pad_w, cropped_face_line.encode("utf-8"), self.cp['face'])
            if self.vline_show:
                self.stdscr.addstr(pad_h + ii, int(self.win_width//2)-1, glyph_lines['line_vdd'], self.cp['vline'])

        # Compute position and dimensions of position bar
        self.posbar_x1 = pad_w+1
        self.posbar_x2 = pad_w+len_w-2
        self.posbar_w = self.posbar_x2 - self.posbar_x1
        self.w_pos_y = pad_h + self.posbar_offset_v

        # Upper Left Notify
        if self.notify_l_show:
            lines = self.notify_l_str.split("\n")
            ii = max(pad_h + self.notify_offset_v, (self.win_height // 10)) # self.notify_offset_v  # Terminal line to start at
            adj = 0                    # used to adjust if any lines are off the terminal window
            w = 0                      # holds the width of the window
            for line in lines:
                # Check if any lines are off window after centering, adjust if they are
                x = int((self.posbar_x1 // 2) - (len(line) // 2) - len(line) % 2)
                adj = min(x, adj)
                w = max(len(line), w)
            if self.notify_pad:
                # Vertical pad with half-down blocks across top of window
                this_line = glyph_blocks['block_hd'] * (w+2)
                x = int((self.posbar_x1 // 2) - (len(this_line) // 2) - len(this_line) % 2) - adj
                x = max(x, 1)
                self.stdscr.addstr(ii, x, this_line, self.cp['notify_ul_pad'])
                # we have padded top, so start text 1 line down
                ii += 1
            for line in lines:
                # Pad shorter lines so window is a nice rectangle
                pad = w - len(line)
                this_line = (" " * (pad // 2)) + line + (" " * ((pad // 2) + (pad % 2)))
                if self.notify_pad:
                    # Horizontal pad with a space at beginning and end of each line
                    this_line = " " + this_line + " "
                x = int((self.posbar_x1 // 2) - (len(this_line) // 2) - len(this_line) % 2) - adj
                x = max(x, 1)
                self.stdscr.addstr(ii, x, this_line, self.cp['notify_ul'] | curses.A_BOLD)
                ii += 1
            if self.notify_pad:
                # Vertical pad with half-up blocks across bottom of window
                this_line = glyph_blocks['block_hu'] * (w+2)
                x = int((self.posbar_x1 // 2) - (len(this_line) // 2) - len(this_line) % 2) - adj
                x = max(x, 1)
                self.stdscr.addstr(ii, x, this_line, self.cp['notify_ul_pad'])

        # Upper Right Notify
        if self.notify_r_show:
            lines = self.notify_r_str.split("\n")
            ii = max(pad_h + self.notify_offset_v, (self.win_height // 10)) # self.notify_offset_v  # Terminal line to start at
            adj = 0
            w = 0
            for line in lines:
                x = (self.posbar_x2+1) + (int(( (self.win_width - self.posbar_x2) // 2) - (len(line) // 2) - len(line) % 2) )
                adj = min(self.win_width - (x + len(line)), adj)
                w = max(len(line), w)
            if self.notify_pad:
                this_line = glyph_blocks['block_hd'] * (w+2)
                x = (self.posbar_x2+1) + (int(( (self.win_width - self.posbar_x2) // 2) - (len(this_line) // 2) - len(this_line) % 2) ) - adj
                x = min(x, self.win_width - len(this_line)-1)
                self.stdscr.addstr(ii, x, this_line, self.cp['notify_ur_pad'])
                ii += 1
            for line in lines:
                pad = w - len(line)
                this_line = (" " * (pad // 2)) + line + (" " * ((pad // 2) + (pad % 2)))
                if self.notify_pad:
                    this_line = " " + this_line + " "
                x = (self.posbar_x2 + 1) + (int(( (self.win_width - self.posbar_x2) // 2) - (len(this_line) // 2) - len(this_line) % 2) ) - adj
                x = min(x, self.win_width-len(this_line)-1)
                self.stdscr.addstr(ii, x, this_line, self.cp['notify_ur'] | curses.A_BOLD)
                ii += 1
            if self.notify_pad:
                this_line = glyph_blocks['block_hu'] * (w+2)
                x = (self.posbar_x2 + 1) + (int(( (self.win_width - self.posbar_x2) // 2) - (len(this_line) // 2) - len(this_line) % 2) ) - adj
                x = min(x, self.win_width - len(this_line) - 1)
                self.stdscr.addstr(ii, x, this_line, self.cp['notify_ur_pad'])

        # Lower left and right notifies are not implemented as they seem a bit overkill

        # Border
        self.stdscr.attron(self.cp['default'])
        self.stdscr.box()
        self.stdscr.attroff(self.cp['default'])

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


        # The position bar and marker
        if self.posbar_show:
            self.stdscr.attron(curses.color_pair(5))
            self.stdscr.addstr(pad_h+self.posbar_offset_v,   self.posbar_x1,   glyph_lines['line_h'] * (self.posbar_w+1), self.cp['posbar_m-d-'])
            self.stdscr.addstr(pad_h+self.posbar_offset_v+1, self.posbar_x1,   glyph_lines['line_h'] * (self.posbar_w+1), self.cp['posbar_m-d-'])
            self.stdscr.addstr(pad_h+self.posbar_offset_v,   self.posbar_x1-1, glyph_lines['corner_ul'],                  self.cp['posbar_m-d-'])
            self.stdscr.addstr(pad_h+self.posbar_offset_v,   self.posbar_x2+1, glyph_lines['corner_ur'],                  self.cp['posbar_m-d-'])
            self.stdscr.addstr(pad_h+self.posbar_offset_v+1, self.posbar_x1-1, glyph_lines['corner_ll'],                  self.cp['posbar_m-d-'])
            self.stdscr.addstr(pad_h+self.posbar_offset_v+1, self.posbar_x2+1, glyph_lines['corner_lr'],                  self.cp['posbar_m-d-'])

            if self.marker_show:
                if self.marker_interp is not None:
                    if self.marker_interp:
                        interp = .5
                    else:
                        interp = 1.
                else:
                    if self.diffuse == 0:
                        interp = .5
                    else:
                        interp = 1.

                # Compute positions
                x = self.round_to(self.posbar_x1 + (self.pos * self.posbar_w), interp)
                x = max(x,self.posbar_x1)
                x = min(x,self.posbar_x2)

                # Diffuse area cannot be interpolated because of limitations with char rendering; specifically, 
                # there is only a fg and a bg, so only 2 things can be rendered in a char position. Here, interp
                # would mean that there would be three things to render in a char position: typical bg, diffuse 
                # bg, and the posbar
                diffuse = self.round_to(int(self.diffuse * self.posbar_w), 1.)
                diffuse_lo = x - diffuse
                diffuse_lo = int(max(diffuse_lo,self.posbar_x1))
                diffuse_lo = int(min(diffuse_lo,self.posbar_x2))

                diffuse_hi = x + diffuse
                diffuse_hi = int(max(diffuse_hi,self.posbar_x1))
                diffuse_hi = int(min(diffuse_hi,self.posbar_x2))
                # Account for marker
                if diffuse > 0: diffuse_hi += 1

                diffuse_w = diffuse_hi-diffuse_lo

                # Draw Diffuse area if present
                if diffuse > 0: 
                    # There is diffuse area. draw it, and assign marker colors: +marker, +diffuse
                    self.stdscr.addstr(pad_h+self.posbar_offset_v,   diffuse_lo, glyph_lines['line_h'] * diffuse_w, self.cp['posbar_m-d+'])
                    self.stdscr.addstr(pad_h+self.posbar_offset_v+1, diffuse_lo, glyph_lines['line_h'] * diffuse_w, self.cp['posbar_m-d+'])
                    # Marker will be drawn on top of diffuse field, use +Marker +Diffuse
                    marker_fmt = self.cp['posbar_m+d+']
                else:
                    # Marker will not be drawn on top of diffuse field, use +Marker -Diffuse
                    marker_fmt = self.cp['posbar_m+d-']

                # Draw marker
                # Determine whether marker position is a whole number (single-char), or half (two-char)
                this_x = int(math.floor(x)) # Get char position or marker1
                if (interp == 1.) or (x*2 % 2) == 0:
                    # Use whole-char marker
                    self.stdscr.addstr(self.w_pos_y, this_x, glyph_blocks['block'], marker_fmt)
                    self.stdscr.addstr(self.w_pos_y+1, this_x, glyph_blocks['block'], marker_fmt)
                    # When showing the 2-char (interpolated) marker, the horiz lines of the  
                    # pos bar disappear for 1/2 char on either side. Here, we recreate that 
                    # for the 1-char marker, by drawing half horizontal lines on either  
                    # side. Also handle when marker is at either end of pos bar.
                    if (x == self.posbar_x1):
                        edge_lu = glyph_lines['line_vl']
                        edge_ld = glyph_lines['line_vu']
                        edge_ru = glyph_lines['line_hr']
                        edge_rd = glyph_lines['line_hr']
                    elif (x == self.posbar_x2):
                        edge_lu = glyph_lines['line_hl']
                        edge_ld = glyph_lines['line_hl']
                        edge_ru = glyph_lines['line_vl']
                        edge_rd = glyph_lines['line_vu']
                    else: 
                        edge_lu = glyph_lines['line_hl']
                        edge_ld = glyph_lines['line_hl']
                        edge_ru = glyph_lines['line_hr']
                        edge_rd = glyph_lines['line_hr']

                    if (x > self.posbar_x1) and (diffuse_lo < x):
                        # There is diffuse area and marker is not at lower edge. Use diffuse bg
                        self.stdscr.addstr(self.w_pos_y,   this_x-1, edge_lu, self.cp['posbar_m-d+'])
                        self.stdscr.addstr(self.w_pos_y+1, this_x-1, edge_ld, self.cp['posbar_m-d+'])
                    else:
                        # Either no diffuse area or marker is at lower edge. Either way use standard bg
                        self.stdscr.addstr(self.w_pos_y,   this_x-1, edge_lu, self.cp['posbar_m-d-'])
                        self.stdscr.addstr(self.w_pos_y+1, this_x-1, edge_ld, self.cp['posbar_m-d-'])

                    if (x < self.posbar_x2) and (diffuse_hi > x):
                        # There is diffuse area and marker is not at upper edge. Use diffuse bg
                        self.stdscr.addstr(self.w_pos_y,   this_x+1, edge_ru, self.cp['posbar_m-d+'])
                        self.stdscr.addstr(self.w_pos_y+1, this_x+1, edge_rd, self.cp['posbar_m-d+'])
                    else:
                        # Either no diffuse area or marker is at upper edge. Either way use standard bg
                        self.stdscr.addstr(self.w_pos_y,   this_x+1, edge_ru, self.cp['posbar_m-d-'])
                        self.stdscr.addstr(self.w_pos_y+1, this_x+1, edge_rd, self.cp['posbar_m-d-'])
                else:
                    # It is x.5; using half-char markers
                    self.stdscr.addstr(self.w_pos_y,   this_x, glyph_blocks['block_hr'], marker_fmt)
                    self.stdscr.addstr(self.w_pos_y+1, this_x, glyph_blocks['block_hr'], marker_fmt)
                    if this_x+1 <= self.posbar_x2:
                        self.stdscr.addstr(self.w_pos_y,   this_x+1, glyph_blocks['block_hl'], marker_fmt)
                        self.stdscr.addstr(self.w_pos_y+1, this_x+1, glyph_blocks['block_hl'], marker_fmt)

        self.stdscr.refresh()


    def rectangle(self, win, uly, ulx, lry, lrx):
        """Draw a rectangle with corners at the provided upper-left
            and lower-right coordinates.

            This is not used ATM, the rect for the posbar is drawn by hand to 
            allow more control over style

            https://stackoverflow.com/questions/52804155/extending-curses-rectangle-box-to-edge-of-terminal-in-python
        """
        win.vline(uly+1, ulx, curses.ACS_VLINE, lry - uly - 1)
        win.hline(uly, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
        win.hline(lry, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
        win.vline(uly+1, lrx, curses.ACS_VLINE, lry - uly - 1)
        win.addch(uly, ulx, curses.ACS_ULCORNER)
        win.addch(uly, lrx, curses.ACS_URCORNER)
        win.addch(lry, lrx, curses.ACS_LRCORNER)
        win.addch(lry, ulx, curses.ACS_LLCORNER)


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

    def update_Notify_Left(self, s, show=None, redraw=False):
        """Update the notify text to the left of the face.

            show is a bool specifying whether to show the text,
            set to None to leave this param unchanged [default].
            show can also be set with show_Notify_Left.

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.notify_l_str = s
        if show is not None:
            self.notify_l_show = show
        if redraw: 
            self.redraw()

    def update_Notify_Right(self, s, show=None, redraw=False):
        """Update the notify text to the left of the face.

            show is a bool specifying whether to show the text,
            set to None to leave this param unchanged [default].
            show can also be set with show_Notify_Left.

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """
        self.notify_r_str = s
        if show is not None:
            self.notify_r_show = show
        if redraw: 
            self.redraw()

    def show_Notify_Left(self, show=None, redraw=True):
        """Show the left notify text

            If show==None, toggle. Otherwise show should be a bool.

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """        
        if show is not None:
            self.notify_l_show = show
        else:
            self.notify_l_show = not self.notify_l_show

        if redraw: 
            self.redraw()

    def show_Notify_Right(self, show=None, redraw=True):
        """Show the right notify text

            If show==None, toggle. Otherwise show should be a bool.

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """        

        if show is not None:
            self.notify_r_show = show
        else:
            self.notify_r_show = not self.notify_r_show

        if redraw: 
            self.redraw()

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

    ## Lateralization-specific user functions

    def set_marker_pos(self, pos=None, diffuse=None, chars=False, show=None, redraw=True):
        """Draws marker at specified position (0>=1) on the position bar

            pos values between 0 and 1 are converted to char positions, 
            and to improve visual resolution char positions are rounded 
            to the nearest half char (1, 1.5, 2, 2.5, etc). Whole char 
            positions (1., 2., etc) are handled with a single full-block 
            character, half char positions are interpolated with two 
            half-block characters, (eg., for 3.5 a right half-block char
            at 3 and a left half block char at 4).

            diffuse values between 0 and 1 are drawn as sort of error
            bars, between (pos - diffuse) and (pos + diffuse). 

            chars allows positions to be specified in chars, for debugging. 
            Because available char space in the position bar is more-or-less
            arbitrary, this should not be used in production.

            show is a bool indicating whether the marker should be shown.
            Default is None, which leaves the value unchanged.

            redraw is True by default, since it is assumed that when marker 
            position changes, it is desired that its visual representation 
            be updated as well.

        """

        if pos is None:
            if chars:
                pos = self.pos * self.posbar_w
            else:
                pos = self.pos
        if diffuse is None:
            if chars:
                diffuse = self.diffuse * self.posbar_w
            else:
                diffuse = self.diffuse

        if chars:
            self.pos = pos / self.posbar_w
            self.diffuse = diffuse / self.posbar_w
        else:
            self.pos = pos
            self.diffuse = diffuse

        if show is not None:
            self.marker_show = show

        # If marker is shown, then a redraw is assumed, even if it wasn't specified
        if redraw | self.marker_show:
            self.redraw()

    def get_Marker_Pos(self):
        """Return the current marker position, which will be 0<=1.
        """
        return self.pos

    def get_Diffuse_Area(self):
        """Return the current diffuse area, which will be 0<=1.
        """
        return self.diffuse

    def show_Position_Bar(self, show=None, redraw=True):
        """Show the position bar

           If show==None, toggle show and force a redraw. Otherwise 
            show should be a bool.

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """        
        if show is not None:
            self.posbar_show = show
            self.redraw()
        else:
            self.posbar_show = not self.posbar_show
            if redraw: 
                self.redraw()

    def show_Marker(self, show=None, redraw=True):
        """Show the lateral position marker

            If show==None, toggle show and force a redraw. Otherwise 
            show should be a bool.

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """

        if show is not None:
            self.marker_show = show
            self.redraw()
        else:
            self.marker_show = not self.marker_show
            if redraw: 
                self.redraw()

    def show_VLine(self, show=None, redraw=True):
        """Show the vertical line indicating the midsagittal plane

            If show==None, toggle show and force a redraw. Otherwise 
            show should be a bool.

            redraw is a bool specifying whether to redraw window. 
            A window redraw can also be set with update.
        """

        if show is not None:
            self.vline_show = show
            self.redraw()
        else:
            self.vline_show = not self.vline_show
            if redraw: 
                self.redraw()


if __name__ == "__main__":

    # Initialize interface
    interface = Interface()
    # Add some text
    interface.update_Notify_Right("Press any key\nto begin", show=True, redraw=True)
    # Get width of position bar. * 2 because steps are .5 chars
    n = interface.posbar_w * 2. 
    # Wait for a keypress
    ret = interface.get_resp()

    # Update some text, show marker
    interface.show_Notify_Left(False)
    interface.update_Title_Center( "Left / right to move cursor")
    interface.update_Title_Right(  "Up / dn to change diffuse field")
    interface.update_Status_Left(  "Press '/' to quit")
    interface.update_Status_Center("Position: 0/{:}".format(int(n)))
    interface.update_Status_Right( "Diffuse: 0/{:}".format(int(n)))
    interface.update_Notify_Left(  "Press 'r' to\ntoggle right\nnotify", show=True)
    interface.update_Notify_Right( "And hit 'l'\nto toggle\nleft notify", show=False)
    interface.show_Marker(True, redraw=True)

    # Enter a blocking loop waiting for keypresses
    x = 0.
    y = 0.
    # Debugging:
    #loops = 0
    waiting = True
    while waiting:
        key = interface.get_resp(timeout=1.) # Wait for keypress
        # If you set a timeout for get_resp, you need to hand key==None, which is a wait
        if key == None:
            # Nothing happened, keep waiting
            #loops += 1
            #interface.update_Title_Center("Main Loops: {:}".format(int(loops)), redraw=True)
            pass
        elif key in ('/', 'q'):
            # User requested to quit. Exit while loop
            waiting = False
        elif key == 'p':
            interface.show_Position_Bar()
        elif key == 'm':
            interface.show_Marker()
        elif key == 'l':
            interface.show_Notify_Left()
        elif key == 'r':
            interface.show_Notify_Right()
        elif key == 'v':
            interface.show_VLine()
        elif key == 'w':
            if interface.line_weight == 'heavy':
                interface.line_weight = 'light'
            else:
                interface.line_weight = 'heavy'
            interface.redraw()
        elif key == 'i':
            if interface.marker_interp:
                interface.marker_interp = False
            else:
                interface.marker_interp = True
            interface.update_Status_Right("Marker interp: {:}".format(interface.marker_interp), redraw=True)
        elif ord(key) == curses.KEY_LEFT:
            # Move marker to the left
            x = max(x-1, 0)
            interface.update_Status_Center("Position: {:}/{:}".format(int(x),int(n)))
            interface.set_marker_pos(x/n)
        elif ord(key) == curses.KEY_RIGHT:
            # Move marker to the right
            x = min(x+1, n)
            interface.update_Status_Center("Position: {:}/{:}".format(int(x),int(n)))
            interface.set_marker_pos(x/n)
        elif ord(key) == curses.KEY_UP:
            # Increase diffuse field
            y = min(y+1, n)
            interface.update_Status_Right("Diffuse: {:}/{:}".format(int(y),int(n)))
            interface.set_marker_pos(diffuse=y/n)
        elif ord(key) == curses.KEY_DOWN:
            # Decrease diffuse field
            y = max(y-1, 0)
            interface.update_Status_Right("Diffuse: {:}/{:}".format(int(y),int(n)))
            interface.set_marker_pos(diffuse=y/n)

    # We are quitting. Let use know, and wait for final keypress to exit interface
    interface.update_Status_Left("")
    interface.update_Notify_Left("Finished.\nPress any key\nto exit...", show=True)
    interface.show_Notify_Right(False)
    interface.show_Marker(False, redraw=True)
    ret = interface.get_resp()

    # # Screenshot layout:
    # interface.update_Status_Left("Status Bar Left")
    # interface.update_Status_Center("Status Bar Center")
    # interface.update_Status_Right("Status Bar Right")

    # interface.update_Title_Left("Title Bar Left")
    # interface.update_Title_Center("Title Bar Center")
    # interface.update_Title_Right("Title Bar Right")

    # interface.update_Notify_Left("Left Notify Area\nis centered\nand Multi-line", show=True)
    # interface.update_Notify_Right("Right Notify Area\nis centered\nand Multi-line", show=True)

    # interface.set_marker_pos(15/50.)
    # interface.show_Marker(True, redraw=True)

    # ret = interface.get_resp()

    interface.destroy()

