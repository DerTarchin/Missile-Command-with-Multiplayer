from __future__ import division
from math import sqrt
from objects import *
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

class SinglePlayer(object):
	def __init__(self,screen,cities,level,score):
		pg.init()
		self.width = 640
		self.height = 480
		#self.screen = pg.display.get_surface()
		self.screen = screen
		self.screen_rect = self.screen.get_rect()
		self.clock = pg.time.Clock()
		self.lastTick = pg.time.get_ticks()
		self.fps = 25.0
		self.keys = pg.key.get_pressed()
		self.initData(cities,level,score)

	def initData(self,cities,level,score):
		self.missiles = []
		self.explosions = []
		self.cities = cities
		self.launchzones = [[10,(49,417)],[10,(309,417)],[10,(608,417)]]
		for c in self.launchzones:
			c.append(Ammo(c[1][0],c[1][1]))
		self.cityImg = [[self.cities[0][0],(90,428)],[self.cities[1][0],(158,430)],
						[self.cities[2][0],(219,433)],[self.cities[3][0],(352,428)],
						[self.cities[4][0],(433,420)],[self.cities[5][0],(504,430)]]
		self.level, self.levelammo = level,5
		self.enemyTimer = 2500
		self.pause = self.levelover = False
		self.done = self.quit = False
		self.loadFile()
		self.score = score
		self.loadText()

	#checks if high scores file exists, creates it if it doesn't, reads high score
	def loadFile(self):
		path = self.path = "data" + os.sep + "scores.txt"
		# create the directory, if it is not there
		if (not os.path.exists("data")):
			os.makedirs("data")
			assert(os.path.exists("data"))
		else: 
			self.hscore = int(readFile(self.path)) #reads high score
			return
		# add new file
		contents = str(0) #default is 0 on file (as int)
		writeFile(path, contents) #write score
		assert(os.path.exists(path))
		self.hscore=0 #default high score if there is 0

	def loadText(self):
		color = (0,255,0)
		self.font = pg.font.Font("resources/pixel_maz.ttf", 40)
		self.scoreText = self.font.render(str(self.score),True,color)
		self.scoreLoc = (164,7)
		self.hscoreText = self.font.render(str(self.hscore),True,color)
		self.hscoreLoc = (self.width//2,7)

	def updateScore(self):
		self.loadFile()
		path = self.path
		s = readFile(path)
		contents = str(self.score)
		if s!=int(0) and int(s)<int(contents): #if score is greater than hscore
			writeFile(path, contents)
			assert(os.path.exists(path))

	def addEnemy(self):
		now = pg.time.get_ticks()
		if now - self.lastTick >= self.enemyTimer and self.levelammo>=0:
			numMissiles = 0
			for m in self.missiles:
				if m.type == "enemy": numMissiles+=1
			if numMissiles<10:
				self.lastTick = now
				for x in xrange(random.randint(2,4)):
					self.EnemyMissile()
				self.levelammo-=1

	def EnemyMissile(self):
		trueLoc = []
		for c in self.cities:
			if c[0]: trueLoc.append(c[1])
		for lz in self.launchzones:
			if lz[0]!=0: trueLoc.append(lz[1])
		if trueLoc != []:
			x1,y1 = random.randint(0,self.width),0
			r = random.randint(0,len(trueLoc)-1)
			x2,y2 = trueLoc[r]
			newMissile = Missile(x1,y1,x2,y2,"enemy",self.level)
			self.missiles.append(newMissile)

	def addEnemyScatter(self):
		r = random.randint(0,75)
		if r == 30 and self.missiles!=[]:
			m = random.randint(0,len(self.missiles)-1)
			for x in xrange(0,3):
				self.EnemyMissileScatter(m)

	def EnemyMissileScatter(self,m):
		missiles = self.missiles
		trueLoc = []
		for c in self.cities:
			if c[0]: trueLoc.append(c[1])
		for lz in self.launchzones:
			if lz[0]!=0: trueLoc.append(lz[1])
		if trueLoc != []:
			x1,y1 = missiles[m].lineCurrent[0],missiles[m].lineCurrent[1]
			if y1 <= self.height//2:
				r = random.randint(0,len(trueLoc)-1)
				x2,y2 = trueLoc[r]
				newMissile = Missile(x1,y1,x2,y2,"enemy",self.level)
				self.missiles.append(newMissile)

	def findStartArea(self,x):
		lz = self.launchzones
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

	def userMissile(self, pos):
		x,y = pos
		if y > 410: y = 410
		startX,startY = self.findStartArea(x)
		if startY != False:
			newMissile = Missile(startX, startY, x, y, "player", self.level)
			self.missiles.append(newMissile)

	def removeLocation(self,missile):
		x,y = missile.lineEnd[0],missile.lineEnd[1]
		for c in xrange(len(self.cities)):
			if x==self.cities[c][1][0] and y==self.cities[c][1][1]:
				self.cities[c][0] = False
				self.cityImg[c][0] = False
				return
		for lz in self.launchzones:
			if x==lz[1][0] and y==lz[1][1]:
				lz[0] = 0
				lz[2].ammoImg = []

	def addExplosion(self,m):
		newExplosion = Explosion(m.lineEnd)
		self.explosions.append(newExplosion)

	def drawCursor(self):
		x,y = pg.mouse.get_pos()
		color = (0,0,255)
		s = 4
		pg.draw.line(self.screen,color,[x-s,y-s],[x+s,y+s],2)
		pg.draw.line(self.screen,color,[x+s,y-s],[x-s,y+s],2)

	def drawText(self):
		self.screen.blit(self.scoreText,self.scoreLoc)
		self.screen.blit(self.hscoreText,self.hscoreLoc)

	def quitToMenu(self):
		missiles = []
		explosions = []
		for c in xrange(len(self.cities)):
			self.cities[c][0] = False
			self.cityImg[c][0] = False
		for lz in self.launchzones:
			lz[0] = 0
			lz[2].ammoImg = []
		self.missiles = []
		self.explosions = []
		self.levelover = True
		self.levelammo = -1

	def event_loop(self):
		for event in pg.event.get():
			if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]: self.quit = True
			if self.keys[pg.K_q]: self.quitToMenu()
			if self.keys[pg.K_e]: self.EnemyMissile()
			if self.keys[pg.K_p]: self.pause = not self.pause
			if not self.pause:
				if event.type == pg.MOUSEBUTTONDOWN and event.button == 1: 
					self.userMissile(event.pos)
		self.addEnemy()

	def update(self):
		self.keys = pg.key.get_pressed()
		if not self.pause:
			for m in self.missiles:
				m.update()
				if not m.isActive:
					if m.type == "enemy": self.removeLocation(m)
					self.addExplosion(m)
					self.missiles.remove(m)
			for e in self.explosions:
				e.update()
				if not e.isActive:
					self.explosions.remove(e)
				else:
					self.score=e.checkCollision(self.missiles,self.explosions,self.score)
			self.levelover = True
			for c in self.cities:
				if c[0]: self.levelover = False
			for lz in self.launchzones:
				if lz[0]: self.levelover = False
			if self.levelammo<0 and self.missiles==[] and self.explosions==[]: self.done=True
			self.updateScore()
		self.loadText()
		self.addEnemyScatter()

	def draw(self):
		self.screen.fill(pg.Color("black"))
		self.screen.blit(img('resources/land'), (0, 0))
		for c in self.cityImg:
			if c[0]: self.screen.blit(img('resources/city'),c[1])
			else: self.screen.blit(img('resources/cityx'),c[1])
		for c in self.launchzones:
			c[2].draw(self.screen)
		for m in self.missiles:
			m.draw(self.screen)
		for e in self.explosions:
			e.draw(self.screen)
		self.drawText()
		self.drawCursor()

	def main_loop(self):
		while not self.done:
			if self.quit: return None,None,None,True
			self.event_loop()
			self.update()
			self.draw()
			pg.display.update()
			self.clock.tick(self.fps)
			pg.display.set_caption("Missile Command")
		return self.score,self.cities,self.launchzones,False
