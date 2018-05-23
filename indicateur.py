# -*- coding: utf-8 -*-

import os.path
import Var
import datetime
import rest
import json
import logging

logger = logging.getLogger()


class indicateur(object):
	""" docstring for indicateur:
					temps = datetime
					Midpoint= Milieu Bid/ask
					"""

	def __init__(self, temps, Midpoint):

		self.MinUpgrade = False
		self.HeureUpgrade = False
		EmaPeriode = 500
		echelle = "heures"  # ou "minutes"

		try:
			self.chronoMinute(temps)
			self.movingaverage("minutes", temps, Midpoint, 9)
			self.ema("minutes", temps, Midpoint, EmaPeriode)
		except():
			raise ValueError

	def preloadma(self, echelle, temps, periode):
		# Timezone Effect a proprement corrigé
		temps = temps + datetime.timedelta(0, (2 * 60 * 60))
		daybefore = temps - \
			datetime.timedelta(1, 0) + datetime.timedelta(0, (2 * 60 * 60))
		if temps.month < 10:
			mois = "0" + str(temps.month)
			mois0 = "0" + str(daybefore.month)
		else:
			mois = str(temps.month)
			mois0 = str(daybefore.month)

		pathname = Var.marketId + str(daybefore.year) + "-" + mois0 + "-" + str(
			daybefore.day) + "_" + str(temps.year) + "-" + mois + "-" + str(temps.day) + ".json"

		if not os.path.isfile("archive/json/" + pathname):
			dateF = str(daybefore).replace(" ", "T")
			dateT = str(temps).replace(" ", "T")
			sample = rest.ig().retrieve(Var.epic, dateF, dateT)
		else:
			with open("archive/json/" + pathname, 'r', encoding="utf-8") as outfile:
				sample = json.load(outfile)

		iterstart = int(sample["metadata"]["size"]) - (periode)
		logger.info("preload start index :{}".format(iterstart))

		if iterstart < 1:
			# check qu'il y a assez de donnée
			logger.error("erreur pas assez de donnée")
		else:
			clef = "ma" + echelle + str(periode)

			if clef in sample["prices"][iterstart].keys():
				for x in range(iterstart, len(sample["prices"])):
					Var.ma["valeurs"].append(
						round(sample["prices"][x][clef], 6))
			else:
				Var.ma["valeurs"].append(
					sample["prices"][iterstart - 1]["closePrice"]["bid"])

				for x in range(iterstart, len(sample["prices"])):
					# moving avg calculus
					rf = sample["prices"][x]
					Mid = round((rf["closePrice"]["bid"] +
								 rf["closePrice"]["ask"]) / 2, 6)
					Var.prixpourma.append(Mid)
				# logger.debug(str(Var.prixpourma))
				a = float()
				for x in range(0, len(Var.prixpourma)):
					a += float(Var.prixpourma[x])
				y = a / periode
				Var.ma["valeurs"].append(y)
				logger.debug("MA: {}".format(Var.ma["valeurs"][0]))
				with open("archive/json/" + pathname, 'w', encoding="utf-8") as outfile:
					json.dump(sample, outfile, ensure_ascii=False)

	def preloadema(self, echelle, temps, EmaPeriode):

		# Timezone Effect a proprement corrigé
		temps = temps + datetime.timedelta(0, (2 * 60 * 60))
		daybefore = temps - \
			datetime.timedelta(1, 0) + datetime.timedelta(0, (2 * 60 * 60))
		if temps.month < 10:
			mois = "0" + str(temps.month)
			mois0 = "0" + str(daybefore.month)
		else:
			mois = str(temps.month)
			mois0 = str(daybefore.month)

		pathname = Var.marketId + str(daybefore.year) + "-" + mois0 + "-" + str(
			daybefore.day) + "_" + str(temps.year) + "-" + mois + "-" + str(temps.day) + ".json"

		if not os.path.isfile("archive/json/" + pathname):
			dateF = str(daybefore).replace(" ", "T")
			dateT = str(temps).replace(" ", "T")
			sample = rest.ig().retrieve(Var.epic, dateF, dateT)
		else:
			with open("archive/json/" + pathname, 'r', encoding="utf-8") as outfile:
				sample = json.load(outfile)

		iterstart = int(sample["metadata"]["size"]) - (EmaPeriode)
		logger.info("preload start index :{}".format(iterstart))

		if iterstart < 2:
			# check qu'il y a assez de donnée
			logger.error("erreur pas assez de donnée")
		else:
			clef = "Ema" + echelle + str(EmaPeriode)

			if clef in sample["prices"][iterstart].keys():
				for x in range(iterstart, len(sample["prices"])):
					Var.ema["valeurs"].append(
						round(sample["prices"][x][clef], 6))
			else:
				Var.ema["valeurs"].append(
					sample["prices"][iterstart - 2]["closePrice"]["bid"])

				for x in range(iterstart - 1, len(sample["prices"])):

					rf = sample["prices"][x]
					Mid = (
						rf["closePrice"]["bid"] +
						rf["closePrice"]["ask"]) / 2
					t = Var.ema["valeurs"][len(Var.ema["valeurs"]) - 1]
					a = 2 / (int(EmaPeriode) + 1)
					y = round((a * Mid + (1 - a) * t), 6)
					Var.ema["valeurs"].append(y)
					sample["prices"][x][clef] = y

				with open("archive/json/" + pathname, 'w', encoding="utf-8") as outfile:
					json.dump(sample, outfile, ensure_ascii=False)

	def HeikinAshi(self):
		pass

	def HeikinAshiCount(self):
		pass

	def movingaverage(self, echelle, temps, Midpoint, periode):
		if Var.ma["echelle"] != echelle:
			Var.ma["echelle"] = echelle
			try:
				self.preloadma(echelle, temps, periode)
			except Exception as e:
				logger.error("erreur pas de preload " + str(e))
				Var.ma["valeurs"].append(Midpoint)
				for x in range(0, periode):
					Var.prixpourma.append(Midpoint)
			Var.mabacktest.append(
				Var.ma["valeurs"][len(Var.ma["valeurs"]) - 1])
		else:
			a = float()
			z = Var.prixpourma
			for x in range(0, periode):
				a += z[x]
			y = round(a / periode, 6)
			# logger.debug("z num: {} ,ma: {}".format(len(z),y))
			if self.HeureUpgrade and echelle == "heures":
				Var.ma["valeurs"].append(y)
				Var.prixpourma.append(Midpoint)
				Var.prixpourma.pop(0)

			elif self.MinUpgrade and echelle == "minutes":
				Var.ma["valeurs"].append(y)
				Var.prixpourma.append(Midpoint)
				Var.prixpourma.pop(0)
				Var.mabacktest.append(
					Var.ma["valeurs"][len(Var.ma["valeurs"]) - 1])

			elif self.MinUpgrade and echelle != "minutes":
				Var.mabacktest.append(
					Var.ma["valeurs"][len(Var.ma["valeurs"]) - 1])

	def ema(self, echelle, temps, Midpoint, periode):
		decalage = 5
		if Var.ema["echelle"] != echelle:
			# Premiere valeur de prix == ema(1)
			# print("debug 1ier tour")
			Var.ema["echelle"] = echelle
			try:
				self.preloadema(echelle, temps, periode)
			except Exception as e:
				Var.ema["valeurs"][0] = round(float(Midpoint), 6)

			Var.emaBacktest.append(Var.ema["valeurs"][len(
				Var.ema["valeurs"]) - 1])  # envoyé au csv

		else:
			# x moyenne bid/ask
			x = float(Midpoint)
			t = float(Var.ema["valeurs"][len(Var.ema["valeurs"]) - 1])
			# n = nb de periode
			n = int(periode)
			# a: poid alpha
			a = 2 / (n + 1)
			y = round((a * x + (1 - a) * t), 6)

			if self.HeureUpgrade and echelle == "heures":
				Var.ema["periode"] = periode
				Var.ema["valeurs"].append(y)
				lastiter = len(Var.ema["valeurs"]) - 1
				if lastiter >= decalage:
					EmaDecalee = Var.ema["valeurs"][lastiter - decalage]

			elif self.MinUpgrade and echelle == "minutes":
				Var.ema["periode"] = periode
				Var.ema["valeurs"].append(y)
				lastiter = len(Var.ema["valeurs"]) - 1
				if lastiter >= decalage:
					EmaDecalee = Var.ema["valeurs"][lastiter - decalage]
				Var.emaBacktest.append(Var.ema["valeurs"][len(
					Var.ema["valeurs"]) - 1])  # envoyé au csv

			elif self.MinUpgrade and echelle != "minutes":
				# pas sur de moi , peut servir en streaming
				Var.emaBacktest.append(Var.ema["valeurs"][len(
					Var.ema["valeurs"]) - 1])  # envoyé au csv

	def chronoMinute(self, temps):
		"""	Horloge:
				chrono déclenche MinUpgrade et HeureUpgrade
		"""
		# Var.lastDatetime est créer au demarrage
		# delta = temps - Var.lastDatetime

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
