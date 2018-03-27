[![Build Status](https://travis-ci.org/cbrown1/gustav.svg?branch=master)](https://travis-ci.org/cbrown1/gustav)

# gustav

A simple but powerful python module to help with psychophysical experimentation.

## Overview

Gustav is designed to automate most or all the aspects of psychophysical 
testing that are more-or-less similar across experiments, such as the 
psychophysical methods used, displaying information to the subject and
experimenter, saving data, keeping track of trials and blocks, etc. Most of
these things are at least customizable, and at most subclass-able, meaning
you can handle them yourself in cases where it makes sense to do so.

In the meantime, the aspects of testing that are unique across experiments, 
like stimulus generation, are left to the experimenter.

Some terms:

    - Variable: An experimental parameter that may have one or more levels

    - Level: One of the possible values that a variable may have

    - Block: a block is a group of one or more trials, in which the levels of 
        each experimental variable are held constant

    - Trial: An event which usually involves presenting a stimulus to the subject, 
	    and soliciting a response, among other things 

## Events

Gustav implements an event-driven framework, wherein certain events are called
at certain times during testing. Most of these events are not required, although
you will need some or not much will happen during the experiment. These events 
are specified in your experiment file as simple python functions, and the `exp`
object is passed to each (eg: `def pre_block(exp):`) which holds all of the 
information about the experiment. If you don't specify an event, nothing will 
happen at that time during the experiment. Available events include:

    - setup
        - Called once at the beginning of experiment, to initialize variables, etc.
        - The only required event

    - pre_exp
        - Called once at the beginning of experiment but after setup
        - EG., to initialize an empty datafile

    - pre_block
        - Called before the start of a block of trials. 
        - All experimental variables will be set to their respective levels prior to 
            this event.
        - EG., set up some variables that will remain constant for each block

    - pre_trial
        - Called prior to the start of each trial
        - EG., stimulus generation

    - present_trial
        - Called during a trial
        - Can be used for stimulus presentation, although pre_trial could also do this

    - prompt response
        - Called at the end of a trial
        - Intended to be used to solicit response

    - post_trial
        - Called after a trial
        - Can be used to record data, plot real-time response, etc

    - post_block
        - Called after a block of trials is completed

    - post_exp
        - Called at the end of the experiment

## The exp object

This is just a python class to hold all of the variables of the experiment. It should
be passed to all event functions as the sole input parameter.

It is organized into several sub-classes:

    - exp.run holds info like current trial and block numbers, etc. (read-only)

    - exp.var holds experimental variables and their levels. See below. (read-only)

    - exp.stim empty class available to the experimenter to hold 
        stimulus-related stuff (eg., `exp.stim.fs = 44100`) (read/write)

    - exp.user empty class available to the experimenter to hold any other data 
        (read/write)

## Variables

Gustav defines an ordered dictionary with which you can specify 
experimental variables. The variable and level names should always be
strings, even when the actual values are otherwise (bool, float, etc).

There are 2 kinds of variables: factorial and covariable

### Factorial Variables

Levels added as 'factorial' variables will be factorialized with each
other. So, if you have 2 fact variables A & B, each with 3 levels, you
will end up with 9 conditions: A1B1, A1B2, A1B3, A2B1 etc..

### Covariable Variables

Levels added as 'covariable' variables will simply be listed (in parallel
with the corresponding levels from the other variables) in the order
specified. So, if you have 2 covariable variables A & B, each with 3
levels, you will end up with 3 conditions: A1B1, A2B2, and A3B3. All
covariable variables must have either the same number of levels, or
exactly one level. When only one level is specified, that level will
be used in all covariable conditions. Eg., if covariable A has 3 levels
and covariable B has 1, you will have three conditions: A1B1, A2B1, A3B1.

### Usage

You can use both types of variables in the same experiment, but both
factorial and covariable must contain exactly the same set of variable
names. factorial levels are processed first, covariable levels are added
at the end.

Both factorial and covariable are Python ordered dicts, where the keys 
are variable names, and the values are lists of levels. During the 
experiment, you have access to the current level of each variable. For 
example, if you have the following variable:

```python
exp.var.factorial['target'] = ['Male', 'Female']
```

Then, you can find out what the level is at any point in the experiment 
with:

```python
exp.var.current['target'] 
```

which would return either 'Male' or 'Female' depending on what the 
condition happened to be. This is probably most useful to generate your 
stimuli, eg., in the pre_trial function. It can also be helpful to specify
a variable even when it has only 1 level, as a way of asserting what it was,
because it can be easily saved to the datafile and thus recorded.

Remember that these variables and levels are all just text, and it is up to 
you to implement stimuli based on their values. Often what you want to do
is read the level of each variable in pre_trial, and generate your stimuli
based on that:

```python
if exp.var.current['frequency'] == '500':
   # Generate a 500-Hz tone
```

### Presentation Order

The order of presentation of the conditions is specified in `exp.var.order`. 
A number of options are available:

    - 'prompt' to prompt for the condition number on each block

    - 'random' to randomize condition order

    - 'menu' to be able to choose from a list of conditions at the start of 
        a run

    - 'natural' to use natural order (1:end)

    - a print-range style string (comma-separated) to specify the order 
        (eg., '1-10, 12, 15'). You can make the first item in the print 
        range 'random' to randomize the specified range.


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

## Usage

See the test_gustav scripts in the user_scripts folder for examples

### General Overview

Gustav is 

There are currently two psychophysical methods available:

    - Method of constant stimuli

    - Adaptive tracking




## Authors

- **Christopher Brown**

## License

This project is licensed under the GPLv3 - see the [LICENSE.md](LICENSE.md) file for details.
