import sys
import subprocess

current_run = 0
file_operate = sys.argv[1]
number_of_runs = sys.argv[2]

while current_run < int(number_of_runs):
	subprocess.call('python avg_time_upload_measurements.py '+ str(file_operate) + ' 1', shell=True)
	subprocess.call('python avg_time_dl_measurements.py '+ str(file_operate) + ' 1', shell=True)
	current_run +=1
