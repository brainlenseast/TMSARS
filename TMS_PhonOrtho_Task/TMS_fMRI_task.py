# TMS R01 Study
# Phonological and Orthographic task for pre/post cTBS fMRI scans - 293 sec
# Nikola Vukovic, Dec 2018

# Initialise Python Libraries
from psychopy import core, visual, gui, data, misc, event, logging, sound, clock
import time, os, serial, csv, random, sys, threading
from itertools import chain
import numpy as np
import pandas as pd
from random import shuffle
import time

# present a dialogue to input subject params
expInfo = {'subjID':'0001','site':['LeftTP','RightTP','LeftPreCG','Vertex'],'session':['PreTMS','PostTMS'], 'run':[1,2,3]}
dictDlg = gui.DlgFromDict(dictionary=expInfo,
        title='Session Parameters', order=['subjID', 'site', 'session', 'run'])
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
script_dir = os.path.dirname(__file__) # absolute path to python script

textHeight = 2
textColor = 'white'
regularFont=['Arial']
falseFont=['BACS2sans']

timer = core.Clock() #to keep track of time
timestr = time.strftime("%Y%m%d%H%M")

# Define backgound sounds to play during phono/ortho tasks
metronome = sound.Sound(os.path.join(script_dir,"metro_loop.wav"))
CVC = sound.Sound(os.path.join(script_dir,"dop_loop.wav"))

metronome_playing = False
CVC_playing = False

# Log file to save timings
datafileName = 'data/' + expInfo['subjID'] + '_' + str(expInfo['site']) + '_' + str(expInfo['session']) + '_' + str(expInfo['run']) + '_resp_' + timestr
dataFile_Stim = open(datafileName+'.csv', 'w')
dataFile_Stim.write('trial,site,session,run,block,subjID,condition,judgement,context,stim1,stim2,onset,offset,corr_resp,resp,rt\n')

# Define trials from csv
if expInfo['site'] == 'LeftTP':
    # load left TP trials
    if expInfo['session'] == 'PreTMS':
        if expInfo['run'] == 1:
            csv_file = "trial_list/trials_ses1_run1.csv"
        elif expInfo['run'] == 2:
            csv_file = "trial_list/trials_ses1_run2.csv"
        elif expInfo['run'] == 3:
            csv_file = "trial_list/trials_ses1_run3.csv"
    elif expInfo['session'] == 'PostTMS':
        if expInfo['run'] == 1:
            csv_file = "trial_list/trials_ses1_run4.csv"
        elif expInfo['run'] == 2:
            csv_file = "trial_list/trials_ses1_run5.csv"
        elif expInfo['run'] == 3:
            csv_file = "trial_list/trials_ses1_run6.csv"
elif expInfo['site'] == 'RightTP':
    # load right TP trials
    if expInfo['session'] == 'PreTMS':
        if expInfo['run'] == 1:
            csv_file = "trial_list/trials_ses2_run1.csv"
        elif expInfo['run'] == 2:
            csv_file = "trial_list/trials_ses2_run2.csv"
        elif expInfo['run'] == 3:
            csv_file = "trial_list/trials_ses2_run3.csv"
    elif expInfo['session'] == 'PostTMS':
        if expInfo['run'] == 1:
            csv_file = "trial_list/trials_ses2_run4.csv"
        elif expInfo['run'] == 2:
            csv_file = "trial_list/trials_ses2_run5.csv"
        elif expInfo['run'] == 3:
            csv_file = "trial_list/trials_ses2_run6.csv"
elif expInfo['site'] == 'LeftPreCG':
    # load Left M1 trials
    if expInfo['session'] == 'PreTMS':
        if expInfo['run'] == 1:
            csv_file = "trial_list/trials_ses3_run1.csv"
        elif expInfo['run'] == 2:
            csv_file = "trial_list/trials_ses3_run2.csv"
        elif expInfo['run'] == 3:
            csv_file = "trial_list/trials_ses3_run3.csv"
    elif expInfo['session'] == 'PostTMS':
        if expInfo['run'] == 1:
            csv_file = "trial_list/trials_ses3_run4.csv"
        elif expInfo['run'] == 2:
            csv_file = "trial_list/trials_ses3_run5.csv"
        elif expInfo['run'] == 3:
            csv_file = "trial_list/trials_ses3_run6.csv"
elif expInfo['site'] == 'Vertex':
    # load Vertex trials
    if expInfo['session'] == 'PreTMS':
        if expInfo['run'] == 1:
            csv_file = "trial_list/trials_ses4_run1.csv"
        elif expInfo['run'] == 2:
            csv_file = "trial_list/trials_ses4_run2.csv"
        elif expInfo['run'] == 3:
            csv_file = "trial_list/trials_ses4_run3.csv"
    elif expInfo['session'] == 'PostTMS':
        if expInfo['run'] == 1:
            csv_file = "trial_list/trials_ses4_run4.csv"
        elif expInfo['run'] == 2:
            csv_file = "trial_list/trials_ses4_run5.csv"
        elif expInfo['run'] == 3:
            csv_file = "trial_list/trials_ses4_run6.csv"

# Import comma separated trial list
trial_csv = pd.read_csv(csv_file)

# Components to present text strings
def showOneString(str,txtH=textHeight,textFont=regularFont,textColor=textColor):
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
    "Instructions006.jpeg",
    "Instructions007.jpeg",
    "Instructions008.jpeg"
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
    keypresses = event.getKeys()
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
showOneString("mri trigger wait...",textColor="green")
event.waitKeys(keyList=['q','5']) #wait for MR trigger
startTime = timer.getTime()
showOneString("+",textColor="green")
event.waitKeys(keyList=['q','5']) #wait for 2nd MR trigger
dataFile_Stim = open(datafileName+'.csv', 'a')
clock = core.Clock()

for trial in trial_csv.itertuples():
    event.clearEvents() # Flush the key buffer
    if trial.instr_start == 1:
        # New Task Starts - Show Instructions
        if trial.context == 'cvc_metronome':
            CVC.stop()
            metronome.play()
            showOneString("Covertly repeat the word 'dop' in time with the metronome!",textColor="green")
            core.wait(3)
            showOneString("+")
            core.wait(random.uniform(0.5, 1.5)) # jitter onset
        elif trial.context == 'metronome_only':
            CVC.stop()
            metronome.play()
            showOneString("Just listen to the metronome without moving!",textColor="green")
            core.wait(3)
            showOneString("+")
            core.wait(random.uniform(0.5, 1.5)) # jitter onset
        elif trial.context == 'cvc_only':
            metronome.stop()
            CVC.play()
            showOneString("Just listen to the sound without moving!",textColor="green")
            core.wait(3)
            showOneString("+")
            core.wait(random.uniform(0.5, 1.5)) # jitter onset
        elif trial.context == 'control':
            metronome.stop()
            CVC.stop()
            showOneString("Just stay still!",textColor="green")
            core.wait(2)
            showOneString("+",textColor="green")
            core.wait(random.uniform(0.5, 1.5)) # jitter onset
        else:
            metronome.stop()
            CVC.stop()
            showOneString("+",textColor="green")
            core.wait(random.uniform(0.5, 1.5)) # jitter onset

        if trial.judgement == 'rhyming':
            textFont = regularFont
            showOneString("Do the words rhyme?",textColor="green")
            core.wait(2)
        elif trial.judgement == 'identity':
            if trial.condition == 'false_font':
                textFont = falseFont
                showOneString("Are the symbols the same?",textColor="green")
            else:
                textFont = regularFont
                showOneString("Are the words the same?",textColor="green")
            core.wait(2)
        elif trial.judgement == 'fixation':
            keypresses = event.getKeys(keyList=['1','2','3','4','q'])
            try:
                # quit experiment if Q pressed
                if 'q' in chain(*keypresses):
                    print('Q pressed - stopping experiment...')
                    win.close()
                    core.quit()
            except IndexError:
                response = "NA"
            textFont = regularFont
            showOneString("+")
            stimOnset = timer.getTime() - startTime
            core.wait(15)
            stimOffset = timer.getTime() - startTime
            response = "NA"
            responseRT = 0
            dataFile_Stim.write(
                '%i,%s,%s,%i,%s,%s,%s,%s,%s,%s,%s,%.3f,%.3f,%s,%s,%.3f\n' %(trial.trial,
                expInfo['site'],expInfo['session'],expInfo['run'],trial.block,
                expInfo['subjID'],trial.condition,trial.judgement,
                trial.context,trial.word1,trial.word2,stimOnset,stimOffset,
                trial.correct_resp,response,responseRT)
            )

            continue

    ## Present Trial
    clock.reset()
    showTwoStrings(trial.word1,trial.word2,textHeight,textFont)
    stimOnset = timer.getTime() - startTime
    core.wait(2,hogCPUperiod=2)
    stimOffset = timer.getTime() - startTime
    showOneString("+")
    iti = random.uniform(1, 2)
    core.wait(iti,hogCPUperiod=iti) # ITI random jitter 1-2 sec
    keypresses = event.getKeys(keyList=['1','2','3','4','q'],timeStamped=clock)
    try:
        if 'q' in chain(*keypresses):
            print('Q pressed - stopping experiment...')
            CVC.stop()
            metronome.stop()
            win.close()
            core.quit()
        response = keypresses[0][0]
    except IndexError:
        response = "NA"
    try:
        responseRT = keypresses[0][1]
    except IndexError:
        responseRT = 0

    dataFile_Stim.write(
        '%i,%s,%s,%i,%s,%s,%s,%s,%s,%s,%s,%.3f,%.3f,%s,%s,%.3f\n' %(trial.trial,
        expInfo['site'],expInfo['session'],expInfo['run'],trial.block,
        expInfo['subjID'],trial.condition,trial.judgement,
        trial.context,trial.word1,trial.word2,stimOnset,stimOffset,
        trial.correct_resp,response,responseRT)
    )

dataFile_Stim.close()
CVC.stop()
metronome.stop()
endTime = timer.getTime() - startTime
print(endTime)
showOneString("Task Complete!",textColor="green")
event.waitKeys(keyList=['q','space'])
win.close()
core.quit()
