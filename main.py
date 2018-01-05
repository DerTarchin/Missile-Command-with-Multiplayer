from __future__ import division
from math import sqrt
from objects import *
from single import *
from multi import *
import os, sys, random
import pygame as pg

screen = pg.display.get_surface()
width,height = 640,480

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

class MissileCommand(object):
	def __init__(self):
		self.width = 640
		self.height = 480
		self.screen = pg.display.get_surface()
		self.screen_rect = self.screen.get_rect()
		self.clock = pg.time.Clock()
		self.fps = 25.0
		self.keys = pg.key.get_pressed()
		#pg.mouse.set_visible(False)
		#######################
		self.initData()
		self.initMulti()

	def initData(self):
		self.cities = [[True,(109,434)],[True,(178,434)],[True,(238,438)],
						[True,(370,434)],[True,(453,425)],[True,(523,437)]]
		self.level = 1
		self.score = 0
		self.gameover = False
		self.mode = "mainmenu" #mainmenu, level, multiplayer, levelend, multichoice
		self.cL = SinglePlayer(self.screen,self.cities,self.level,self.score)
		self.loadText()

	def initMulti(self):
		self.cities1 = [[True,(109,434)],[True,(178,434)],[True,(238,438)],
						[True,(370,434)],[True,(453,425)],[True,(523,437)]]
		self.cities2 = [[True,(115,41)],[True,(188,53)],[True,(269,45)],
						[True,(403,40)],[True,(463,42)],[True,(533,42)]]
		self.score1 = self.score2 = 0
		self.connType = None

	def loadText(self):
		color = (0,255,0)
		self.font1 = pg.font.Font("resources/pixel_maz.ttf", 80)
		self.font2 = self.cL.font
		self.title = self.font1.render("MISSILE COMMAND",True,color)
		textpos = self.title.get_rect()
		centerx = textpos.centerx
		self.titleLoc = (self.width//2-centerx,40)
		self.single = self.font2.render("Single Player", True, color)
		textpos = self.single.get_rect()
		centerx = textpos.centerx
		self.singleLoc = (self.width//2-centerx, self.height//2)
		self.multi = self.font2.render("Multiplayer", True, color)
		textpos = self.multi.get_rect()
		centerx = textpos.centerx
		self.multiLoc = (self.width//2-centerx, self.height//2+40)

	def loadLevelText(self,cities,ammo):
		color = (0,255,0)
		self.LTpts = self.font1.render("BONUS POINTS",True,color)
		centerx = self.LTpts.get_rect().centerx
		self.LTptsLoc = (self.width//2-centerx,self.height//3-40)
		self.LTscore = self.font2.render(str(self.score),True,color)
		self.LTscoreLoc = (164,7)
		self.LThscore = self.font2.render(str(self.cL.hscore),True,color)
		self.LThscoreLoc = (self.width//2,7)
		self.LTammo = self.font1.render(str(ammo),True,(0,0,255))
		self.LTammoLoc = (self.width//2-100, self.height//2)
		self.LTcity = self.font1.render(str(cities),True,(0,255,255))
		self.LTcityLoc = (self.width//2-100,self.height//2+50)
		self.LTcont = self.font2.render("continue",True,color)
		centerx = self.LTcont.get_rect().centerx
		self.LTcontLoc = (self.width//2-centerx,self.height-40)
		self.LTgo = self.font1.render("GAME OVER",True,color)
		centerx = self.LTgo.get_rect().centerx
		self.LTgoLoc = (self.width//2-centerx,self.height//2-20)

	def loadMultiText(self):
		color = (0,255,0)
		self.MPhost = self.font1.render("HOST",True,color)
		CX = self.MPhost.get_rect().centerx
		self.MPhostLoc = (self.width//3-CX,self.height//2-20)
		self.MPconn = self.font1.render("CONNECT",True,color)
		CX = self.MPconn.get_rect().centerx
		self.MPconnLoc = (self.width-self.width//3-CX,self.height//2-20)
		self.IPtext = self.font2.render("Enter IP:",True,color)
		CX = self.IPtext.get_rect().centerx
		self.IPtextLoc = (self.width//2-CX,self.height//3)

	def loadMultiEndText(self):
		r,g,b = (255,0,0),(0,255,0),(0,0,255)
		self.MEcont = self.font2.render("continue",True,b)
		centerx = self.MEcont.get_rect().centerx
		self.MEcontLoc = (self.width//2-centerx,self.height-40)
		if self.score1 > self.score2:
			self.MEgo = self.font1.render("Player1 WINS",True,g)
		elif self.score1 < self.score2:
			self.MEgo = self.font1.render("Player2 WINS",True,r)
		else: self.MEgo = self.font1.render("TIE GAME",True,b)
		centerx = self.MEgo.get_rect().centerx
		self.MEgoLoc = (self.width//2-centerx,self.height//3-40)
		self.MEscore1 = self.font2.render("Player1: "+str(self.score1),True,g)
		centerx = self.MEscore1.get_rect().centerx
		self.MEscore1Loc = (self.width//2-centerx, self.height//2+15)
		self.MEscore2 = self.font2.render("Player2: "+str(self.score2),True,r)
		centerx = self.MEscore2.get_rect().centerx
		self.MEscore2Loc = (self.width//2-centerx, self.height//2-15)

	def showLevelScreen(self):
		score = self.score
		cities = ammo = 0
		if self.cities != [] or self.cities!= None:
			for c in self.cities:
				if c[0]: cities+=1
		for lz in self.cL.launchzones:
			ammo+=lz[0]
		ammo *= 5
		cities *= 100
		self.bonus = ammo+cities
		self.loadLevelText(cities,ammo)
		self.screen.fill(pg.Color("black"))
		self.screen.blit(self.LTscore,self.LTscoreLoc)
		self.screen.blit(self.LThscore,self.LThscoreLoc)
		if self.bonus > 0:
			self.screen.blit(self.LTpts,self.LTptsLoc)
			for x in xrange(ammo//5):
				i = x%15
				loc = (self.width//2+(i*10),self.height//2+25)
				if x>=15: loc = (loc[0],loc[1]-15)
				self.screen.blit(img('resources/missilee'),loc)
			self.screen.blit(self.LTammo,self.LTammoLoc)
			for x in xrange(cities//100):
				loc = (self.width//2+(x*40),self.height//2+75)
				self.screen.blit(img('resources/citye'),loc)
			self.screen.blit(self.LTcity,self.LTcityLoc)
		else: self.screen.blit(self.LTgo,self.LTgoLoc)
		self.screen.blit(self.LTcont,self.LTcontLoc)

	def playLevel(self):
		self.cL = SinglePlayer(self.screen,self.cities,self.level,self.score)
		self.score,self.cities,lz,quit = self.cL.main_loop()
		if quit: return self.initData()
		self.mode = "mainmenu"
		if self.cities != [] or self.cities!= None:
			for c in self.cities:
				if c[0]: self.mode = "level"
		self.mode = "levelend"

	def showMultiEnd(self):
		self.loadMultiEndText()
		self.screen.fill(pg.Color("black"))
		self.screen.blit(self.MEgo,self.MEgoLoc)
		self.screen.blit(self.MEcont,self.MEcontLoc)
		self.screen.blit(self.MEscore1,self.MEscore1Loc)
		self.screen.blit(self.MEscore2,self.MEscore2Loc)

	def chooseMulti(self):
		self.loadMultiText()
		self.screen.fill(pg.Color("black"))
		if self.connType == None:
			self.screen.blit(self.MPhost,self.MPhostLoc)
			self.screen.blit(self.MPconn,self.MPconnLoc)
		elif self.connType == "conn":
			color = (0,255,0)
			IP = self.font1.render(self.value+":8888",True,color)
			CX = IP.get_rect().centerx
			IPLoc = (self.width//2-CX,self.height//2-20)
			self.screen.blit(IP,IPLoc)
			self.screen.blit(self.IPtext,self.IPtextLoc)

	def loadErrorText(self):
		color = (0,255,0)
		self.errorBox = self.font2.render(self.error,True,color)
		CX = self.errorBox.get_rect().centerx
		self.errorLoc = (self.width//2-CX,self.height-40)

	def playMulti(self):
		if self.connType == "host": 
			self.error = ''
			ip = 'localhost'
		else: 
			self.error = ''
			ip = self.value
		self.loadErrorText()
		try:
			multi = Multiplayer(self.screen,self.cities1,self.cities2,self.score1,self.score2,ip)
			self.error = "Waiting for opponent to connect..."
			self.loadErrorText()
			self.screen.fill(pg.Color("black"))
			self.screen.blit(self.errorBox,self.errorLoc)
			pg.display.update()
			multi.conn.s.setblocking(0)
			while True:
				if self.connType == "host":
					data = multi.conn.listen()
					if data != None: 
						x,y = literal_eval(data)
						if x == -100 and y == -100: 
							multi.conn.send("(-200,-200)")
							pg.time.delay(1998)
							break
				elif self.connType == "conn":
					pg.time.delay(2000)
					multi.conn.send("(-100,-100)")
					data = multi.conn.listen()
					if data != None: 
						x,y = literal_eval(data)
						if x == -200 and y == -200: break
			multi.connType = self.connType
			self.score1,self.score2,self.cities1,self.cities2,quit = multi.main_loop()
			if quit: 
				self.mode = "mainmenu"
				return self.initMulti()
			self.mode = "multiend"
		except:
			self.error = "Error: Server is not active. Waiting for server..."
			self.loadErrorText()
			self.screen.fill(pg.Color("black"))
			self.screen.blit(self.errorBox,self.errorLoc)


	def drawCursor(self):
		x,y = pg.mouse.get_pos()
		color = (0,0,255)
		s = 4
		pg.draw.line(self.screen,color,[x-s,y-s],[x+s,y+s],2)
		pg.draw.line(self.screen,color,[x+s,y-s],[x-s,y+s],2)

	def addIPValue(self):
		if len(self.value) != 15:
			if self.keys[pg.K_0]: self.value += '0'
			elif self.keys[pg.K_1]: self.value += '1'
			elif self.keys[pg.K_2]: self.value += '2'
			elif self.keys[pg.K_3]: self.value += '3'
			elif self.keys[pg.K_4]: self.value += '4'
			elif self.keys[pg.K_5]: self.value += '5'
			elif self.keys[pg.K_6]: self.value += '6'
			elif self.keys[pg.K_7]: self.value += '7'
			elif self.keys[pg.K_8]: self.value += '8'
			elif self.keys[pg.K_9]: self.value += '9'
			elif self.keys[pg.K_PERIOD]: self.value += '.'
			elif self.keys[pg.K_BACKSPACE]: self.value = self.value[:-1]
			if self.keys[pg.K_RETURN]: self.mode = "multiplayer"
		if len(self.value) == 15:
			if self.keys[pg.K_RETURN]: self.mode = "multiplayer"
			elif self.keys[pg.K_BACKSPACE]: self.value = self.value[:-1]

	def event_loop(self):
		self.keys = pg.key.get_pressed()
		for event in pg.event.get():
			if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]: 
				self.gameover = True
			if event.type == pg.MOUSEBUTTONDOWN and event.button == 1: 
				self.click(event.pos)
			if self.mode=="multichoice" and self.connType=="conn":
				self.addIPValue()

	def click(self,pos):
		x,y = pos
		sX,sY = self.singleLoc
		mX,mY = self.multiLoc
		if self.mode == "mainmenu":
			if x>=sX and x<=sX+140 and y>=sY and y<=sY+25: 
				self.initData()
				self.mode = "level"
			if x>=mX and x<=mX+140 and y>=mY and y<=mY+25:
				self.initData()
				self.mode = "multichoice"
		if self.mode == "levelend":
			if x>=self.width//2-46 and x<= self.width//2+46 and \
				y>=self.height-40 and y<=self.height-20:
					if self.bonus>0:
						self.level+=1
						if self.level == 4: self.level = 0
						self.mode = "level"
						self.score += self.bonus
					else: self.mode = "mainmenu"
		if self.mode == "multiend":
			if x>=self.width//2-46 and x<= self.width//2+46 and \
				y>=self.height-40 and y<=self.height-20:
					self.initMulti()
					self.mode = "mainmenu"
		if self.mode == "multichoice" and self.connType==None:
			if x>=160 and x<=261 and y>=232 and y<=263:
				self.connType = "host"
				self.mode = "multiplayer"
			if x>=345 and x<=504 and y>=232 and y<=263:
				self.connType = "conn"
				self.value = '128.237.134.213'

	def mainmenu(self):
		self.screen.fill(pg.Color("black"))
		self.screen.blit(self.title,self.titleLoc)
		self.screen.blit(self.single,self.singleLoc)
		self.screen.blit(self.multi,self.multiLoc)

	def checkMode(self):
		if self.mode == "mainmenu": self.mainmenu()
		elif self.mode == "hscore": self.hscore()
		elif self.mode == "level": self.playLevel()
		elif self.mode == "multiplayer": self.playMulti()
		elif self.mode == "levelend": self.showLevelScreen()
		elif self.mode == "multichoice": self.chooseMulti()
		elif self.mode == "multiend": self.showMultiEnd()

	def main_loop(self):
		while not self.gameover:
			self.event_loop()
			self.checkMode()
			self.drawCursor()
			pg.display.update()
			self.clock.tick(self.fps)
			pg.display.set_caption("Missile Command")

if __name__ == "__main__":
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pg.display.set_mode((width,height))
	run_it = MissileCommand()
	run_it.main_loop()
	pg.quit()
	sys.exit()
