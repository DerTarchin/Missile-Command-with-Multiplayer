from __future__ import division
from math import sqrt
import os, sys, random
import pygame as pg

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

class Missile(object):
	def __init__(self, x1, y1, x2, y2, color, level=1):
		if color == "enemy": self.color = (255,0,0)
		elif color == "player": self.color = (0,255,0)
		self.type = color
		self.colorIndex = 0
		self.lineStart = [x1, y1]
		self.lineEnd = [x2, y2]
		self.lineCurrent = [x1,y1]
		if x1 != x2: self.slope = (y2-y1)/(x2-x1)
		else: self.slope = 1
		self.yintercept = y1-self.slope*x1
		self.isActive = True
		self.speedP = 20
		self.speedE = 1 * level
		self.getCrossHairs()
		self.loadColors()
		self.update()

	def loadColors(self):
		self.colors = [(255,255,255),(255,255,0),(255,0,255),
						(0,255,0),(0,255,255),(255,0,0)]

	def getCrossHairs(self):
		size = 3
		self.cTL = [self.lineEnd[0]-size,self.lineEnd[1]-size]
		self.cBR = [self.lineEnd[0]+size,self.lineEnd[1]+size]
		self.cTR = [self.lineEnd[0]+size,self.lineEnd[1]-size]
		self.cBL = [self.lineEnd[0]-size,self.lineEnd[1]+size]

	def getAxis(self):
		if self.lineStart[1]-self.lineEnd[1]>= \
		pos(self.lineStart[0] - self.lineEnd[0]): return "y"
		else: return "x"

	def updatePlayer(self,axis):
		c = self.lineCurrent
		if axis == "y":
			dist = c[1]-self.lineEnd[1]
			if dist >= self.speedP: c[1] -= self.speedP
			else: c[1] = self.lineEnd[1]
			c[0] = int((c[1]-self.yintercept)/self.slope)
		if axis == "x":
			dist = pos(c[0]-self.lineEnd[0])
			if dist >= self.speedP: 
				if c[0]<self.lineEnd[0]: c[0]+= self.speedP
				else: c[0]-= self.speedP
			else: c[0] = self.lineEnd[0]
			c[1] = int(self.slope*c[0]+self.yintercept)

	def update(self):
		c = self.lineCurrent
		if self.type == "player":
			if c[1]>self.lineEnd[1]:
				self.updatePlayer(self.getAxis())
			else: self.isActive = False
		if self.type == "enemy":
			if c[1]<self.lineEnd[1]:
				c[1] += self.speedE
				c[0] = int((c[1]-self.yintercept)/self.slope)
			else: self.isActive = False
		self.colorIndex=(self.colorIndex+1)%len(self.colors)

	def draw(self, Surface):
		if self.isActive:
			pg.draw.line(Surface,self.color,self.lineStart, self.lineCurrent)
			pg.draw.line(Surface,(255,255,0),self.lineCurrent,self.lineCurrent,3)
			colors,i = self.colors, self.colorIndex
			if self.type == "player":
				pg.draw.line(Surface,colors[i],self.cTL,self.cBR)
				pg.draw.line(Surface,colors[i],self.cTR,self.cBL)

class MultiMissile(object):
	def __init__(self, x1, y1, x2, y2, color):
		if color == "conn": self.color = (255,0,0)
		elif color == "host": self.color = (0,255,0)
		self.type = color
		self.colorIndex = 0
		self.lineStart = [x1, y1]
		self.lineEnd = [x2, y2]
		self.lineCurrent = [x1,y1]
		self.isActive = True
		###########################
		self.speed = 5#13
		distance = sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))
		self.xChange = ((x1-x2)*self.speed)/distance
		self.yChange = ((y1-y2)*self.speed)/distance
		###########################
		self.getCrossHairs()
		self.loadColors()
		self.update()

	def loadColors(self):
		self.colors = [(255,255,255),(255,255,0),(255,0,255),
						(0,255,0),(0,255,255),(255,0,0)]

	def getCrossHairs(self):
		size = 3
		self.cTL = [self.lineEnd[0]-size,self.lineEnd[1]-size]
		self.cBR = [self.lineEnd[0]+size,self.lineEnd[1]+size]
		self.cTR = [self.lineEnd[0]+size,self.lineEnd[1]-size]
		self.cBL = [self.lineEnd[0]-size,self.lineEnd[1]+size]

	def update(self):
		self.colorIndex=(self.colorIndex+1)%len(self.colors)
		s,e,c = self.lineStart,self.lineEnd,self.lineCurrent
		dist = sqrt((c[0]-e[0])*(c[0]-e[0])+(c[1]-e[1])*(c[1]-c[1]))
		if c != e and self.type=="host" and c[1]>e[1]:
			c[0] -= self.xChange
			c[1] -= self.yChange
			if c[1]<e[1]: c[0],c[1] = e[0], e[1]
		elif c != e and self.type=="conn" and c[1]<e[1]:
			c[0] -= self.xChange
			c[1] -= self.yChange
			if c[1]>e[1]: c[0],c[1] = e[0], e[1]
		else: self.isActive = False

	def draw(self, Surface):
		if self.isActive:
			pg.draw.line(Surface,self.color,self.lineStart, self.lineCurrent)
			pg.draw.line(Surface,(255,255,0),self.lineCurrent,self.lineCurrent,3)
			colors,i = self.colors, self.colorIndex
			pg.draw.line(Surface,colors[i],self.cTL,self.cBR)
			pg.draw.line(Surface,colors[i],self.cTR,self.cBL)

class Ammo(object):
	def __init__(self,centerX,centerY,amount = 10):
		self.ammoImg = []
		if centerY > 240:
			sx,sy = centerX-4, centerY-3
			for v in xrange(4):
				for h in xrange(v+1):
					self.ammoImg.append(((sx-v*7)+h*15, sy+v*7))
		else:
			sx,sy = centerX-4, centerY-3
			for v in xrange(4):
				for h in xrange(v+1):
					self.ammoImg.append(((sx-v*7)+h*15, sy-v*7))

	def remove(self):
		last = len(self.ammoImg)-1
		self.ammoImg.remove(self.ammoImg[last])

	def draw(self,Surface):
		for a in self.ammoImg:
			if a[1]>240: Surface.blit(img('resources/missile'),a)
			else: Surface.blit(img('resources/missilem'),a)

class Explosion(object):
	def __init__(self, center, connType=None,  \
		canDestroy=None, pointsGoTo="me"):
		if connType != None:
			if canDestroy == None and connType == "host": canDestroy = "conn"
			if canDestroy == None and connType == "conn": canDestroy = "host"
			if pointsGoTo == "me": pointsGoTo = connType
		self.canDestroy = canDestroy
		self. pointsGoTo = pointsGoTo
		self.x, self.y = center[0],center[1]
		self.r = 1
		self.maxSize = 25
		self.growSpeed = 1
		self.color = 0
		self.isActive = True
		self.loadColors()
		self.type = connType

	def loadColors(self):
		self.colors = [(255,255,255),(255,255,0),(255,0,255),
						(0,255,0),(0,255,255),(255,0,0)]

	def checkCollision(self,missiles,explosions,score):
		for m in missiles:
			if m.type == "enemy":
				x,y = m.lineCurrent[0], m.lineCurrent[1]
				dist = sqrt((x - self.x)**2 + (y - self.y)**2)
				if dist <= self.r:
					newExplosion = Explosion(m.lineCurrent)
					explosions.append(newExplosion)
					missiles.remove(m)
					score+=25
		return score

	def checkCollisionMulti(self,missiles,explosions,score1,score2,connType):
		for m in missiles:
			if m.type == self.canDestroy:
				x,y = m.lineCurrent[0], m.lineCurrent[1]
				dist = sqrt((x - self.x)**2 + (y - self.y)**2)
				if dist <= self.r:
					newExplosion = Explosion(m.lineCurrent,canDestroy=self.canDestroy,pointsGoTo=self.pointsGoTo)
					explosions.append(newExplosion)
					if self.pointsGoTo == "host": score1 += 25
					if self.pointsGoTo == "conn": score2 += 25
					missiles.remove(m)
		return score1, score2

	def update(self):
		self.r += self.growSpeed
		if self.r >= self.maxSize: 
			self.growSpeed *= -1
			self.r = self.maxSize
		if self.r <= 0: self.isActive = False
		self.color=(self.color+1)%len(self.colors)

	def draw(self,Surface):
		colors,i = self.colors, self.color
		pg.draw.circle(Surface, colors[i], (int(self.x),int(self.y)), int(self.r))