#!/usr/bin/env python
"""
Created on Thu Oct  4 21:55:54 2018

@author: puneet singh
@version: 0.1
"""


from mpi4py import MPI
import sys
import argparse
import subprocess
import datetime 

size = MPI.COMM_WORLD.Get_size()
rank = MPI.COMM_WORLD.Get_rank()
name = MPI.Get_processor_name()
data={}
input_filename="";
verbosity=0;
if size < 2 :
	print "atleast 2 processes required!"
	exit(1)

if rank==0:
	parser=argparse.ArgumentParser()
	parser.add_argument("-f","--input-filename",dest="input_file",help="filename having linux commands",required=True)
	parser.add_argument("-v","--verbosity",dest="verbosity",type=int,help="values greater than 0 force processes to emit more information")
	args = parser.parse_args()	
	input_filename=args.input_file	
 	verbosity=args.verbosity
	
	#count lines in file
	nlines=0
	with open(input_filename,'r') as f:
		for line in f:
			nlines=nlines+1
	#alott no. of lines per process, line number in file to each rank
	data={}
	for _rank in range(size):
		data[_rank]=[nlines/size,0]	
	
	#if #of lines are not erfectly divisible by #of processes, distribute additional lines 
	remaining_lines=nlines%size
	for _rank in range(remaining_lines):
		data[_rank][0]=data[_rank][0]+1
		
	
#sync dictionary with all processes!	
data = MPI.COMM_WORLD.bcast(data, root = 0)
verbosity = MPI.COMM_WORLD.bcast(verbosity, root = 0)

input_filename=MPI.COMM_WORLD.bcast(input_filename, root = 0)
#line_number=MPI.COMM_WORLD.exscan(data[rank][0],op=MPI.SUM)
end_line_number=MPI.COMM_WORLD.scan(data[rank][0],op=MPI.SUM)
start_line_number=end_line_number - data[rank][0]


data=[]
#print data,rank,start_line_number,end_line_number,input_filename
with open(input_filename,'r') as f:
	for line in f.readlines()[start_line_number:end_line_number]:
		data.append(line.strip())

if verbosity > 1:
	v_filename="rmscip"+datetime.datetime.strftime(datetime.datetime.now(),"%Y%m%d_%H%M%S")+"_"+str(rank)+".info";
	with open(v_filename,'w') as f:
		for line in data:
			line="Rank-" +str(rank)+ ",Command-" +line+ ",filename-" +input_filename+ ",start line-" +str(start_line_number)+ ",end line-" +str(end_line_number)
			f.write(line+'\n')

for command in data:
	output=subprocess.check_output([command],shell=True)	
	if verbosity > 0:
		print output
