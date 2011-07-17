#!/usr/bin/env python -OO
import pygame, state, subprocess
from pygame.locals import *
from workout import *
from gui import *
from time import time,sleep
from os import system

pygame.init()

# Lazily attempt to optimize with psyco
# if it exists, and import gobject.
# If one of these fail, just ignore it.
try:
	import psyco
	psyco.full()
except ImportError:
	pass

try:
	import gobject
except ImportError:
	pass

# Change the res here if you want.
RES = (800,480)

# But don't touch this if you want the script to
# do anything :)
RUNNING = True

# Check whether we're running on a mobile device,
# based on `uname -a` output.
# NOTE: This needs changing to accomodate for Android
# devices too!
system('uname -a > os.txt')
MOBILE = False
if 'Nokia-N900' in open('os.txt','r').read():
	MOBILE = True

# Quit and save 'week' and 'workout' variables to state.py
# (state.py is imported when starting this script)
def quit():
	global RUNNING
	RUNNING = False
	f = open('state.py','w+')
	f.write('week = '+str(state.week)+'\nworkout = '+str(state.workout)+'\n')
	f.close()

def start():
	global w
	w.start(time())

def say(string):
	if MOBILE: process = '/usr/bin/espeak'
	else: process = '/usr/bin/say'
	subprocess.Popen([process,str(string)])

def set(week=0,workout=0):
	if (state.week+week) in range(1,10) and (state.workout+workout) in range(1,4):
		state.week += week
		state.workout += workout
	w = Workout(state.week,state.workout)
	labels['status'].text = 'Week: '+str(state.week)+', Workout: '+str(state.workout)

# Prettify seconds into a string
def minutes(n):
	min = str(int(n/60) % 60)
	sec = str(int(n) % 60)

	return ('0'*(2-len(min)))+min+':'+('0'*(2-len(sec)))+sec

# If on a mobile device, run fullscreen, without cursor, since it's
# a touchscreen. Otherwise, run in a window, the size defined in RES
# at the top of this file.
if MOBILE == True:
	RES = (pygame.display.Info().current_w,pygame.display.Info().current_h)
	screen = pygame.display.set_mode(RES,FULLSCREEN|SRCALPHA)
	pygame.mouse.set_visible(False)
else:
	screen = pygame.display.set_mode(RES,SRCALPHA)

# This part is horrible to look at. It's responsible for scaling + placing
# the UI elements correctly on the screen, resolution-independent.
FRES = RES[0]*RES[1]/1000
initFonts(FRES)
pygame.display.set_caption("Couch to 5k Coach")
c = pygame.time.Clock()
w = Workout(state.week,state.workout)
background = pygame.image.load('footsteps_in_the_desert.jpg')
background = pygame.transform.smoothscale(background, RES)
buttons = {
	'quit': Button('Quit',(690,10),f=quit,font=fonts['h1']),
	'start': Button('Start!',(10,10),f=start,font=fonts['h1']),
	'weekPlus': Button('Week +',(10,0),f=lambda: set(1,0),font=fonts['h2']),
	'weekMinus': Button('Week -',(10,0),f=lambda: set(-1,0),font=fonts['h2']),
	'workoutPlus': Button('Workout +',(10,0),f=lambda: set(0,1),font=fonts['h2']),
	'workoutMinus': Button('Workout -',(10,0),f=lambda: set(0,-1),font=fonts['h2'])
}
buttons['quit'].right = RES[0]-10
padding = distances([buttons['weekPlus'],buttons['weekMinus'],buttons['workoutPlus'],buttons['workoutMinus']])
buttons['weekMinus'].left = (padding[0])+20
buttons['workoutMinus'].left = (padding[0])+20
for b in ['Plus','Minus']:
	buttons['week'+b].top = RES[1]-(2*padding[1])-20
	buttons['week'+b].size = padding[0:2]
	buttons['workout'+b].top = RES[1]-padding[1]-10
	buttons['workout'+b].size = padding[0:2]

labels = {
	'hello': Label('Ready?',(10,0),font=fonts['h2']),
	'status': Label('Week: '+str(state.week)+', Workout: '+str(state.workout),(10,0),font=fonts['h1']),
	'command': Label('',(0,0),font=fonts['huge']),
	'distanceTxt': Label('Distance Travelled',(10,0),font=fonts['h2']),
	'distance': Label('0.0 mi.',(0,0),font=fonts['huge'])
}
tmpPad = distances(labels.values(),'max')
labels['hello'].centery = (RES[1]/2)-(tmpPad[1]+buttons['weekPlus'].height)
labels['status'].centery = (RES[1]/2)-buttons['weekPlus'].height
labels['distanceTxt'].centery = (RES[1]/2)+(tmpPad[1]-buttons['weekPlus'].height)
labels['command'].right = RES[0]-10
labels['command'].centery = (RES[1]/2)-((tmpPad[1]-20)+buttons['weekPlus'].height)
labels['distance'].right = RES[0]-10
labels['distance'].centery = (RES[1]/2)+(tmpPad[1]-buttons['weekPlus'].height)
labelBgRect = pygame.rect.Rect(0,labels['hello'].top-10,RES[0],0)
labelBgRect.height = (labels['distance'].bottom+10)-(labels['hello'].top-10)
labelBg = pygame.Surface((labelBgRect.width,labelBgRect.height),SRCALPHA)
labelBg.fill(pygame.Color(0,0,0,160),(0,0,RES[0],labelBgRect.height))

change = ''

# Set up gobject loop to play nicely with my own main loop.
try:
	loop = gobject.MainLoop()
	gobject.threads_init()
	context = loop.get_context()
except:
	pass

# MAKE IT HAPEN
while RUNNING:
	if w.started:

		details = w.get(time())
		if change != details[0]:
			say(details[0]+'\n')
			change = details[0]

		# Update elapsed time and distance travelled.
		# Make sure labels are still aligned to the right of
		# the screen correctly.
		labels['hello'].text = minutes(details[1])+' elapsed'
		labels['command'].text = details[0]
		labels['command'].right = RES[0]-10
		labels['distance'].text = str(w.distance)+' mi.'

		# Play nice, gobject.
		try:
			context.iteration(False)
		except:
			pass

	for e in pygame.event.get():
		if e.type == QUIT:
			quit()
		elif e.type == KEYDOWN:
			if e.key == K_ESCAPE:
				quit()
		# Check for button clicks
		elif e.type == MOUSEBUTTONDOWN:
			map((lambda button: Button.down(button,e.pos)),buttons.values())
		elif e.type == MOUSEBUTTONUP:
			map((lambda button: Button.up(button,e.pos)),buttons.values())

	screen.blit(background,(0,0))
	screen.blit(labelBg,labelBgRect)

	# Draw the UI elements
	map((lambda button: Button.draw(button,screen)),buttons.values())
	map((lambda label: Label.draw(label,screen)),labels.values())

	pygame.display.flip()

	# Sleep a little to save some CPU. Since nothing needs less than a second
	# for update granularity. This obviously makes the UI less responsive however.
	if MOBILE:
		sleep(0.5)