[![Build Status](https://travis-ci.org/cbrown1/gustav.svg?branch=master)](https://travis-ci.org/cbrown1/gustav)

# gustav

A simple but powerful python module to help with psychophysical experimentation.


## Overview

Gustav is designed to automate most or all the aspects of psychophysical testing that are more-or-less similar across experiments, such as the psychophysical methods used, displaying information to the subject and experimenter, saving data, keeping track of trials and blocks, etc. Most of these things are at least customizable, and at most subclass-able, meaning you can handle them yourself in cases where it makes sense to do so. Gustav is also extensible, allowing new modules for additional testing methods, new frontends, etc., to be easily added.

In the meantime, the aspects of testing that are unique across experiments, like stimulus generation, are left to the experimenter. Gustav tries to make it as easy as possible to do so using events, which are just python functions that get called at various points during testing. See the events section for more.

Some terms:

    - `Variable`: An experimental variable that may have one or more levels

    - `Level`: One of the possible values that an experimental variable may have

    - `Parameter` : There are many variables to be set in a gustav experiment file, but for clarity, the term `variable` will be reserved for experimental variables, as described above and elsewhere. Other more typical Python variables will be referred to as `parameters` to avoid confusion.

    - `Condition` : A unique combination of levels across the experimental variables. Each condition has a unique condition number, assigned by gustav, that can be used to identify or specify that condition. 

    - `Block`: A block is a group of one or more trials, run in a given condition (ie., in which the levels of each variable are held constant).

    - `Trial`: An event which usually involves presenting a stimulus to the subject, and soliciting a response, among other things.


## Events

Gustav implements an event-driven framework, wherein certain events are called at certain times during testing. Most of these events are not required, although you will need some or not much will happen during the experiment. These events are specified in your experiment file as simple python functions, and the `exp` object is passed to each (eg: `def pre_block(exp):`) which holds, and thus makes available, all of the information about the experiment. If you don't specify an event, nothing will happen at that time during the experiment. Available events include:

    - `setup` : Called once at the beginning of experiment, to initialize parameters, experimental variables, etc. This is the only required event.

    - `pre_exp` : Called once at the beginning of experiment but after setup. 
        - Eg., to initialize an empty datafile.

    - `pre_block` : Called before the start of a block of trials. 
        - All experimental variables will be set to their respective levels prior to 
            this event.
        - Eg., set up some variables that will remain constant for each block

    - `pre_trial` : Called prior to the start of each trial.
        - Eg., stimulus generation.

    - `present_trial` : Called during a trial.
        - Eg., can be used for stimulus presentation, although pre_trial could also do this.

    - `prompt_response` : Called at the end of a trial.
        - Intended to be used to solicit a response.

    - `post_trial` : Called after a trial.
        - Eg., can be used to record data, plot real-time response, etc

    - `post_block` : Called after a block of trials is completed.

    - `post_exp` : Called at the end of the experiment.


## The exp object

This is just a python class to hold all of the parameters and variables of the experiment. It should be passed to all event functions as the sole input parameter.

It is organized into several sub-classes:

    - `exp.run` : holds info like current trial and block numbers, etc. (read-only access)

    - `exp.var` : holds experimental variables and their levels. See below. (read-only access)

    - `exp.stim` : empty class available to the experimenter to hold stimulus-related stuff (eg., `exp.stim.fs = 44100`) (read/write access)

    - `exp.user` : empty class available to the experimenter to hold any other data (read/write access)

Note that read-only access is not enforced, the read-only descriptors above are just a reminder that you should not write to these classes.


## Variables

Gustav defines an ordered dictionary with which you can specify experimental variables. The variable and level names should always be strings, even when the actual values are otherwise (bool, float, etc).

Variables should be initialized in the setup event.

There are 2 kinds of variables: factorial and covariable. Each is a dict 


### Factorial Variables

Variables added as 'factorial' variables will be factorialized with each other. So, if you have 2 factorial variables A & B, each with 3 levels, you will end up with 9 conditions: A1B1, A1B2, A1B3, A2B1 etc..

```python
exp.var.factorial['target'] = ['male', 'female3']
exp.var.factorial['masker'] = ['noise', 'babble']
# Would result in 4 conditions: 
#   1: target == male, masker == noise
#   2: target == male, masker == babble
#   3: target == female, masker == noise
#   4: target == female, masker == babble
```


### Covariable Variables

Variables added as 'covariable' variables will simply be listed (in parallel with the corresponding levels from the other variables) in the order specified. So, if you have 2 covariable variables A & B, each with 3 levels, you will end up with 3 conditions: A1B1, A2B2, and A3B3. All covariable variables must have either the same number of levels, or exactly one level. When only one level is specified, that level will be used in all covariable conditions. Eg., if covariable A has 3 levels and covariable B has 1, you will have three conditions: A1B1, A2B1, A3B1. Covariables are intended for use alone when you don't need factorialization, or in addition to factorial variables when you need to add a condition or two that are not factorial, such as control conditions etc..

```python
exp.var.covariable['target'] = ['tone', 'speech']
exp.var.covariable['masker'] = ['noise', 'babble']
# Would result in 2 conditions: 
#    target == tone, masker == noise
#    target == speech, masker == babble
```


### Variable Usage

You can use both types of variables in the same experiment, but both factorial and covariable must contain exactly the same set of variable names. factorial levels are processed first, covariable levels are added at the end.

Both factorial and covariable are Python ordered dicts, where the keys are variable names, and the values are lists of levels. During the  experiment, you have access to the current level of each variable. For example, if you have the following variable:

```python
exp.var.factorial['talker'] = ['Male', 'Female']
```

Then, you can find out what the level is at any point in the experiment 
with:

```python
if exp.var.current['talker'] == 'Male':
    # The talker is male
else:
    # The talker is female
    
```

which would return either 'Male' or 'Female' depending on what the condition happened to be. This is probably most useful to generate your  stimuli, eg., in the pre_trial function. It can also be helpful to specify a variable even when it has only 1 level, as a way of asserting what it was, because it can be easily saved to the datafile and thus recorded.

Remember that these variables and levels are all just text, and it is up to  you to implement stimuli based on their values. Often what you want to do is read the level of each variable in pre_trial, and generate your stimuli based on that:

```python
if exp.var.current['frequency'] == '500':
   # Generate a 500-Hz tone
```

Gustav will generate a list of conditions in which all of the factorial combinations are listed first, and the covariable conditions are added last. Each condition will have a unique condition number that can be used during runtime to select it to run, using either the menu, prompt, or print-range style string methods as described in the `Presentation Order` section.

## Setup event

This is a required event where you set many parameters that control various aspects of the experiment. 

Parameters include:

    - `exp.name` : The name of the experiment

    - `exp.method` : 'constant' for constant stimuli, or 'adaptive' for an adaptive / staircase procedure (SRT, etc). See `Psychophysical Methods` for more information.

    - `exp.logFile` = the path and name of a log file. Any data written to the console will also be written to this file. Name and date vars only on logfile name (eg., `$name_$date.log`)

    - `exp.recordData` : A bool to indicate whether to record data using in-built methods. See `Recording Data` below for more information.

    - `exp.dataFile` : The path and name to a datafile. See `Recording Data` below for more information. 

    - `exp.frontend` : What to use to interact with the experimenter when input is needed. See `Frontends` below for more information.

    - `exp.debug` : A bool indicating whether to print debug information to the console during testing

In addition, you should also set up your experimental variables and presentation order in setup, as well as any settings that are specific to the psychophysical method you are using.


### Presentation Order

The order of presentation of the conditions is specified in `exp.var.order`. A number of options are available:

    - `prompt` : Prompt for the condition number on each block

    - `random` : Randomize condition order

    - `menu` : Choose from a list of conditions at the start of a run

    - `natural` : Use natural order (1:end)

    - `'1-10, 12, 15'` : a print-range style string (comma-separated) that 
        specifies the conditions to run and their order. You can make the 
        first item in the print range 'random' to randomize the specified range.


## Psychophysical Methods

There are currently two psychophysical methods available:

    - Method of constant stimuli

    - Adaptive tracking


### Method of Constant Stimuli

This method will run a defined number of trials per block. To use, in the setup event set 'exp.method' to 'constant'. In addition the `exp.var.constant` dict contains 3 parameters, `trialsperblock`, `startblock` and `starttrial`. For example:

```python
exp.method = 'constant'
exp.var.constant = {
    'trialsperblock' : 10,
    'startblock' : 1,
    'starttrial' : 1,
    }
```

Will run 10 trials per block or condition. The `startblock` and `starttrial` parameters are intended to be used for crash recovery. Setting both to 1 will start at the beginning. 


### Adaptive Tracking

The adaptive tracking method uses a dict named `exp.var.dynamic`. Here is an example, with some descriptions of each of the parameters:

```python
exp.method = 'adaptive'
exp.var.dynamic = { 
    'name': 'ild_coeff', # Name of the dynamic variable
    'units': 'dB',       # Units of the dynamic variable
    'steps': [.1, .1, .02, .02, .02, .02, .02, .02], # Stepsizes to use at each reversal (#revs = len)
    'downs': 2,          # Number of 'downs'
    'ups': 1,            # Number of 'ups'
    'val_start': .2,    # Starting value
    'val_floor': 0,      # Floor
    'val_ceil': 1,       # Ceiling
    'val_floor_n': 3,    # Number of consecutive floor values to quit at
    'val_ceil_n': 3,     # Number of consecutive ceiling values to quit at
    'run_n_trials': 0,   # Set to non-zero to run exactly that number of trials
    'max_trials': 60,    # Maximum number of trials to run
    'vals_to_avg': 6,    # The number of values to average
    'step': step,     # A custom step function. Signature: def step(exp):
                }
```

This method has a function to record data, accessed here `exp.method.save_data_block(exp)`. You can call this at the end of a block (say, in `post_block`), and data will be save to a text file specified in `exp.dataFile`, where each run is represented as a python class, which means the file can be run as a python script and the data will be loaded automatically.

This method also implements logging, if the logging parameters are set to None. 


## Recording Data

Data can be recorded automatically. To utilize this function, set `exp.recordData` to True, and specify the full file path to write to in `exp.dataFile`. You can save data after any event specifying a dataString with that event name:

```python
exp.recordData = True
exp.dataFile = '/path/to/datafile'
exp.dataString_post_trial = "$trial,$response\n"
```

There are many string parameters available, use the parameter name and it will be expanded

        - $name            : The name of the experiment
        - $host            : The name of the machine that the exp is being run on
        - $subj            : The subject id
        - $resp            : The most recent response
        - $trial           : The most recent trial number
        - $trial_block     : The most recent trial number within the current block
        - $block           : The current block number
        - $condition       : The current condition number
        - $conditions      : The total number of conditions
        - $time            : The time the session started
        - $date            : The date the session started
        - $var[varname]    : The current level of the specified variable
        - $currentvars[';']: A delimited list of the current levels of all vars
                            The delimiter can be specified (use empty brackets
                            to specify default: ',')
        - $currentvarsvals : Same as currentvars, but you will get 'var = val'
                            instead of just 'val'
        - @currentvars     : Same as currentvars, but you will get var names 
                            instead of values (eg., for datafile header). 
        - $user[varname]   : The value of a user variable
        - $stim[varname]   : The value of a stim variable


    exp.dataFile = os.path.join(workdir,'data','$name.csv')
    exp.recordData = True
    exp.dataString_header = "# A datafile created by Gustav!\n# \n# Experiment: $name\n# \n\nS,Trial,Date,Block,Condition,Practice,SNR,@currentvars[],KWP,KWC\n"
    exp.dataString_post_trial = "$subj,$trial,$date,$block,$condition,$user[pract],$user[snr],$currentvars[],$user[trial_kwp],$response\n"




## Logging

To do...


## Frontends

Frontends represent ways of interacting with either the experimenter or the subject. There are several available, and it is easy to add others. Currently, the frontends available are:

    - `term`: the terminal, or console, which requires no graphical toolkit

    - `tk`: the tkinter toolkit, which comes with python

    - `qt`: the qt4 toolkit

Specify the frontend you want to use in the setup function:

```python
exp.frontend = term
```

Each frontend is a python script that contains a set of predefined functions (analagous to simple system dialog boxes) to interact with the user. If you want to use a different gui kit like gtk, simply implement the required functions, which are listed here with their signatures:

    - get_input(parent=None, title = 'User Input', prompt = 'Enter a value:'):

        - Opens a simple prompt for user input, returns a string

    - get_item(parent=None, title = 'User Input', prompt = 'Choose One:', items = [], current = 0, editable = False):

    - Opens a simple prompt to choose an item from a list, returns a string

    - get_yesno(parent=None, title = 'User Input', prompt = 'Yes or No:'):

        - Opens a simple yes/no message box, returns a bool

    - show_message(parent=None, title = 'Title', message = 'Message', msgtype = 'Information'):

        - Opens a simple message box with an OK button, returns None

These functions are used by gustav and are also available in your experiment scripts to interact with a user, eg., 

```python
ret = exp.frontend.get_yesno(None, 'Gustav!', prompt='Ready to begin testing?')
if ret == 'yes':
    # Begin!
else:
    # User canceled...
```


## User Forms

To do...


## Installing


### Download:

```bash
git clone https://github.com/cbrown1/gustav.git
```


### Compile and install:

```bash
python setup.py build
sudo python setup.py install
```


## Usage Examples

See the test_gustav set of scripts in the user_scripts directory for examples.


## Authors

- **Christopher Brown**


## License

This project is licensed under the GPLv3 - see the [LICENSE.md](LICENSE.md) file for details.
