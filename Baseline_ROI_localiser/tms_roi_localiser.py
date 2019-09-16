# fMRI Functional Localiser for Phon/Ortho TMS ROIs.
# duration 338 sec

# Initialise Python Libraries
from psychopy import core, visual, gui, data, misc, event, logging, sound, clock
import time, os, serial, csv, random, sys, threading
from itertools import chain
import numpy as np
import pandas as pd
from random import shuffle
import time

timer = core.Clock() #to keep track of time
timestr = time.strftime("%Y%m%d%H%M")
experimentStart = timer.getTime()

expInfo = {'subjID':'0001', 'run':[1,2]}
dictDlg = gui.DlgFromDict(dictionary=expInfo,
        title='Session Parameters', order=['subjID', 'run'])
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

# Some Global Properties and Components
# Import comma separated trial list as dictionary
script_dir = os.path.dirname(__file__) # absolute path to python script

# Log file to save timings
datafileName = 'data/' + expInfo['subjID'] + '_run' + str(expInfo['run']) + '_resp_' + timestr
dataFile_Stim = open(datafileName+'.csv', 'w')
dataFile_Stim.write('trial,subjID,run,task,stim1,stim2,onset,corr_resp,resp,rt\n')

textHeight = 2
textColor = 'white'
regularFont=['Arial']
falseFont=['BACS2sans']

# Define trials from csv
if expInfo['run'] == 1:
    csv_file = "trial_list/trials_run1.csv"
elif expInfo['run'] == 2:
    csv_file = "trial_list/trials_run2.csv"

trial_csv = pd.read_csv(csv_file)

# Components to present text strings

def showOneString(str,txtH=textHeight,textFont=regularFont):
    win.flip()
    textString = visual.TextStim(win, color = textColor, pos=[0,0],
                                alignHoriz='center', height = txtH,
                                font=textFont, wrapWidth=20, text=str)
    textString.draw()
    win.flip()
    return;

def showTwoStrings(str1,str2,txtH=textHeight,textFont=regularFont):
    win.flip()
    textString1 = visual.TextStim(win, color = textColor, pos=[0,3],
                                alignHoriz='center', height = txtH,
                                font=textFont, wrapWidth=20, text=str1)
    fixationString = visual.TextStim(win, color = textColor, pos=[0,0],
                                alignHoriz='center', height = txtH,
                                font=textFont, wrapWidth=20, text="+")
    textString2 = visual.TextStim(win, color = textColor, pos=[0,-3],
                                alignHoriz='center', height = txtH,
                                font=textFont, wrapWidth=20, text=str2)
    textString1.draw()
    fixationString.draw()
    textString2.draw()
    win.flip()
    return;

# Define Instructions

instructions = [
    "Instructions001.jpeg",
    "Instructions002.jpeg",
    "Instructions003.jpeg",
    "Instructions004.jpeg",
    "Instructions005.jpeg",
    "Instructions006.jpeg"
    ]

instructions_short = [
    "ShortInstructions001.jpeg"
    ]

# PRESENT INSTRUCTIONS
win.setMouseVisible(False) #hide mouse
startMessage = visual.TextStim(win, pos=[-2,0],
            height = 1.5,
            color = 'gray',
            wrapWidth=20,
            text="Experimenter:\nPress space to begin\nPress q during the experiment to quit")
startMessage.draw()
win.flip()
event.waitKeys(keyList=['q','space']) #wait for response

if expInfo['run'] == 1:
    present_instr = instructions
    waittime = 5
else:
    present_instr = instructions_short
    waittime = 10

for instruction in present_instr:
    keypresses = event.getKeys(keyList=['1','2','3','4','q'])
    try:
        # quit experiment if Q pressed
        if 'q' in chain(*keypresses):
            print('Q pressed - stopping experiment...')
            win.close()
            core.quit()
    except IndexError:
        response = "NA"
    instructionImg = visual.ImageStim(win,image=os.path.join(script_dir,'Instructions', instruction), pos = (0, 0))
    instructionImg.draw()
    win.flip()
    core.wait(waittime)


# PRESENT TRIALS HERE
showOneString("mri trigger wait...")
event.waitKeys(keyList=['q','5']) #wait for MR trigger
startTime = timer.getTime()
showOneString("+")
event.waitKeys(keyList=['q','5']) #wait for 2nd MR trigger
dataFile_Stim = open(datafileName+'.csv', 'a')
clock = core.Clock()

for trial in trial_csv.itertuples():
    if trial.instr_start == 1:
        # New Task Starts - Show Instructions
        if trial.judgement == 'rhyming':
            textFont = regularFont
            showOneString("Decide: Do the words rhyme?")
            core.wait(2)
        elif trial.judgement == 'identity':
            textFont = falseFont
            showOneString("Decide: Are the letter strings the same?")
            core.wait(2)
        elif trial.judgement == 'fixation':
            textFont = regularFont
            showOneString("+")
            stimOnset = timer.getTime() - startTime
            core.wait(14)
            response = "NA"
            responseRT = 0
            dataFile_Stim.write(
                '%s,%s,%i,%s,%s,%s,%.3f,%s,%s,%.3f\n' %(trial.trial,expInfo['subjID'],
                expInfo['run'],trial.condition,trial.word1,trial.word2,stimOnset,trial.correct_resp,response,responseRT)
            )

            continue

    ## Present Trial
    event.clearEvents() #Flush the key buffer
    showTwoStrings(trial.word1,trial.word2,textHeight,textFont)
    clock.reset()
    stimOnset = timer.getTime() - startTime
    core.wait(2,hogCPUperiod=2)
    showOneString("+")
    iti = random.uniform(1, 2)
    core.wait(iti,hogCPUperiod=iti) #ITI
    keypresses = event.getKeys(keyList=['1','2','3','4','q'],timeStamped=clock)
    try:
        # quit experiment if Q pressed
        if 'q' in chain(*keypresses):
            print('Q pressed - stopping experiment...')
            win.close()
            core.quit()
        response = keypresses[0][0]
    except IndexError:
        response = "NA"
    try:
        responseRT = keypresses[0][1]
    except IndexError:
        responseRT = 0
    print(response + " speed: " + str(responseRT))
    dataFile_Stim.write(
        '%s,%s,%i,%s,%s,%s,%.3f,%s,%s,%.3f\n' %(trial.trial,expInfo['subjID'],
        expInfo['run'],trial.condition,trial.word1,trial.word2,stimOnset,trial.correct_resp,response,responseRT)
    )

dataFile_Stim.close()
showOneString("Task Complete!")
event.waitKeys(keyList=['q','space'])
win.close()
core.quit()
