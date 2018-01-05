"""
Simple socket server using threads
Localhost through telnet:

telnet 128.237.91.98 8888

"""

import socket, sys
from thread import *

HOST = ''	# Symbolic name meaning all available interfaces
PORT = 8888	# Arbitrary non-privileged port
CLIENT = dict()
print "Creating socket...",
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print '			Socket created.'
#Bind socket to local host and port
print "Binding socket...",
try:
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((HOST, PORT))
except socket.error as msg:
	print '			Bind failed. Error Code : ' + str(msg[0]) + ' Message: ' + msg[1]
	sys.exit()
print '			Socket bind complete.'
print "Attempting listen...",
#Start listening on socket
s.listen(10)
print '			Socket now listening.'

#Function for handling connections. This will be used to create threads
def clientthread(conn,s,CLIENT):
	#Sending message to connected client
	#conn.send('Welcome to the server. Type something and hit enter:\n') #send only takes string
	#infinite loop so that function do not terminate and thread do not end.
	while True:
		#Receiving from client
		client,name,ip = CLIENT[conn]
		data = conn.recv(1024)
		print "%s: "%(name), data
		if "exit" in data:
			conn.sendall("Terminating Connection\n")
			break
		reply = data
		if not data: 
			break
		for c in CLIENT:
			if c!= conn:
				client,name,ip = CLIENT[c]
				client.sendall(reply)
	#came out of loopa
	#conn.close()

#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
	conn, addr = s.accept()
	print 'Connected with ' + addr[0] + ':' + str(addr[1])
	name = "Guest"+str(addr[1])
	if addr[0] == '128.237.91.98': name = "Hizal"
	CLIENT[conn] = (conn,name,addr[0]+':'+str(addr[1]))
	#start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
	start_new_thread(clientthread ,(conn,s,CLIENT))


s.close()