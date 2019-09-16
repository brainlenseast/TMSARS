# TMS R01 Study
# Motor fMRI localiser task - mouth and lips movements - 307 sec
# Nikola Vukovic, Sep 2018

# Initialise Python Libraries
from psychopy import core, visual, gui, data, misc, event, logging, sound, clock
import time, os, serial, csv, random, sys, threading
from itertools import chain
import numpy as np
from random import shuffle
import time

# present a dialogue to input subject params

expInfo = {'subjID':'0001', 'run':1}
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

timer = core.Clock() #to keep track of time
timestr = time.strftime("%Y%m%d%H%M")
script_dir = os.path.dirname(__file__) # absolute path to python script

# Log file to save timings
datafileName = 'data/' + expInfo['subjID'] + '_run' + str(expInfo['run']) + '_motor_' + timestr
dataFile_Stim = open(datafileName+'.csv', 'w')
dataFile_Stim.write('block,subjID,run,condition,onset,offset\n')

# pucture prompts
tongueLeft = visual.ImageStim(win,
                              image=os.path.join(script_dir,"tongue_left.png"),
                              pos = (0, 0))
tongueRight = visual.ImageStim(win,
                              image=os.path.join(script_dir,"tongue_right.png"),
                              pos = (0, 0))
puckerLeft = visual.ImageStim(win,
                             image=os.path.join(script_dir, "pucker_left.png"),
                             pos = (0, 0))
puckerRight = visual.ImageStim(win,
                             image=os.path.join(script_dir, "pucker_right.png"),
                              pos = (0, 0))

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

instructions = [
    "WELCOME:\nPlease read these instructions carefully!",
    "In this task, you will make small movements with your lips and tongue. Please keep your head still while making these movements.",
    "A picture prompt will tell you whether to move the lips or the tongue.",
    "TONGUE MOVEMENT:\nMove your tongue side to side, as shown in the picture, with your lips closed and without moving the jaw.",
    "LIPS MOVEMENT:\nPucker your lips back and forth, as if kissing, without moving the head."]

# ESPERIMENT STARTS!
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

for instruction in instructions:
    showString(instruction,1.5)
    core.wait(5)
    showString("")

showString("waiting for MRI trigger...")
event.waitKeys(keyList=['q','5']) #wait for MR trigger
startTime = timer.getTime()
showString("+")
event.waitKeys(keyList=['q','5']) #wait for 2nd MR trigger

# experiment start
# Display Blocks: Tongue, Lips, and Rest
blockList = ['tongue', 'lips', 'tongue', 'lips', 'lips', 'tongue', 'lips',
          'tongue', 'tongue', 'lips']
N = 0 # block counter

for block in blockList: # step throught block list
    win.flip()
    if block=='tongue':
        # present tongue animation at 0.4Hz for 15 sec
        stimOnset = timer.getTime() - startTime
        condition = "tongue"
        N += 1
        for x in range(18):
            event.clearEvents() # Flush the key buffer
            tongueLeft.draw()
            win.flip()
            core.wait(0.415)
            tongueRight.draw()
            win.flip()
            core.wait(0.415)
            keypresses = event.getKeys(keyList=['1','2','3','4','q'])
            try:
                # quit experiment if Q pressed
                if 'q' in chain(*keypresses):
                    print('Q pressed - stopping experiment...')
                    win.close()
                    core.quit()
            except IndexError:
                response = "NA"
        stimOffset = timer.getTime() - startTime
        dataFile_Stim.write(
            '%i,%s,%i,%s,%.3f,%.3f\n' %(N,expInfo['subjID'],
            expInfo['run'],condition,stimOnset,stimOffset)
        )

    elif block=='lips':
        # present lips animation at 0.4Hz for 15 sec
        stimOnset = timer.getTime() - startTime
        condition = "lips"
        N += 1
        for y in range(18):
            event.clearEvents() # Flush the key buffer
            puckerLeft.draw()
            win.flip()
            core.wait(0.415)
            puckerRight.draw()
            win.flip()
            core.wait(0.415)
            keypresses = event.getKeys(keyList=['1','2','3','4','q'])
            try:
                # quit experiment if Q pressed
                if 'q' in chain(*keypresses):
                    print('Q pressed - stopping experiment...')
                    win.close()
                    core.quit()
            except IndexError:
                response = "NA"
        stimOffset = timer.getTime() - startTime
        dataFile_Stim.write(
            '%i,%s,%i,%s,%.3f,%.3f\n' %(N,expInfo['subjID'],
            expInfo['run'],condition,stimOnset,stimOffset)
        )
    # present fixation rest period
    stimOnset = timer.getTime() - startTime
    showString("+")
    condition = "fixation"
    N += 1
    core.wait(15) # wait 15 sec
    stimOffset = timer.getTime() - startTime
    # save log
    dataFile_Stim.write(
        '%i,%s,%i,%s,%.3f,%.3f\n' %(N,expInfo['subjID'],
        expInfo['run'],condition,stimOnset,stimOffset)
    )

dataFile_Stim.close()
showString("Task Complete!")
event.waitKeys(keyList=['q','space'])
win.close()
core.quit()
