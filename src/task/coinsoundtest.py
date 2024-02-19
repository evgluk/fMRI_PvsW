#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from psychopy import logging, prefs
logging.console.setLevel(logging.DEBUG)  # get messages about the sound lib as it loads

prefs.hardware['audioLib'] = ['pygame'] # sets pygame as the preffered sound library, needed to be able to use .play(loops = ...)

from psychopy import sound, core

coinsound = sound.Sound('coin_echo5.wav')
coinsound.play()
core.wait(2)
coinsound.play(loops = 4)
core.wait(4)
coinsound.play(loops = 15)
core.wait(10)
print('all coin sounds played')

core.quit()

