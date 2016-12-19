# -*- coding: utf-8 -*-
import socket
import time
from threading import Thread, Timer

from ord import player
from ord.pokemon import *
from ord.player import *
import random
import json

# The constant parameters of the PokeCat module
pokeNum = 150
worldSz = 1000
maxPokeNum = 50
spawning_time = 60
despawning_time = 300

# Binding Server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("", 9000))

# Initialize pokeworld - to generate Pokemon
poke_world = [[0 for x in range(worldSz)] for y in range(worldSz)]
# Initialize playerworld - to move around
player_world = [[0 for x in range(worldSz)] for y in range(worldSz)]
# Get all Pokemons Data
file = open('../../data/pokedex.json').read()
data = json.loads(file)
# print data

print "Game server is waiting for connection ..."

def generate_pos():
	x = random.randint(0, worldSz - 1)
	y = random.randint(0, worldSz - 1)
	return (x,y)

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

	global player_world
	global poke_world

	Timer(spawning_time, generate_pokemon).start()
	batch_loc = []
	print 'Spawning Pokemon.............!!!'
	count = 0
	while count < maxPokeNum:
		# Pokemon random index 1 - 150
		index = random.randint(1, pokeNum)
		x,y = generate_pos()
		batch_loc.append((x,y))
		if poke_world[x][y] == 0:
			poke_world[x][y] = index
			count += 1
	print 'Complete Spawning !!!'
	time.sleep(despawning_time) # Wait for 5 mins
	for loc in batch_loc:
		x = loc[0]
		y = loc[1]
		# Search for current spawn batch and despawn them
		if poke_world[x][y] != 0:
			poke_world[x][y] = 0
	print 'Despawned Pokemon............!!!'
	return


class PlayerHandler(Thread):

	def __init__(self, name, age, address):
		Thread.__init__(self)
		self.name = name
		self.age = age
		x, y = self.generate_player()
		self.x = x
		self.y = y
		self.adr = address
		self.player = player(self.name, self.age, [self.x, self.y])

	def run(self):

		print "Start moving"
		move_thread = self.automove()

		time.sleep(120)

		print "End moving"
		# move_thread.cancel()

		return

	def automove(self):

		global player_world

		Timer(1, self.automove).start()

		# Options: clockwise
		# 1: Move up
		# 2: Move right
		# 3: Move down
		# 4: Move left

		oldX = self.x
		oldY = self.y

		option = random.randint(1, 4)

		print "Player ", self.name, " ", option
		if option == 1:
			self.y += 1
		elif option == 2:
			self.x += 1
		elif option == 3:
			self.y -= 1
		elif option == 4:
			self.x -= 1

		if self.x < 0:
			self.x = worldSz - 1

		if self.y < 0:
			self.y = worldSz - 1

		self.x %= worldSz
		self.y %= worldSz

		player_world[oldX][oldY] = 0
		player_world[self.x][self.y] = 1

	def generate_player(self):
		"""
		When player join server, randomize a location
		If player spawn where pokemon, he will automatically catch it
		:return:
		"""
		global player_world
		global poke_world

		x, y = generate_pos()
		while player_world[x][y] == 1:
			x, y = generate_pos()

		if poke_world[x][y] != 0:
			index = poke_world[x][y]
			self.catch_pokemon(index)
			poke_world[x][y] = 0
		player_world[x][y] = 1

		return (x, y)  # Return location for new Player

	def catch_pokemon(self, index):
		"""
		From index, create a pokemon with random level
		Add to Player's bag
		:param player:
		:param index:
		:return:
		"""

		poke_a = pokemonDAO(data[index - 1]).create_pokemon()
		self.player.add_pokemon(poke_a)
		return


adr_list = []
playerThreads = []

generatingThread = Thread(target=generate_pokemon).start()

while 1:
	# Player joined
	data, address = server_socket.recvfrom(256)
	# If new player
	if address not in adr_list:
		if 'Connect' in data:
			temp = data.split('-')

		# Address will now have the new player
		adr_list.append(address)

		player_thread = PlayerHandler(temp[1], temp[2], address)
		player_thread.start()
		playerThreads.append(player_thread)

	# print adr_list.keys()
	print "(",address[0]," ", address[1],") said: ",data

generatingThread.join()
server_socket.close()
