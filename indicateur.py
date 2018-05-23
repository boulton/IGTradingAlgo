# -*- coding: utf-8 -*-

import Var
import datetime

class indicateur(object):
	""" docstring for indicateur:
			temps = datetime
			Midpoint= Milieu Bid/ask
			"""

	def __init__(self, temps, Midpoint):

		self.MinUpgrade = False
		self.HeureUpgrade = False

		try:
			self.chronoMinute(temps)
			# self.delta()
			self.emaMin(Midpoint, 71)
			
		except():
			raise ValueError

	def HeikinAshi(self):
		pass

	def HeikinAshiCount(self):
		pass

	def emaHeure(self, Midpoint, periode):
		echelle = "heures"
		decalage = 5
		
		if Var.ema["echelle"] != echelle:
			# Premiere valeur de prix == ema(1)
			# print("debug 1ier tour")
			Var.ema["valeurs"][0] = round(float(Midpoint), 6)
			Var.ema["echelle"] = echelle
		else:
			# print("Minutes:",len(Var.ema["valeurs"]))
			y = float
			# x moyenne bid/ask
			x = float(Midpoint)
			t = float(Var.ema["valeurs"][len(Var.ema["valeurs"]) - 1])
			# n = nb de periode
			n = int(periode)
			# poid alpha
			a = 2 / (n + 1)
			y = round((a * x + (1 - a) * t), 6)

			if self.HeureUpgrade:
				Var.ema["periode"] = periode
				Var.ema["valeurs"].append(y)
				lastiter = len(Var.ema["valeurs"]) - 1
				if lastiter >= decalage:
					EmaDecalee = Var.ema["valeurs"][lastiter - decalage]
				# print("Ask: ",Var.price["Ask"][self.i],"\n ","Ema: ", Var.ema["valeurs"][len(Var.ema["valeurs"])-1])
				self.HeureUpgrade = False
	
		Var.emaBacktest.append(Var.ema["valeurs"][len(Var.ema["valeurs"]) - 1])  # envoyé au csv 
			
	def emaMin(self, Midpoint, periode): # pas a jour
		echelle = "minutes"
		decalage = 5
		
		if Var.ema["echelle"] != echelle:
			# Premiere valeur de prix == ema(1)
			# print("debug 1ier tour")
			Var.ema["valeurs"][0] = round(float(Midpoint), 6)
			Var.ema["echelle"] = echelle
		else:
			# print("Minutes:",len(Var.ema["valeurs"]))
			y = float
			# x moyenne bid/ask
			x = float(Midpoint)
			t = float(Var.ema["valeurs"][len(Var.ema["valeurs"]) - 1])
			# n = nb de periode
			n = int(periode)
			# poid alpha
			a = 2 / (n + 1)
			y = round((a * x + (1 - a) * t), 6)

			if self.MinUpgrade:
				Var.ema["periode"] = periode
				Var.ema["valeurs"].append(y)
				lastiter = len(Var.ema["valeurs"]) - 1
				if lastiter >= decalage:
					EmaDecalee = Var.ema["valeurs"][lastiter - decalage]
				# print("Midpoint",Midpoint,"\n ","Ema:", Var.ema["valeurs"][lastiter])
				self.MinUpgrade = False

		Var.emaBacktest.append(Var.ema["valeurs"][len(Var.ema["valeurs"]) - 1])  # envoyé au csv 

	def chronoMinute(self, temps):
		"""	Horloge:
			chrono déclenche MinUpgrade et HeureUpgrade
		"""
		# Var.lastDatetime est créer au demarrage
		#delta = temps - Var.lastDatetime

		if temps.minute != Var.lastDatetime.minute:
			Var.Minute = Var.Minute + 1
			Var.lastMinute = Var.lastDatetime.minute
			# print("min:",Var.Minute)
			# print("lastMinute:",Var.lastMinute) 
			self.MinUpgrade = True  # Trigger Minute data Upgrade

			if temps.hour != Var.lastDatetime.hour:
				Var.lastHeure = Var.lastDatetime.hour
				print("Heure:", temps.hour)
				self.HeureUpgrade = True  # Trigger Hourly data upgrade
		else:
			# print(delta)
			pass
			
		Var.lastDatetime = temps

