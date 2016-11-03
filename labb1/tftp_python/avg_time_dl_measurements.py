import time
import sys
import subprocess
import os

start_time = time.time()
file_to_dl = sys.argv[1]



if len(sys.argv) == 3:
	number_of_runs = int(sys.argv[2])

current_run = 0
while current_run < number_of_runs:
	try:
		os.remove(file_to_dl)
	except OSError:
		pass

	downloaded_file = subprocess.call('python tftp.py -g ' + str(file_to_dl) + " rabbit.it.uu.se", shell=True)
	subprocess.call('md5sum '+ str(file_to_dl), shell=True)
	current_run = current_run+1

total_time = ((time.time() - start_time)/current_run)


print "Avg time to download:"+ str(total_time) + " seconds --------  Number of samples:" + str(current_run)


