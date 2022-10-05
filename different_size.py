#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 14:42:44 2022

@author: jielinglee
"""

import ball_class as bc
import numpy as np
from copy import deepcopy 
import time
import json
import sys

# set the parameters

box_size= np.array([30, 40, 30]) # the size of cathode 

mu= 5 # mean of the distribution 

sigma= 1 # std of the distribution 

min_dis_APs= 0.15 # minimum distance between two active particles 

coating= min_dis_APs

# choose to input the number of balls or volume fraction 
'''
choose = 0 means to input the number of balls. For example, if no_balls = 30, 
it means 30 balls will be arranged inside the box. 

choose = 1 means to input the target volume fraction. For example, if vf= 0.23 
is chosen, the algorithm will calculate the number of balls close to the target 
volume fraction. 16 balls has the volume fraction of 0.2327 which is the closest 
value to the target volume, so 16 balls will be aranged inside the box.
'''
choose=0 # type either 0 or 1. 0 for the number of balls and 1 for volume fraction 

# if choose = 0
no_balls= 25 # type the number of balls if choose = 0 (ignore this if choose = 1)

# if choose = 1 
vf_target= 0.42 # type the target volume fraction if choose = 1 (ignore this if choose = 0)

# type the accpeted error of the target volume fraction 
# For example, if the target volume fraction = 0.42 and vf_delta = 0.03,
# the alogrithm will find the volume fraction between 0.39 and 0.45

vf_delta= 0.03


# set the positions of balls 
def rand_pos(i, radius):
	a= box_size[i]/2- radius- min_dis_APs/2
	return np.random.uniform(-a, a)


def volume_fraction(Balls):
	ball_volume= 0
	for ball in Balls:
		v= (4*np.pi* ball.radius**3)/3
		ball_volume+= v
	vf= ball_volume/ (box_size[0]*box_size[1]*box_size[2])	
	return vf


# calculate the volume fraction if choose = 0 
def actual_vf_no(no_balls):
	n=0
	vf_i= 1
	# 0.47 is the maximum volume fraction that can be archived 
	# so only generate the value less than 0.47
	while vf_i > 0.47:
		Balls=[]
		for i in range(no_balls):
			# generate a normal distribution and sort by size in the list 
			radius= sorted(np.random.normal(loc=mu, scale=sigma, size=no_balls), reverse=True)
			ball_radius= radius[i]
			ball= bc.Ball(rand_pos(0, ball_radius), rand_pos(1, ball_radius), rand_pos(2, ball_radius), ball_radius, min_dis_APs)
			Balls.append(ball)	
		vf_i= volume_fraction(Balls)
		n+=1
		if n>100: 
			print('Impossible to generate this distribution')
			print('Please change the number of balls')
			break
	print('Actual volume fraction=', vf_i)
	return Balls, vf_i


# calculate the volume fraction if choose = 1 
def actual_vf_vf(vf_target, vf_delta):
	vf_i= 1 # set vf_i to be a value that can pass the first attempt 
	v_box= box_size[0]*box_size[1]*box_size[2] # volume of the box
	no_balls_need= int(vf_target*v_box/(4/3* np.pi* mu**3)) # calculate the number of balls needed 
	n=0 # the number of times to find the actual volume fraction 
	# 0.47 is the maximum volume fraction that can be archived 
	# so only generate the value less than 0.47
	# find the volume fraction in the range of target volume fraction plus and minus error 
	while vf_i > 0.47 or vf_i> vf_target+vf_delta or vf_i< vf_target-vf_delta:
		Balls=[]
		for i in range(no_balls_need):
			# generate a normal distribution and sort by size in the list 
			radius= sorted(np.random.normal(loc=mu, scale=sigma, size=no_balls), reverse=True)
			ball_radius= radius[i]
			ball= bc.Ball(rand_pos(0, ball_radius), rand_pos(1, ball_radius), rand_pos(2, ball_radius), ball_radius)
			Balls.append(ball)	
		vf_i= volume_fraction(Balls)
		n+=1
		# ends if wait too long to find the volume fraction 
		if n>100: 
			print('Impossible to generate this distribution')
			print('Please change the number of balls')
			break
	print('Actual volume fraction=', vf_i)
	print('')
	print('There are', no_balls_need,'balls in total')
	return Balls, vf_i, no_balls_need

if choose==0:
	Balls, actual_vf= actual_vf_no(no_balls)
else:
	Balls, actual_vf, no_balls= actual_vf_vf(vf_target, vf_delta)

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

def arrange(Balls, print_overlap, print_text=False):
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
		if print_text:
			print('The number of attempts:', n)
		# refers to the arrangement in ball_class.py
		sim= bc.Simulation(Balls)
		a = sim.run(num_steps=num_steps,box_size= box_size, delta=delta, print_overlap= print_overlap, animate= False)
		overlap= a[0]
		count= a[1]
		if overlap==999:
			if print_text:
				print('')
				print('Final configuration has been archived')
			break
		small=  previous_overlap- overlap
		previous_overlap= deepcopy(overlap)
		Balls= deepcopy(Balls)
		delta= overlap/count 
		if print_text:
			print('Delta', delta)
			print('')
		n+=1
	
	if small<= 0.001:
		reach=1
		print('')
		print('Final configuration CAN NOT be archived')	
	return Balls, reach

	

start = time.time()


for i in range(3):
	Balls_1, reach= arrange(Balls[0:int(no_balls/2)], 1)
	Balls= Balls_1+ Balls[int(no_balls/2):]
	Balls, reach= arrange(Balls, 0, print_text=True)
	if reach==0:
		break
	else:
		print('')
		print('TRY AGAIN')
		print('')

end= time.time()

print('')
print("The time of execution is :",  end-start, '(s)')

if reach==1:
	sys.exit(0)
	print('')
	print('FINAL CONFIGURATION CAN NOT BE ARCHIVED')


#%% save the final configuration in the Jason file 

# generate a point on the surface 

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
		'VF': actual_vf,
		'delmin_APs': min_dis_APs}

file_name= 'APs_differentSize_N'+str(no_balls)+'.json'

with open(file_name, 'w') as f:
	json.dump(data, f)






