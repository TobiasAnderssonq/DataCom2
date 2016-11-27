#! /usr/bin/python

import sys,socket,struct,select

BLOCK_SIZE= 512

OPCODE_RRQ=   1
OPCODE_WRQ=   2
OPCODE_DATA=  3
OPCODE_ACK=   4
OPCODE_ERR=   5

MODE_NETASCII= "netascii"
MODE_OCTET=    "octet"
MODE_MAIL=     "mail"

TFTP_PORT= 20069

# Timeout in seconds
TFTP_TIMEOUT= 2
HEADER_SIZE = 4

ERROR_CODES = ["Undef",
               "File not found",
               "Access violation",
               "Disk full or allocation exceeded",
               "Illegal TFTP operation",
               "Unknown transfer ID",
               "File already exists",
               "No such user"]

# Internal defines
TFTP_GET = 1
TFTP_PUT = 2


def make_packet_rrq(filename, mode):
    # Note the exclamation mark in the format string to pack(). What is it for?
    return struct.pack("!H", OPCODE_RRQ) + filename + '\0' + mode + '\0'

def make_packet_wrq(filename, mode):
    return struct.pack("!H", OPCODE_WRQ) + filename + '\0' + mode + '\0'

def make_packet_data(blocknr, data):
	return struct.pack("!HH", OPCODE_DATA, blocknr) + data

def make_packet_ack(blocknr):
    return struct.pack("!HH", OPCODE_ACK,blocknr)

def make_packet_err(errcode, errmsg):
    return struct.pack("!HH", OPCODE_ERR, errcode) + errmsg + '\0'

def parse_packet(msg):
    #"""This function parses a recieved packet and returns a tuple where the
    #   first value is the opcode as an integer and the following values are
    #    the other parameters of the packets in python data types"""
	opcode = struct.unpack("!H", msg[:2])[0]
	
	if opcode == OPCODE_RRQ:
		l = msg[2:].split('\0')
		if len(l) != 3:
			return None
		return opcode, l[0], l[1] #PREVIOUSLY 1 AND 2

	elif opcode == OPCODE_WRQ:
		l = msg[2:].split('\0')
		if len(l) != 3:
			return None
		return opcode, l[0], l[1] #PREVIOUSLY 1 AND 2

	elif opcode == OPCODE_DATA:
		sizeOfData = len(msg[4:])
		blocknr = struct.unpack("!H", msg[2:4])[0]
		data = struct.unpack("!"+str(sizeOfData)+"s", msg[4:])
		if blocknr != None and data != None:
			return opcode, blocknr, data
		return None

	elif opcode == OPCODE_ACK:
		blocknr = struct.unpack("!H", msg[2:4])[0]
		if blocknr != None:
			return opcode, blocknr
		return None
	
	elif opcode == OPCODE_ERR:
		errcode = struct.unpack("!H", msg[2:4])[0]
		errmsg = msg[4:].split('\0')
		if errcode != None and errmsg != None:
			return opcode, errcode, errmsg
		return None	

	return None

#Special while-loop for the acknowledgement when sending the last data packet.
def waitForLastAck(data_packet, expblocknr, cs, addr, maxresend=10):
	while True:
		try:
			if maxresend <= 0:
				cs.close()
				sys.exit(1)

			rcv_buffer, addr = cs.recvfrom(BLOCK_SIZE+HEADER_SIZE)		
			packet = parse_packet(rcv_buffer)
			if packet[1] != expblocknr:
				continue

		except socket.timeout, e:
			if e.args[0] == 'timed out':
				print "Timed out, resending data from blocknumber: " + str(expblocknr)
				cs.sendto(data_packet,addr)
				maxresend = maxresend - 1
				continue
		return None

#Tries to get the address info
def getAddrInfo(hostname):
	try:
		return socket.getaddrinfo(hostname, TFTP_PORT)[1]
	except Exception as e:
		print "Failed to get address info on hostname: " + str(hostname) + "\nERROR: %s" % e
		sys.exit(1)

#Creates a socket
def createSocket(family, socktype, proto):
	try:
		return socket.socket(family, socktype, proto)
	except Exception as e:
		print "Failed to create socket with data: " + str(family) + " " + str(socktype) + " " + str(proto) + "\nERROR: %s" % e 
		sys.exit(1)


def tftp_transfer(fd, hostname, direction, maxresend=10):
    # Implement this function
    
	# Get adress info
	(family, socktype, proto, canonname, addr) = getAddrInfo(hostname)
	
	# Create socket
	cs = createSocket(family, socktype, proto)
	
	# Set the socket timeout
	cs.settimeout(0.8)

	# Check if we are putting a file or getting a file and send
    	# the corresponding request.
	if direction == TFTP_GET:
		request = make_packet_rrq(fd.name, MODE_OCTET)
	elif direction == TFTP_PUT:
		request = make_packet_wrq(fd.name, MODE_OCTET)
	else:
		print "Invalid direction!"
		cs.close()
		sys.exit(1)


	# Make the intial request to the server
	try:
		cs.sendto(request, addr)
	except Exception as e:
		print "Failed to send to address: " + str(addr) + "\nERROR: %s" % e
		sys.exit(1)



	# Declearing some variables before the while-loop 	
	oldblocknr = -1
	rcv_total = 0
	upload_total = 0
	next_packet = request
	
	# Put or get the file, block by block, in a loop.
	while True:

 

		if direction == TFTP_GET:
			
			try:				
				rcv_buffer, addr = cs.recvfrom(BLOCK_SIZE+HEADER_SIZE)
				maxresend = 10
			except socket.timeout, e:
				if e.args[0] == 'timed out':
					if maxresend <= 0:
						cs.close()
						sys.exit(1)

					print "Timed out, resending ack for blocknumber: " + str(oldblocknr)
					cs.sendto(next_packet, addr)
					maxresend = maxresend - 1
					
			except Exception as e:
				print "Failed to receieve data from socket " + str(cs) + "\nError: %s" % e
				cs.close()
				sys.exit(1)


			packet = parse_packet(rcv_buffer)

			
			if packet[0] == OPCODE_DATA:
				#Check if duplicate
				if oldblocknr >= packet[1]:
					continue
				blocknr = packet[1]
				fd.write(packet[2][0]) #Write to filedescriptor
				next_packet = make_packet_ack(packet[1]) #Create acknoledgement packet

				try:
					
					cs.sendto(next_packet, addr) #Send acknowledgement
					oldblocknr = blocknr #Keep track of old blocknumber
				except Exception as e:
					print "Failed to send to address: " + addr + "\nERROR: %s" % e
					cs.close()
					sys.exit(1)

				rcv_total += len(rcv_buffer)-HEADER_SIZE
				if len(rcv_buffer) < BLOCK_SIZE:
					print "Received: " + str(rcv_total) + " Bytes"
					break
			
			elif packet[0] == OPCODE_ERR:
				print packet[2]
				sys.exit(1)
				


		if direction == TFTP_PUT:
			
			try:
				rcv_buffer, addr = cs.recvfrom(BLOCK_SIZE+HEADER_SIZE) #Read data from socket	
			except socket.timeout, e:
				if e.args[0] == 'timed out':
					if maxresend <= 0:
						cs.close()
						sys.exit(1)
					print "Timed out, resending data from blocknumber: " + str(oldblocknr)
					cs.sendto(next_packet,addr)
					maxresend = maxresend - 1

			except Exception as e:
				print "Failed to receieve data from socket " + str(cs) + "\nError: %s" % e
				cs.close()
				sys.exit(1)

			

			packet = parse_packet(rcv_buffer)
			
			if packet[0] == OPCODE_ACK:
				if packet[1] != oldblocknr + 1:
					continue
				oldblocknr = packet[1]

				data = fd.read(BLOCK_SIZE) #Read data from filedescriptor
				next_packet = make_packet_data(oldblocknr+1,data) #Make the data packet
				try:
					cs.sendto(next_packet,addr) #Send data packet
				except Exception as e:
					print "Failed to send to address: " + addr + "\nERROR: %s" % e
					cs.close()
					sys.exit(1)
				upload_total += len(data)

			#Check if last package has been sent.
			if len(data) < BLOCK_SIZE:
					waitForLastAck(next_packet, oldblocknr+1, cs, addr)
					break			

			elif packet[0] == OPCODE_ERR:
				print packet[2]
				cs.close()
				sys.exit(1)

        pass


def usage():
    """Print the usage on stderr and quit with error code"""
    sys.stderr.write("Usage: %s [-g|-p] FILE HOST\n" % sys.argv[0])
    sys.exit(1)


def main():
    # No need to change this function
    direction = TFTP_GET
    if len(sys.argv) == 3:
        filename = sys.argv[1]
        hostname = sys.argv[2]
    elif len(sys.argv) == 4:
        if sys.argv[1] == "-g":
            direction = TFTP_GET
        elif sys.argv[1] == "-p":
            direction = TFTP_PUT
        else:
            usage()
            return
        filename = sys.argv[2]
        hostname = sys.argv[3]
    else:
        usage()
        return

    if direction == TFTP_GET:
        print "Transfer file %s from host %s" % (filename, hostname)
    else:
        print "Transfer file %s to host %s" % (filename, hostname)

    try:
        if direction == TFTP_GET:
            fd = open(filename, "wb")
        else:
            fd = open(filename, "rb")
    except IOError as e:
        sys.stderr.write("File error (%s): %s\n" % (filename, e.strerror))
        sys.exit(2)

    tftp_transfer(fd, hostname, direction)
    fd.close()

if __name__ == "__main__":
    main()
