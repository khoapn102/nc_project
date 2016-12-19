import socket
import time
import threading

# Using UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = "Connect-Khoa-26"
flag = True

while 1:
    # Send 'Connect Signal'
	client_socket.sendto(data,("localhost", 9000))
	
	if(data.lower() == 'q'):
		break

	data = raw_input("(Type q or Q to quit)")
	
client_socket.close()
# t.join()