#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  8 12:13:07 2022

@author: jielinglee
"""

'''
This is the section for me to practise writing the same function using the OOP concept,
otherwise I will forget completely 
'''

import pylab as pl
import numpy as np
import matplotlib.pyplot as plt
import random

'''
11/8/2022
I was finding the reason why some ball groups can never finish loading 
I found that I didn't accept and reject the move and also my constrain is too strict.
so the overlap function might increase in some cases 
the loop never ends
'''


min_dis_APs= 0.5

class Ball:
	def __init__(self, x, y, z, radius):
		self.centre = np.array([x, y, z])
		self.radius = radius
		self.equ_radius= radius+ min_dis_APs/2
		
# the surface of the ball 
	def surface(self):
		u= np.linspace(0, 2 * np.pi, 100)
		v= np.linspace(0, np.pi, 100)
		x = self.radius * np.outer(np.cos(u), np.sin(v))
		y = self.radius * np.outer(np.sin(u), np.sin(v))
		z = self.radius * np.outer(np.ones(np.size(u)), np.cos(v))
		return x+self.centre[0], y+self.centre[1], z+self.centre[2]

# calculate how far two balls are 
	def ball_dis(self, other):
		dis= np.linalg.norm(self.centre-other.centre)
		return dis
	
	def overlap(self, other):
		diff= self.equ_radius+ other.equ_radius-self.ball_dis(other)
		if diff <= 0:
			overlap= 0
		else:
			overlap= diff
		#print('overlap', overlap)
		return overlap
	
# move the ball if two balls are overlapped
	def move(self, other):
		# r is the position vector pointing from centre of this ball to the ball overlapped 
		r = other.centre- self.centre 
		r_hat= r/np.linalg.norm(r)
		self.centre= self.centre + (self.equ_radius+ other.equ_radius-np.linalg.norm(r))*(-r_hat)



class Simulation():
	def __init__(self, balls):
		self.balls= balls
		self.overlap_sequence=[]

		for i in range(len(self.balls)):
			for j in range(i+1,len(self.balls),1):
				dis= self.balls[i].ball_dis(self.balls[j])
				# if two balls are not overlapped, then we say the overlapping region is zero
				if dis >= self.balls[i].equ_radius+self.balls[j].equ_radius:
					overlap=0 
				# otherwise, calculate the overlapping region 
				else:
					overlap= self.balls[i].overlap(self.balls[j])
				self.overlap_sequence.append([overlap,i,j]) # record all overlap and pairs
				
		self.overlap_sequence = sorted(self.overlap_sequence, key = lambda t: t[0], reverse= True) # sort by how much the region overlaps 
# 		print(self.overlap_sequence)
# 		self.change_next() # refresh next overlap parameters
# 	def change_next(self):
# 		self.overlapping = self.overlap_sequence[0][0]
# 		self.i = self.overlap_sequence[0][1]
# 		self.j = self.overlap_sequence[0][2]

	def advance(self):
# 		if self.overlap_sequence[0][0] < 0:
# 		self.overlap_sequence[0][0] = self.balls[self.i].overlap[self.j]
		i = self.overlap_sequence[0][1]
		j = self.overlap_sequence[0][2]
		initial_ball1= self.balls[i].centre
		initial_ball2= self.balls[j].centre
		initial_overlap= self.overlap_sequence[0][0]
		self.balls[i].move(self.balls[j])
		final_overlap= self.balls[i].overlap(self.balls[j])
		
		if final_overlap < initial_overlap:
			self.overlap_sequence[0][0]= final_overlap
		#update every other overlap region 
			for index in range(len(self.overlap_sequence)):
				ball1= self.overlap_sequence[index][1]
				ball2= self.overlap_sequence[index][2]
				self.overlap_sequence[index][0]= self.balls[ball1].overlap(self.balls[ball2])
			self.overlap_sequence = sorted(self.overlap_sequence, key = lambda t: t[0], reverse= True) 
			#print(self.overlap_sequence)
			
		else:
			self.balls[i].centre= initial_ball1
			self.balls[j].centre= initial_ball2	
			
	def overlap_function(self):
		overlap_fun=0
		for index in range(len(self.overlap_sequence)):
			overlap= self.overlap_sequence[index][0]
			overlap_fun += overlap
		#print('Current overlap function=', overlap_fun)
		return overlap_fun

	
	# check if two of the balls are overlapped as sometimes we can't see the overlapping region properly in the graph 
	def check(self):
		for i in range(len(self.balls)):
			for j in range(i+1, len(self.balls),1):
				diff_centre= np.linalg.norm(Balls[i].centre- Balls[j].centre)
				two_radius= Balls[i].equ_radius+ Balls[j].equ_radius
				if diff_centre - two_radius < 0:
					print('ball number', i, 'and', j, 'are overlapped')
					print('overlapping distance=', two_radius-diff_centre)
					break
		
				
	def run(self, num_step, animate= False):
		'''
		if animate:
			fig= plt.figure()
			ax = fig.add_subplot(projection='3d')
			ax.set_box_aspect([1,1,1])
		'''
		for i in range(num_step):
			if self.overlap_function() != 0:
				self.advance()
			else:
				break
		'''
			if animate:
				for ball in self.balls:
					x, y, z = ball.surface()[0], ball.surface()[1], ball.surface()[2]
					ax.scatter(ball.centre[0], ball.centre[1], ball.centre[2], color='black', s=1)
					ax.plot_surface(x, y, z,  rstride=4, cstride=4, color='b', linewidth=1, alpha=0.5)
				'''
		self.check()
			
	
	
Balls= []
box_size= np.array([30, 40, 30])
no_balls= 25
num_step= 1000

# r= np.ones(no_balls)*ball_radius
# centre= np.zeros([no_balls, 3])


'''

# Try three balls. It does work 
ball_a= Ball(x=1, y=0, z=0, radius=1)
ball_b= Ball(x=0, y=0, z=0, radius=1.5)
ball_c= Ball(x=0, y=1, z=0, radius=2)

Balls= [ball_a, ball_b, ball_c]



print('The centre of ball_a:', ball_a.centre)
print('The centre of ball_b:', ball_b.centre)
print('The centre of ball_c:', ball_c.centre)
'''


# Now try mulitple balls 

for i in range(no_balls):
	ball_radius= np.random.normal(loc=3, scale= 2.5/3)
	ball= Ball(random.random()*box_size[0], random.random()*box_size[1], random.random()*box_size[2], ball_radius)
	'''
	cen= np.loadtxt('cen.txt')
	rad= np.loadtxt('rad.txt')
	x= cen[3*i]
	y= cen[3*i+1]
	z= cen[3*i+2]
	radius= rad[i]
	ball= Ball(x, y, z, radius)
	'''
	Balls.append(ball)
# 	
# 	# ball= Balls[i]
# 	# sph= ball.surface()
# 	# x, y, z = sph[0], sph[1], sph[2]
# 	# ax.scatter(ball.centre[0], ball.centre[1], ball.centre[2], color='black', s=1)
# 	# ax.plot_surface(x, y, z,  rstride=4, cstride=4, color='b', linewidth=1, alpha=0.5)



sim= Simulation(Balls)
sim.run(1000)

#%%
'''
cen=np.array([])
rad= np.array([])

for i in range(len(Balls)):
	centre= Balls[i].centre
	radius= Balls[i].radius
	cen= np.append(cen,centre)
	rad= np.append(rad, radius)


np.savetxt('cen.txt', cen, delimiter=',')
np.savetxt('rad.txt', cen, delimiter=',')

'''


