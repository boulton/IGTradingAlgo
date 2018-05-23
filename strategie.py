# -*- coding: utf-8 -*-

import time
import rest
import Var
import datetime
import logging

logger = logging.getLogger()


class strategie():
	"""	regroupe les strategie d'achat/vente
																	temps = YYYY-MM-JJTHH:MM:SS(datetime)
	"""

	def __init__(self, BidAsk, temps, Price_0, backtest):

		self.pauseordre(temps, backtest)
		self.maEmaCross1(BidAsk, Price_0, backtest, temps)
		# self.balai(BidAsk, Price_0, temps, backtest)

		# print("strategie failed")

	def pauseordre(self, temps, backtest):
		""" Effectue une pause apres un ordre passé
		"""
		if Var.ordrePassee:
			if not backtest:
				logger.info("Ordre passé,\n 2Min de pause")
				time.sleep(Var.pauseordre)
				Var.ordrePassee = False
			else:
				if len(Var.FakeDeal["Time"]) == 0:
					# cas : cloture de toute position avant fin de délai
					logger.debug("Cas ou y a plus de deal")
					Var.ordrePassee = False
				else:
					tnow = temps
					DealT = Var.FakeDeal["Time"][len(Var.FakeDeal["Time"]) - 1]
					tdeal = datetime.datetime(int(DealT[:4]), int(DealT[5:7]), int(
						DealT[8:10]), int(DealT[11:13]), int(DealT[14:16]), int(DealT[17:19]))
					if (tnow - tdeal) >= datetime.timedelta(0, Var.pauseordre):
						#print(int((tnow-tdeal).seconds/60)," minutes depuis dernier trade")
						Var.ordrePassee = False
		pass

	def SimpleEmaCross0(self, BidAks, Price_0, backtest, tempo):
		# Brouillon, ne prend pas en compte des limite
		# "n'utilise" pas le balai
		bid, ask = BidAsk
		bid0, ask0 = Price_0  # Prix précedent

		taille = len(Var.ema["valeurs"]) - 1  # <- delai de 5 periode
		EMAdecalee = float(Var.ema["valeurs"][taille])

		# Crosses condition
		c11 = float(ask0) <= EMAdecalee
		c1 = float(ask) > EMAdecalee
		c21 = float(bid0) >= EMAdecalee
		c2 = float(bid) < EMAdecalee

		initparam = (tempo - Var.starttime).seconds > Var.AlgoInitialTime
		condition1 = initparam and c1 and c11
		condition2 = initparam and c2 and c21

		if condition1:
			sens = "BUY"
			Var.sens = sens
			Var.makeadeal = True
			# print(sens + " \n", str(ask) + "\n EMA: " + str(Var.ema["valeurs"][taille]))
			# self.event(backtest, sens, tempo, BidAsk, Price_0)
			Var.tempsaucross = tempo

		elif condition2:
			sens = "SELL"
			Var.sens = sens
			Var.makeadeal = True
			# print(sens + " \n", "prix: " + str(bid) + "\n EMA: " + str(Var.ema["valeurs"][taille]))
			# self.event(backtest, sens, tempo, BidAsk, Price_0)
			Var.tempsaucross = tempo
		else:
			# Garde fou:
			autre = self.stopandlimit(BidAsk, tempo, backtest, [])
			if backtest:
				rest.backtest().CloseFakeOrders(autre, BidAsk, tempo)
			else:
				# BUGGY
				rest.ig().CloseOrders(dealId=autre[0], orderType="MARKET")
			if Var.makeadeal and Var.minderniercross >= 2:
				Var.makeadeal = False
				self.event(backtest, Var.sens, tempo, BidAsk, Price_0)

		#-----------NEW-------
		Var.minderniercross = int((tempo - Var.tempsaucross).seconds / 60)
		# print(Var.minderniercross)

	def maEmaCross1(self, BidAsk, Price_0, backtest, tempo):
		""" Croisement entre MovingAvg 14 et EMA 500 
		"""
		bid, ask = BidAsk
		bid0, ask0 = Price_0  # Prix précedent
		MovingAvg = Var.ma["valeurs"][len(Var.ma["valeurs"]) - 1]
		MovingAvg0 = Var.ma["valeurs"][len(Var.ma["valeurs"]) - 2]

		taille = len(Var.ema["valeurs"]) - 1  # <- delai de 5 periode
		EMAdecalee = float(Var.ema["valeurs"][taille])

		# Crosses condition
		c11 = float(MovingAvg0) <= EMAdecalee
		c1 = float(MovingAvg) > EMAdecalee
		c21 = float(MovingAvg0) >= EMAdecalee
		c2 = float(MovingAvg) < EMAdecalee

		initparam = (tempo - Var.starttime).seconds > Var.AlgoInitialTime
		condition1 = initparam and c1 and c11
		condition2 = initparam and c2 and c21

		if condition1:
			sens = "BUY"
			Var.sens = sens
			Var.makeadeal = True
			# print(sens + " \n", str(ask) + "\n EMA: " + str(Var.ema["valeurs"][taille]))
			# self.event(backtest, sens, tempo, BidAsk, Price_0)
			Var.tempsaucross = tempo

		elif condition2:
			sens = "SELL"
			Var.sens = sens
			Var.makeadeal = True
			# print(sens + " \n", "prix: " + str(bid) + "\n EMA: " + str(Var.ema["valeurs"][taille]))
			# self.event(backtest, sens, tempo, BidAsk, Price_0)
			Var.tempsaucross = tempo
		else:
			# Garde fou:
			autre = self.stopandlimit(BidAsk, tempo, backtest, [])
			if backtest:
				rest.backtest().CloseFakeOrders(autre, BidAsk, tempo)
			else:
				# BUGGY
				rest.ig().CloseOrders(dealId=autre[0], orderType="MARKET")
			if Var.makeadeal and Var.minderniercross >= 0:
				Var.makeadeal = False
				self.event(backtest, Var.sens, tempo, BidAsk, Price_0)

		#-----------NEW-------
		Var.minderniercross = int((tempo - Var.tempsaucross).seconds / 60)
		# print(Var.minderniercross)

	def SimpleEmaCross(self, BidAsk, Price_0, backtest, tempo):
		""" Croisement PRIX et EMA a la periode j """
		bid, ask = BidAsk
		bid0, ask0 = Price_0  # Prix précedent a
		taille = len(Var.ema["valeurs"]) - 1  # <- delai de 5 periode
		EMAdecalee = Var.ema["valeurs"][taille]

		# Crosses condition
		c11 = float(ask0) <= EMAdecalee
		c1 = float(ask) > EMAdecalee and c11

		c21 = float(bid0) >= EMAdecalee
		c2 = float(bid) < EMAdecalee and c21

		sparam = (len(Var.FakeDeal["Id"])) < Var.PositionSimultanee

		initparam = (tempo - Var.starttime).seconds > Var.AlgoInitialTime
		cparam = sparam and initparam
		condition1 = cparam and c1
		condition2 = cparam and c2

		if condition1:
			sens = "BUY"
			print(sens + " \n", "prix: " + str(ask) +
				  "\n EMA: " + str(Var.ema["valeurs"][taille]))

			if backtest is False:
				rest.ig().CreateOrders(orderType="MARKET", direction=sens,
									   stopDistance=Var.Stoploss, limitDistance=self.limit, epic=Var.epic)
				# rest.ig() crée une nouvelle instance -> overload de connection
			else:
				rest.backtest().fakeOrders(BidAsk, sens, tempo)
			Var.ordrePassee = True

		elif condition2:
			sens = "SELL"
			print(sens + " \n", "prix: " + str(bid) +
				  "\n EMA: " + str(Var.ema["valeurs"][taille]))

			if backtest is False:
				rest.ig().CreateOrders(orderType="MARKET", direction=sens,
									   limitDistance=self.limit, stopDistance=self.stoploss, epic=Var.epic)
				# redondance rest.ig()
			else:
				rest.backtest().fakeOrders(BidAsk=BidAsk, sens=sens, temps=tempo)

			Var.ordrePassee = True

		else:
			pass

	def event(self, backtest, sens, tempo, BidAsk, Price_0):
		""" Handle maxposition de Var et 1 seul sens de trade
		"""
		maxposition = (len(Var.FakeDeal["Id"])) >= Var.PositionSimultanee
		vague1 = self.ordresInv(BidAsk, Price_0, tempo, sens, backtest)
		suppr = self.stopandlimit(BidAsk, tempo, backtest, vague1)
		if backtest:
			rest.backtest().CloseFakeOrders(suppr, BidAsk, tempo)
			if not maxposition:
				print(sens)
				rest.backtest().fakeOrders(BidAsk, sens, tempo)
		else:
			# BUGGY
			rest.ig().CloseOrders(dealId=suppr[0], orderType="MARKET")
			if not maxposition:
				rest.ig().CreateOrders(
					orderType="MARKET",
					direction=sens,
					stopDistance=Var.Stoploss,
					limitDistance=Var.Limit,
					epic=Var.epic)
				# rest.ig() crée une nouvelle instance -> overload de connection
		Var.ordrePassee = True

	def ordresInv(self, BidAsk, Price_0, temps, sens, backtest):
		"""	groupe les INDEX des Deal inversé au sens du trade"""
		suppresion = []
		if backtest:
			dico = Var.FakeDeal
		else:
			dico = Var.DealDone
		for x in range(0, (len(dico["Id"]))):
			dealsens = dico["sens"][x]
			if dealsens != sens:
				# print("profit@close: ",self.profit(dico, x, BidAsk))
				suppresion.append(x)

		return suppresion

	def balai(self, BidAsk, Price_0, temps, backtest):
		""" 23/03/2018
										non testé
										cloture les deal existant
		"""
		DealACloturer = []

		bid, ask = BidAsk
		bid0, ask0 = Price_0  # BidAsk précedent

		for x in range(0, (len(Var.FakeDeal["Id"]))):
			# x : index de l'id
			# condition de cross d'ema
			p = 0
			taille = len(Var.ema["valeurs"]) - 1
			# <- delai de 5 periode
			c11 = float(ask0) <= Var.ema["valeurs"][taille]
			c1 = float(ask) > Var.ema["valeurs"][taille] and c11

			c21 = float(bid0) >= Var.ema["valeurs"][taille]
			c2 = float(bid) < Var.ema["valeurs"][taille] and c21

			# Id existant
			prixentree = float(Var.FakeDeal["entry"][x])

			if Var.FakeDeal["sens"][x] == "SELL":
				prixactuel = float(ask)
				p = round((prixentree - prixactuel) * 10000, 2)
				# x100 caren pip
				# A modif selon l'instrument et son levier
			elif Var.FakeDeal["sens"][x] == "BUY":
				prixactuel = float(bid)
				p = round((prixactuel - prixentree) * 10000, 2)
				# x100 caren pip

			else:
				print("erreur: ", Var.FakeDeal["sens"][x])
				break

			# print("profit :", p)
			# cloture si stoploss/limit ou emacross
			if p > Var.Limit or p < Var.Stoploss:
				print("stoploss")
				DealACloturer.append(x)  # x = index dans dict
			elif c1 and Var.FakeDeal["sens"][x] == "SELL":
				DealACloturer.append(x)
				print("Croisement vendeur invalidé")
			elif c2 and Var.FakeDeal["sens"][x] == "BUY":
				DealACloturer.append(x)
				print("Croisement acheteur invalidé")

		if backtest is False:
			# NOT WORKING , DealId bad behavior
			rest.ig().CloseOrders(dealId=DealACloturer[0], orderType="MARKET")

		else:
			rest.backtest().CloseFakeOrders(DealACloturer, BidAsk, temps)

	def ClientSentiment(self, BidAsk, sens, temps, epic):
		"""Strategie autour des Positions des clients IG """

		position = rest.ig().IgClientPositions(epic)
		Bullish = position["Bull"]
		Bearish = position["Bear"]

		c1 = Bullish > 89
		if c1:
			Id = rest.fakeOrders(BidAsk, "sell", temps)
			return Id
		else:
			pass
		# self.archiveSentiment(position, epic)

	def profit(self, dico, i, BidAsk):
		profit = 0
		bid, ask = BidAsk
		sens = dico["sens"][i]
		prixentree = float(dico["entry"][i])
		# print("profit ;",dico["Id"][i])

		if sens == "SELL":
			prixactuel = float(ask)
			profit = round((prixentree - prixactuel) * 100, 2)
		else:
			prixactuel = float(bid)
			profit = round((prixactuel - prixentree) * 100, 2)
			# profit x100 caren pip
			# A modif selon l'instrument et son levier
		# print(profit)
		return profit

	def stopandlimit(self, BidAsk, temps, backtest, suppresion):
		if backtest:
			dico = Var.FakeDeal
		else:
			dico = Var.DealDone

		for x in range(0, len(dico["Id"])):
			# DealT = dico["Time"][x]
			# tdeal = datetime.datetime(int(DealT[:4]), int(DealT[5:7]), int(DealT[8:10]), int(DealT[11:13]), int(DealT[14:16]), int(DealT[17:19]))
			# nighclose = datetime.datetime(int(DealT[:4]), int(DealT[5:7]), int(DealT[8:10]), 22, 50, 0)
			p = self.profit(dico, x, BidAsk)

			if p < Var.Stoploss:
				logger.info("stoploss")
				suppresion.append(x)  # x = index dans dict
			elif p > Var.Limit:
				logger.info("Limit")
				suppresion.append(x)
			# elif temps > nighclose:
			# suppresion.append(x)
			else:
				pass
		return suppresion

	def CloseAll(self, BidAsk, temps, backtest):
		"""	Ferme tout les ordres 
		"""
		toute = []
		for x in range(0, len(dico["entry"])):
			toute.append(x)

		if backtest:
			rest.backtest().CloseFakeOrders(toute, BidAsk, temps)
		else:
			rest.ig().CloseOrders(dealId=toute[0], orderType="MARKET")
			