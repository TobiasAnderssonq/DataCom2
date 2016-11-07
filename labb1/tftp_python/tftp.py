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

TFTP_PORT= 6969

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

def waitForLastAck(data_packet, blocknr, cs, addr):
	while True:
		try:
			rcv_buffer, addr = cs.recvfrom(BLOCK_SIZE+HEADER_SIZE)		
		except socket.timeout, e:
			if e.args[0] == 'timed out':
				print "Timed out, resending data from blocknumber: " + str(blocknr)
				cs.sendto(data_packet,addr)
				continue
		return None

def openSocketInterface(hostname):
	try:
		return socket.getaddrinfo(hostname, TFTP_PORT)[1]
	except Exception as e:
		print "Failed to get address info on hostname: " + str(hostname) + "\nERROR: %s" % e
		sys.exit(1)


def createSocket(family, socktype, proto):
	try:
		return socket.socket(family, socktype, proto)
	except Exception as e:
		print "Failed to create socket with data: " + str(family) + " " + str(socktype) + " " + str(proto) + "\nERROR: %s" % e 
		sys.exit(1)

def waitForFDs(cs):
	try:
		return select.select([cs], [cs], [], TFTP_TIMEOUT)
	except Exception as e:
		print "Socket not ready: " + str(cs) + "\nERROR: %s" % e
		sys.exit(1)


def tftp_transfer(fd, hostname, direction):
    # Implement this function
    
    # Open socket interface
	(family, socktype, proto, canonname, address) = openSocketInterface(hostname)
	
	# Create socket
	cs = createSocket(family, socktype, proto)
	
	# Set the socket timeout
	cs.settimeout(0.8)

	# Check if we are putting a file or getting a file and send
    	# the corresponding request.
	if direction == TFTP_GET:
		request = make_packet_rrq(fd.name, MODE_OCTET)
	else:
		request = make_packet_wrq(fd.name, MODE_OCTET)

	# Make the intial request to the server
	try:
		cs.sendto(request, address)
	except Exception as e:
		print "Failed to send to address: " + str(address) + "\nERROR: %s" % e
		sys.exit(1)



	# Declearing some variables before the while-loop 
	blocknr = 0
	oldblocknr = 0
	rcv_total = 0
	upload_total = 0
	
	
	# Put or get the file, block by block, in a loop.
	while True:

		# Waiting until the file descriptors are ready for either read or write.
		(rl,wl,xl) = waitForFDs(cs)
 

		if direction == TFTP_GET:
			
			try:				
				rcv_buffer, addr = cs.recvfrom(BLOCK_SIZE+HEADER_SIZE)
			except socket.timeout, e:
				if e.args[0] == 'timed out':
					print "Timed out, resending ack for blocknumber: " + str(blocknr)
					# Check if the inital request failed if so try to send the request again
					# else send the ack again			
					if blocknr == 0:						
						cs.sendto(request, address) 
					else:
						cs.sendto(ack_packet, addr)
					continue
			except Exception as e:
				print "Failed to receieve data from socket " + str(cs) + "\nError: %s" % e
				sys.exit(1)


			packet = parse_packet(rcv_buffer)

			
			if packet[0] == OPCODE_DATA:
				if oldblocknr >= packet[1]:
					continue
				blocknr = packet[1]
				fd.write(packet[2][0])
				ack_packet = make_packet_ack(packet[1])

				try:
					
					cs.sendto(ack_packet, addr)
					oldblocknr = packet[1]
				except Exception as e:
					print "Failed to send to address: " + addr + "\nERROR: %s" % e
					sys.exit(1)

				rcv_total += len(rcv_buffer)-HEADER_SIZE
				if len(rcv_buffer) < BLOCK_SIZE:
					print "Received: " + str(rcv_total) + " Bytes"
					break
			
			if packet[0] == OPCODE_ERR:
				print packet[2]
				


		if direction == TFTP_PUT:
			
			try:
				rcv_buffer, addr = cs.recvfrom(BLOCK_SIZE+HEADER_SIZE)		
			except socket.timeout, e:
				if e.args[0] == 'timed out':
					print "Timed out, resending data from blocknumber: " + str(blocknr)
					if blocknr == 0:
						#Inital request failed, try to send again
						cs.sendto(request, address) 
					else:					
						cs.sendto(data_packet,addr)
					continue
			except Exception as e:
				print "Failed to receieve data from socket " + str(cs) + "\nError: %s" % e

			

			packet = parse_packet(rcv_buffer)
			
			if packet[0] == OPCODE_ACK:
								
				blocknr = packet[1]+1
				print str(packet[1])
				if oldblocknr > packet[1]:
					print "Received package: " + str(packet[1]) + " Expected: " + str(oldblocknr)
					blocknr = oldblocknr+1

				data = fd.read(BLOCK_SIZE)
				data_packet = make_packet_data(blocknr,data)
				oldblocknr = blocknr
				try:
					cs.sendto(data_packet,addr)
				except Exception as e:
					print "Failed to send to address: " + addr + "\nERROR: %s" % e
					sys.exit(1)
				upload_total += len(data)

			if len(data) < BLOCK_SIZE:
					waitForLastAck(data_packet, blocknr, cs, addr)
					break			

			if packet[0] == OPCODE_ERR:
				print packet[2]
				
        # Wait for packet, write the data to the filedescriptor or
        # read the next block from the file. Send new packet to server.
        # Don't forget to deal with timeouts and received error packets.
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
