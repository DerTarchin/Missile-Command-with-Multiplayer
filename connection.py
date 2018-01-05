import socket

class Connection(object):
	def __init__(self, ip):
		HOST = ip				
		PORT = 8888              # The same port as used by the server
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORT))
		self.HOST, self.PORT = HOST, PORT
		self.s = s

	def send(self,x):
		self.s.sendall(x)

	def listen(self):
		try:
		    data = self.s.recv(1024)
		except:
		    return None
		#data = self.s.recv(1024)
		return data

	def close(self):
		self.s.close()