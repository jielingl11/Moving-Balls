#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 13:46:47 2022

@author: jielinglee
"""
import ball_class as bc
import numpy as np
from copy import deepcopy 
import time
import sys
import json 

# set the parameters

box_size= np.array([30, 40, 30]) # the size of cathode 

ball_radius= 5 # the radius of active particles

min_dis_APs= 0.15 # minimum distance between two active particles 

coating = min_dis_APs

# choose to input the number of balls or volume fraction 

'''
choose = 0 means to input the number of balls. For example, if no_balls = 30, 
it means 30 balls will be arranged inside the box. 

choose = 1 means to input the target volume fraction. For example, if vf= 0.23 
is chosen, the algorithm will calculate the number of balls close to the target 
volume fraction. 16 balls has the volume fraction of 0.2327 which is the closest 
value to the target volume, so 16 balls will be aranged inside the box.
'''
choose= 1 # type either 0 or 1. 0 for the number of balls and 1 for volume fraction 

no_balls = 32 # type the number of balls if choose = 0 (ignore this if choose = 1)
 
vf= 0.23 # type the target volume fraction if choose = 1 (ignore this if choose = 0)


#%%

# Set the positions of balls. The balls are randomly allocated inside the box

def rand_pos(i):
	a= box_size[i]/2- ball_radius- min_dis_APs/2
	return np.random.uniform(-a, a)

# Find the actual volume fraction if choose is set to be 1

'''
The function find_volume_fraction is to find the actual volume fraction if choose = 1. 
To do so, the volume fractions from 1 to 40 balls are calculated and saved in an array. 
As the volume fractions are known, we can find the value in the array that is the closest 
to the target volume fraction, and hence know the number of balls in the box.
'''
def find_volume_fraction(vf):
	vf_array= np.array([])
	# calculate the volume fraction from 1 to 40 balls and save the values in an array
	for no_balls in range(1, 41, 1):
		ball_volume= (4* np.pi* ball_radius**3*no_balls)/3
		vf_i= ball_volume/ (box_size[0]*box_size[1]*box_size[2])
		vf_array= np.append(vf_array, vf_i)
	# find the closest value 
	# calculate the difference between every value in the array and the target volume fraction 
	diff= vf_array- np.ones(40)*vf 
	# the closest value is either the largest negative value or the smallest positive value in the array 
	diff_n= np.where(diff<0, diff, -1)
	diff_p= np.where(diff>0, diff, 1)
	# calculate the absolute values 
	diff_p_min= abs(min(diff_p))
	diff_n_max= abs(max(diff_n))
	# choose the smaller value 
	# this will give the number of balls corrpsponding to the target volume fraction 
	if diff_p_min > diff_n_max:
		no= np.argmax(diff_n)+1
	else:
		no= np.argmin(diff_p)+1
	return no

if choose==1:
	no_balls = find_volume_fraction(vf)
	print('There are', no_balls, 'balls in total')



# create a list to save all balls 
Balls=[]

# the positions of balls are randomly arranged inside the box
for i in range(no_balls):
	ball= bc.Ball(rand_pos(0), rand_pos(1), rand_pos(2), ball_radius, min_dis_APs)
	Balls.append(ball)


# calculate the volume_fraction
def actual_volume_fraction(no_balls, ball_radius):
	ball_volume= 4/3* np.pi* ball_radius**3*no_balls
	vf= ball_volume/ (box_size[0]*box_size[1]*box_size[2])	
	return vf


print('')
vf= actual_volume_fraction(no_balls, ball_radius)
print('The actual volume fraction=', '%.4f'%vf)



#%%
# start arranging the balls 

'''
The algorithm is set to perform 10000 moves (num_steps) in a cycle.In each cycle, 
the distance that the ball moves is a ramdonly selectd value between 0 and delta. 
In each move, whether to accept or not will be decided. If the overlap function 
increases, then the move is rejected; otherwise, the move is accepted. 

The overlap function at the end of each cycle (= each 10000ish move) is recorded. 

The algorithm ends if the overlap function equals zero, and if it happens, 
"Final configuration has been archived" will be printed. However, If the overlap 
function keep remaining the same (i.e. the change of the overlap function is small),
the algortihm ends. To determine the small change, the difference of the overlap 
function between the current and the previous cycle is calculated (small). 
If small < 0.001, then the algorithm ends. 
'''

def arrange(Balls):
	# the difference of the overlap function between the current and the previous cycle 
	# assign a big value so the first attempt is always accepted 
	small=999 
	previous_overlap= 999
	# the number of attempts 
	n=1
	# the maximum distance for each move 
	delta= 5
	# the number of moves in a cycle 
	num_steps= 10000
	# a value to determine whether the final configuration has been archived 
	reach=0
	
	while small> 0.001:
		print('The number of attempts:', n)
		# refers to the arrangement in ball_class.py
		sim= bc.Simulation(Balls)
		a = sim.run(num_steps=num_steps, delta=delta, box_size= box_size, print_overlap=0, animate= False)
		overlap= a[0]
		count= a[1]
		if overlap==999:
			print('')
			print('Final configuration has been archived')
			break
		small=  previous_overlap- overlap
		previous_overlap= deepcopy(overlap)
		Balls= deepcopy(Balls)
		delta= overlap/count 
		print('Delta', delta)
		print('')
		n+=1
	
	if small<= 0.001:
		reach=1
	return Balls, reach 


start = time.time()

# Try three times if the final configuration still can not be archived, then the algorithm ends 
for j in range(3):
	Balls,reach = arrange(Balls)
	if reach==0:
		break 
	else:
		print('')
		print('TRY AGAIN')
		print('')
			
end = time.time()

print('')
print("The time of execution is :",  end-start, '(s)')

if reach==1:
	print('')
	print('Final configuration CAN NOT be archived')	
	sys.exit(0)



#%% save the final configuration in a Jason file 


# find a point on the surface 

APs_data=[]

for ball in Balls:
	alpha= 0
	beta= np.pi/4
	# translation on the coordinate plane 
	ball.centre= ball.centre+box_size/2
	# find a point on the surface of the ball
	xr= ball.radius*np.cos(alpha)*np.cos(beta)
	yr= ball.radius*np.cos(alpha)*np.sin(beta)
	zr= ball.radius*np.sin(alpha)
	# find a point on the surface of the coating 
	xr_c= (ball.radius+coating)*np.cos(alpha)*np.cos(beta)
	yr_c= (ball.radius+coating)*np.cos(alpha)*np.sin(beta)
	zr_c= (ball.radius+coating)*np.sin(alpha)
	xyzr= np.array([xr, yr, zr])+ ball.centre
	xyzr_c= np.array([xr_c, yr_c, zr_c])+ ball.centre
	# APs data structure: radius + the centre of the ball + a point on the surface + radius with coating + a point on the coating 
	APs= list(np.array([float(ball.radius)]))+list(ball.centre)+list(xyzr)+list(np.array([float(ball.radius+coating)]))+list(xyzr_c)
	APs_data.append(APs)



# save data to a json file 

data = {'APs_data': tuple(APs_data),
		'Cathode_data': tuple(box_size.astype(np.float64)),
		'Same_size':1,
		'VF': vf,
		'delmin_APs': min_dis_APs}

file_name= 'APs_sameSize_N'+str(no_balls)+'.json'

with open(file_name, 'w') as f:
	json.dump(data, f)
	
	




