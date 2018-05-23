# -*- coding: utf-8 -*-

import sys
import os
import strat
from tkinter import *
#from multiprocessing import Process
import time
import rest
import stream
import pprint 
#from memory_profiler import profile
import Var
from datetime import datetime
import matplotlib.dates as pld
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class appli(object):
	"""docstring for app"""
	fresh= True	
	data = rest.ig().Auth(Var.login,Var.password)
	epic="CS.D.EURUSD.MINI.IP"
	timing="SECOND"
	started = False
	firstrun = True
	LStoken = rest.ig().streamingToken(data)
	lightstreamer_client = stream.LSClient(LStoken['addr'],"",LStoken['user'],LStoken['password'])
	sub_key = int
	
	app = Tk()
	app.title("ALGO-0.1a")
	T = Text
	
	def WidgetSetup(self):

		F = Frame(self.app,height=100,width=100) 
		self.T = Text(self.app,height=20, width= 35,bg='light grey',undo= False)
		B1 = Button(self.app,text="start",command=self.conn)
		B2 = Button(self.app,text="Stop", command=self.deconnection)
		B3 = Button(self.app,text="Delta",command=self.Graph)

		self.T.pack()
		B1.pack(side=LEFT)
		B2.pack(side=LEFT)
		B3.pack(side=LEFT)


	def textrefresh(self):
		EntryNum = len(Var.price["Time"])-1
		a =("Marché: "+self.epic,
		"Heure: "+Var.price["Time"][EntryNum],
		"Bid: "+Var.price["Bid"][EntryNum],
		"Ask: "+Var.price["Ask"][EntryNum],
		"DeltaPip: "+str(round(float(Var.delta["Bid"][EntryNum-1]*100000),1)),
		"FDEAL: "+str(Var.FakeDeal),
		"Clean: "+str(Var.CleanedDeal))
		s = "\n"
		if self.started == True :
			self.T.delete(1.0,END)
			self.T.insert(END,s.join(a))
			#self.T.pack()
		pass
		
	def conn(self):
		
		print(self.LStoken['addr'])
		Var.price["Date"] = time.strftime('%x')
		try:
			self.lightstreamer_client.connect()
		except Exception as e:
			#print("Unable to connect to Lightstreamer Server")
			#print(traceback.format_exc())
			sys.exit(1)

		# Making a new Subscription in MERGE mode
		subscription = stream.Subscription(
			mode="MERGE",
			items=["CHART:"+self.epic+":"+self.timing],
			fields=["BID_CLOSE","OFR_CLOSE","UTM"],
			adapter="DEFAULT")
		
		# Adding the "on_item_update" function to Subscription
		subscription.addlistener(stream.on_item_update)

		# Registering the Subscription
		self.sub_key = self.lightstreamer_client.subscribe(subscription)
		self.started = True

	def deconnection(self):
		
		self.started = False
		# Unsubscribing from Lightstreamer by using the subscription key	
		self.lightstreamer_client.unsubscribe(self.sub_key)
		self.fresh = False
		
		stream.archive()
		# Disconnecting
		self.lightstreamer_client.disconnect()

		#Tkinter
		time.sleep(0.02)
		self.app.destroy()

	def Graph(self):
		if self.firstrun :
			Var.delta["Ask"].remove(0)
			self.firstrun = False
		else :
			print(Var.delta["Ask"])
			date = pld.date2num(Var.daties)
			plt.plot_date(date,Var.delta["Ask"],
				xdate=True,ydate= False ,ls="solid",animated=True)
			plt.ylabel("Prix")
			plt.xlabel("Temps")

			#strat.strat.delta(self.EntryNum)
			plt.show()
			pass

	def loopin(self):
		self.textrefresh()
		self.app.update_idletasks()
		self.app.update()
		self.app.after(1,self.loopin)
	
	def main(self):
		self.WidgetSetup()
		self.app.after(1,self.loopin)
		self.app.mainloop()
		#Mainloop	
		"""while self.fresh == True:
			self.textrefresh()
			self.app.update_idletasks()
			self.app.update()
		"""
	

if __name__ == '__main__':
	appli().main()
