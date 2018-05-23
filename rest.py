# -*- coding: utf-8 -*-

import requests
import json
import pprint
import os.path
import datetime
import indicateur
import strategie
import time
import Var
from jsonmerge import Merger
import pandas as pd

"""
	ToDo : 
			- réecrire retrieve avec un while au lieu de if : for ...
			- codé le Refresh Token apres 60 seconde ou en cas d'erreur 400
			  enlever les if de reconnexion dans pnl , retrieve 
			- créer un schema pour les header ?
			— epurer init !!!
"""


class ig:

	def __init__(self):

		self.essaiPnl = 0
		self.passage2 = False
		self.serverAddr = "https://demo-api.ig.com/gateway/deal" # <-serveur demo
		
		""" data = {
			'clientId': '',
			'accountId': '',
			'timezoneOffset': 1,
			'lightstreamerEndpoint': '',
			'oauthToken': { 
				'access_token': '',
				'refresh_token': '',
				'scope': '',
				'token_type': '',
				'expires_in': ''
				}
			}
		"""	
		
		self.Auth(Var.login,Var.password)
		#print(Var.data)
		
	def Auth(self, login, password):
		""" Procedure d'ID Oauth2 
		"""
		if Var.authentified == False :
			print("AUTHENFICATION")
			payloads = {"identifier": login ,
						"password": password }
			headers = {'X-IG-API-KEY': "cbcf3ac23f07eef2ba494576a6fb38dde0a7ebd2",
					   'Version': '3'}
			url = self.serverAddr+"/session"
			r = requests.post(url, data=json.dumps(payloads), headers=headers)

			# resultat
			#print(r.url) <--- debug/log
			r.status_code
			if r.status_code == 200:
				
				data = r.json()  # donnée Oauth pour prochaine requete
				
				#self.data redondant, peut etre remplacé par var
				Var.authentified = True
				Var.data = data
				return Var.data
			else:
				print("Echec !")
		else :
			print("REFRESH")
			Var.data = self.refresh(Var.data)

	def refresh(self, data):
		# Rafraichissement du Access token
		url = self.serverAddr + "/session/refresh-token"
		payloads = { "refresh_token" : data.get('oauthToken').get('refresh_token')}
		head = { 'X-IG-API-KEY': "cbcf3ac23f07eef2ba494576a6fb38dde0a7ebd2",
				 'Version': '1', 'IG-ACCOUNT-ID': data.get('accountId')}

		r = requests.post(url, data=json.dumps(payloads), headers=head)
	  
		if r.status_code == 200 :
			data['oauthToken']['access_token'] = r.json().get('access_token')
			data['oauthToken']['refresh_token'] = r.json().get('refresh_token')
			#print("Data-apres:") #"""DEBUG"""
			#pprint.pprint(data)
			return data
		elif (r.status_code == 400 and self.passage2 == False) : # relance l'Auth
			self.refresh(self.Auth())
			print("Passage 2")
			self.passage2 = True # pas sur de l'efficacité. A verifié !
		else : #retour console
			print("\n ERREUR serveur :")
			print(r.status_code)
			print("Detail: ")
			return r.json()		

	def streamingToken(self, arg):
		data = arg
		LSData = {}
		h1 = {'IG-ACCOUNT-ID': data.get('accountId'),
			  'Authorization': data.get('oauthToken').get('token_type')+" "+data.get('oauthToken').get('access_token'),
			  'Version': '1', 'X-IG-API-KEY': "cbcf3ac23f07eef2ba494576a6fb38dde0a7ebd2" 
			  }
		url = self.serverAddr + "/session?fetchSessionTokens=true"
		r = requests.get(url , headers =h1)
		
		LSData['addr'] = (r.json().get('lightstreamerEndpoint')).encode('utf8')
		LSData['user'] = (r.json().get("accountId")).encode('utf8')
		LSData['password'] = ("CST-"+r.headers.get('CST')+"|XST-"+r.headers.get('X-SECURITY-TOKEN'))

		return LSData

	def getcurrencycode(self, epic):
		
		data = Var.data
		url= self.serverAddr+"/markets/"+epic
		head={
			'IG-ACCOUNT-ID': data.get('accountId'),
			'Authorization': data.get('oauthToken').get('token_type')+" "+data.get('oauthToken').get('access_token'),
			'Version': '3',
			'X-IG-API-KEY': "cbcf3ac23f07eef2ba494576a6fb38dde0a7ebd2"
			}
		r = requests.get(url, headers=head)
		if r.status_code == 200:
			raw = dict(r.json())
			code = raw.get("instrument").get("currencies")[0].get("code")
			return code
		else :
			print("Statut: "+r.status_code)

	def marketId(self,epic):

		url = self.serverAddr+"/markets/"+epic
			#print(url)
		h1 = {'IG-ACCOUNT-ID': Var.data.get('accountId'),
			  'Authorization': Var.data.get('oauthToken').get('token_type')+" "+Var.data.get('oauthToken').get('access_token'),
			  'Version': '1', 'X-IG-API-KEY': "cbcf3ac23f07eef2ba494576a6fb38dde0a7ebd2" 
			}

		r = requests.get(url, headers=h1)
		#print (r.status_code)
		marketId = r.json().get("instrument").get("marketId")
		#print(marketId)
		return marketId

	def IgClientPositions(self,epic):

		url = self.serverAddr + "/clientsentiment/" + str(self.marketId(epic))

		h1 = {'IG-ACCOUNT-ID': Var.data.get('accountId'),
			  'Authorization': Var.data.get('oauthToken').get('token_type')+" "+Var.data.get('oauthToken').get('access_token'),
			  'Version': '1', 'X-IG-API-KEY': "cbcf3ac23f07eef2ba494576a6fb38dde0a7ebd2" 
			  }

		r = requests.get(url, headers=h1)
		raw = r.json()
		if not r.status_code == 200 :
			print("Erreur : ")
			print(r.status_code)				
		
		Bullish = raw.get("longPositionPercentage")
		Bearish = raw.get("shortPositionPercentage")
		a = {"Bull":int(Bullish),"Bear":int(Bearish)}
		#print(a)
		return a

	def pnl(self):
		# fonction pour recuperer le PnL
		url =  self.serverAddr+"/accounts"
		
		h1 = {'IG-ACCOUNT-ID': Var.data.get('accountId'),
		  'Authorization': Var.data.get('oauthToken').get('token_type')+" "+Var.data.get('oauthToken').get('access_token'),
		  'Version': '1', 'X-IG-API-KEY': "cbcf3ac23f07eef2ba494576a6fb38dde0a7ebd2" 
		  }
		r = requests.get( url, headers=h1)
		raw = r.json()
		value= str
		print(r.status_code)
		print(raw)
		
		if r.status_code == 200 :
			for x in range(len(raw['accounts'])):
				print(raw['accounts'][x]['accountId'])
				if raw['accounts'][x]['accountId'] == Var.data.get('accountId') :	 
					value = str(raw['accounts'][x]['balance']['balance'])
				else :
					print("Id de compte non trouvé !")
					print(r.status_code)
			
			return value

		elif r.status_code == 401 and self.essaiPnl < 1 :
			Var.data = self.refresh(Var.data)
			self.essaiPnl = self.essaiPnl + 1
			self.pnl()
		
		else :
			print("Erreur : ")
			print(r.status_code)

	def retrieve(self, epic, dateF, dateT):
		""" Par default resolution = MINUTE
			date(UTC) format : "2017-MM-DDTHH:MM:SS"(string) 
		"""
		schema = {
			"prices": [{"type": "object", "mergeStrategy": "append"}],
			"instrumentType": "",
			"metadata": {
				"allowance": {},
				"size": "",
				"pageData": {
					"pageSize": "",
					"pageNumber": "",
					"totalPages": ""
					}
				}
			}

		# standard get requests apres ID
		h1 = {'IG-ACCOUNT-ID': Var.data.get('accountId'), 'Authorization': Var.data.get('oauthToken').get('token_type') + " " + Var.data.get(
			'oauthToken').get('access_token'), 'Version': '3', 'X-IG-API-KEY': "cbcf3ac23f07eef2ba494576a6fb38dde0a7ebd2"}

		resolution = 'MINUTE'
		dateFrom = dateF.replace(":", "%3A")
		dateTo = dateT.replace(":", "%3A")
		pageSize = "100"
		pageNumber = "1"
		totalPages = ""
		phrase = ""

		# DEBUG
		print("\n" + "Headers: ")
		pprint.pprint(h1)

		url1 = [ self.serverAddr, "/prices/", epic, "?resolution=", resolution,
				"&from=", dateFrom, "&to=", dateTo, "&pageSize=", pageSize, "&pageNumber=", pageNumber]
		r1 = requests.get(phrase.join(url1), headers=h1)

		# aggrégation des feuilles de prix
		if r1.status_code == 200:
			merger = Merger(schema)
			base = None

			# pprint.pprint(r1.json())
			print("\nMETADATA : ")
			pprint.pprint(r1.json().get("metadata"))
			print("\nPageData: ")
			print(r1.json().get("metadata").get("pageData"))

			totalPages = r1.json().get("metadata").get("pageData").get("totalPages")
			x = int(pageNumber)
			y = int(totalPages)
			for x in range(y):

				pageNumber = str(int(pageNumber) + 1)
				url2 = [self.serverAddr,"/prices/", epic, "?resolution=", resolution,
						"&from=", dateFrom, "&to=", dateTo, "&pageSize=", pageSize, "&pageNumber=", pageNumber]
				r2 = requests.get(phrase.join(url2), headers=h1)
				if r2.status_code == 200:
	
					raw = r2.json()
					base = merger.merge(base, raw, meta={'page': 1})
					pprint.pprint(r2)
				elif r2.status_code ==403 :
					print(r2)
					break

			with open("archive/"+self.marketId(epic)+dateF[:10]+"_"+dateT[:10]+ ".json", 'w', encoding="utf-8") as outfile:
				json.dump(base, outfile, ensure_ascii=False) 

			return base

		else:
			code = str(r1.status_code)
			print("ERREUR:" + code + " !\n")
			pprint.pprint(r1.json())

			if r1.json().get('errorCode') == 'error.security.oauth-token-invalid':
					   # Refreshing token

				code = str(r1.status_code)
				print("Code HTTP: " + code)

	def CreateOrders(self,orderType,direction,stopDistance,limitDistance,epic,*args):
		url= [self.serverAddr,"/positions/otc"]
		code = self.getcurrencycode(epic)

		if orderType == "MARKET" :
			level = None
		
		h1 = {
			'IG-ACCOUNT-ID': Var.data.get('accountId'),
			'Authorization': Var.data.get('oauthToken').get('token_type')+" "+Var.data.get('oauthToken').get('access_token'),
			'Version': '2',
			'X-IG-API-KEY': "cbcf3ac23f07eef2ba494576a6fb38dde0a7ebd2"
			}
		payloads = {
			# python Dict et non du JSON (None == null)
			"epic": epic,
			"expiry": "-",
			"direction": direction,
			"size": "1",
			"orderType": orderType,
			"timeInForce": None,
			"level": level,
			"guaranteedStop": "false",
			"stopLevel": None,
			"stopDistance": stopDistance,
			"trailingStop": None,
			"trailingStopIncrement": None,
			"forceOpen": "true",
			"limitLevel": None,
			"limitDistance": limitDistance,
			"quoteId": None,
			"currencyCode": code
			}

		#pprint.pprint(json.dumps(payloads))
		r= requests.post(str("").join(url), data=json.dumps(payloads), headers=h1)
		print(r.status_code)
		#print(r.json())
		
		if r.status_code == 200:
			dealref = r.json().get("dealReference")
			#print(dealref)
			h={'IG-ACCOUNT-ID': Var.data.get('accountId'),
				'Authorization': Var.data.get('oauthToken').get('token_type')+" "+Var.data.get('oauthToken').get('access_token'),
				'Version': '1', # VERSION 1
				'X-IG-API-KEY': "cbcf3ac23f07eef2ba494576a6fb38dde0a7ebd2"}

			url1 = self.serverAddr+"/confirms/"+dealref
			r1= requests.get(url1, headers=h)
			raw1 = r1.json()
			
			if raw1.get("dealStatus") == "ACCEPTED" :
				print(raw1.get('dealStatus'))
				Var.DealDone["Time"].append(raw1.get("date"))
				Var.DealDone["Id"].append(raw1.get("dealId"))
				Var.DealDone["sens"].append(raw1.get("direction"))

			elif raw1.get("dealStatus") == "REJECTED" :
				print("Rejected")
				raw1.get("reason")
			else :
				print("Erreur: ",r1.status_code)

		else :
			print(r.status_code)

	def CloseOrders(self, dealId, orderType, *args):
		"""SEUL un Deal ID devrait etre passé, avec MARKET type"""
		if orderType == "MARKET" :
			level = None
		
		url =[self.serverAddr, "/positions/otc"]
		url0 = self.serverAddr + "/positions/" + dealId
		h0 = {
			'IG-ACCOUNT-ID': Var.data.get('accountId'),
			'Authorization': Var.data.get('oauthToken').get('token_type') + " " + Var.data.get('oauthToken').get('access_token'),
			'Version': '1',
			'X-IG-API-KEY': "cbcf3ac23f07eef2ba494576a6fb38dde0a7ebd2",
		}

		h1 = {
			'IG-ACCOUNT-ID': Var.data.get('accountId'),
			'Authorization': Var.data.get('oauthToken').get('token_type') + " " + Var.data.get('oauthToken').get('access_token'),
			'Version': '1',
			'X-IG-API-KEY': "cbcf3ac23f07eef2ba494576a6fb38dde0a7ebd2",
			'_method': "DELETE"
		}

		#  Verifie et ajuste le sens et la taille par rapport a l'initiale
		r0 = requests.get(url0, headers=h0)
		raw0 = r0.json()
		print(raw0)

		if (raw0.get("position").get("direction")) == "BUY":
			CloseDir = "SELL"
		else:
			CloseDir = "BUY"

		initialSize = raw0.get("position").get("dealSize")
		initialeLevel = raw0.get("position").get("openLevel")

		if float(initialSize) == int(initialSize):
			initialSize = int(initialSize)

		payloads = {
			"dealId": dealId,
			"epic": None,
			"expiry": None,
			"direction": CloseDir,
			"size": str(initialSize),
			"level": level,
			"orderType": orderType,
			"timeInForce": None,
			"quoteId": None
		}
		print(json.dumps(payloads))
		r = requests.post(str("").join(url), headers=h1, data=json.dumps(payloads))

		if r.status_code == 200:
			dealref = r.json().get("dealReference")
			url1 = self.serverAddr + "/confirms/" + dealref
			r1 = requests.get(url1, headers=h0)
			raw1 = r1.json()

			if raw1.get("dealStatus") == "ACCEPTED":
				# print(raw1)
				Var.CleanedDeal["CloseTime"].append(raw1.get("date"))
				Var.CleanedDeal["OpenTime"].append(raw1.get("dealId"))
				Var.CleanedDeal["closelevel"].append(raw1.get("level"))
				Var.CleanedDeal["profit"].append(raw1.get("profit"))
				Var.CleanedDeal["entrylevel"].append(initialeLevel)

			elif (raw1.get("dealStatus")) == "REJECTED" :
				print("Rejected")

			else :
				print("Erreur: ")
				print(r1.status_code)

			Var.PnL =+ (round(float(raw1.get("profit")),2))
		else:
			print("erreur:",r.status_code)
			print(r.json())


class backtest:
	"""docstring for backtest"""
	def __init__(self):
		pass

	def Pull(self, DayF, DayT):

		api = ig()
		dateF = DayF + "T00:00:00"
		dateT = DayT + "T00:00:00"
		marketId = api.marketId(Var.epic)

		if not os.path.isfile("archive/" + marketId + dateF[:10] + "_" + dateT[:10] + ".json"):
			sample = api.retrieve(Var.epic, dateF, dateT)
		else:
			with open("archive/"+marketId+dateF[:10]+"_"+dateT[:10]+ ".json", 'r', encoding="utf-8") as outfile:
				# sample Data
				sample = json.load(outfile)

		self.pricediscovery(sample)

		df = self.jsonpricetocsv(sample)

		pd.DataFrame(Var.FakeDeal).to_csv("entry.csv", index=False)
		pd.DataFrame(Var.CleanedDeal).to_csv("close.csv", index=False)
		pd.DataFrame(df).to_csv("priceclose.csv", index=False)

	def pricediscovery(self,sample):
		""" sample.json passe dans le "systeme"
		"""
		t = sample["prices"][0]["snapshotTimeUTC"]
		Var.lastDatetime = datetime.datetime(int(t[:4]), int(t[5:7]), int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19]))

		for x in range(0, len(sample.get("prices")) - 1):

			bidbefore = float(sample.get('prices')[x - 1].get('closePrice').get('bid'))
			askbefore = float(sample.get('prices')[x - 1].get('closePrice').get('ask'))
			bid = float(sample.get('prices')[x].get('closePrice').get('bid'))
			ask = float(sample.get('prices')[x].get('closePrice').get('ask'))
			
			t = sample["prices"][x]["snapshotTimeUTC"]
			temps = datetime.datetime(int(t[:4]), int(t[5:7]), int(t[8:10]), int(t[11:13]), int(t[14:16]), int(t[17:19]))
			
			indicateur.indicateur(temps=temps, Midpoint=((bid+ask)/2))
			strategie.strategie(BidAsk=[bid,ask],Price_0=[bidbefore,askbefore], temps=temps, backtest=Var.backtest) 

			# print(temps)
			# print("b: ",bid," a: ",ask, "t:", temps,"b0: ",bidbefore,"a0: ",askbefore)
			time.sleep(Var.DebugTime)  # Pour debug 

	def jsonpricetocsv(self, sample):
		"""	sample : json object
			Retrieve Json to dictsa object named df
			"""
		df = {"Time": [],
			"bidClose": [],
			"askClose": [],
			"TradedVolume": [],
			"ema": [],
			"Open": [],
			"Close": []
			}

		for x in range(0, len(sample["prices"])):

			df["Time"].append(sample["prices"][x]["snapshotTimeUTC"].replace("T","  "))
			df["bidClose"].append(sample["prices"][x]["closePrice"]["bid"])
			df["askClose"].append(sample["prices"][x]["closePrice"]["ask"])
			df["TradedVolume"].append(sample["prices"][x]["lastTradedVolume"])
		
		# boucle migrant deal vers priceclose.csv
		opendealscan = 1
		closedealscan = 1
		for x in range(0,len(df["Time"])-1):
			t = df["Time"][x]
			a = datetime.datetime(int(t[:4]), int(t[5:7]), int(t[8:10]), int(t[12:14]), int(t[15:17]), int(t[18:20]))
			
			for y1 in range(opendealscan, len(Var.CleanedDeal["OpenTime"])):
				t1 = Var.CleanedDeal["OpenTime"][y1]
				if len(t1) != 0:
					up = datetime.datetime(int(t1[5:9]), int(t1[10:12]), int(t1[13:15]), int(t1[16:18]), int(t1[19:21]), int(t1[22:24]))
					if up == a:
						df["Open"].append(df["bidClose"][x])
						opendealscan += 1
						break
					else: 
						df["Open"].append(0)
						break
				else :
					df["Open"].append(0)
					opendealscan += 1
					break

			for y in range(closedealscan, len(Var.CleanedDeal["CloseTime"])):
				t0 = Var.CleanedDeal["CloseTime"][y-1]
				t2 = Var.CleanedDeal["CloseTime"][y]
				if len(t2) != 0:
					down= datetime.datetime(int(t2[:4]), int(t2[5:7]), int(t2[8:10]), int(t2[11:13]), int(t2[14:16]), int(t2[17:19]))
					#print("down:",str(down))
					if down == a :
						#print("match !!!-------------")
						df["Close"].append(df["bidClose"][x])	
						closedealscan += 1
						break
						# pas de break car d'autre position
						# peuvent s'etre cloturer a ce moment
					elif y==closedealscan and t2 == t0 :
						#print("meme que precedent")
						closedealscan += 1
						y +=1
					elif y == len(Var.CleanedDeal["CloseTime"])-1:
						df["Close"].append(0)
						#print("PAS MATCH -------------")
						break	
				else :
					df["Close"].append(0)
					closedealscan += 1
					break

			#print("v1:",opendealscan," V2:",closedealscan)
			p1 = opendealscan == (len(Var.CleanedDeal["OpenTime"]))
			p2 = closedealscan == (len(Var.CleanedDeal["CloseTime"]))
			if p1 :
				df["Open"].append(0)
				# fini de remplir le tableau apres tout les deal matché
			if p2 : 
				df["Close"].append(0)

		Var.emaBacktest[0] = Var.emaBacktest[1] # corrige le premier 0
		df["ema"] = Var.emaBacktest
		
		if Var.ema["echelle"] =="minutes" :
			df["Close"].append(0) # bug pour la derniere min on dirait
		
		# DEBUG array lengh :
		print("open:",len(df["Open"]),len(df["Close"]), "ema:",len(df["ema"])," autre:",len(df["bidClose"]))
		return df
		
	def fakeOrders(self, BidAsk, sens, temps):

			if sens == "BUY":
				inverse = float(BidAsk[1])  # inverse = Ask
			elif sens == "SELL":
				inverse = float(BidAsk[0])  # inverse = Bid
			else:
				print("erreur direction trade")

			Var.FakeDeal["Time"].append(str(temps))
			Var.FakeDeal["entry"].append(inverse)
			Var.FakeDeal["sens"].append(sens)
			Var.FakeDeal["Id"].append("Fake:" + str(temps))

	def CloseFakeOrders(self, Dealtuple, BidAsk, temps):
		""" cloture les ordres selon leur ID """
		y=0 # x-y index pour suppresion du dictionnaire FakeDeal
		
		for x in range(len(Dealtuple)):
			i = Dealtuple[x] # index du deal
			FakeId = Var.FakeDeal["Id"][i]
			entry = Var.FakeDeal["entry"][i]
			sens = Var.FakeDeal["sens"][i]
			# print("cloturé a",entry,'sens ;',sens,"heure= ",Var.FakeDeal["Time"][i])

			if sens =="SELL":
				prixsortie = float(BidAsk[1]) #Ask
				profit = round((entry - prixsortie ) * 10000, 2)
			else: 
				prixsortie =float(BidAsk[0]) # Bid
				profit = round((prixsortie - entry) * 10000, 2)

			Var.PnL += profit

			Var.CleanedDeal["CloseTime"].append(str(temps))	
			Var.CleanedDeal["OpenTime"].append(FakeId)
			Var.CleanedDeal["profit"].append(profit)
			Var.CleanedDeal["entrylevel"].append(entry)
			Var.CleanedDeal["closelevel"].append(prixsortie)

		# print(Dealtuple)
		for x in Dealtuple:	
			#supprime les valeurs traitées
			#print("Deal "+Var.FakeDeal["Time"][x-y]+" CLOTURE !")
			Var.FakeDeal["Time"].pop(x-y)
			Var.FakeDeal["Id"].pop(x-y)
			Var.FakeDeal["entry"].pop(x-y)
			Var.FakeDeal["sens"].pop(x-y) 
			# apres destruction de une entrée dans Fakedeal,
			# l'index relatif dans Dealtuple regresse de 1
			y+=1


# if __name__ == '__main__':
#    self.main()
