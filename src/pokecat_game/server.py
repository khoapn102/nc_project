# -*- coding: utf-8 -*-
import socket
import time
import threading
from ord.pokemon import *
from ord.player import *
import random
import json

# Binding Server
server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server_socket.bind(("",9000))

# Initialize pokeworld - to generate Pokemon =
poke_world = [[0 for x in range(1000)] for y in range(1000)]
# Initialize playerworld - to move around
player_world = [[0 for x in range(1000)] for y in range(1000)]
# Get all Pokemons Data
file = open('../../data/pokedex.json').read()
data = json.loads(file)
# print data

print "Game server is waiting for connection ..."

# Handling multi players
class Handler(threading.Thread):
	def __init__(self,socket, data, adr):
		threading.Thread.__init__(self)
		self.data = data
		self.socket = socket
		self.adr = adr
	def run(self):
			# #print "run"
			# if (self.data.lower() == "q" and address == self.adr):
			# 	self.socket.sendto(self.data, self.adr) # send 'q' only to that client
			# 	print str(self.adr) + " --> ended"
			#
			# if not (address == self.adr): # prevent from sending back msg to its sender
			# 	reply = '[' + self.adr[0] + ':' + str(self.adr[1]) + '] - ' + data
			# 	self.socket.sendto(reply, self.adr)
			# 	print str(self.adr) + " --> sent"
			#
			return

def automove():
	return

def catch_pokemon(player, index):
	"""
	From index, create a pokemon with random level
	Add to Player's bag
	:param player:
	:param index:
	:return:
	"""
	poke_a = pokemonDAO(data[index-1]).create_pokemon()
	player.add_pokemon(poke_a)
	return

def generate_pos():
	x = random.randint(0,999)
	y = random.randint(0,999)
	return (x,y)

def generate_player(player):
	"""
	When player join server, randomize a location
	If player spawn where pokemon, he will automatically catch it
	:return:
	"""
	x,y = generate_pos()
	while player_world[x][y] == 1:
		x,y = generate_pos()
	if player_world[x][y] == 0:
		if poke_world[x][y] != 0:
			index = poke_world[x][y]
			catch_pokemon(player, index)
			poke_world[x][y] = 0
		player_world[x][y] = 1
	return (x,y) # Return location for new Player

def generate_pokemon():
	"""
	Randomize 50 pokemon at random location in the poke_world
	Tracking with the Id of the pokemon itself.
	Will use the index to retrieve the pokemon info
	Pokemons spawn every 1 minutes
	After 5 minutes, will check all the 50 pokemon
	If no one catches it, pokemon will be despawned
	:return:
	"""
	threading.Timer(60, generate_pokemon).start()
	batch_loc = []
	print 'Spawning Pokemon.............!!!'
	count = 0
	while count < 50:
		# Pokemon random index 1 - 150
		index = random.randint(1, 150)
		x,y = generate_pos()
		batch_loc.append((x,y))
		if poke_world[x][y] == 0:
			poke_world[x][y] = index
			count += 1
	print 'Complete Spawning !!!'
	time.sleep(300) # Wait for 5 mins
	for loc in batch_loc:
		x = loc[0]
		y = loc[1]
		# Search for current spawn batch and despawn them
		if poke_world[x][y] != 0:
			poke_world[x][y] = 0
	print 'Despawned Pokemon............!!!'
	return

adr_list = {}
# thread_list = []

while 1:

	# Player joined
	data, address = server_socket.recvfrom(256)
	# If new player
	if address not in adr_list:
		if 'Connect' in data:
			temp = data.split('-')
		x,y = generate_pos()
		# Address will now have the new player
		adr_list[address] = player(temp[0], temp[1], [x,y])

	# print adr_list.keys()
	print "(",address[0]," ", address[1],") said: ",data
	# Spawning Pokemon
	threading.Thread(target=generate_pokemon).start()
	# for x in adr_list:
	# 	t = Handler(server_socket,data,x)
	# 	t.start()
	# 	thread_list.append(t)
	# if(data.lower() == 'q'):
	# 	adr_list.remove(address)
	# for th in thread_list:
	# 	th.join()
server_socket.close()
