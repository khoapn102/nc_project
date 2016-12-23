import socket
from ord import player
from ord import pokemon
from threading import Thread

# Binding Server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("", 9000))

print "Pokecat game server is waiting for connection ..."

class GameHandler(Thread):
    def __init__(self):
        global playerList
        Thread.__init__(self)
        self.p1 = playerList[0]
        self.p2 = playerList[1]

    def run(self):

        return

    def choosePokemon(self):
        pass

    def fight(self):
        pass

    def switch(self):
        pass

    def surrender(self):
        pass

playerList = []
adr_list = []

while 1:
    data, address = server_socket.recvfrom(1024)

    if len(adr_list) > 2:
        server_socket.sendto("Waiting", address)
        continue

    if address not in adr_list:
        if 'Connect' in data:
            temp = data.split('-')

        p = player(temp[1], temp[2])
        playerList.append(p)
        adr_list.append(address)
    else:
        pass

    if len(adr_list) == 2:
        game = GameHandler()
    else:
        server_socket.sendto("Waiting", adr_list[0])


server_socket.close()