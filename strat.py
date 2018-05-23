# -*- coding: utf-8 -*-

import time
import rest
import Var
import tweepy
import json

#from memory_profiler import profile

class strategie(object):
	"""	regroupe les strategie d'achat/vente algorithmique"""

	def __init__(self,n):

		self.ordrePassee = False

		self.EmaCross(n-1)
		self.close(n)

		if self.ordrePassee:
			print("Ordre passé, PAUSE")
			time.sleep(40)
		else :
			pass

	def ClientSentiment(self, i, epic):
		"""Strategie autour des Positions des clients IG """
		
		position =rest.ig().IgClientPositions(epic)
		Bullish =position["Bull"]
		Bearish =position["Bear"]
				
		c1 = Bullish > 89
		if c1 :
			Id = rest.fakeOrders(i,"sell")
			return Id
		else :
			pass
		
		self.archiveSentiment(position, epic)		
		return Bullish, Bearish

	def EmaCross(self,j):
		""" Croisement PRIX et EMA a la periode j """
		emataille = len(Var.ema["valeurs"])-1 #<- delai de 5 periode
		cparam= (len(Var.FakeDeal["Id"])-1) < Var.PositionSimultanee and Var.Minute>Var.Ematempsinit

		# Crosses conditions
		c11 = float(Var.price["Ask"][j-1]) <= Var.ema["valeurs"][emataille]
		c1 = float(Var.price["Ask"][j]) > Var.ema["valeurs"][emataille] and c11
		
		c21 = float(Var.price["Bid"][j-1]) >= Var.ema["valeurs"][emataille]
		c2 = float(Var.price["Bid"][j]) < Var.ema["valeurs"][emataille] and c21
		
		condition1= cparam and c1
		condition2= cparam and c2
		
		if condition1 :
			print("Buy ema cross")
			print("prix: "+str(Var.price["Ask"][j])+"\n EMA: "+str(Var.ema["valeurs"][emataille]))
			print("prix precedent: "+str(Var.price["Ask"][j-1])+"\n EMA: "+str(Var.ema["valeurs"][emataille-1]))
			sens ="buy"
			Id = rest.fakeOrders(j,sens)
			self.ordrePassee = True
			return Id
		elif condition2 :
			sens = "sell"
			print("prix: "+str(Var.price["Bid"][j])+"\n EMA: "+str(Var.ema["valeurs"][emataille]))
			print("prix precedent: "+str(Var.price["Bid"][j-1])+"\n EMA: "+str(Var.ema["valeurs"][emataille-1]))
			Id = rest.fakeOrders(j,sens)
			self.ordrePassee = True
			return Id
		else :
			pass

	def scalping(self,price):
		i = (price-1) 
		trigger = 4 #<-%var/seconde declencheur
		cparam = (len(Var.FakeDeal["Id"])-1) < Var.PositionSimultanee

		try:
			c11 = float(Var.delta["Ask"][i]) >= float(trigger) 	
			c21 = float(Var.delta["Ask"][i]) < float(trigger)
		except IndexError:
			c11 = float(Var.delta["Ask"][0]) >= float(trigger) 	
			c21 = float(Var.delta["Ask"][0]) < float(trigger)


		condition1 = c11 and cparam and Var.Minute> 20
		conditions2 = c21 and cparam
		
		if condition1 :
			sens = "buy"
			Id = rest.fakeOrders(price, sens)
			# vrai ordre http :rest.MarketOrders()
			print("DEAL: "+sens)
			self.ordrePassee = True
			return Id
		elif conditions2 :
			sens = "sell"
			Id = rest.fakeOrders(price, sens)
			# vrai ordre http :rest.MarketOrders()
			print("DEAL: "+sens)
			self.ordrePassee = True
			return Id
		else :
			pass

	def close(self,i):
		""" cloture les deal existant 
			A REECRIRE !!!
			i : indice du prix a l'appel de fnction
			Id : Id du Deal"""
		DealACloturer = []

		for x in range(1,len(Var.FakeDeal["Id"])-1):
			#x : index de l'id
			j = str
			#condition de cross d'ema
			emataille = len(Var.ema["valeurs"])-1 #<- delai de 5 periode
			c11 = float(Var.price["Ask"][i-1]) <= Var.ema["valeurs"][emataille]
			c1 = float(Var.price["Ask"][i]) > Var.ema["valeurs"][emataille] and c11
		
			c21 = float(Var.price["Bid"][i-1]) >= Var.ema["valeurs"][emataille]
			c2 = float(Var.price["Bid"][i]) < Var.ema["valeurs"][emataille] and c21

			if x != 0 :
				# Id existant
				if Var.FakeDeal["sens"][x] == "sell" :
					j = "Ask"
				elif Var.FakeDeal["sens"][x] == "buy":
					j = "Bid"  
				else :
					print("erreur: ",Var.FakeDeal["sens"][x])
					break

				prixactuel = float(Var.price[j][i])
				prixentree = float(Var.FakeDeal["entry"][x+1])
				p = round(prixactuel-prixentree*100000,2) # x100 caren pip
				limit =  20
				stoploss = -20
				
				# cloture si stoploss/limit ou emacross 
				if p > limit or p < stoploss :
					DealACloturer.append(x)	
				elif c1 and Var.FakeDeal["sens"][x]=="sell":
					DealACloturer.append(x)
					print("Croisement vendeur invalidé")
				elif c2 and Var.FakeDeal["sens"][x]=="buy":
					DealACloturer.append(x)
					print("Croisement acheteur invalidé")
			else :
				pass
		rest.CloseFakeOrders(DealACloturer)

	def archiveSentiment(self, position, epic):
		"""archive les positions au format json"""
		#Archivage Snippet
		titre = epic.replace('.','-')+"_"+time.strftime('%x').replace('/','-')
		try:
			open("archive/Sentiment/"+titre+'.txt','x')
		except FileExistsError as a:
			pass # <--warning/log
		with open("archive/Sentiment/"+titre+'.txt','r+') as out:
			json.dump(position, out)
			out.close()






class twitter(object):
	"""docstring for twitter"""
	def __init__(self):
		super(twitter, self).__init__()
		self.consumer_key = 'YOUR_KEY '
		self.consumer_secret = "YOUR_KEY"
		self.access_token = "YOUR_KEY"
		self.access_token_secret = "YOUR_KEY"

	def main(self):
		

		auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
		auth.set_access_token(self.access_token, self.access_token_secret)

		api = tweepy.API(auth)

		public_tweets = api.home_timeline()
		for tweet in public_tweets:
			print (tweet.text)