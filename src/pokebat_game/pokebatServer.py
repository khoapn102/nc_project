import socket
import json
import random
import threading

# Binding Server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("", 9000))

print "PokeBat game server is waiting for connection ..."

# playerList = []
adr_list = {}
threadList = []
collectingThreads = []

class PlayerHandler():
    def __init__(self, username, password, address, playerjson):
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
        # 2: Choose turn
        # 3: Fight, Switch or Surrender
        # 4: Processing quitting
        # 5: Done
        self.status = 0
        self.pokemons = []

    def setStatus(self, newStatus):
        self.status = newStatus

    def execute(self, data):

        s = self.status

        # Status:
        # 0: Waiting
        # 1: Choose Pokemon
        # 2: Choose turn
        # 3: Fight, Switch or Surrender
        # 4: Processing quitting
        # 5: Done
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
        elif s == 4:
            if self.result == "Won":
                print "Processing Winning"
                self.processWinning()
            self.setStatus(5)
            # print self.username, "-self status", self.status

    def choosePokemon(self):
        global server_socket

        server_socket.sendto(self.playerjson, self.address)

        self.setStatus(2)

    def chooseTurn(self, recvData):

        global adr_list
        global server_socket

        pokes = recvData.split("-")

        # print "Pokes", pokes

        file = open(self.playerjson).read()
        playerData = json.loads(file)

        tempList = playerData["player_bag"]
        curid = 0

        while len(self.pokeList) < 3:
            for poke in tempList:
                if str(poke["id"]) == pokes[curid]:
                    self.pokeList.append(poke)
                    curid += 1
                    break

        # print self.pokeList

        self.curpoke = self.pokeList[0]
        # print self.curpoke["name"], self.curpoke["id"]
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
        global threadList
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

            maxMultiply = 1
            for atk in specialAtks:
                for oppType in oppTypes:
                    if atk["type"] == oppType and int(atk["multiply"]) > maxMultiply:
                        maxMultiply = int(atk["multiply"])

            dmg = float(self.curpoke["spec_atk"]) * float(maxMultiply) - float(adr_list[self.opponent].curpoke["b_def"])

        # print fightType, dmg, initialHP

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
                oppSendData += " by normal attack.\n" + str(adr_list[self.opponent].curpoke["id"]) + "\n"
            else:
                selfSendData += " by special attack.\n"
                oppSendData += " by special attack.\n" + str(adr_list[self.opponent].curpoke["id"]) + "\n"

            # print len(adr_list[self.opponent].pokeList)

            for poke in adr_list[self.opponent].pokeList:
                if poke["id"] == adr_list[self.opponent].curpoke["id"]:
                    adr_list[self.opponent].pokeList.remove(poke)
                    break

            # print len(adr_list[self.opponent].pokeList)

            if len(adr_list[self.opponent].pokeList) == 0:
                selfSendData += "Won"
                oppSendData += "Lost"
                self.status = 4
                adr_list[self.opponent].status = 4
                self.result = "Won"
                adr_list[self.opponent].result = "Lost"

            server_socket.sendto(selfSendData, self.address)
            server_socket.sendto(oppSendData, adr_list[self.opponent].address)

            if len(adr_list[self.opponent].pokeList) == 0:
                t = threading.Thread(target=adr_list[self.address].execute, args=(data,))
                t.start()
                threadList.append(t)

                t = threading.Thread(target=adr_list[self.opponent].execute, args=(data,))
                t.start()
                threadList.append(t)

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
        else:
            selfSendData = "You could not damage " + adr_list[self.opponent].curpoke["name"] + " using " + self.curpoke[
                "name"]
            oppSendData = "Your " + adr_list[self.opponent].curpoke["name"] + " was not damaged by " + self.curpoke["name"]

            if fightType == 0:
                selfSendData += " by normal attack.\n"
                oppSendData += " by normal attack.\n"
            else:
                selfSendData += " by special attack.\n"
                oppSendData += " by special attack.\n"

            server_socket.sendto(selfSendData, self.address)
            server_socket.sendto(oppSendData, adr_list[self.opponent].address)
            pass

        return

    def switch(self, data):

        global server_socket

        newid = data.split("-")[1]

        selfSendData = "You just switched from " + self.curpoke["name"] + " to "
        oppSendData = "Your opponent just switched from " + self.curpoke["name"] + " to "

        for poke in self.pokeList:
            if str(poke["id"]) == str(newid):
                self.curpoke = poke
                break

        selfSendData += self.curpoke["name"] + "\n"
        oppSendData += self.curpoke["name"] + "\n"

        server_socket.sendto(selfSendData, self.address)
        server_socket.sendto(oppSendData, adr_list[self.opponent].address)

        return

    def surrender(self):

        global adr_list
        global server_socket
        global threadList

        sendData = "Player " + self.username + " just surrendered.\n"
        sendData += "Player " + adr_list[self.opponent].username + " just won the game.\n"
        sendData += "The current game session ended.\n"

        print sendData

        server_socket.sendto(sendData, self.address)
        server_socket.sendto(sendData, adr_list[self.opponent].address)

        self.status = 4
        adr_list[self.opponent].status = 4
        self.result = "Lost"
        adr_list[self.opponent].result = "Won"

        t = threading.Thread(target=adr_list[self.address].execute, args=(data,))
        t.start()
        threadList.append(t)

        t = threading.Thread(target=adr_list[self.opponent].execute, args=(data,))
        t.start()
        threadList.append(t)

        return

    def processWinning(self):
        return

def validateLogin(username, password, address):

    global server_socket

    # Get all Player Data
    file = open('../../data/players.json').read()
    playerData = json.loads(file)

    # print playerData

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

def collectGarbage():

    global adr_list
    global threadList

    while len(adr_list.keys()) == 2:

        p1 = adr_list.keys()[0]
        p2 = adr_list.keys()[1]

        # print "Current status", adr_list[p1].status, adr_list[p2].status

        if adr_list[p1].status == 5 and adr_list[p2].status == 5:
            del adr_list[p1]
            del adr_list[p2]
            break

    for t in threadList:
        t.join()
        threadList.remove(t)


while 1:
    data, address = server_socket.recvfrom(1024)

    players = adr_list.keys()

    playerNo = len(players)
    # print "Current player no", playerNo

    if address in adr_list:
        print "Server received", data, "from", adr_list[address].username

    if playerNo == 2:
        if address != players[0] and address != players[1]:
            server_socket.sendto("Full", address)
        elif address == players[0] or address == players[1]:
            if adr_list[address].status != 0:
                # print "Executing"
                t = threading.Thread(target=adr_list[address].execute, args=(data,))
                t.start()
                threadList.append(t)

    elif playerNo == 1:
        if address not in adr_list:
            if 'Connect' in data:
                temp = data.split('-')
            link, check = validateLogin(temp[1], temp[2], address)

            if check:
                p2 = PlayerHandler(temp[1], temp[2], address, link)
                adr_list[address] = p2

                collector = threading.Thread(target=collectGarbage, args=())
                collector.start()
                collectingThreads.append(collector)

                p1.opponent = p2.address
                p2.opponent = p1.address

                p1.setStatus(1)
                p2.setStatus(1)

                p1.execute("")
                p2.execute("")
        else:
            server_socket.sendto("Waiting", address)
    elif playerNo == 0:

        if address not in adr_list:
            if 'Connect' in data:
                temp = data.split('-')

            link, check = validateLogin(temp[1], temp[2], address)

            if check:
                p1 = PlayerHandler(temp[1], temp[2], address, link)
                adr_list[address] = p1
        else:
            server_socket.sendto("Waiting", address)


for t in collectingThreads:
    t.join()
    collectingThreads.remove(t)

server_socket.close()
