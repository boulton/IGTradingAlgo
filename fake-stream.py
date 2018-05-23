#!/usr/bin/python

import threading
import json
import datetime
import Var
import rest
import indic
import strat
import pprint


import matplotlib.pyplot as plt

""" faux stream chargeant un set de donnée csv tel 
	un lighstream serveur pour backtest"""

class backtest(object):
	"""docstring for ClassName"""
	def __init__(self):
		self.arg = None
		self.mainThread = None
		self.name ="retrieve26"
		
	def handler(self):
		pass

	def receive(self):
		
		datex = []

		with open("/archive/"+self.name+'.json', 'r+') as out :
			info = json.loads(out)
			
			#Var.price["Date"].append("/".join(year,month,day))

			for x in range (len(info.get("prices"))) :
				tempX = info["prices"][x].get("snapshotTimeUTC")
				
				timeX = info.get("prices").get("snapshotTimeUTC")
				year = timeX[0:4]
				month = timeX[5:7]
				day = timeX[8:10]
				time = timeX[11:20]
				fulldatestr = "-".join(year,month,day,time)
				dateformated = datetime.datetime.strptime(fulldatestr,"%y-%m-%d-%H-%m-%s")
				datex.append(dateformated)
				Var.datePrix = datex

				openP = info.get("prices")[x].get("openPrice")
				
				Var.prix.append(float(openP.get("bid")))

				#closeP = info.get("prices")[x].get("closePrice")
				#highP = info.get("prices")[x].get("highPrice")
				#lowP = info.get("prices")[x].get("lowPrice")

		pprint.pprint(Var.datePrix)
		pprint.pprint("\n",Var.prix)


	def item_update(self):
		for x in range(1,len(Var.price["Bid"])):
			
			indic.indicateur(x)

			strat.strategie(x)
	print("update")



if __name__ == '__main__':
	backtest.receive()
