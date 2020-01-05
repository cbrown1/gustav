# -*- coding: utf-8 -*-

# A Gustav settings file!

import os, sys
import numpy as np
import time
import gustav
from gustav.forms import nafc as theForm
import psylab                              # https://github.com/cbrown1/psylab
import medussa as m                        # https://github.com/cbrown1/medussa

def setup(exp):

    # General Experimental Variables
    exp.name = '_quiet_thresholds_'
    exp.method = 'adaptive' # 'constant' for constant stimuli, or 'adaptive' for a staircase procedure (SRT, etc)
    exp.prompt = 'Which interval?' # Prompt for subject
    exp.frontend = 'tk'
    exp.logFile = './$name_$date.log'
    exp.logConsole = True
    exp.logConsoleDelay = True # When using a curses form, the console is not available. True = delay print until end of exp.
    exp.debug = False
    exp.recordData = True
    exp.dataFile = './$name_$subj.py'
    exp.dataString_trial = ''
    exp.dataString_block = ''
    exp.dataString_exp = ''
    exp.dataString_header = ''
    exp.cacheTrials = False
    exp.validKeys = '1,2';  # comma-delimited list of valid responses
    exp.quitKey = '/'
    exp.note = "Quiet thresholds for pure tones"
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
                                    '125',
                                    '250',
                                    '500',
                                    '1000',
                                  ]
    def step(exp):
        exp.var.dynamic['value'] += exp.var.dynamic['cur_step'] * exp.var.dynamic['steps'][exp.var.dynamic['n_reversals']]
        exp.var.dynamic['value'] = max(exp.var.dynamic['value'], exp.var.dynamic['val_floor'])
        exp.var.dynamic['value'] = min(exp.var.dynamic['value'], exp.var.dynamic['val_ceil'])

    
    exp.var.dynamic = { 'name': 'Level',     # Name of the dynamic variable
                    'units': 'dBSPL',    # Units of the dynamic variable
                    'alternatives': 2,   # Number of alternatives
                    'steps': [5, 5, 2, 2, 2, 2, 2, 2], # Stepsizes to use at each reversal (#revs = len)
                    #'steps': [2, 2],    # Stepsizes to use at each reversal (#revs = len)
                    'downs': 2,          # Number of 'downs'
                    'ups': 1,            # Number of 'ups'
                    'val_start': 50,     # Starting value
                    #'val_start': 0,     # Starting value
                    'val_floor': 0,      # Floor
                    'val_ceil': 70,      # Ceiling
                    'val_floor_n': 3,    # Number of consecutive floor values to quit at
                    'val_ceil_n': 3,     # Number of consecutive ceiling values to quit at
                    'run_n_trials': 0,   # Set to non-zero to run exactly that number of trials
                    'max_trials': 60,    # Maximum number of trials to run
                    'vals_to_avg': 6,    # The number of values to average
                    'step': step,        # A custom step function. Signature: def step(exp)
                    'max_level': 80, 
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

"""CUSTOM PROMPT
    If you want a custom response prompt, define a function for it
    here. run.response should receive the response as a string, and
    if you want to cancel the experiment, set both run.block_on and
    run.pylab_is_go to False
"""
def prompt_response(exp):
    while True:
        ret = exp.interface.get_resp()
        if ret in exp.validKeys:
            exp.run.response = ret
            break
        elif ret in exp.quitKeys:
            exp.run.block_on = False
            exp.run.gustav_is_go = False
            exp.var.dynamic['msg'] = "Cancelled by user"
            break

"""PRE_TRIAL
    This function gets called on every trial to generate the stimulus, and
    do any other processing you need. All settings and variables are
    available. For the current level of a variable, use
    var.current['varname']. 
"""
def pre_trial(exp):
    exp.interface.update_Status_Right("Trial {:}".format(exp.run.trials_block), redraw=True)
    isi = np.zeros(int(psylab.signal.ms2samp(int(exp.user.isi),int(exp.user.fs))))
    interval_noi = np.zeros(int(exp.user.interval/1000.*exp.user.fs))
    interval_sig = psylab.signal.tone(float(exp.var.current['frequency']),exp.user.fs,exp.user.interval)
    interval_sig = psylab.signal.ramps(interval_sig,exp.user.fs)
    interval_sig = psylab.signal.atten(interval_sig,exp.var.dynamic['max_level']-exp.var.dynamic['value'])

    exp.var.dynamic['correct'] = np.random.randint(1, exp.var.dynamic['alternatives']+1)
    if exp.var.dynamic['correct'] == 1:
        exp.stim.out = np.hstack((interval_sig, isi, interval_noi))
    else:
        exp.stim.out = np.hstack((interval_noi, isi, interval_sig))
    
    
def present_trial(exp):
    #pass
    #m.play_array(stim.out,user.fs)
    time.sleep(.1)
    exp.interface.show_Notify_Left(False)    # Hide the 'press space' text since they just pressed it
    exp.interface.show_Notify_Right(True)    # Show the listen text
    exp.interface.show_Prompt(False)         # Don't show prompt during presentation b/c we don't want a response
    exp.interface.show_Buttons(True, redraw=True) # Show buttons so user gets visual feedback on interfal playback
    s = exp.audiodev.open_array(exp.stim.out,exp.user.fs)
    s.play()
    for i in range(len(exp.interface.alternatives)):
        exp.interface.set_border(i, 'Heavy', redraw=True)
        time.sleep(exp.user.interval/1000.)
        exp.interface.set_border(i, 'Light', redraw=True)
        time.sleep(exp.user.isi/1000.)
    exp.interface.show_Notify_Right(False)
    exp.interface.show_Prompt(True, redraw=True)


def post_trial(exp):
#    exp.interface.button_light([1,2], None)
    if exp.run.gustav_is_go:
        if str(exp.var.dynamic['correct']).lower() == exp.run.response.lower():
            color = 'Green'
        else:
            color = 'Red'
        for i in range(3):
            exp.interface.set_color(exp.var.dynamic['correct']-1, color, redraw=True)
            time.sleep(.1)
            exp.interface.set_color(exp.var.dynamic['correct']-1, 'None', redraw=True)
            time.sleep(.05)

def pre_exp(exp):
    exp.interface = theForm.Interface(alternatives = exp.validKeys.split(","))
    exp.interface.update_Title_Center(exp.note)
    exp.interface.update_Title_Right("Subject {:}".format(exp.subjID), redraw=True)
    exp.audiodev = m.open_device()
    exp.interface.show_Buttons(False)
    exp.interface.show_Notify_Left(False)
    exp.interface.update_Notify_Right("Listen", show=False)
    exp.interface.update_Prompt("Press any key to begin", show=True, redraw=True)
    # Wait for a keypress
    ret = exp.interface.get_resp()
    exp.interface.update_Prompt("Which Interval?", show=False, redraw=True)


def post_exp(exp):
    exp.interface.destroy()

def pre_block(exp):
    exp.interface.update_Status_Center("Block {:} of {:}".format(exp.run.block+1, exp.var.nblocks+1))

if __name__ == '__main__':
    argv = sys.argv[1:]
    argv.append("--experimentFile={}".format(os.path.realpath(__file__)))
    gustav.main(argv)
