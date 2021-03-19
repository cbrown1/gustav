# -*- coding: utf-8 -*-

# A Gustav settings file!

import os
import sys
import time

import psylab           # https://github.com/cbrown1/psylab
import numpy as np
import soundfile as sf

import gustav
from gustav.forms.html import nafc as theForm


def setup(exp):
    print(f'n-AFC setup')
    # setup gets called before the experiment begins

    # General Experimental Variables
    exp.name = '_quiet_thresholds_'     # Experiment name. Accessible as $name when logging or recording data
    exp.method = 'adaptive'             # 'constant' for constant stimuli, or 'adaptive' for a staircase procedure (SRT, etc)
    exp.prompt = 'Which interval?'      # A prompt for subject
    exp.frontend = 'term'               # The frontend to use when interacting with subject or experimenter. Can be 'term', 'tk', or 'qt' (pyqt4)
    exp.logFile = './$name_$date.log'   # The path to the logfile
    exp.logConsole = True               # Whether to direct log info to the console
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
    exp.title = 'n-AFC'
    exp.note = "Quiet thresholds for pure tones"
    exp.comments = '''\
    '''
    exp.info = '''Quiet thresholds for pure tones

    In this experiment you will see 2 boxes on the screen displaying an audio player
    The sounds will be played sequentially and you will be asked to choose the louder one
    Please press 1 or 2 to make your selection
    '''
    exp.welcome = f'''Welcome to the experiment.
    Before we start please provide informed consent on the next page.
    '''
    exp.welcome += "\nID: " + exp.subjID


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

    exp.var.factorial['frequency']= [
                                    # '125',
                                    # '250',
                                    # '500',
                                    '1000',
                                  ]
    def step(exp):
        print(f'STEP')
        # A custom step function for adaptive tracking. This is actually the same as the default one, here for demo purposes
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
                    'run_n_trials': 3,   # Set to non-zero to run exactly that number of trials
                    'max_trials': 60,    # Maximum number of trials to run
                    'vals_to_avg': 3,    # The number of values to average
                    'step': step,        # optional. A custom step function. Signature: def step(exp)
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
    exp.user.isi = 250       # wait duration between audio files (ms)
    exp.user.interval = 500  # duration of 1 audio file (ms)

"""CUSTOM PROMPT
    If you want a custom response prompt, define a function for it
    here. run.response should receive the response as a string, and
    if you want to cancel the experiment, set both run.block_on and
    run.pylab_is_go to False
"""
def pre_exp(exp):
    print('PRE EXP')
    # Get ID and port
    if ':' in exp.subjID:
        exp.subjID, port = exp.subjID.split(':')
    else:
        port = 5050
    print(f'Subject ID: {exp.subjID} port: {port}')
    # Only runs once before the whole thing
    exp.interface = theForm.Interface(alternatives=exp.validKeys.split(","), port=port)
    # Setup styling here (see style.json for more)
    exp.interface.style['logo'] = 'static/index.svg'
    exp.interface.style["--background_color"] = "#232323"
    exp.interface.style["--second_color"] = "#c0c0c0"
    exp.interface.style["--button_size"] = "100px"
    exp.interface.style["--button-border"] = "2px"
    exp.interface.style["--button-border-playing"] = "6px"
    exp.interface.style["--corner-text-fs"] = "20px"
    exp.interface.style["message"] = exp.welcome.replace('\n', '<br>')
    exp.interface.style["performance_feedback"] = True
    exp.interface.style["trial_pause"] = False
    exp.interface.feedback_duration = 500
    # Save styling information for the server
    exp.interface.dump_style()
    # Wait for initial client input
    # This will trigger if the main page is loaded in a browser
    # That's why the max timeout is larger than the default

    exp.interface.id = exp.subjID
    exp.interface.subjdir = os.path.join(exp.interface.expdir, exp.interface.id)
    exp.interface.client_subjdir = f'{exp.interface.client_portdir}/{exp.subjID}'
    exp.interface.info = exp.info
    exp.interface.upper_left_text = f"Subject {exp.subjID}"
    exp.interface.prompt1 = "Press space to begin"
    exp.interface.prompt2 = "Which Interval?"
    # Wait for info call
    ret = exp.interface.get_resp()
    fname = os.path.join(exp.interface.subjdir, ret['response_file'].split('/')[-1])
    exp.interface.dump_info(fname)

def prompt_response(exp):
    """
    Only called after present_trial and before post_trial

    Wait for input from the client.
    Check user specific directory for a new input.
    """
    print('PROMPT RESPONSE')
    while True:
        ret = exp.interface.get_resp()
        if 'answer' in ret:
            exp.run.response = ret['answer']
            break
        elif 'type' in ret and ret['type'] == 'abort':
            exp.interface.abort(exp, archive=True)
            exp.run.block_on = False
            exp.run.gustav_is_go = False
            exp.var.dynamic['msg'] = "Cancelled by user"
            break

def pre_trial(exp):
    """PRE_TRIAL
        This function gets called on every trial to generate the stimulus, and
        do any other processing you need. All settings and variables are
        available. For the current level of a variable, use
        var.current['varname'].
    """
    print(f'PRE TRIAL {exp.run.trials_block}')
    exp.interface.lower_left_text = f'Trial: {exp.run.trials_block}'
    interval_noi = np.zeros(int(exp.user.interval/1000.*exp.user.fs))
    interval_sig = psylab.signal.tone(float(exp.var.current['frequency']),exp.user.fs,exp.user.interval)
    interval_sig = psylab.signal.ramps(interval_sig,exp.user.fs)
    interval_sig = psylab.signal.atten(interval_sig,exp.var.dynamic['max_level']-exp.var.dynamic['value'])

    # Select correct answer randomly
    exp.var.dynamic['correct'] = np.random.randint(1, exp.var.dynamic['alternatives']+1)
    if exp.var.dynamic['correct'] == 1:
        # If the correct answer is 1 send the signal first
        audio = [interval_sig, interval_noi]
    else:
        # Else send the 'silence' first
        audio = [interval_noi, interval_sig]

    exp.interface.audio = []
    for i, a in enumerate(audio, start=1):
        fname = os.path.join(exp.interface.subjdir, f'{exp.run.block}_{exp.run.trials_block}_{i}.wav')
        sf.write(fname, a, exp.user.fs)
        client_fname = os.path.join(exp.interface.client_subjdir, f'{exp.run.block}_{exp.run.trials_block}_{i}.wav')
        exp.interface.audio.append({'name': i, 'file': client_fname, 'id': i})

def present_trial(exp):
    """
    Update interface with trial information.
    """
    print('PRESENT TRIAL')
    # Probably should save json file here with output
    exp.interface.present_trial(exp)

def post_trial(exp):
    # Updates the buttons according to correct answer
    # this is handled on the server side
    print('POST TRIAL')
    if not exp.interface.style["trial_pause"]:
        exp.interface.prompt1 = ""
    if exp.run.gustav_is_go:
        correct = False
        if str(exp.var.dynamic['correct']).lower() == int(exp.run.response):
            correct = True
        print(f'Got answer {exp.run.response}, correct: {correct}')

def post_exp(exp):
    print('POST EXP')
    exp.interface.stop(exp, prompt="Experiment completed, thank you for participating.", archive=True, destroy=True, sleep=10)

def pre_block(exp):
    print(f'PRE BLOCK {exp.run.block}')
    # Runs once before every block of trials (4 blocks in this case because of 4 frequencies)
    exp.interface.lower_right_text = f"Block {exp.run.block + 1} of {exp.var.nblocks}"

if __name__ == '__main__':
    argv = sys.argv[1:]
    argv.append("--experimentFile={}".format(os.path.realpath(__file__)))
    gustav.main(argv)
