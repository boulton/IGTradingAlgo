# -*- coding: utf-8 -*-

import time
import rest
import pprint 
import Var
from decimal import *
from datetime import datetime
from memory_profiler import profile


class strat(object):

	firstrun = True
	PositionSimultanee = 4

	
	def closingcondition(self,i,Id):
		""" i : prix fixé a ce moment dans la fonction
			Id : Id du Deal"""
		t = Var.price["Time"][i]
		
		for x in range(len(Var.FakeDeal["Id"])-1):
			#x : index de l'id
			print(len(Var.FakeDeal["Id"])-1)
			j = str
			if Var.FakeDeal["sens"][x+1] == "sell" :
				j = "Ask"
			elif Var.FakeDeal["sens"][x+1] == "buy":
				j = "Bid"  
			else:
				print("x: ",x)
				print(Var.FakeDeal["sens"][x])

			d = float(Var.price[j][i]) - float(Var.FakeDeal["entry"][x+1])
			print("prfit : ",d)
			p= round(d,5)
			limit =  10
			print("diff: ",p)
			if p > limit :
				rest.CloseFakeOrders(x+1)
			else :
				pass 

	def scalping(self,price):
		trigger = 1.2e-3 # ML arbitraire 
		# volatile = 15 
		DeltaBid = Var.delta["Ask"]
		#print(DeltaBid)
		conditions = float(DeltaBid[price-1]) > trigger and (len(Var.FakeDeal["Id"])-1) < self.PositionSimultanee
		conditions2 = float(DeltaBid[price-1]) < trigger and (len(Var.FakeDeal["Id"])-1) < self.PositionSimultanee
		if conditions :
			print("DEAL !")
			sens = "buy"
			Id = rest.fakeOrders(price, sens)
			#rest.MarketOrders()
			return Id
		elif conditions2 :
			pass

	def DateConverter(self,i):
		# strind date to datetime
		DateComplete = Var.price["Date"]+"/"+Var.price["Time"][i] 

		d = datetime.strptime(DateComplete, '%m/%d/%y/%H:%M:%S')
		return d

	def delta(self,i):
		if self.firstrun:
			self.firstrun = False
		else:
			# i : periode 
			#print("Bid: ",Var.price["Bid"][i])
			Var.delta["Bid"].append(float(Var.price["Bid"][i]) - float(Var.price["Bid"][i-1]))
			Var.delta["Ask"].append(float(Var.price["Ask"][i]) - float(Var.price["Ask"][i-1]))
			Var.delta["Time"].append(str(self.DateConverter(i) - self.DateConverter(i-1)))
			Var.daties.append(datetime.strptime(Var.price["Time"][i],'%H:%M:%S'))
			#print(Var.delta["Bid"][i-1])


	def truncate(self, f, n):
		'''Truncates/pads a float f to n decimal places without rounding'''
		s = '{}'.format(f)
		if 'e' in s or 'E' in s:
			return '{0:.{1}f}'.format(f, n)
			i, p, d = s.partition('.')
			return '.'.join([i, (d+'0'*n)[:n]])

