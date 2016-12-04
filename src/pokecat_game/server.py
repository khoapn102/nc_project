# -*- coding: utf-8 -*-

import socket
import time
import threading
import ord.pokemon
import ord.player

# Binding Server
server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server_socket.bind(("",9000))

print "Game server is waiting for connection ..."

# Handling multi players
class Handler(threading.Thread):
	def __init__(self,socket, data, adr):
		threading.Thread.__init__(self)
		self.data = data
		self.socket = socket
		self.adr = adr
	def run(self):
		
			#print "run"
			if (self.data.lower() == "q" and address == self.adr):
				self.socket.sendto(self.data, self.adr) # send 'q' only to that client
				print str(self.adr) + " --> ended"
			
			if not (address == self.adr): # prevent from sending back msg to its sender
				reply = '[' + self.adr[0] + ':' + str(self.adr[1]) + '] - ' + data
				self.socket.sendto(reply, self.adr)
				print str(self.adr) + " --> sent"
			
			return

adr_list = {}
thread_list = []
# Initialize pokeworld
poke_world = [[0 for x in range(1000)] for y in range(1000)]

while 1:
	# Player joined
	data, address = server_socket.recvfrom(256)
	# If address not player not exist
	if(address not in adr_list):
		adr_list[address] = []
	# Message connecting will have format:
	if 'Connect' in data:
		temp = data.split('-')
	print adr_list
	print "(",address[0]," ", address[1],") said: ",data
	for x in adr_list:

		t = Handler(server_socket,data,x)
		t.start()
		thread_list.append(t)
	if(data.lower() == 'q'):
		adr_list.remove(address)
	for th in thread_list:
		th.join()
server_socket.close()
