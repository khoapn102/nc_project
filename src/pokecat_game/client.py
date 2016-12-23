import socket

# Using UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print '-------------- Welcome to Pokemon World ! ------------------\n'

# Login Credential
opt = int(raw_input('Please enter 1 to start logging in or 2 for registering an account: '))
if opt == 1:
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
			break
		elif recvData == 'error':
			print 'Invalid Login Credential !!!'
elif opt == 2:
	while 1:
		print 'Please register a unique username and a password !'
		username = raw_input('Username: ')
		password = raw_input('Password: ')
		data = "Register-"
		data += username + '-' + password
		print data
		client_socket.sendto(data,("localhost", 9000))
		recvData, address = client_socket.recvfrom(1024)
		if recvData == 'proceed':
			break
		elif recvData == 'error':
			print 'Not an unique username !!!'

while 1:

	recvData, address = client_socket.recvfrom(1024)

	if recvData.lower() == 'q':
		print "End the current session Pokecat game"
		print "Thank you for playing"
		break

	print recvData

	# data = raw_input("(Type q or Q to quit)")
	
client_socket.close()