# TMS R01 Study
# Localiser task modelled after Pinel et al. (2007) BMC Neurosci 8 - duration 438 sec
# Nikola Vukovic, Aug 2018

# Initialise Python Libraries
from psychopy import core, visual, gui, data, misc, event, logging, sound, clock
import time, os, serial, csv, random, sys, threading
from itertools import chain
import numpy as np
from random import shuffle
import time


# present a dialogue to input subject params

expInfo = {'subjID':'0001', 'session':1}
dictDlg = gui.DlgFromDict(dictionary=expInfo,
        title='Session Parameters', order=['subjID', 'session'])
if dictDlg.OK:
    print(expInfo)
    expInfo['date'] = data.getDateStr()  # add a timestamp
else:
    print('User cancelled, end run')
    core.quit()

# Setup the Window
win = visual.Window(
    size = (1024,768),
    fullscr=True,
    monitor='testMonitor', color='#000000',
    units='deg')

# Import comma separated trial list as dictionary
script_dir = os.path.dirname(__file__) # absolute path to python script
filename = os.path.join(script_dir, "trials_list.csv")
trialList = csv.DictReader(open(filename))

timer = core.Clock() #to keep track of time
timestr = time.strftime("%Y%m%d%H%M")

# Log file to save timings
datafileName = 'data/' + expInfo['subjID'] + '_run' + str(expInfo['session']) + '_log_' + timestr
dataFile_Stim = open(datafileName+'.csv', 'w')
dataFile_Stim.write('trial,session,subjID,modality,trialType,stimulus,stimOnset,stimOffset,expectedDuration\n')


# Some Global Properties and Components
staticITI = core.StaticPeriod(win=win,screenHz=60)

checkH1 = visual.ImageStim(win,image=os.path.join(script_dir, "checkerboardH1.png"), pos = (0, 0))
checkH2 = visual.ImageStim(win,image=os.path.join(script_dir, "checkerboardH2.png"), pos = (0, 0))
checkV1 = visual.ImageStim(win,image=os.path.join(script_dir, "checkerboardV1.png"), pos = (0, 0))
checkV2 = visual.ImageStim(win,image=os.path.join(script_dir, "checkerboardV2.png"), pos = (0, 0))

textHeight = 2
textColor = 'white'
textFont='Source Code Pro'

# Component to present text string
def showString(str,txtH=textHeight):
    win.flip()
    textString = visual.TextStim(win, color = textColor, pos=[0,0], alignHoriz='center',
                                height = txtH, font=textFont, wrapWidth=20, text=str)
    textString.draw()
    win.flip()
    return;

# define instructions

instructions1 = [
    "WELCOME:\nPlease read these instructions carefully!",
    "For this activity you will do 4 different tasks in a randomized order:",
    "1 - Listen to short sentences or Read them attentively (silently in your"
    + " head i.e. without pronouncing them)",
    "2 - Listen to or Read subtractions\nYou will have to solve them mentally"
    + " i.e. don't say the results out loud",
    "3 - Press three times the left-hand or right-hand button:\nYou have to press the"
    + " button 3 times as fast as possible according to auditory or visual"
    + " instructions (relax the other hand).",
    "4 - Passive viewing of black and white checkerboards\n"
    + "(fixate the center of the checkerboard)",
    "Visual stimulation will consist of groups of words presented fast"
    + " one after another",
    "Here are two examples:"]

examples = [
    "An accident",
    "hapenned",
    "at the entry",
    "of the factory.",
    "+",
    "+",
    "Calculate",
    "ten",
    "minus",
    "three."]

instructions2 = [
    "During each trial try not to move your eyes. A cross (+) will help"
    + " you to keep your gaze at the center of the screen.",
    "Auditory stimulation will sound like the following examples:"
    ]

instructions3 = [
    "ATTENTION:\nTrials will start in a moment\nTry to stay attentive"
    + " throughout (5 minutes)",
    "Please let us know if you have any questions about the task. If not,"
    + " we will start the experiment now."
    ]

# EXPERIMENT STARTS!
# Display instructions
win.setMouseVisible(False) #hide mouse

startMessage = visual.TextStim(win, pos=[-2,0],
            height = 1.5,
            color = 'gray',
            wrapWidth=20,
            text="Experimenter:\nPress space to begin\nPress q during the experiment to quit")
startMessage.draw()
win.flip()
event.waitKeys(keyList=['q','space']) #wait for response

for instruction in instructions1:
    keypresses = event.getKeys()
    try:
        # quit experiment if Q pressed
        if 'q' in chain(*keypresses):
            print('Q pressed - stopping experiment...')
            win.close()
            core.quit()
    except IndexError:
        response = "NA"
    showString(instruction,1.5)
    core.wait(7)
    showString("")

for seg in examples:
    showString(seg)
    core.wait(0.5)
    showString("")

for instruction in instructions2:
    keypresses = event.getKeys()
    try:
        # quit experiment if Q pressed
        if 'q' in chain(*keypresses):
            print('Q pressed - stopping experiment...')
            win.close()
            core.quit()
    except IndexError:
        response = "NA"
    showString(instruction,1.5)
    core.wait(7)
    showString("")

# Play audio example Here
exampleAudio1 = sound.Sound(os.path.join(script_dir,"example_audio1.wav"))
exampleAudio2 = sound.Sound(os.path.join(script_dir,"example_audio2.wav"))

win.flip()
showString("+")
core.wait(0.2)
exampleAudio1.play()
core.wait(2.4)
exampleAudio1.stop()
core.wait(2)
exampleAudio2.play()
core.wait(2.4)
exampleAudio2.stop()
showString("")
core.wait(2)

for instruction in instructions3:
    keypresses = event.getKeys()
    try:
        # quit experiment if Q pressed
        if 'q' in chain(*keypresses):
            print('Q pressed - stopping experiment...')
            win.close()
            core.quit()
    except IndexError:
        response = "NA"
    showString(instruction,1.5)
    core.wait(5)
    showString("")

showString("waiting for MRI trigger...")
event.waitKeys(keyList=['q','5']) #wait for MR trigger
startTime = timer.getTime()
showString("+")
event.waitKeys(keyList=['q','5']) #wait for 2nd MR trigger

# Display Trials
N = 0 # trial counter
startTime = timer.getTime()

for trial in trialList: # step through the trials list
    N += 1 # increment trial counter
    event.clearEvents() # Flush the key buffer
    if trial['modality']=='audio':

        win.flip()
        showString("+")
        # start a (static) preloading ITI period as per trials csv
        staticITI.start(float(trial['ITI']))
        sentAudio = sound.Sound(os.path.join(script_dir,trial['audio']))
        stimulus = trial['audio']
        staticITI.complete()
        # Play Audio Sentence
        sentAudio.play()
        trialOnset = timer.getTime() - startTime
        core.wait(float(trial['seg_dur']))
        sentAudio.stop()
        trialOffset = timer.getTime() - startTime
        expectedDur = float(trial['seg_dur'])

    elif trial['modality']=='visual':

        # Present Sentence Visually
        showString("+")
        core.wait(float(trial['ITI']))
        stimulus = "-".join([trial['string1'],trial['string2'],
                            trial['string3'],trial['string4']])
        showString(trial['string1'])
        trialOnset = timer.getTime() - startTime
        core.wait(float(trial['seg_dur']))
        showString("")
        core.wait(float(trial['ISI']))
        showString(trial['string2'])
        core.wait(float(trial['seg_dur']))
        showString("")
        core.wait(float(trial['ISI']))
        showString(trial['string3'])
        core.wait(float(trial['seg_dur']))
        showString("")
        core.wait(float(trial['ISI']))
        showString(trial['string4'])
        core.wait(float(trial['seg_dur']))
        trialOffset = timer.getTime() - startTime
        expectedDur = 4*(float(trial['seg_dur'])) + 3*(float(trial['ISI']))

    elif trial['modality']=='checkerH':

        showString("+")
        core.wait(float(trial['ITI']))
        stimulus = trial['modality']
        trialOnset = timer.getTime() - startTime
        # Show Horizontal Checkerboard
        for x in range(6): # repeat
            win.flip()
            checkH1.draw()
            win.flip()
            core.wait(float(trial['ISI']))
            checkH2.draw()
            win.flip()
            core.wait(float(trial['ISI']))
        trialOffset = timer.getTime() - startTime
        expectedDur = 12*(float(trial['ISI']))


    elif trial['modality']=='checkerV':

        showString("+")
        core.wait(float(trial['ITI']))
        stimulus = trial['modality']
        trialOnset = timer.getTime() - startTime
        # Show Vertical Checkerboard
        for x in range(6): # repeat
            win.flip()
            checkV1.draw()
            win.flip()
            core.wait(float(trial['ISI']))
            checkV2.draw()
            win.flip()
            core.wait(float(trial['ISI']))
        trialOffset = timer.getTime() - startTime
        expectedDur = 12*(float(trial['ISI']))
    keypresses = event.getKeys()
    try:
        # quit experiment if Q pressed
        if 'q' in chain(*keypresses):
            print('Q pressed - stopping experiment...')
            win.close()
            core.quit()
    except IndexError:
        response = "NA"
    dataFile_Stim.write(
        '%i,%s,%i,%s,%s,%s,%.3f,%.3f,%.3f\n' %(N,expInfo['subjID'],
        expInfo['session'],trial['modality'],trial['type'],stimulus,trialOnset,trialOffset,expectedDur)
    )


dataFile_Stim.close()
showString("Task Complete!")
endTime = timer.getTime() - startTime
print(endTime)
event.waitKeys(keyList=['q','space'])
win.close()
core.quit()
