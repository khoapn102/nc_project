# -*- coding: utf-8 -*-

import json
from pokemon import *

class player(object):
    def __init__(self, name, age, location):
        self.name = name
        self.age = age
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

    def saveToJson(self, index):
        file = 'player' + str(index) + '.json'
        result = {
            'player_name': self.player.name,
            'player_age': self.player.age,
            'player_bag': self.player.bag
        }
        with open(file, 'w') as outfile:
            json.dump(result, outfile, indent=4, sort_keys=True)

# file = open('../data/pokedex.json').read()
# data = json.loads(file)
# index = random.randint(0,4)
# print index+1, ' ', data[index]['name']
# poke_a = pokemonDAO(data[1]).create_pokemon()
# # Pokemon spawn
# print poke_a.cur_lvl, poke_a.hp, poke_a.atk, poke_a.ev
# poke_a.curr_exp = poke_a.accum_exp
# poke_a.level_up()
# print poke_a.cur_lvl, poke_a.hp, poke_a.atk
# player_a = player('Khoa', 26, [0,0])
# player_a.add_pokemon(poke_a)
# dao = playerDAO(player_a)
# dao.saveToJson(1)

