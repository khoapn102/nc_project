import socket

# Using UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = "Connect-Khoa-26"
client_socket.sendto(data,("localhost", 9000))

while 1:
    # Send 'Connect Signal'
	recvData, address = client_socket.recvfrom(1024)

	print recvData
	
	if(recvData.lower() == 'q'):
		print "End the current session Pokecat game"
		print "Thank you for playing"
		break

	# data = raw_input("(Type q or Q to quit)")
	
client_socket.close()