from __future__ import division
from ast import literal_eval
from math import sqrt
from objects import *
from connection import *
import os, sys, random
import pygame as pg

#load images once to be more efficient
imgLib = {}
def img(path):
	path = path+".bmp"
	image = imgLib.get(path)
	if image == None:
		canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
		image = pg.image.load(canonicalized_path)
		imgLib[path] = image
	return image
#change number to positive
def pos(num):
	if num<0: return num*-1
	return num
#change number to negative
def neg(num): 
	if num>0: return num*-1
	return num
#readFile function
def readFile(filename, mode="rt"):
	with open(filename, mode) as fin: return fin.read()
#writeFile function
def writeFile(filename, contents, mode="wt"):
	with open(filename, mode) as fout: fout.write(contents)

class Multiplayer(object):
	def __init__(self,screen,cities1,cities2,score1,score2,ip):
		pg.init()
		self.width = 640
		self.height = 480
		self.screen = screen
		self.screen_rect = self.screen.get_rect()
		self.clock = pg.time.Clock()
		self.lastTick = pg.time.get_ticks()
		self.fps = 25.0
		self.keys = pg.key.get_pressed()
		self.initData(cities1,cities2,score1,score2,ip)
		self.startConnection(ip)

	def initData(self,cities1,cities2,score1,score2,ip):
		self.missiles = []
		self.explosions = []
		self.cities1 = cities1
		self.cities2 = cities2
		self.launchzones1 = [[10,(49,417)],[10,(309,417)],[10,(608,417)]]
		self.launchzones2 = [[10,(32,57)],[10,(331,57)],[10,(591,57)]]
		for c in self.launchzones1:
			c.append(Ammo(c[1][0],c[1][1]))
		for c in self.launchzones2:
			c.append(Ammo(c[1][0],c[1][1]))
		self.cityImg1 = [[self.cities1[0][0],(90,428)],[self.cities1[1][0],(158,430)],
						[self.cities1[2][0],(219,433)],[self.cities1[3][0],(352,428)],
						[self.cities1[4][0],(433,420)],[self.cities1[5][0],(504,430)]]
		self.cityImg2 = [[self.cities2[0][0],(100,36)],[self.cities2[1][0],(172,48)],
						[self.cities2[2][0],(253,40)],[self.cities2[3][0],(386,35)],
						[self.cities2[4][0],(447,38)],[self.cities2[5][0],(516,36)]]
		self.pause = self.levelover = False
		self.done = self.quit = False
		self.score1, self.score2 = score1, score2
		self.connType = None
		self.ip = ip
		self.loadText()

	def startConnection(self,ip):
		self.conn = Connection(ip)

	def loadText(self):
		self.font = pg.font.Font("resources/pixel_maz.ttf", 40)
		color = (0,0,255)
		self.score1Text = self.font.render(str(self.score1),True,color)
		CX = self.score1Text.get_rect().centerx
		self.score1TextLoc = (self.width//2-CX,self.height-30)
		color = (255,0,0)
		self.score2Text = self.font.render(str(self.score2),True,color)
		self.score2TextLoc = (self.width//2-CX,5)

	def findStartArea(self,x):
		if self.connType == "host": lz = self.launchzones1
		else: lz = self.launchzones2
		zone, distance = None, None
		for i in xrange(len(lz)):
			if lz[i][0]!=0:
				if zone == None: 
					zone,distance=i,max(lz[i][1][0],x)-min(lz[i][1][0],x)
				if distance > max(lz[i][1][0],x)-min(lz[i][1][0],x):
					zone,distance=i,max(lz[i][1][0],x)-min(lz[i][1][0],x)
		if zone != None: 
			lz[zone][0]-=1
			lz[zone][2].remove()
		if zone == None: return False,False
		return lz[zone][1]

	def checkEndArea(self,x,y):
		if y<60 or y>414:
			endArea = "launchzone"
			if self.connType == "host" and y<60: lz = self.launchzones2
			elif self.connType=="conn" and y>414: lz = self.launchzones1
			zone, distance = None, None
			for i in xrange(len(lz)):
				if zone == None:
					zone, distance = i, max(lz[i][1][0],x)-min(lz[i][0],x)
				if distance > max(lz[i][1][0],x)-min(lz[i][1][0],x):
					zone,distance = i,max(lz[i][1][0],x)-min(lz[i][1][0],x)
			if self.connType == "host" and y<60: c = self.cities2
			elif self.connType == "conn" and y>414: c = self.cities1
			for j in xrange(len(c)):
				if distance > max(c[j][1][0],x)-min(c[j][1][0],x):
					zone,distance,endArea = j,max(c[j][1][0],x)-min(c[j][1][0],x),"city"
			if zone == None: return x,y
			elif endArea == "launchzone": return lz[zone][1]
			elif endArea == "city": return c[zone][1]
		else: return x,y

	def hostMissile(self, pos):
		x,y = pos
		if self.connType == "host" and y>410: y = 410
		elif self.connType == "conn" and y<70: y = 70
		startX,startY = self.findStartArea(x)
		x,y = self.checkEndArea(x,y)
		if startY != False:
			newMissile = MultiMissile(startX, startY, x, y, self.connType)
			self.missiles.append(newMissile)
			self.conn.send(str((x, y))+"\n")

	def connMissile(self):
		try:
			x,y = literal_eval(self.input)
			if self.connType == "host": self.connType = "conn"
			else: self.connType = "host"
			startX, startY = self.findStartArea(x)
			newMissile = MultiMissile(startX, startY, x, y, self.connType)
			if self.connType == "host": self.connType = "conn"
			else: self.connType = "host"
			self.missiles.append(newMissile)
		except:
			pass

	def removeLocation(self,m):
		x,y = m.lineEnd[0],m.lineEnd[1]
		if m.type == "host":
			for c in xrange(len(self.cities2)):
				if x==self.cities2[c][1][0] and y==self.cities2[c][1][1]:
					if self.cities2[c][0]:
						self.cities2[c][0] = False
						self.cityImg2[c][0] = False
						self.score1+=100
			for lz in self.launchzones2:
				if x==lz[1][0] and y==lz[1][1] and lz[0]>0:
						lz[0] = 0
						lz[2].ammoImg = []
						self.score1+=150
		elif m.type == "conn":
			for c in xrange(len(self.cities1)):
				if x==self.cities1[c][1][0] and y==self.cities1[c][1][1]:
					if self.cities1[c][0]:
						self.cities1[c][0] = False
						self.cityImg1[c][0] = False
						self.score2+=100
			for lz in self.launchzones1:
				if x==lz[1][0] and y==lz[1][1] and lz[0]>0:
					lz[0] = 0
					lz[2].ammoImg = []
					self.score2+=150

	def addExplosion(self,m):
		newExplosion = Explosion(m.lineEnd,m.type)
		self.explosions.append(newExplosion)

	def drawCursor(self):
		x,y = pg.mouse.get_pos()
		color = (0,0,255)
		s = 4
		pg.draw.line(self.screen,color,[x-s,y-s],[x+s,y+s],2)
		pg.draw.line(self.screen,color,[x+s,y-s],[x-s,y+s],2)

	def drawText(self):
		self.screen.blit(self.score1Text,self.score1TextLoc)
		self.screen.blit(self.score2Text,self.score2TextLoc)

	def event_loop(self):
		for event in pg.event.get():
			if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]: self.quit = True
			if self.keys[pg.K_p]: self.pause = not self.pause
			if self.keys[pg.K_e]: 
				self.hostMissile((320,100))
				self.input = "(320,200)"
				self.connMissile()
				self.hostMissile((50,380))
				self.input = "(50,380)"
				self.connMissile()
			if not self.pause:
				if event.type == pg.MOUSEBUTTONDOWN and event.button == 1: 
					self.hostMissile(event.pos)

	def update(self):
		self.keys = pg.key.get_pressed()
		self.input = self.conn.listen()
		if self.input != None: self.connMissile()
		if not self.pause:
			for m in self.missiles:
				m.update()
				if not m.isActive:
					self.removeLocation(m)
					self.addExplosion(m)
					self.missiles.remove(m)
			for e in self.explosions:
				e.update()
				if not e.isActive:
					self.explosions.remove(e)
				else:
					self.score1, self.score2=e.checkCollisionMulti(self.missiles,self.explosions,self.score1,self.score2,self.connType)
			if self.missiles==[] and self.explosions==[]:
				ammo1 = ammo2 = cities1 = cities2 = 0
				for c in self.cities1:
					if c[0]: cities1 += 1
				for c in self.cities2:
					if c[0]: cities2 += 1
				for lz in self.launchzones1:
					if lz[0]>0: ammo1+= 1
				for lz in self.launchzones2:
					if lz[0]>0: ammo2+= 1
				if (ammo1==0 and ammo2==0) or \
				cities1==0 or cities2==0: self.levelover = True
		self.loadText()

	def draw(self):
		self.screen.fill(pg.Color("black"))
		self.screen.blit(img('resources/land'), (0, 0))
		self.screen.blit(img('resources/landm'), (0,0))
		for c in self.cityImg1:
			if c[0]: self.screen.blit(img('resources/city'),c[1])
			else: self.screen.blit(img('resources/cityx'),c[1])
		for c in self.cityImg2:
			if c[0]: self.screen.blit(img('resources/citym'),c[1])
			else: self.screen.blit(img('resources/cityxm'),c[1])
		for c in self.launchzones1:
			c[2].draw(self.screen)
		for c in self.launchzones2:
			c[2].draw(self.screen)
		for m in self.missiles:
			m.draw(self.screen)
		for e in self.explosions:
			e.draw(self.screen)
		self.drawText()
		self.drawCursor()

	def main_loop(self):
		while not self.done:
			if self.quit: 
				self.conn.close()
				return None,None,None,None,True
			if self.levelover:
				self.conn.close()
				return self.score1,self.score2,self.cities1,self.cities2,False
			self.event_loop()
			self.update()
			self.draw()
			pg.display.update()
			self.clock.tick(self.fps)
			pg.display.set_caption("Missile Command")
		self.conn.close()
		return self.score1,self.score2,self.cities1,self.cities2,False
