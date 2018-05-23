# -*- coding: utf-8 -*-

from datetime import datetime
import Var

class indicateur(object):
	"""docstring for indicateur"""
	def __init__(self, indice):
		self.i = indice
		self.MinUpgrade = False

		self.chrono()
		self.delta()
		self.ema(14)
		

	def delta(self):
		if self.i == 1 :
			#print("delta firstrun")
			pass
		else:
			# i : periode 
			i = self.i
			
			# pip de variation/ seconde
			#Var.daties.append(self.DateConverter(i))
			#Var.deltaaffiche.append(round((float(Var.price["Ask"][i]) - float(Var.price["Ask"][i-1]))*100000,2))

			if self.MinUpgrade :
				Var.delta["Bid"].append(round((float(Var.price["Bid"][i]) - float(Var.price["Bid"][Var.lastMinIndice[0]]))*100000,2))
				Var.delta["Ask"].append(round((float(Var.price["Ask"][i]) - float(Var.price["Ask"][Var.lastMinIndice[0]]))*100000,2))
				Var.delta["Time"].append(str(self.DateConverter(i) - self.DateConverter(Var.lastMinIndice[0])))
				#Var.daties.append(datetime.strptime(Var.price["Time"][i],'%H:%M:%S'))
				Var.daties.append(self.DateConverter(i))
				Var.deltaaffiche.append(Var.delta["Bid"][len(Var.delta["Bid"])-1])

				#print("delta min: "+str(float(Var.price["Bid"][i]))+" last price :"+str(float(Var.price["Bid"][Var.lastMinIndice[0]])))
				#print("delta= ",(round((float(Var.price["Bid"][i]) - float(Var.price["Bid"][Var.lastMinIndice[0]]))*100000,2)))
			else :
				pass
		
	def ema(self, periode) :
		#
		decalage = 1
		if self.i == 1 :
			#print("ema firstrun")
			# add 5 value pr le decalage
			for x in range(0,(decalage-0)) :
				Var.ema["valeurs"][x] = float(Var.price["Ask"][self.i])
				
		else:	
			#print("Minutes:",len(Var.ema["valeurs"]))
			y = float 
			# x moyenne bid/ask
			x = (float(Var.price["Bid"][self.i])+float(Var.price["Bid"][self.i]))/2
			t = float(Var.ema["valeurs"][len(Var.ema["valeurs"])-1])
			# n = nb de periode
			n = int(periode)
			# poid alpha
			a = 2/(n+1)
			y = (a*x+(1-a)*t)
			
			Var.emachart.append(round(y,5))
			Var.emadate.append(self.DateConverter(self.i))
			
			#---erreur date avec timezone different d'utc
			#print(Var.emadate[len(Var.emadate)-1])
			#print(Var.datePrix[len(Var.emadate)-1])

			if self.MinUpgrade :
				#print((self.DateConverter(self.i)-self.DateConverter(0)))
				#print (Var.Minute)
				Var.ema["periode"] = periode
				Var.ema["valeurs"].append(y)
				
				print("Ask: ",Var.price["Ask"][self.i],"\n ","Ema: ", Var.ema["valeurs"][len(Var.ema["valeurs"])-1])

				self.MinUpgrade = False
				
			else:
				pass

	def DateConverter(self,i):
		# string date to datetime format
		if i == 0:
			DateComplete = Var.price["Date"]+"/"+Var.price["Time"][i+1] 
			d = datetime.strptime(DateComplete, '%Y/%m/%d/%H:%M:%S')
			return d

		else:
			DateComplete = Var.price["Date"]+"/"+Var.price["Time"][i] 
			d = datetime.strptime(DateComplete, '%Y/%m/%d/%H:%M:%S')
			return d

	def chrono(self):
		t1 = int((Var.price["Time"][self.i])[3:5])
		#print (t1, Var.lastMinute)
		delta = t1-Var.lastMinute

		if delta >= 1 or delta == -59:
			#print("min:",Var.Minute)
			Var.Minute= Var.Minute+1
			Var.lastMinute = t1
			Var.lastMinIndice.append(self.i)
			if len(Var.lastMinIndice)>2 :
				Var.lastMinIndice.pop(0)
			self.MinUpgrade = True
			#Var.prix.append(float(Var.price["Ask"][self.i]))
		else:
			pass

