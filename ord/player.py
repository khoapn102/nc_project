# -*- coding: utf-8 -*-

import json
from pokemon import *

class player(object):
    def __init__(self, name, password, location):
        self.name = name
        self.password = password
        self.location = location
        # Bag to store pokemon
        self.bag = []
        self.amount_pokemon = 0

    def update_loc(self, location):
        self.location = location # Will be list

    def add_pokemon(self, pokemon):
        # Maximum 200 Pokemon
        if self.amount_pokemon < 200:
            self.bag.append(pokemon.__dict__)
            self.amount_pokemon += 1

class playerDAO(object):
    def __init__(self, player):
        self.player = player

    # Save New player info to Json
    def saveToJson(self, index):
        file = '../../data/'
        file += 'player_' + str(index) + '.json'
        player = {
            'player_name': self.player.name,
            'player_password': self.player.password,
            'player_bag': self.player.bag
        }
        with open(file, 'w') as outfile:
            json.dump(player, outfile, indent=4, sort_keys=True)

    # Update current play info to Json
    def updateToJson(self, index):
        file = '../../data/'
        file += 'player_' + str(index) + '.json'
        with open(file) as readfile:
            player = json.load(readfile)
        # print '-----------------------', player['player_bag']
        for pokemon in self.player.bag:
            player['player_bag'].append(pokemon)
        # print '========================', player['player_bag']
        with open(file, 'w') as outfile:
            json.dump(player, outfile, indent=4, sort_keys=True)


# file = open('../data/pokedex.json').read()
# data = json.loads(file)
#
# index = random.randint(1,1)
# print index+1, ' ', data[index]['name']
# lvl = random.randint(35,35)
# poke_a = pokemonDAO(data[index]).create_pokemon(lvl)
# # Pokemon spawn
# print poke_a.cur_lvl, poke_a.hp, poke_a.atk
# poke_a.curr_exp = poke_a.accum_exp
# poke_a.level_up()
# print poke_a.name, poke_a.cur_lvl, poke_a.hp, poke_a.atk

"""
This is for Pokemon Evolution CODE!!!
"""
# if poke_a.cur_lvl == poke_a.evolve_lvl:
#     poke_a.evolve(data, poke_a.evolve_id-1)
#
#
# print poke_a.name, poke_a.cur_lvl, poke_a.hp, poke_a.atk
#
# player_a = player('Khoa',123, [0,0])
# player_a.add_pokemon(poke_a)
# dao = playerDAO(player_a)
# dao.saveToJson(1)
#
# index = random.randint(0,4)
# print index+1, ' ', data[index+1]['name']
# lvl = random.randint(1,5)
# poke_a = pokemonDAO(data[1]).create_pokemon(lvl)
# poke_a.level_up()
#
# player_a.add_pokemon(poke_a)
# dao.updateToJson(1)


