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

try:
	from PyQt4 import QtGui, QtCore
except ImportError:
	pass
else:
	from . import qt

try:
    # Python2
    import Tkinter
    import tkFileDialog, tkSimpleDialog, tkMessageBox
except ImportError:
	try:
	    # Python3
	    import tkinter
	    from tkinter import filedialog, simpledialog, messagebox
	except ImportError:
		pass
	else:
		from . import tk
else:
	from . import tk

from . import term
