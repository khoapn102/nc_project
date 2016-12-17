import socket
import time
import threading


# class Handler(threading.Thread):
# 	def __init__(self,socket):
# 		threading.Thread.__init__(self)
# 		self.socket = socket
# 	def run(self):
# 		while 1:
# 			msg = self.socket.recvfrom(256)
# 			if (msg[0].lower() == 'q'):
# 				break
# 			print "\n<===> ",msg[0]," <===>\n"
		


client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# t = Handler(client_socket)
# t.start()
data = "Connect-Khoa-26"
flag = True

while 1:
    # Send 'Connect Signal'
	client_socket.sendto(data,("localhost",9000))
	
	if(data.lower() == 'q'):
		break
	
	data = raw_input("(Type q or Q to quit)")	
	
client_socket.close()
# t.join()