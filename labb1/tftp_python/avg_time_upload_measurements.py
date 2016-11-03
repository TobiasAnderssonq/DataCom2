import time
import sys
import subprocess
import os

start_time = time.time()
file_to_upload = sys.argv[1]


if (os.path.exists(file_to_upload)):

	if len(sys.argv) == 3:
		number_of_runs = int(sys.argv[2])


	current_run = 0
	while current_run < number_of_runs:
	
		downloaded_file = subprocess.call('python tftp.py -p ' + str(file_to_upload) + " rabbit.it.uu.se", shell=True)
		current_run = current_run+1
	

	total_time = ((time.time() - start_time)/current_run)
	subprocess.call('echo Average time: ' + str(total_time) + " File size: " + str(file_to_upload) + " >> result.txt", shell=True)
	print "Avg time to upload:"+ str(total_time) + " seconds --------  Number of samples:" + str(current_run)
else:
	print "No such file"

