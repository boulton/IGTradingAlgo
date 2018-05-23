# -*- coding: utf-8 -*-

import requests
import json
import pprint
import io
from rest import ig

""" TODO :
		créer un thread dans la limite des quotas Broker
		+ refreshing du token tt les 10 min + horaire d'ouverture """

class hue:

	def __init__(self):
		pass
		# Fonction importdef 
	
	def main (self) :
		global xy
		#ig().Auth()
		PnL = ig().PnL()
		if PnL > 0 :
			xy = 18000# vert
		elif PnL <= 0 :
			xy = 2000 # rouge
		self.modif(xy)
		
	def modif(self, xy) :
		
		ipBridge = "192.168.0.10"
		user = "gDfyoacHkDypPsSSq14GnXcn79r5WyoC3apg-4cz"
		lightId ="4"
		url ="http://"+ipBridge+"/api/"+user+"/lights/"+lightId+"/state"
		saturation =170

		body ='{"on":true, "sat":'+str(saturation)+', "bri":100,"hue":'+str(xy)+"}"  
		print(json.dumps(body))
		r=requests.put(url, data=json.loads(json.dumps(body)))
		#pprint.pprint(r.json())


if __name__ == '__main__' :
	hue().main()
