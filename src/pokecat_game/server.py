# -*- coding: utf-8 -*-
import socket
import time
from threading import Thread, Timer
from ord.pokemon import *
from ord.player import *
import random
import json
from core.validation import *

# The constant parameters of the PokeCat module
# pokeNum = 13
# worldSz = 1000
# maxPokeNum = 50
# moveDuration = 1
# turnDuration = 120
# spawning_time = 60
# despawning_time = 300

pokeNum = 13
worldSz = 5
maxPokeNum = 5
moveDuration = 1
turnDuration = 10
spawning_time = 5
despawning_time = 6

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

# New Player List
new_player_list = []

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

# Update Player list
def update_player_list(rerun):
	"""
	new_list only contains UNIQUE player
	Rerun = 1 means to update players list every 4 seconds.
	Rerun = 0 means this funct only run once.
	:param new_list:
	:return:
	"""
	global new_player_list
	if rerun == 1:
		Timer(4, update_player_list, [1]).start()
	print 'Updating player list.... !'
	file = '../../data/players.json'
	with open(file) as readfile:
		player_list = json.load(readfile)
	# print player_list
	curr_index = len(player_list)
	for item in new_player_list:
		player = {
			'username': item[0],
			'password': item[1],
			'player_profile': 'player_' + str(curr_index+1) + '.json'
		}
		player_list.append(player)
		curr_index += 1
		# Remove new_player that has been added
		new_player_list.remove(item)
	# Update json data
	with open(file, 'w') as outfile:
		json.dump(player_list, outfile, indent=4, sort_keys=True)
	return player_list

# A class to handle the connection of each player

adr_list = []
playerThreads = []

generatingThread = Thread(target=generate_pokemon).start()
updatePlayerListThread = Thread(target=update_player_list, args=(1,)).start()

# Get all Player Data
file = open('../../data/players.json').read()
playerData = json.loads(file)

class PlayerHandler(Thread):

	def __init__(self, username, password, address, index):
		Thread.__init__(self)

		self.username = username
		self.password = password
		self.adr = address
		self.index = index

		# Create a class player to store their info for later use (e.g., save to Json)
		self.player = player(self.username, self.password, [0,0])

		# Has to be set order like this to work correctly !!!!! DONT change anything HERE

		x, y = self.generate_player()
		self.x = x
		self.y = y

		self.player.location = [self.x, self.y]

		self.done = False

	def run(self):

		global server_socket
		global playerData

		print "Start moving"

		# Automove the player to catch pokemon
		# displayPlayer()
		self.automove(0)

        # End the current session of the client after 120 seconds
		while not self.done:
			pass

		print "End moving"

		if self.index != -1:
			playerDAO(self.player).updateToJson(self.index)
		else:
			temp_list = update_player_list(0)
			# print '++++++++++++++++', temp_list
			for user in temp_list:
				if user['username'] == username:
					print username, 'login'
					temp_link = user['player_profile']
					temp_link = temp_link[0: temp_link.index('.')]
					self.index = int(temp_link.split('_')[1])
			playerDAO(self.player).saveToJson(self.index)
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

		status = "Player " + self.username + " "
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
		# print status
		# Send the moving information back to the current client
		server_socket.sendto(status, self.adr)

		self.x = newX
		self.y = newY

		# Reset the position of the player on the field
		player_world[oldX][oldY] = 0
		player_world[self.x][self.y] = 1

		# displayPlayer()

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
		poke_lvl = random.randint(1,10)
		poke_a = pokemonDAO(pokeData[index - 1]).create_pokemon(poke_lvl)
		status = "Player " + self.username + " just caught " + poke_a.name
		print status
		# Send the name of caught pokemon to client
		server_socket.sendto(status, self.adr)
		self.player.add_pokemon(poke_a)
		return

# MAIN GAME
while 1:
	# Player joined
	user_index = -1
	data, address = server_socket.recvfrom(256)
	temp = data.split('-')
	# If new player
	# if address not in adr_list:
	if 'Connect' in data:
		check_connect = False
		username = temp[1]
		password = temp[2]
		for user in playerData:
			if user['username'] == username:
				if user['password'] == password:
					print username, 'login'
					temp_link = user['player_profile']
					temp_link = temp_link[0: temp_link.index('.')]
					user_index = int(temp_link.split('_')[1])
					server_socket.sendto('proceed', address)
					check_connect = not check_connect
					break
				else:
					continue
		if check_connect == False:
			server_socket.sendto('error', address)
			continue
	elif 'Register' in data:
		check_register = False
		username = temp[1]
		password = temp[2]
		# curr_index = len(playerData) # Retrieve curr_index for player_list
		for user in playerData:
			if user['username'] == username: # username is not unique
				print 'Username is not unique !'
				server_socket.sendto('error', address)
				check_register = not check_register
				break
		# print check_register
		if check_register == False:
			print username, 'registered'
			new_player_list.append([username, password])
			server_socket.sendto('proceed', address)
		else:
			continue

	# Address will now have the new player
	adr_list.append(address)
	player_thread = PlayerHandler(temp[1], temp[2], address, user_index)
	player_thread.start()
	# playerThreads.append(player_thread)

	# print adr_list.keys()
	print "(",address[0]," ", address[1],") said: ",data

generatingThread.join()
server_socket.close()
