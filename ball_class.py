#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 12:13:07 2022

@author: jielinglee
"""

'''
The main algorithm works as 
(1) initilise the postion and the radius 
(2) find the overlapping region and ball number 
(3) randomly move any ball in the system 
move can be move randomly in any direction, swap two balls or shrink a ball 
(4) check if the overlapping function decreases. If decreases, then accept; otherwise, reject.
(5) continue until the overlapping function reaches the mininal value 

'''


import numpy as np
from numpy.random import normal
import random
import copy 
from copy import deepcopy 




class Ball:
	def __init__(self, x, y, z, radius, min_dis_APs):
		self.centre = np.array([x, y, z]) # the centre of the ball 
		self.radius = radius # the radius of the ball 
		# treat the spacing between two particles as an extension of the radius
		# so the packing problem with spacing between particles can be simplified as a normal packing problem 
		self.equ_radius= radius+ min_dis_APs/2 # equivalent radius
		
		
	# define the surface of the ball  
	# this is only for plotting the balls in python
	def surface(self):
		u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
		x = self.radius* np.cos(u)*np.sin(v) + self.centre[0]
		y = self.radius* np.sin(u)*np.sin(v) + self.centre[1]
		z = self.radius* np.cos(v) + self.centre[2]
		return x, y, z
	
	
	# calculate how far two balls are from the centres
	def ball_dis(self, other):
		dis= np.linalg.norm(self.centre-other.centre)
		return dis
	
	# calculate how much two balls overlap 
	# if two balls are overlapping, the function returns how much the balls overlap 
	# otherwise, the function returns 0
	def overlap(self, other):
		diff= self.equ_radius+ other.equ_radius- self.ball_dis(other)
		if diff <= 0.01:
			overlap= 0
		else:
			overlap= diff
		return overlap
		
	# move the ball if two balls overlap 
	def move(self, delta):
		# move along a random direction 
		r_move= np.random.uniform(-delta, delta, size=3)
		self.centre= self.centre + r_move

	# reject if the ball has been moved out of the boundary 
	def close_to_edge(self, box_size):
		# see if each dimension of the ball exceeds the size of the box 
		# If it exceeds, then return 1. If it passes, then return 0
		for t in range(3):
			x= self.centre[t]
			x_plane= box_size[t]/2
			if x>=0:
				dis= abs(x_plane-x)
			else:
				dis= abs(x+x_plane)
			if dis < self.equ_radius:
				return 1 
				break 
		return 0
				
	
class Simulation():
	def __init__(self, balls):
		self.balls= balls # the ball list 
		# a big list that saves the ball number and how much the balls overlap 
		# for example, a list [2, 5, 2.53] means ball number 2 and 5 are overlapping with the distance of 2.53
		# every list will be saved in self.overlap_sequence (a big list)
		self.overlap_sequence=[] 
		# overlap function: the sum of overlapping regions
		self.overlap_function=0
		# to see how many moves are accepted in a cycle 
		self.accept=0
		
		for i in range(len(self.balls)):
			for j in range(i+1,len(self.balls),1):
				dis= self.balls[i].ball_dis(self.balls[j])
				# if two balls are not overlapped, then we say the overlapping region is zero
				if dis >= self.balls[i].equ_radius+self.balls[j].equ_radius:
					overlap=0 
				# otherwise, calculate the overlapping region 
				else:
					overlap= self.balls[i].overlap(self.balls[j])
					self.overlap_function += overlap
				self.overlap_sequence.append([overlap,i,j]) # record all overlap and pairs
		self.initial_overlap= deepcopy(self.overlap_function)
		
	# calculate the overlap function 
	def overlap_fun(self):
		overlap_fun=0
		for index in range(len(self.overlap_sequence)):
			overlap= self.overlap_sequence[index][0]
			overlap_fun += overlap
		return overlap_fun
	
	# if a ball is selected, we only check the balls related to this ball
	'''
	For example, if ball number 5 is selected to perform a move, we only update 
	the overlap distance related to ball number 5. We don't care about the overlap
	between other ball pairs (e.g. overlap between ball number 2 and 3), so
	find_index and find_related_index are functions that finds related ball index 
	'''
	def find_index(self, i, j):
		index_array= np.arange(1, len(self.balls), 1)
		index_array= index_array[::-1]
		if i == 0:
			index= j-1
		else:
			index= 0
			for t in range(i):
				index+= index_array[t]
			index= index+j-1
		return index 
	
	
	def find_related_index(self, i):
		index= np.array([])
		for k in range(len(self.overlap_sequence)):
			ball1= self.overlap_sequence[k][1]
			ball2= self.overlap_sequence[k][2]
			if ball1==i or ball2==i:
				index= np.append(index, k)
		return index
	
	# update overlap distance between each ball pair after the selected ball is moved 
	def update_overlap(self, ball_index):
		index_array= self.find_related_index(ball_index)
		for index in index_array:
			overlap_index= self.overlap_sequence[int(index)]
			ball1= self.balls[overlap_index[1]]
			ball2= self.balls[overlap_index[2]]
			overlap= ball1.overlap(ball2)
			self.overlap_sequence[int(index)][0]= overlap
			
	# make a copy 
	def initial_info(self, ball_index):
		centre= deepcopy(self.balls[ball_index].centre)
		radius= deepcopy(self.balls[ball_index].radius)
		overlap_sequence= deepcopy(self.overlap_sequence)
		overlap_fun= deepcopy(self.overlap_function.copy())
		
		return centre, radius, overlap_sequence, overlap_fun
		
	# to decide if the move is accepted or rejected 
	def advance(self, box_size, delta):
		# randomly select a ball
		selected_ball_index= random.randint(0,len(self.balls)-1)
		initial_centre, initial_radius, initial_overlap_sequence, initial_overlap_fun= self.initial_info(selected_ball_index)
		# perform a move 
		self.balls[selected_ball_index].move(delta) 
		# update the overlap sequence after the move is performed 
		self.update_overlap(selected_ball_index)

				
		# calculate the overlap function after the move is performed 
		final_overlap_fun= self.overlap_fun()
		
		# see if the ball moves out of the boundary 
		edge= self.balls[selected_ball_index].close_to_edge(box_size)
		# 
		a= np.random.randint(0,9)
		
		# if the overlap function increases or the ball moves out of the boundary, the move is rejected  
		if final_overlap_fun > initial_overlap_fun or edge==1:
			self.balls[selected_ball_index].centre= initial_centre
			self.overlap_sequence= initial_overlap_sequence
			self.overlap_function= initial_overlap_fun
		
		# if the overlap function remains the same, the move is accepted by 50% of the chance 
		elif final_overlap_fun == initial_overlap_fun and edge!=1 and a>=5:
			self.overlap_function= final_overlap_fun
			self.accept+=1
		
		# if the overlap function decreases, the move is accepted 
		else:
			# update every other overlap region 
			self.overlap_function= final_overlap_fun
			self.accept+=1
	
	# check if two balls overlap 
	def check(self, print_overlap):
		count= 0
		for i in range(len(self.overlap_sequence)):
			if self.overlap_sequence[i][0] != 0:
				if print_overlap==0:
					print('ball number', self.overlap_sequence[i][1],'and', self.overlap_sequence[i][2], 'are overlapping with', '%.4f'% self.overlap_sequence[i][0])
				count+=1
		return count
	# the second method to check if two balls overlap
	def check2(self):
		for i in range(len(self.balls)):
			for j in range(i+1, len(self.balls),1):
				diff_centre= np.linalg.norm(self.balls[i].centre- self.balls[j].centre)
				two_radius= self.balls[i].equ_radius+ self.balls[j].equ_radius
				if diff_centre - two_radius < 0:
					print('ball number', i, 'and', j, 'are overlapping')
					print('overlap distance=', two_radius-diff_centre)

	
	def run(self, num_steps, box_size, delta, print_overlap, animate= False):
		# uncomment if it is essential to see the plot in python 
		#if animate:
			#fig = plt.figure() 
			#ax = plt.axes(projection='3d')
			#ax.set_xlim(-box_size[0]/2, box_size[0]/2)
			#ax.set_ylim(-box_size[1]/2, box_size[1]/2)
			#ax.set_zlim(-box_size[2]/2, box_size[2]/2)
			#ax.set_box_aspect((30,30,30))
			

		for i in range(num_steps):
			if self.overlap_function == 0:
				a= 999
				break
			
			else:
				self.advance(box_size, delta)
				a= self.overlap_function
				# uncomment if it is essential to see the plot in python 
				#if animate:
					#for ball in self.balls:
						#x, y, z= ball.surface()
						#ax.plot_wireframe(x, y, z, color="r")
					#plt.show()
					#plt.pause(0.01)
					#if i < num_steps:
						#ax.collections.clear()
		
		count= self.check(print_overlap)
		return (a, count)

					
