#!/usr/bin/env python -OO
import pygame, state, subprocess
from commands import getoutput
from pygame.locals import *
from workout import *
from gui import *
from time import time,strftime,localtime,sleep
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
	f.write('gps = '+str(buttons['gpsToggle'].pressed)+'\nsound = '+str(buttons['soundToggle'].pressed)+'\n')
	f.close()

def minimize():
	if MOBILE:
		system("dbus-send /com/nokia/hildon_desktop com.nokia.hildon_desktop.exit_app_view")
	else:
		pygame.display.iconify()

def getBattery():
	try:
		out = getoutput('lshal | grep battery.charge_level.percentage').split(' ')[4]
		return int(out)
	except:
		return 0

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
	return strftime('%M:%S',localtime(n))

# If on a mobile device, run fullscreen, without cursor, since it's
# a touchscreen. Otherwise, run in a window, the size defined in RES
# at the top of this file.
flags = 0
if MOBILE == True:
	RES = (pygame.display.Info().current_w,pygame.display.Info().current_h)
	flags = FULLSCREEN
	pygame.mouse.set_visible(False)
else:
	flags = RESIZABLE
pygame.display.set_mode(RES,flags|SRCALPHA)

# This part is horrible to look at. It's responsible for scaling + placing
# the UI elements correctly on the screen, resolution-independent.
pygame.display.set_caption("Couch to 5k Coach")
c = pygame.time.Clock()
w = Workout(state.week, state.workout)
bell = pygame.mixer.Sound('bicycle_bell.wav')
bg = pygame.image.load('jogger.jpg')
background = pygame.transform.smoothscale(bg, RES)
FRES = RES[0]*RES[1]/1000
fonts = initFonts(FRES)

buttons = {
	'minimize': Button(' - ', (10,10),f=minimize,font='h1'),
	'quit': Button(' x ',(690,10),f=quit,font='h1'),
	'start': Button('Start!',(10,10),f=start,font='huge'),
	'weekPlus': Button('Week +',(10,0),f=lambda: set(1,0),font='h2'),
	'weekMinus': Button('Week -',(10,0),f=lambda: set(-1,0),font='h2'),
	'workoutPlus': Button('Workout +',(10,0),f=lambda: set(0,1),font='h2'),
	'workoutMinus': Button('Workout -',(10,0),f=lambda: set(0,-1),font='h2'),
	'gpsToggle': ToggleButton('GPS',(10,0),font='h2'),
	'soundToggle': ToggleButton('Sound', (10,0),font='h2')
}

labels = {
	'hello': Label('Ready?',(10,0),font='h2'),
	'status': Label('Week: '+str(state.week)+', Workout: '+str(state.workout),(10,0),font='h1'),
	'command': Label('',(0,0),font='huge'),
	'distanceTxt': Label('Distance Travelled',(10,0),font='h2'),
	'distance': Label('0.0 mi.',(0,0),font='huge'),
	'time': Label('00:00',(0,10),font='h2'),
	'battery': Label('100%',(0,20),font='h2')
}

def setupUI():
	global background,buttons,labels,labelBg,labelBgRect,screen,flags,fonts
	FRES = min(RES)
	fonts = initFonts(FRES)
	for b in buttons.values():
		b.font = fonts[b.fontName]
	for l in labels.values():
		l.font = fonts[l.fontName]

	screen = pygame.display.set_mode(RES, flags|SRCALPHA)
	background = pygame.transform.smoothscale(bg, RES)
	buttons['quit'].right = RES[0]-10
	buttons['start'].centerx = RES[0]/2
	padding = distances([buttons['weekPlus'],buttons['weekMinus'],buttons['workoutPlus'],buttons['workoutMinus'],buttons['gpsToggle'],buttons['soundToggle']])
	buttons['weekMinus'].left = (padding[0])+20
	buttons['workoutMinus'].left = (padding[0])+20
	for b in ['Plus','Minus']:
		buttons['week'+b].top = RES[1]-(2*padding[1])-20
		buttons['week'+b].size = padding[0:2]
		buttons['workout'+b].top = RES[1]-padding[1]-10
		buttons['workout'+b].size = padding[0:2]
	padding = distances([buttons['gpsToggle'],buttons['soundToggle']])
	for b in ['gps','sound']:
		buttons[b+'Toggle'].size = padding[0:2]
		buttons[b+'Toggle'].right = RES[0]-10
		line = compile("buttons['"+b+"Toggle'].pressed = state."+b,'<string>','single')
		exec line in globals(),locals()
		buttons[b+'Toggle'].update()
	buttons['gpsToggle'].top = RES[1]-(2*padding[1])-20
	buttons['soundToggle'].top = RES[1]-padding[1]-10
	tmpPad = distances(labels.values(),'max')
	tmpPad[1] -= 10
	labels['time'].right = buttons['quit'].left-10
	labels['battery'].right = buttons['quit'].left-10
	labels['battery'].top = labels['time'].bottom
	labels['battery'].text = str(getBattery())+'%'
	labels['hello'].centery = (RES[1]/2)-(tmpPad[1]+buttons['weekPlus'].height)
	labels['status'].centery = (RES[1]/2)-buttons['weekPlus'].height
	labels['distanceTxt'].centery = (RES[1]/2)+(tmpPad[1]-buttons['weekPlus'].height)
	labels['command'].right = RES[0]-10
	#labels['command'].centery = (RES[1]/2)-((tmpPad[1]-20)+buttons['weekPlus'].height)
	labels['command'].top = labels['hello'].top
	labels['distance'].right = RES[0]-10
	labels['distance'].centery = (RES[1]/2)+(tmpPad[1]-buttons['weekPlus'].height)
	labelBgRect = pygame.rect.Rect(0,labels['hello'].top-10,RES[0],0)
	labelBgRect.height = (labels['distance'].bottom+20)-(labels['hello'].top-10)
	labelBg = pygame.Surface((labelBgRect.width,labelBgRect.height),SRCALPHA)
	labelBg.fill(pygame.Color(0,0,0,160),(0,0,RES[0],labelBgRect.height))
	labelBg.fill(pygame.Color(0,0,0,230),(0,labelBgRect.height-20,RES[0],labelBgRect.height))
	# END OF HORRIBLE CODE CHUNK

change = ''

# Set up gobject loop to play nicely with my own main loop.
try:
	loop = gobject.MainLoop()
	gobject.threads_init()
	context = loop.get_context()
except:
	pass

setupUI()

# MAKE IT HAPEN
while RUNNING:
	if w.started:

		details = w.get(time())

		# Update elapsed time and distance travelled.
		# Make sure labels are still aligned to the right of
		# the screen correctly.
		labels['hello'].text = minutes(details[1])+' elapsed'
		labels['command'].text = details[0]
		labels['command'].right = RES[0]-10
		labels['distance'].text = str(w.distance)+' mi.'
		labelBg.fill(pygame.Color(0,int(details[2]),int(150+(details[2]*1.05)),230),
			(0,labelBgRect.height-20,(details[2]*(RES[0]/100)),labelBgRect.height))
		
		if details[0] == 'Finished!':
			try:
				w.gpsControl.stop()
			except:
				pass
			w.started = False
		if change != details[0]:
			if buttons['soundToggle'].pressed:
				bell.play()
				say(details[0]+'\n')
			labels['battery'].text = str(getBattery())+'%'
			change = details[0]

		# Play nice, gobject.
		try:
			if buttons['gpsToggle'].pressed:
				context.iteration(False)
		except:
			pass

	labels['time'].text = strftime('%H:%M',localtime())

	for e in pygame.event.get():
		if e.type == QUIT:
			quit()
		elif e.type == KEYDOWN:
			if e.key == K_ESCAPE:
				quit()
		# Check for button clicks
		elif e.type == MOUSEBUTTONDOWN:
			#map((lambda button: button.down(e.pos)),buttons.values())
			[button.down(e.pos) for button in buttons.values()]
		elif e.type == MOUSEBUTTONUP:
			#map((lambda button: button.up(e.pos)),buttons.values())
			[button.up(e.pos) for button in buttons.values()]
		elif e.type == VIDEORESIZE:
			RES = e.size
			setupUI()

	screen.blit(background,(0,0))
	screen.blit(labelBg,labelBgRect)
	#screen.blit(batteryBg, batteryBgRect)

	# Draw the UI elements
	#map((lambda button: button.draw(screen)),buttons.values())
	#map((lambda label: label.draw(screen)),labels.values())
	[button.draw(screen) for button in buttons.values()]
	[label.draw(screen) for label in labels.values()]

	pygame.display.flip()

	# Sleep a little to save some CPU. Since nothing needs less than a second
	# for update granularity. This obviously makes the UI less responsive however.
	if MOBILE:
		sleep(.5)
