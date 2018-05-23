# -*- coding: utf-8 -*-

import requests
import json
import pprint
import io
import sys
import Var
from jsonmerge import Merger

"""
	ToDo : 
			-  fusionné 2 a n pages json. DONE
			- réecrire retrieve avec un while au lieu de if : for ...
			- codé le Refresh Token apres 60 seconde ou en cas d'erreur 400
			  enlever les if de reconnexion dans pnl , retrieve 
			- créer un schema pour les header ?
			— epurer init !!!
"""

class ig:

	data = {'clientId': '', 'accountId': '', 'timezoneOffset': 1, 'lightstreamerEndpoint': '',
			'oauthToken': {'access_token': '', 'refresh_token': '', 'scope': '', 'token_type': '', 'expires_in': ''}}
	authentified = False
	essaiPnl = 0
	serverAddr = "https://demo-api.ig.com/gateway/deal" # <-serveur demo
			

	schema = {
			"prices": [{"type": "object", "mergeStrategy": "append"}],
			"instrumentType": "",
			"metadata": {
				"allowance": {},
				"size": "",
				"pageData": {
					"pageSize": "",
						"pageNumber": {"mergeStrategy": "arrayMergeById", "mergeOptions": "pageNumber"},
						"totalPages": ""
				}
			}
		}

	def main(self): #marche pas
		self.Auth(Var.login,Var.password)
		self.PnL()

	def __init__(self):

		passage2 = False
		

	def Auth(self, login, password):
		# procedure d'ID Oauth2 
		#suppr global authentified

		payloads = {"identifier": login ,
					"password": password }
		headers = {'X-IG-API-KEY': "YOUR-API-KEY",
				   'Version': '3'}
		url = self.serverAddr+"/session"
		r = requests.post(url, data=json.dumps(payloads), headers=headers)

		# resultat
		#print(r.url) <--- debug/log
		r.status_code
		if r.status_code == 200:
			#print("Connexion établie") <-- log/debug
			data = r.json()  # donnée Oauth pour prochaine requete
			#pprint.pprint(r.json())
			self.authentified = True
			self.data = data
			return data
		else:
			print("Echec !")

	def refresh(self, data):
		# Rafraichissement du Access token
		url = self.serverAddr + "/session/refresh-token"
		payloads = { "refresh_token" : data.get('oauthToken').get('refresh_token')}
		head = { 'X-IG-API-KEY': "YOUR-API-KEY",
				 'Version': '1', 'IG-ACCOUNT-ID': data.get('accountId')}

		r = requests.post(url, data=json.dumps(payloads), headers=head)
	  
		if r.status_code == 200 :
			data['oauthToken']['access_token'] = r.json().get('access_token')
			data['oauthToken']['refresh_token'] = r.json().get('refresh_token')
			print("Data-apres:") #"""DEBUG"""
			pprint.pprint(data)
			return data
		elif (r.status_code == 400 and passage2 == False) : # relance l'Auth
			self.refresh(self.Auth())
			print("Passage 2")
			passage2 = True # pas sur de l'efficacité. A verifié !
		else : #retour console
			print("\n ERREUR serveur :")
			print(r.status_code)
			print("Detail: ")
			return r.json()
			pass

	def streamingToken(self, arg):
		data = arg
		LSData = {}
		h1 = {'IG-ACCOUNT-ID': data.get('accountId'),
			  'Authorization': data.get('oauthToken').get('token_type')+" "+data.get('oauthToken').get('access_token'),
			  'Version': '1', 'X-IG-API-KEY': "YOUR-API-KEY" 
			  }
		url = self.serverAddr + "/session?fetchSessionTokens=true"
		r = requests.get(url , headers =h1)
		
		LSData['addr'] = (r.json().get('lightstreamerEndpoint')).encode('utf8')
		LSData['user'] = (r.json().get("accountId")).encode('utf8')
		LSData['password'] = ("CST-"+r.headers.get('CST')+"|XST-"+r.headers.get('X-SECURITY-TOKEN'))

		return LSData

	def PnL(self):
		# fonction pour recuperer le PnL
		url =  self.serverAddr+"/accounts"
		

		if not self.authentified :
			self.Auth(Var.login,Var.password)
			self.PnL()
		else :
			h1 = {'IG-ACCOUNT-ID': self.data.get('accountId'),
			  'Authorization': self.data.get('oauthToken').get('token_type')+" "+self.data.get('oauthToken').get('access_token'),
			  'Version': '1', 'X-IG-API-KEY': "YOUR-API-KEY" 
			  }
			r = requests.get( url, headers=h1)
			raw = r.json()
			value= str
			print(r.status_code)
			print(raw)
			
			if r.status_code == 200 :
				for x in range(len(raw['accounts'])):
					print(raw['accounts'][x]['accountId'])
					if raw['accounts'][x]['accountId'] == self.data.get('accountId') :	 
						value = str(raw['accounts'][x]['balance']['balance'])
					else :
						print("Id de compte non trouvé !")
						print(r.status_code)
				
				return value

			elif r.status_code == 401 and self.essaiPnl < 1 :
				self.data = self.refresh(self.data)
				self.essaiPnl = self.essaiPnl + 1
				self.PnL()
			
			else :
				print("Erreur : ")
				print(r.status_code)
				


	def retrieve(self): 
		# standard get requests apres ID
		h1 = {'IG-ACCOUNT-ID': self.data.get('accountId'), 'Authorization': self.data.get('oauthToken').get('token_type') + " " + self.data.get(
			'oauthToken').get('access_token'), 'Version': '3', 'X-IG-API-KEY': "YOUR-API-KEY"}

		epic = "CS.D.USDSEK.MINI.IP"   # input() essai d'un retour console
		resolution = 'HOUR'
		dateF = "2017-11-22T00:00:00"
		dateT = "2017-11-23T00:00:00"
		dateFrom = dateF.replace(":", "%3A")
		dateTo = dateT.replace(":", "%3A")
		pageSize = "1"
		pageNumber = "1"
		totalPages = "2"
		phrase = ""

		# DEBUG
		# pprint.pprint(data)
		print("\n" + "Headers: ")
		pprint.pprint(h1)
		#print("\n EPIC:"+epic)

		url1 = [ self.serverAddr, "/prices/", epic, "?resolution=", resolution,
				"&from=", dateFrom, "&to=", dateTo, "&pageSize=", pageSize, "&pageNumber=", pageNumber]
		r1 = requests.get(phrase.join(url1), headers=h1)

		# aggrégation des feuilles de prix
		if r1.status_code == 200:
			merger = Merger(self.schema)
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

			with open("retrieve" + pageNumber + ".json", 'w', encoding="utf-8") as outfile:
				json.dump(base, outfile, ensure_ascii=False) 

		else:
			code = str(r1.status_code)
			print("ERREUR:" + code + " !")
			pprint.pprint(r1.json())
			if r1.json().get(errorCode) == 'error.security.oauth-token-invalid':
					   # Refreshing Token

				code = str(r1.status_code)
				print("Code HTTP: " + code)


def fakeOrders(i,sens):
		
		if sens == "buy" :
			j = "Ask"
		elif sens == "sell":
			j = "Bid"
		else :
			print("erreur direction trade")
			pass
		Var.FakeDeal["Time"].append(Var.price["Time"][i])
		Var.FakeDeal["entry"].append(Var.price[j][i])
		Var.FakeDeal["sens"].append(sens)
		Var.FakeDeal["Id"].append("Fake:"+Var.price["Time"][i])
		return ("Fake:"+Var.price["Time"][i]) # Id : Classiquement issu du confirm IG

def CloseFakeOrders(i):
	FakeId = Var.FakeDeal["Id"][i]
	entry = Var.FakeDeal["entry"][i]
	sens = Var.FakeDeal["sens"][i]
	j = str
	if sens == "sell" :
			j = "Ask"
	elif sens == "buy":
		j = "Bid"
	else :
		print("erreur direction trade")
		pass
	currentiter = len(Var.price["Time"])-1
	profit = (float(Var.price[j][currentiter]) -float(entry))
	Var.CleanedDeal["Time"].append(Var.price["Time"][currentiter])	
	Var.CleanedDeal["Id"].append(FakeId)
	Var.CleanedDeal["profit"].append(profit)
	Var.CleanedDeal["entry"].append(entry)
	Var.CleanedDeal["close"].append(Var.price["Time"][currentiter])

	Var.FakeDeal["Id"].pop(i)
	Var.FakeDeal["entry"].pop(i)
	Var.FakeDeal["sens"].pop(i)

def CloseOrders(self):

	dealId = Var.DealDone["Id"][len(Var.DealDone["Id"])-1]
	h1 = {'IG-ACCOUNT-ID': self.data.get('accountId'), 'Authorization': self.data.get('oauthToken').get('token_type') + " " + self.data.get(
		'oauthToken').get('access_token'), 'Version': '3', 'X-IG-API-KEY': "YOUR-API-KEY"}
	url =[self.serverAddr, "positions/otc"]
	payloads = {
		"dealId": dealId,
		"epic": self.epic,
		"expiry": null,
		"direction": null,
		"size": null,
		"level": null,
		"orderType": null,
		"timeInForce": null,
		"quoteId": null
	}

	r = requests.delete(str("").join(url),headers=h1,data=payloads)

def MarketOrders(self,sens,size):
	
	sens
	size
	h1 = {'IG-ACCOUNT-ID': self.data.get('accountId'), 'Authorization': self.data.get('oauthToken').get('token_type') + " " + self.data.get(
		'oauthToken').get('access_token'), 'Version': '3', 'X-IG-API-KEY': "YOUR-API-KEY"}

	url=[self.serverAddr,"/positions/otc"]
	payloads= {
		"epic": self.epic,
		"expiry": "-",
		"direction": sens,
		"size": "1",
		"orderType": "MARKET",
		"timeInForce": null,
		"level": null,
		"guaranteedStop": "false",
		"stopLevel": null,
		"stopDistance": "20",
		"trailingStop": null,
		"trailingStopIncrement": null,
		"forceOpen": "true",
		"limitLevel": null,
		"limitDistance": "30",
		"quoteId": null,
		"currencyCode": "EUR"
		}

	positionbool = False
	r= requests.post(str("").join(url), data=payloads, headers=h1)
	print(r.status_code)
	print(r.json())
	
	if r.status_code == 200:
		t =Var.refTrade["Time"].append(time.now().strftime("%h:%m:%s"))

		url1 = self.serverAddr+"/confirms/"+dealId
		r1= requests.get(url1, headers=h1)
		print(r1.status_code)
		if r1.json().get("dealStatus") == "ACCEPTED" :
			print(r1.json())
			i = Var.refTrade["Id"].append(r1.json().get("dealId"))
			print('archivé: {'+t+", "+i+"}")
			return True
		else :
			print("Rejected")
	else :
		print(r.status_code)
		

# if __name__ == '__main__':
#    self.main()
