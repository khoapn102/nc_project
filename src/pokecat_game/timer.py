import threading

def hello():
    print "Hello"

t = threading.Timer(1.0, hello)
t.start()