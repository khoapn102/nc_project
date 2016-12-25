# -*- coding: utf-8 -*-

import random
import json
__author__ = 'Khoa Phan, Triet Le'
__version__ = '0.01'


class pokemon(object):
    # Define Attributes
    def __init__(self, id, name, type, b_exp, hp, atk, b_def, speed,
                 spec_atk, spec_def, evolve_lvl, evolve_id, dmg_atked, cur_lvl):
        # Inialize Pokemon
        self.is_new = True # pokemon just spawn
        self.id = id
        self.name = name
        self.type = type
        # Base exp that Pokemon yield after defeated
        self.b_exp = b_exp
        # Current Experience of Pokemon
        self.curr_exp = 0
        # Amount Exp Pokemon need to lvl up
        self.accum_exp = self.b_exp #
        self.hp = hp #
        self.atk = atk #
        self.b_def = b_def #
        self.speed = speed
        self.spec_atk = spec_atk #
        self.spec_def = spec_def #
        self.evolve_lvl = evolve_lvl
        self.evolve_id = evolve_id
        self.dmg_atked = dmg_atked
        # EV = 0.5 -> 1.0 rounded with 1 decimal
        self.ev = round(random.uniform(0.5, 1.0),1)
        # Pokemon when spawning get random lvl 1-5
        self.cur_lvl = cur_lvl
        self.nxt_lvl = self.cur_lvl + 1
        # Recalculate Attribute when lvl up
        self.level_up()
        self.turn_off_new()

    def turn_off_new(self):
        self.is_new = False

    def level_up(self):

        if self.is_new == True:
            for i in range(2, self.cur_lvl+1):
                self.accum_exp *= 2
                self.hp = round(self.hp*(1+self.ev), 1)
                self.atk = round(self.atk*(1+self.ev), 1)
                self.b_def = round(self.b_def*(1+self.ev), 1)
                self.spec_atk = round(self.spec_atk*(1+self.ev), 1)
                self.spec_def = round(self.spec_def*(1+self.ev), 1)

            return

        while self.curr_exp >= self.accum_exp:
            self.cur_lvl += 1
            self.nxt_lvl = self.cur_lvl + 1
            self.curr_exp -= self.accum_exp
            self.accum_exp *= 2
            self.hp = round(self.hp*(1+self.ev), 1)
            self.atk = round(self.atk*(1+self.ev), 1)
            self.b_def = round(self.b_def*(1+self.ev), 1)
            self.spec_atk = round(self.spec_atk*(1+self.ev), 1)
            self.spec_def = round(self.spec_def*(1+self.ev), 1)

        return

    def evolve(self, data, evolve_id):
        poke_evolved = pokemonDAO(data[evolve_id]).create_pokemon(self.cur_lvl)
        self.id = poke_evolved.id
        self.name = poke_evolved.name
        self.type = poke_evolved.type
        # Base exp that Pokemon yield after defeated
        self.b_exp = poke_evolved.b_exp

        self.hp = poke_evolved.hp #
        self.atk = poke_evolved.atk #
        self.b_def = poke_evolved.b_def #
        self.speed = poke_evolved.speed
        self.spec_atk = poke_evolved.spec_atk #
        self.spec_def = poke_evolved.spec_def #
        self.evolve_lvl = poke_evolved.evolve_lvl
        self.evolve_id = poke_evolved.evolve_id
        self.dmg_atked = poke_evolved.dmg_atked

        self.nxt_lvl = self.cur_lvl + 1

        return

# Parsing generated pokemon data
class pokemonDAO(object):
    def __init__(self, data):
        self.data = data

    # Parsing JSON data and return a Pokemon
    def create_pokemon(self, cur_lvl):
        id = self.data['id']
        name = self.data['name']
        type = self.data['type']
        b_exp = self.data['base_experience']
        hp = self.data['base_hp']
        atk = self.data['base_atk']
        b_def = self.data['base_def']
        speed = self.data['base_speed']
        spec_atk = self.data['base_special_atk']
        spec_def = self.data['base_special_def']
        evolve_lvl = self.data['evolve_level']
        evolve_id = self.data['evolve_id']
        dmg_atked = self.data['dmg_when_atked']
        return pokemon(id, name, type, b_exp, hp, atk, b_def, speed,
                       spec_atk, spec_def, evolve_lvl, evolve_id, dmg_atked, cur_lvl)


# file = open('../data/pokedex.json').read()
# data = json.loads(file)
#
# print data[5]['name']


