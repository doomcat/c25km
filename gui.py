import pygame
from pygame.locals import *

FRES = 800*480/1000

pygame.font.init()
fonts = {'default': pygame.font.SysFont('Arial',12)}
def initFonts(fres=FRES):
	global fonts
	fonts['huge'] = pygame.font.SysFont('Arial',fres/7,bold=True)
	fonts['h1'] = pygame.font.SysFont('Arial',fres/12,bold=True)
	fonts['h2'] = pygame.font.SysFont('Arial',fres/16,bold=True)
	fonts['bold'] = pygame.font.SysFont('Arial',fres/22,bold=True)
	fonts['normal'] = pygame.font.SysFont('Arial',fres/28)
	fonts['small'] = pygame.font.SysFont('Arial',fres/36)

class Button(pygame.Rect):
	def __init__(self,label,pos,size=None,f=None,fg=pygame.Color(255,255,255,255),bg=pygame.Color(128,0,0,160),font=fonts['default'],pad=5):
		self.label = label
		self.pressed = False
		self.f = f
		self.fg = fg
		self.bg = bg
		self.font = font
		self.pad = pad

		self.labels = [
			self.font.render(self.label,True,fg),
			self.font.render(self.label,True,bg)
		]

		if size != None:
			pygame.Rect.__init__(self,pos,size)
		else:
			self.size = self.labels[0].get_size()
			self.width += self.pad*4
			self.height += self.pad*4
			pygame.Rect.__init__(self,pos,self.size)

		self.surface = pygame.Surface(self.size,SRCALPHA)
		self.oldSize = self.size
		self.update()

	def update(self):
		fg = self.fg
		bg = self.bg
		label = self.labels[0]
		if self.pressed:
			fg = self.bg
			bg = self.fg
			label = self.labels[1]

		self.surface.fill(bg)
		pygame.draw.rect(self.surface,fg,(0,0,self.width,self.height),self.pad)
		labelX = self.pad*2
		labelY = self.pad*2
		self.surface.blit(label,(labelX,labelY))

	def draw(self,surface):
		if self.size != self.oldSize:
			self.surface = pygame.Surface(self.size,SRCALPHA)
			self.oldSize = self.size
			self.update()

		surface.blit(self.surface,self)

	def down(self,pos):
		if self.collidepoint(pos):
			self.pressed = True
			self.update()

	def up(self,pos):
		if self.collidepoint(pos) and self.pressed:
			self.f()
		self.pressed = False
		self.update()

class Label(pygame.Rect):
	def __init__(self,text,pos,fg=pygame.Color(255,255,255,255),bg=None,font=fonts['default'],sc=pygame.Color(0,0,0,100)):
		pygame.Rect.__init__(self,pos,(0,0))
		self.label = font.render(text,True,fg)
		self.shadow = font.render(text,True,sc)
		self.size = self.label.get_size()
		self.text = text
		self.oldText = text
		self.fg = fg
		self.bg = bg
		self.font = font
		self.sc = sc

	def draw(self,surface):
		if self.oldText != self.text:
			self.label = self.font.render(self.text,True,self.fg)
			self.shadow = self.font.render(self.text,True,self.sc)
			self.size = self.label.get_size()
			self.oldText = self.text
		
		surface.blit(self.shadow,(self.left+3,self.top+3))
		surface.blit(self.label,self)

def distances(rects,maxOrMin='max'):
	widths = []
	heights = []
	xs = []
	ys = []
	for r in rects:
		widths.append(r.width)
		heights.append(r.height)
		xs.append(r.left)
		ys.append(r.top)
	if maxOrMin == 'max':
		return (max(widths),max(heights),max(xs),max(ys))
	else:
		return (min(widths),min(heights),min(xs),min(ys))
