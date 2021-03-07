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


"""Gustav: An event-based framework for psychophysical experiments

    Gustav tries to handle all of the aspects of experimentation that are 
    common across experiments (organizing and enumerating experimental 
    variables, the psychophysical procedure, interacting with subjects, 
    logging, saving data, etc.), and leaves to the experimenter the aspects 
    that are unique to each experiment (stimulus generation and delivery, etc). 
    
    An experiment is represented by a Gustav experiment file, which is simply 
    a python script that has various functions and properties specified. For 
    example, the setup function is where many aspects of the experiment are 
    set, such as the name of the experiment, where and how to save data, what 
    the experimental variables and their levels are, and so on. The best way 
    to understand how one works is to have a look at one. See the test_gustav 
    python scripts in the user_scripts directory for more information.

"""

__version__ = '0.8.0'

from .gustav import run, info, main
from . import frontends, methods, forms
