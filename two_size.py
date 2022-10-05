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
import random 
import sys
import json

# set the parameters

box_size= np.array([30, 40, 30])# the size of cathode 

no_balls= 40 # the radius of active particles

ball_radius_1= 5 # the radius of the larger size of the balls

ball_radius_2= 3 # the radius of the smaller size of the balls 

# ratio of larger size of the balls and smaller size of the balls
# For example, (0.75, 0.25) means 75% of balls with radius of 5 and 25% of balls with radius of 3
ball_ratio=(0.75, 0.25) 

min_dis_APs= 0.15 # minimum distance between two active particles 

coating = min_dis_APs 

# calculate the equivalent radius 

equ_radius_1= ball_radius_1+ min_dis_APs/2

equ_radius_2= ball_radius_2+ min_dis_APs/2

# calculate the number of balls for each radius 

no_balls_1= int(no_balls*ball_ratio[0])

no_balls_2= int(no_balls*ball_ratio[1])

# calculate the volume fraction 
def volume_fraction(Balls):
	ball_volume= 0
	for ball in Balls:
		v= (4* np.pi* ball.radius**3)/3
		ball_volume+= v
	vf= ball_volume/ (box_size[0]*box_size[1]*box_size[2])
	return vf



# check if the balls exceed the boundary 
def inside_box(pos, equ_radius):
	for j in range(3):
		pos_i= pos[j]
		if pos_i >= 0:
			diff= box_size[j]/2 - pos[j] 
			if diff < equ_radius:
				return 1 # return 1 if the ball exceeds the boundary 
				break
		else:
			diff= box_size[j]/2+ pos[j]
			if diff < equ_radius:
				return 1 
				break
			
# set the position of balls randomly and save the balls in a list 
def bound(i):
	return box_size[i]/2- equ_radius_1

def rand_pos(i):
	return random.uniform(-1, 1)* bound(i)

def ball_list(no_ball_1, no_ball_2):
	Balls=[]
	for i in range(no_balls):
		if i < no_ball_1:
			ball_radius= ball_radius_1
		else:
			ball_radius= ball_radius_2
		ball= bc.Ball(rand_pos(0), rand_pos(1), rand_pos(2), ball_radius, min_dis_APs)
		Balls.append(ball)
	return Balls

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

def arrange(Balls, print_overlap, print_text= False):
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
		a = sim.run(num_steps=num_steps, delta=delta, box_size= box_size, print_overlap= print_overlap, animate= False)
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
	return Balls, reach


start = time.time()

Balls= ball_list(no_balls_1, no_balls_2)
vf= volume_fraction(Balls)
print('Volume fraction=', vf)
print('')

for j in range(3):
	# arrange the balls with larger radius first 
	Balls_1, reach= arrange(Balls[0:no_balls_1], 1)
	# add the balls with smaller radius and arrange again 
	# arranging larger radius before smaller radius might get a higher chance of reaching the final configuration
	Balls= Balls_1+ Balls[no_balls_1:]
	Balls, reach= arrange(Balls, 0, print_text=True)
	if reach ==0:
		break
	else:
		print('')
		print('TRY AGAIN')
		print('')


end= time.time()

print('')
print("The time of execution is :",  end-start, '(s)')

if reach==1:
	print('')
	print('FINAL CONFIGURATION CAN NOT BE ARCHIVED')
	sys.exit(0)



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
	# APs data structure: radius + the centre of the ball + a point on the surface + radius with coating+ a point on the coating 
	APs= list(np.array([float(ball.radius)]))+list(ball.centre)+list(xyzr)+list(np.array([float(ball.radius+coating)]))+list(xyzr_c)
	APs_data.append(APs)



# save data to a json file 

data = {'APs_data': tuple(APs_data),
		'Cathode_data': tuple(box_size.astype(np.float64)),
		'Same_size':1,
		'VF': vf,
		'delmin_APs': min_dis_APs}

file_name= 'APs_twoSize_N'+str(no_balls)+'.json'

with open(file_name, 'w') as f:
	json.dump(data, f)







