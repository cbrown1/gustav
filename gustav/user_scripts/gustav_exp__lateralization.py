# -*- coding: utf-8 -*-

# A Gustav settings file!

import os, sys
import numpy as np
import time
import curses
import gustav
from gustav.forms import lateralization as theForm
import psylab                              # https://github.com/cbrown1/psylab
import medussa as m                        # https://github.com/cbrown1/medussa

def setup(exp):
    # setup gets called before the experiment begins

    # General Experimental Variables
    exp.name = '_lateralization_'   # Experiment name. Accessible as $name when logging or recording data
    exp.method = 'constant'             # 'constant' for constant stimuli, or 'adaptive' for a staircase procedure (SRT, etc)
    exp.prompt = 'Where did you hear it?' # A prompt for subject
    exp.frontend = 'tk'                 # The frontend to use when interacting with subject or experimenter. Can be 'term', 'tk', or 'qt' (pyqt4)
    exp.logFile = './$name_$date.log'   # The path to the logfile
    exp.logConsole = False               # Whether to direct log info to the console
    exp.logConsoleDelay = True          # When using a curses form, the console is not available. Set to True to delay print until end of exp when curses form is destroyed.
    exp.debug = False                   # Currently unused
    exp.recordData = True               # Whether to record data
    exp.dataFile = './$name_$subj.py'   # The name of the data file
    exp.dataString_trial = ''
    exp.dataString_block = ''
    exp.dataString_exp = ''
    exp.dataString_header = ''
    exp.cacheTrials = False             # Currently unused
    exp.validKeys = '1,2';              # comma-delimited list of valid responses
    exp.quitKey = '/'
    exp.note = "Lateralization of pure tones"
    exp.comments = '''\
    '''

    """EXPERIMENT VARIABLES
        There are 2 kinds of variables: factorial and ordered

        Levels added as 'factvars' variables will be factorialized with each
        other. So, if you have 2 fact variables A & B, each with 3 levels, you
        will end up with 9 conditions: A1B1, A1B2, A1B3, A2B1 etc..

        Levels added as 'listvars' variables will simply be listed (in parallel
        with the corresponding levels from the other variables) in the order
        specified. So, if you have 2 'listvars' variables A & B, each with 3
        levels, you will end up with 3 conditions: A1B1, A2B2, and A3B3. All
        'listvars' variables must have either the same number of levels, or
        exactly one level. When only one level is specified, that level will
        be used in all 'listvars' conditions. Eg., A1B1, A2B1, A3B1, etc.

        You can use both types of variables in the same experiment, but both
        factvars and listvars must contain exactly the same set of variable
        names. Factvars levels are processed first, listvars levels are added at
        the end.

        Each variable (whether factvars or listvars) should have 3 properties:

        'name' is the name of the variable, as a string

        'type' is either 'manual' or 'stim'. 'manual' variables are ones that
                the experimenter will handle in the stimgen. 'stim' variables
                are ones that will load stimulus files. One usecase would be
                eg., if you preprocess your stimuli and want to read the same
                files, but from different directories depending on the
                treatment.

        'levels' should be a list of strings that identify each level of interest

        for file in stim['masker_files']:
            masker,fs,enc = utils.wavread(file)
            stim['masker'] += masker
        stim['masker'] = stim['masker'][0:stim['masker_samples_needed']]
    """
    # TODO: for python 2.7, change these to ordered dicts, where name is the key
    # and the dict {type, levels} is the val
    
    exp.var.factorial['frequency']= [
                                    '250',
                                    '4000',
                                  ]

    exp.var.factorial['cue']= [
                                    'ild',
                                    'itd',
                                  ]


    """CONSTANT METHOD VARIABLES
        The method of constant stimuli requires three variables to be set.
            trialsperblock
            startblock [crash recovery]
            starttrial [crash recovery]
    """
    exp.var.constant = {
        'trialsperblock' : 15,
        'startblock' : 1,
        'starttrial' : 1,
        }
        
    """CONDITION PRESENTATION ORDER
        Use 'prompt' to prompt for condition on each block, 'random' to randomize
        condition order, 'menu' to be able to choose from a list of conditions at
        the start of a run, 'natural' to use natural order (1:end), or a
        print-range style string to specify the order ('1-10, 12, 15'). You can
        make the first item in the print range 'random' to randomize the specified
        range.
    """
    exp.var.order = 'random'

    """IGNORE CONDITIONS
        A list of condition numbers to ignore. These conditions will not be
        reflected in the total number of conditions to be run, etc. They will
        simply be skipped as they are encountered during a session.
    """
    exp.var.ignore = []

    '''USER VARIABLES
        Add any additional variables you need here
    '''
    exp.user.fs = 44100
    exp.user.isi = 250 # ms
    exp.user.interval = 500
    exp.user.range = {}
    exp.user.range['ild'] = [-15, 15]
    exp.user.range['itd'] = [-750, 750]


"""CUSTOM PROMPT
    If you want a custom response prompt, define a function for it
    here. run.response should receive the response as a string, and
    if you want to cancel the experiment, set both run.block_on and
    run.pylab_is_go to False
"""
def prompt_response(exp):
    exp.interface.show_Notify_Right(False)
    exp.interface.update_Notify_Left('Respond', show=True, redraw=True)
    exp.stim.x = exp.stim.n/2.
    exp.interface.set_marker_pos(exp.stim.x/exp.stim.n)
    exp.interface.show_Marker(True)
    while True:
        ret = exp.interface.get_resp()
        if ord(ret) == curses.KEY_LEFT:
            exp.stim.x = max(exp.stim.x-1, 0)
            exp.interface.set_marker_pos(exp.stim.x/exp.stim.n)
        elif ord(ret) == curses.KEY_RIGHT:
            exp.stim.x = min(exp.stim.x+1, exp.stim.n)
            exp.interface.set_marker_pos(exp.stim.x/exp.stim.n)
        elif ord(ret) == curses.KEY_SLEFT:
            exp.stim.x = max(exp.stim.x-5, 0)
            exp.interface.set_marker_pos(exp.stim.x/exp.stim.n)
        elif ord(ret) == curses.KEY_SRIGHT:
            exp.stim.x = min(exp.stim.x+5, exp.stim.n)
            exp.interface.set_marker_pos(exp.stim.x/exp.stim.n)
        elif ret == curses.KEY_ENTER or ord(ret) == 10 or ord(ret) == 13:
            exp.run.response = str(exp.stim.x)
            exp.user.resps.append(exp.stim.x)
            break
        elif ret in exp.quitKeys:
            exp.run.block_on = False
            exp.run.gustav_is_go = False
            exp.var.dynamic['msg'] = "Cancelled by user"
            break
    exp.interface.show_Notify_Left(False)
    exp.interface.show_Marker(False)

def pre_trial(exp):
    """PRE_TRIAL
        This function gets called on every trial to generate the stimulus, and
        do any other processing you need. All settings and variables are
        available. For the current level of a variable, use
        var.current['varname']. 
    """
    exp.interface.update_Status_Right("Trial {:} of {:}".format(exp.run.trials_block+1, exp.var.constant['trialsperblock']), redraw=True)
    cue = exp.var.current['cue']

    sig = psylab.signal.tone(float(exp.var.current['frequency']),exp.user.fs,exp.user.interval)
    sig = psylab.signal.ramps(sig,exp.user.fs)

    if cue == 'ild':
        exp.stim.out = psylab.signal.apply_ild(sig, exp.user.this_range[exp.run.trials_block])
    else:
        exp.stim.out = psylab.signal.apply_itd(sig, exp.user.fs, exp.user.this_range[exp.run.trials_block])
    
def present_trial(exp):
    #pass
    #m.play_array(stim.out,user.fs)
    time.sleep(.1)
    exp.interface.update_Notify_Right('Listen', show=True, redraw=True)
    exp.interface.show_Marker(show=False)
    exp.interface.show_Notify_Left(False)    # Show the listen text
    s = exp.audiodev.open_array(exp.stim.out,exp.user.fs)
    s.play()
    while s.is_playing:
        time.sleep(.05)

    exp.interface.show_Notify_Right(False)

def pre_exp(exp):
    exp.audiodev = m.open_device()
    exp.interface = theForm.Interface()
    exp.interface.update_Title_Center(exp.note)
    exp.interface.update_Title_Right("Subject {:}".format(exp.subjID) )
    exp.interface.update_Status_Left("Press '/' to quit")
    exp.interface.show_Notify_Left(False)
    exp.interface.show_Notify_Right(False)
    exp.stim.n = exp.interface.posbar_w * 2.
    exp.user.results = "Subject: {:}\n".format(exp.subjID)
    # Wait for a keypress
    ret = exp.interface.get_resp()

def post_exp(exp):
    exp.interface.destroy()
    print(exp.user.results)

def pre_block(exp):
    exp.interface.update_Status_Center("Block {:} of {:}".format(exp.run.block+1, exp.var.nblocks))
    cue = exp.var.current['cue']
    exp.user.this_range = np.linspace(exp.user.range[cue][0], exp.user.range[cue][1], exp.var.constant['trialsperblock'])
    np.random.shuffle(exp.user.this_range)
    exp.user.resps = []


def post_block(exp):
    cue = exp.var.current['cue']
    f = exp.var.current['frequency']
    std = np.std(exp.user.resps)
    exp.user.results += "cue: {}, f: {:}, mean: {:}\n".format(cue,f,std)

if __name__ == '__main__':
    argv = sys.argv[1:]
    argv.append("--experimentFile={}".format(os.path.realpath(__file__)))
    gustav.main(argv)
