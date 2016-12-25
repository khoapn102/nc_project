import socket
import json

# Using UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# data = "Connect-Khoa-26"
# client_socket.sendto(data, ("localhost", 9000))

# Login Credential
print "Please log in: "

while 1:
    print 'Please enter username/password to begin adventure !'
    username = raw_input('Username: ')
    password = raw_input('Password: ')
    data = "Connect-"
    data += username + '-' + password
    print data
    client_socket.sendto(data,("localhost", 9000))
    recvData, address = client_socket.recvfrom(1024)
    if recvData == 'proceed':
        print "Logged in successfully"
        break
    elif recvData == 'error':
        print 'Invalid Login Credential !!!'
    elif recvData == "Full":
        print "The game room is currently full. Please come back later"
        client_socket.close()
        exit(0)


print "Waiting for the game to start"
recvData, address = client_socket.recvfrom(1024)

# Open the received json file to select 3 pokemons
file = open(recvData).read()
playerData = json.loads(file)

pokeList = playerData["player_bag"]

selectedPokemons = []
killedPokemons = []
curpoke = -1

def displayPokemonList(playerBag):

    global killedPokemons

    print "List of your pokemons: "
    for poke in playerBag:

        canSelect = True

        for killedPoke in killedPokemons:
            if int(poke["id"]) == killedPoke:
                canSelect = False
                break

        if canSelect:
            print "Pokemon name:", poke["name"]
            print "Pokemon id:", poke["id"]
            print "Pokemon attributes:"
            print "Accumulated experience:", poke["accum_exp"]
            print "Current level", poke["cur_lvl"]
            print "Type:", poke["type"]
            print "HP:", poke["hp"]
            print "Attack:", poke["atk"]
            print "Defense:", poke["b_def"]
            print "Special attack:", poke["spec_atk"]
            print "Special defense:", poke["spec_def"]
            print "\n"
    return

while len(selectedPokemons) < 3:
    displayPokemonList(pokeList)
    pokeid = raw_input("Please select your pokemon by id: ")
    selectedPokemons.append(pokeid)
    # print len(pokeList)

    for poke in pokeList:
        # print poke["id"], pokeid
        if str(poke["id"]) == str(pokeid):
            pokeList.remove(poke)
            break
    # print len(pokeList)

curpoke = selectedPokemons[0]
data = "-".join(selectedPokemons)
print data
client_socket.sendto(data, ("localhost", 9000))

recvData, address = client_socket.recvfrom(1024)
print "Turn", recvData

# Turn:
# 0: My turn
# 1: Other player's turn
turn = int(recvData)

# Used to determine the next turn
# If killed then must switch or surrender
# else can fight, switch or surrender
wasKilled = False

def fight():
    global client_socket
    client_socket.sendto("Fight", ("localhost", 9000))

def switch():
    global client_socket
    client_socket.sendto("Switch", ("localhost", 9000))

    global curpoke
    global playerData

    pokeList = playerData["player_bag"]
    for poke in pokeList:
        # print poke["id"], pokeid
        if str(poke["id"]) == str(curpoke):
            pokeList.remove(poke)
            break

    displayPokemonList(pokeList)
    pokeid = raw_input("Please choose the id of the pokemon you want to switch")
    curpoke = pokeid
    sendData = "Switch-" + pokeid
    client_socket.sendto(sendData, ("localhost", 9000))


def surrender():
    global client_socket
    client_socket.sendto("Surrender", ("localhost", 9000))

def displayMenu():

    global wasKilled

    if not wasKilled:
        cmd = "Please choose your action:\n"
        cmd += "1: Fight\n"
        cmd += "2: Switch pokemon\n"
        cmd += "3: Surrender"

        while True:
            opt = raw_input(cmd)
            if opt == "1":
                fight()
                return "Fight"
            elif opt == "2":
                switch()
                return "Switch"
            elif opt == "3":
                surrender()
                return "Surrender"
    else:
        cmd = "Please choose your action:\n"
        cmd += "1: Switch pokemon\n"
        cmd += "2: Surrender"

        while True:
            opt = raw_input(cmd)
            if opt == "1":
                switch()
                return "Switch"
            elif opt == "2":
                surrender()
                return "Surrender"

while 1:
    # Send 'Connect Signal'
    if turn == 0:

        print "It's your turn"

        status = displayMenu()

        if "Surrender" in status:
            recvData, address = client_socket.recvfrom(1024)
            print recvData

            client_socket.sendto("q", ("localhost", 9000))
            break
        elif "Fight" in status:
            recvData, address = client_socket.recvfrom(1024)
            print recvData

            if "Won" in recvData:
                client_socket.sendto("q", ("localhost", 9000))
                break

    elif turn == 1:
        print "It's other player's turn"

        recvData, address = client_socket.recvfrom(1024)

        if "surrendered" in recvData:
            print recvData
            client_socket.sendto("q", ("localhost", 9000))
            break
        elif recvData == "killed":
            killedPokemons.append(int(recvData.split("\n")[1]))
            wasKilled = True
        else:
            wasKilled = False

        print recvData.split("\n")[0]

        if "Lost" in recvData:
            print "You just lost the game"
            client_socket.sendto("q", ("localhost", 9000))
            break

    turn = (turn + 1) % 2

print "Thank you for playing"
client_socket.close()
