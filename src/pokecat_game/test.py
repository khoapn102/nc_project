import threading
from time import sleep
import random

poke_world = [[0 for x in range(1000)] for y in range(1000)]
# Initialize playerworld - to move around
player_world = [[0 for x in range(1000)] for y in range(1000)]

def main():
    t = Test()
    t.go()
    try:
        join_threads(t.threads)
    except KeyboardInterrupt:
        print "\nKeyboardInterrupt catched."
        print "Terminate main thread."
        print "If only daemonic threads are left, terminate whole program."


class Test(object):
    def __init__(self):
        self.running = True
        self.threads = []
    def generate_pos(self):
        x = random.randint(0,999)
        y = random.randint(0,999)
        return (x,y)
    def generate_pokemon(self):
        while(self.running):
            threading.Timer(10, self.generate_pokemon).start()
            batch_loc = []
            print 'Spawning Pokemon.............!!!'
            count = 0
            while count < 50:
                # Pokemon random index 1 - 150
                index = random.randint(1, 150)
                x,y = self.generate_pos()
                batch_loc.append((x,y))
                if poke_world[x][y] == 0:
                    poke_world[x][y] = index
                    count += 1
            print 'Complete Spawning !!!'
            sleep(20) # Wait for 5 mins
            for loc in batch_loc:
                x = loc[0]
                y = loc[1]
                # Search for current spawn batch and despawn them
                if poke_world[x][y] != 0:
                    poke_world[x][y] = 0
            print 'Despawned Pokemon............!!!'

    def get_user_input(self):
        while True:
            x = raw_input("Enter 'e' for exit: ")
            if x.lower() == 'e':
               self.running = False
               break

    def go(self):
        t1 = threading.Thread(target=self.generate_pokemon)
        t2 = threading.Thread(target=self.get_user_input)
        # Make threads daemonic, i.e. terminate them when main thread
        # terminates. From: http://stackoverflow.com/a/3788243/145400
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()
        self.threads.append(t1)
        self.threads.append(t2)


def join_threads(threads):
    """
    Join threads in interruptable fashion.
    From http://stackoverflow.com/a/9790882/145400
    """
    for t in threads:
        while t.isAlive():
            t.join(5)


if __name__ == "__main__":
    main()