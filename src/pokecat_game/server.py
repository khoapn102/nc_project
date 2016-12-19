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
pokeNum = 13
worldSz = 1000
maxPokeNum = 50
moveDuration = 1
turnDuration = 120
spawning_time = 60
despawning_time = 300

# pokeNum = 13
# worldSz = 5
# maxPokeNum = 5
# moveDuration = 1
# turnDuration = 5
# spawning_time = 5
# despawning_time = 6

# Binding Server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("", 9000))

# Initialize pokeworld - to generate Pokemon
poke_world = [[0 for x in range(worldSz)] for y in range(worldSz)]
# Initialize playerworld - to move around
player_world = [[0 for x in range(worldSz)] for y in range(worldSz)]
# Get all Pokemons Data
file = open('../../data/pokedex.json').read()
pokeData = json.loads(file)
# print data

print "Game server is waiting for connection ..."

def displayPoke():
	global poke_world
	for x in range(worldSz):
		for y in range(worldSz):
			print poke_world[x][y],
		print ""

	print "\n"

def displayPlayer():
	global player_world
	for x in range(worldSz):
		for y in range(worldSz):
			print player_world[x][y],
		print ""

	print "\n"


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
	# displayPoke()
	time.sleep(despawning_time) # Wait for 5 mins
	for loc in batch_loc:
		x = loc[0]
		y = loc[1]
		# Search for current spawn batch and despawn them
		if poke_world[x][y] != 0:
			poke_world[x][y] = 0
	print 'Despawned Pokemon............!!!'
	# displayPoke()
	return

# A class to handle the connection of each player
class PlayerHandler(Thread):

	def __init__(self, name, age, address):
		Thread.__init__(self)
		self.name = name
		self.age = age
		x, y = self.generate_player()
		self.x = x
		self.y = y
		self.adr = address
		# Create a class player to store their info for later use (e.g., save to Json)
		self.player = player(self.name, self.age, [self.x, self.y])
		self.done = False

	def run(self):

		global server_socket

		print "Start moving"

		# Automove the player to catch pokemon
		displayPlayer()
		self.automove(0)

        # End the current session of the client after 120 seconds
		while not self.done:
			pass

		print "End moving"

		# playerDAO(self.player).saveToJson()
		server_socket.sendto("q", self.adr)

		return

	def automove(self, sec):

		global player_world
		global server_socket
		global worldSz

		if sec == turnDuration:
			self.done = True
			return

		# Repeat the automove function every 1 second until 120 seconds
		Timer(moveDuration, self.automove, (sec + 1,)).start()

		# Old position of the player
		oldX = self.x
		oldY = self.y

		# New position of the player
		newX = self.x
		newY = self.y

		status = "Player " + self.name + " "
		direction = ""

		while player_world[newX][newY] != 0:
			newX = self.x
			newY = self.y

			# Options: clockwise
			# 1: Move up
			# 2: Move right
			# 3: Move down
			# 4: Move left
			option = random.randint(1, 4)

			if option == 1:
				newX -= 1
				direction = "moved up."
			elif option == 2:
				newY += 1
				direction = "moved right."
			elif option == 3:
				newX += 1
				direction = "moved down."
			elif option == 4:
				newY -= 1
				direction = "moved left."

			if newX < 0:
				newX = worldSz - 1

			if newY < 0:
				newY = worldSz - 1

			newX %= worldSz
			newY %= worldSz

		# print option
		status += direction
		print status
		# Send the moving information back to the current client
		server_socket.sendto(status, self.adr)

		self.x = newX
		self.y = newY

		# Reset the position of the player on the field
		player_world[oldX][oldY] = 0
		player_world[self.x][self.y] = 1

		displayPlayer()

        # Catch a pokemon if found
		if poke_world[self.x][self.y] != 0:
			index = poke_world[self.x][self.y]
			self.catch_pokemon(index)
			poke_world[self.x][self.y] = 0


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

		global pokeData
		global server_socket

		poke_a = pokemonDAO(pokeData[index - 1]).create_pokemon()
		status = "Player " + self.name + " just caught " + poke_a.name
		print status
		# Send the name of caught pokemon to client
		server_socket.sendto(status, self.adr)
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
