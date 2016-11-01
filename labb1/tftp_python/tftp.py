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

TFTP_PORT= 69

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
		data = struct.unpack("!"+str(sizeOfData)+"s", msg[4:])[0]
		print sizeOfData
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

def tftp_transfer(fd, hostname, direction):
    # Implement this function
    
    # Open socket interface
	
	(family, socktype, proto, canonname, address) = socket.getaddrinfo(hostname, TFTP_PORT)[1]
	cs = socket.socket(family, socktype, proto)
	if direction == TFTP_GET:
		request = make_packet_rrq(fd.name, MODE_OCTET)
	else:
		request = make_packet_wrq(fd.name, MODE_OCTET)
    # Check if we are putting a file or getting a file and send
    #  the corresponding request.
	cs.sendto(request, address)
    # Put or get the file, block by block, in a loop.

	rcv_total = 0
	
	while True:
		(rl,wl,xl) = select.select([cs], [cs], [], TFTP_TIMEOUT)

		if direction == TFTP_GET:
			
			rcv_buffer, addr = cs.recvfrom(BLOCK_SIZE+HEADER_SIZE)	
			opcode, blocknr, data = parse_packet(rcv_buffer)
			fd.write(data[0])
			ack_packet = make_packet_ack(blocknr)
			cs.sendto(ack_packet, addr)	
			rcv_total += len(rcv_buffer)
			
			if len(rcv_buffer) < BLOCK_SIZE:
				print "Received: " + str(rcv_total) + " Bytes"
				break


		if direction == TFTP_PUT:
			rcv_buffer, addr = cs.recvfrom(BLOCK_SIZE+HEADER_SIZE)		
			packet = parse_packet(rcv_buffer)

			if packet[0] == OPCODE_ACK:
				blocknr = packet[1]+1
				data = fd.read(BLOCK_SIZE)
				data_packet = make_packet_data(blocknr,data)
				
				cs.sendto(data_packet,addr)
				if len(data) < BLOCK_SIZE:
					print "Finished Uploading!"
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
