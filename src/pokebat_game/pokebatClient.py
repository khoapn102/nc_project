import socket
import json

# Using UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

player_json = recvData
# Open the received json file to select 3 pokemons
file = open(recvData).read()
playerData = json.loads(file)

pokeList = list(playerData["player_bag"])

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
    return

def switch():
    global client_socket

    global curpoke
    global playerData

    global selectedPokemons

    pokeList = []

    # print "The current pokemon list:"
    # print pokeList

    curid = 0

    while curid < len(selectedPokemons):
        if selectedPokemons[curid] == curpoke:
            curid += 1

        for poke in playerData["player_bag"]:
            # print poke["id"], str(curpoke), str(selectedPokemons[curid])

            if str(poke["id"]) != str(curpoke) and str(poke["id"]) == str(selectedPokemons[curid]):
                pokeList.append(poke)
                curid += 1
                break

    # print "The current pokemon list:"
    # print pokeList

    displayPokemonList(pokeList)
    pokeid = raw_input("Please choose the id of the pokemon you want to switch: ")

    curpoke = pokeid
    sendData = "Switch-" + pokeid
    client_socket.sendto(sendData, ("localhost", 9000))
    return

def surrender():
    global client_socket
    client_socket.sendto("Surrender", ("localhost", 9000))
    return

def displayMenu():

    global wasKilled

    if not wasKilled:
        cmd = "Please choose your action:\n"
        cmd += "1: Fight\n"
        cmd += "2: Switch pokemon\n"
        cmd += "3: Surrender\n"

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
        cmd += "2: Surrender\n"

        while True:
            opt = raw_input(cmd)
            if opt == "1":
                switch()
                return "Switch"
            elif opt == "2":
                surrender()
                return "Surrender"
    return ""

def destroy_pokemon():
    print '--- List of possible pokemon for destroying ----\n'
    # for pokemon in pokeList:
    #     print "Pokemon name:", poke["name"]
    #     print "Pokemon id:", poke["id"]
    #     print "Accumulated experience:", poke["accum_exp"]
    #     print "Current level", poke["cur_lvl"]
    #     print "Type:", poke["type"]

    displayPokemonList(pokeList)
    id_destroy = int(raw_input('Enter the id of pokemon you want to destroy: '))
    id_receive = int(raw_input('Enter the id of pokemon you want to give to: '))

    given_exp = 0
    temp_bag = playerData['player_bag']
    # print temp_bag
    poke_a = {}
    poke_b = {}
    for pokemon in temp_bag:
        if id_destroy == pokemon['id']:
            poke_a = pokemon.copy()
            # temp_bag.remove(poke_a)
            break
    print '++++++++++', poke_a

    for pokemon in temp_bag:
        if id_receive == pokemon['id']:
            poke_b = pokemon.copy()
            # temp_bag.remove(poke_b)
            break

    print '----------', poke_b['name'], poke_b['cur_exp']

    check = False

    for element in poke_a['type']:
        if element in poke_b['type']:
            check = True
            break

    if check == True:
        temp_bag.remove(poke_a)
        temp_bag.remove(poke_b)
        given_exp = poke_a['accum_exp']
        poke_b['curr_exp'] += given_exp
        lvl_up_amt = 0
        if poke_b['curr_exp'] > poke_b['accum_exp']:
            lvl_up_amt = poke_b['curr_exp']/poke_b['accum_exp']
            poke_b['curr_exp'] %= poke_b['accum_exp']
        for i in range(0, lvl_up_amt):
            poke_b['cur_lvl'] += 1
            poke_b['nxt_lvl'] = poke_b['cur_lvl'] + 1
            poke_b['accum_exp'] *= 2
            poke_b['hp'] = round(poke_b['hp']*(1+poke_b['ev']), 1)
            poke_b['atk'] = round(poke_b['atk']*(1+poke_b['ev']), 1)
            poke_b['b_def'] = round(poke_b['b_def']*(1+poke_b['ev']), 1)
            poke_b['spec_atk'] = round(poke_b['spec_atk']*(1+poke_b['ev']), 1)
            poke_b['spec_def'] = round(poke_b['spec_def']*(1+poke_b['ev']), 1)
        print 'Scarified !'
        print '----------', poke_b['name'], poke_b['cur_exp']
    # else:
    #     print 'Cant Sacrified'
    #     return
        temp_bag.append(poke_b)
        playerData['player_bag'] = temp_bag
        with open(player_json, 'w') as outfile:
            json.dump(playerData, outfile, indent=4, sort_keys=True)

    print 'Done'

    return

while 1:
    # Send 'Connect Signal'
    if turn == 0:

        print "It's your turn"

        answer = raw_input('Do you want to destroy a pokemon to level up your fighting pokemons ? (y/n)')

        if answer == 'y':

            destroy_pokemon()

        status = displayMenu()

        # print "Current status", status

        if "Surrender" in status:
            recvData, address = client_socket.recvfrom(1024)
            print recvData

            # client_socket.sendto("q", ("localhost", 9000))
            break

        elif "Fight" in status:
            recvData, address = client_socket.recvfrom(1024)

            if "Won" in recvData:
                print recvData.split("\n")[0]
                print "You just won the PokeBat game."
                # client_socket.sendto("q", ("localhost", 9000))
                break

            print recvData

        elif "Switch" in status:
            recvData, address = client_socket.recvfrom(1024)
            print recvData

    elif turn == 1:
        print "It's other player's turn"

        recvData, address = client_socket.recvfrom(1024)

        if "surrendered" in recvData:
            print recvData
            # client_socket.sendto("q", ("localhost", 9000))
            break

        elif "killed" in recvData:
            selectedPokemons.remove(recvData.split("\n")[1])
            wasKilled = True
        else:
            wasKilled = False

        print recvData.split("\n")[0]

        if "Lost" in recvData:
            print "You just lost the PokeBat game."
            # client_socket.sendto("q", ("localhost", 9000))
            break

    turn = (turn + 1) % 2

print "Thank you for playing PokeBat game."

client_socket.close()
