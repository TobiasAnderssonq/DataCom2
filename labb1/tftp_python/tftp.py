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
	numberOfH = sys.getsizeof(data)/2
    return struct.pack("!"+str(numberOfH+2)+"H", OPCODE_DATA, blocknr, data)

def make_packet_ack(blocknr):
    return struct.pack("!HH", OPCODE_ACK,blocknr)

def make_packet_err(errcode, errmsg):
    return struct.pack("!HH", OPCODE_ERR, errcode) + errmsg + '\0'

def parse_packet(msg):
    """This function parses a recieved packet and returns a tuple where the
        first value is the opcode as an integer and the following values are
        the other parameters of the packets in python data types"""
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
		sizeOfData = sys.getsizeof(msg[4:])/2
		blocknr = struct.unpack("!H", msg[2:4])[0]
		data = struct.unpack("!"+str(sizeofData)+"H", msg[4:])	
		if blocknr != None and data != None    	
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
		if errcode != None and errormsg != None:
			return opcode, errcode, errmsg
		return None	

	return None	

def tftp_transfer(fd, hostname, direction):
    # Implement this function
    
    # Open socket interface
    cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	(family, socktype, proto, canonname, sockaddr) = getaddrinfo(hostname)
    # Check if we are putting a file or getting a file and send
    #  the corresponding request.
    
    # Put or get the file, block by block, in a loop.
    while True:
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
