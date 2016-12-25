import socket
import json
import random
from ord import player
from ord import pokemon
from threading import Thread

# Binding Server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("", 9000))

print "PokeBat game server is waiting for connection ..."

# playerList = []
adr_list = {}

class PlayerHandler(Thread):
    def __init__(self, username, password, address, playerjson):
        Thread.__init__(self)
        self.username = username
        self.password = password
        self.address = address
        self.opponent = ""
        self.playerjson = "../../data/" + playerjson

        self.pokeList = []
        self.speed = -1

        self.curpoke = -1

        # Result: Won or Lost
        self.result = ""

        # Status:
        # 0: Waiting
        # 1: Choose Pokemon
        # 2: Fight, Switch or Surrender
        self.status = 0
        self.pokemons = []

    def run(self):
        while 1:
            address = self.address
            data = ""

            if self.status != 0 and self.status != 1:
                data, address = server_socket.recvfrom(1024)
                print data

            if address == self.address:
                if data == "q":
                    break
                self.execute(data)
            elif address == self.opponent:
                adr_list[self.opponent].execute(data)

        if self.result == "Won":
            self.processWinning()

        # Remove all players
        adr_list[self.address].join()
        del adr_list[self.address]

        return

    def setStatus(self, newStatus):
        self.status = newStatus

    def execute(self, data):

        s = self.status
        # Status:
        # 0: Waiting
        # 1: Choose Pokemon
        # 2: Fight, Switch or Surrender
        if s == 1:
            self.choosePokemon()
        elif s == 2:
            self.chooseTurn(data)
        elif s == 3:
            if "Fight" in data:
                self.fight()
            elif "Switch" in data:
                self.switch(data)
            elif "Surrender" in data:
                self.surrender()

    def choosePokemon(self):
        global server_socket

        server_socket.sendto(self.playerjson, self.address)

        self.setStatus(2)

    def chooseTurn(self, recvData):

        global adr_list
        global server_socket

        pokes = recvData.split("-")

        print "Pokes", pokes

        file = open(self.playerjson).read()
        playerData = json.loads(file)

        tempList = playerData["player_bag"]

        for poke in tempList:
            for curid in pokes:
                if str(poke["id"]) == curid:
                    self.pokeList.append(poke)
                    pokes.remove(curid)
                    break

        self.curpoke = self.pokeList[0]
        self.speed = int(self.pokeList[0]["speed"])

        while adr_list[self.opponent].speed == -1:
            pass

        if adr_list[self.opponent].speed >= self.speed:
            server_socket.sendto("1", self.address)
        else:
            server_socket.sendto("0", self.address)

        self.setStatus(3)
        return

    def fight(self):

        global adr_list
        global server_socket
        # Fight type:
        # 0: Normal
        # 1: Special
        fightType = random.randint(0, 1)
        dmg = 0.0
        initialHP = float(adr_list[self.opponent].curpoke["hp"])

        if fightType == 0:
            dmg = float(self.curpoke["atk"]) - float(adr_list[self.opponent].curpoke["b_def"])

        elif fightType == 1:
            oppTypes = adr_list[self.opponent].curpoke["type"]
            specialAtks = self.curpoke["dmg_atked"]

            maxMultiply = -1
            for atk in specialAtks:
                for oppType in oppTypes:
                    if atk["type"] == oppType and int(atk["multiply"]) > maxMultiply:
                        maxMultiply = int(atk["multiply"])

            dmg = float(self.curpoke["spec_atk"]) * float(maxMultiply) - float(adr_list[self.opponent].curpoke["b_def"])

        if dmg > 0.0:
            adr_list[self.opponent].curpoke["hp"] = str(float(adr_list[self.opponent].curpoke["hp"]) - dmg)
            for poke in adr_list[self.opponent].pokeList:
                if poke["id"] == adr_list[self.opponent].curpoke["id"]:
                    poke["hp"] = str(float(adr_list[self.opponent].curpoke["hp"]) - dmg)
                    break

        if float(adr_list[self.opponent].curpoke["hp"]) <= 0.0:

            selfSendData = "You just killed " + adr_list[self.opponent].curpoke["name"] + " using " + self.curpoke[
                "name"]
            oppSendData = "Your " + adr_list[self.opponent].curpoke["name"] + " was killed by " + self.curpoke["name"]

            if fightType == 0:
                selfSendData += " by normal attack.\n"
                oppSendData += " by normal attack.\n" + adr_list[self.opponent].curpoke["id"] + "\n"
            else:
                selfSendData += " by special attack.\n"
                oppSendData += " by special attack.\n"

            print len(adr_list[self.opponent].pokeList)

            for poke in adr_list[self.opponent].pokeList:
                if poke["id"] == adr_list[self.opponent].curpoke["id"]:
                    adr_list[self.opponent].pokeList.remove(poke)
                    break

            print len(adr_list[self.opponent].pokeList)

            if len(adr_list[self.opponent].pokeList) == 0:
                selfSendData += "Won"
                oppSendData += "Lost"

            server_socket.sendto(selfSendData, self.address)
            server_socket.sendto(oppSendData, adr_list[self.opponent].address)

        elif float(adr_list[self.opponent].curpoke["hp"]) < initialHP:
            selfSendData = "You just damaged " + str(dmg) + " HP of " +\
                           adr_list[self.opponent].curpoke["name"] + " using " + self.curpoke["name"]
            oppSendData = "Your " + adr_list[self.opponent].curpoke["name"] + " was damaged " + str(dmg) +\
                          " HP by " + self.curpoke["name"]

            if fightType == 0:
                selfSendData += " by normal attack.\n"
                oppSendData += " by normal attack.\n"
            else:
                selfSendData += " by special attack.\n"
                oppSendData += " by special attack.\n"

            server_socket.sendto(selfSendData, self.address)
            server_socket.sendto(oppSendData, adr_list[self.opponent].address)

        return

    def switch(self, data):

        newid = data.split("-")[1]
        for poke in self.pokeList:
            if poke["id"] == newid:
                self.curpoke = poke
                break

        return

    def surrender(self):

        global adr_list
        global server_socket

        sendData = "Player " + self.username + " just surrendered.\n"
        sendData += "Player " + adr_list[self.opponent].username + " just won the game.\n"
        sendData += "The current game session ended.\n"

        print sendData

        server_socket.sendto(sendData, self.address)
        server_socket.sendto(sendData, adr_list[self.opponent].address)

        self.result = "Lost"
        adr_list[self.opponent].result = "Won"

        return

    def processWinning(self):
        return

def validateLogin(username, password, address):

    global server_socket

    # Get all Player Data
    file = open('../../data/players.json').read()
    playerData = json.loads(file)

    print playerData

    for user in playerData:
        if user['username'] == username and user['password'] == password:
            print username, 'login'
            temp_link = user['player_profile']
            temp_link = temp_link[0: temp_link.index('.')]
            server_socket.sendto('proceed', address)
            return (user['player_profile'], True)

    # If not found any matching user
    server_socket.sendto('error', address)
    return ("", False)

while 1:
    data, address = server_socket.recvfrom(1024)

    players = adr_list.keys()

    playerNo = len(players)

    if playerNo == 2:
        if address != players[0] and address != players[1]:
            server_socket.sendto("Full", address)
        elif adr_list[address] is p1:
            p1.execute(data)
        elif adr_list[address] is p2:
            p2.execute(data)
    elif playerNo == 1:
        if address not in adr_list:
            if 'Connect' in data:
                temp = data.split('-')
            link, check = validateLogin(temp[1], temp[2], address)

            if check:
                p2 = PlayerHandler(temp[1], temp[2], address, link)
                p2.start()

                adr_list[address] = p2

                p1.opponent = p2.address
                p2.opponent = p1.address

                p1.setStatus(1)
                p2.setStatus(1)
        else:
            server_socket.sendto("Waiting", address)
    elif playerNo == 0:
        if address not in adr_list:
            if 'Connect' in data:
                temp = data.split('-')

            link, check = validateLogin(temp[1], temp[2], address)

            if check:
                p1 = PlayerHandler(temp[1], temp[2], address, link)
                p1.start()
                adr_list[address] = p1
        else:
            server_socket.sendto("Waiting", address)

server_socket.close()