# -*- coding: utf-8 -*-

import json

def validate(username, password):
	file = '../../data/players.json'
	with open(file) as readfile:
		data = json.load(readfile)
	print data
	for p in data:
		if p['username'] == username:
			if p['password'] == password:
				return p['player_profile']
	return -1

def is_unique(username):
	file = '../../data/players.json'
	with open(file) as readfile:
		data = json.load(readfile)
	for p in data:
		if p['username'] == username:
			return False
	return True

def update_player_list(new_list):
	"""
	new_list only contains UNIQUE player
	:param new_list:
	:return:
	"""
	file = '../../data/players.json'
	with open(file) as readfile:
		data = json.load(readfile)
	curr_index = len(data)
	for item in new_list:
		player = {
			'username': item[0],
			'password': item[1],
			'player_profile': 'player_' + str(curr_index+1) + '.json'
		}
		data.append(player)
		curr_index += 1
	with open(file, 'w') as outfile:
		json.dump(data, outfile, indent=4, sort_keys=True)
	return


