# -*- coding: utf-8 -*-

"""
Minimale app template :
	ON/OFF streamer
	ON/OFF strategy
	SEND order + GET confirm
"""
import sys
from tkinter import *
import time
import rest
import stream
import Var


from datetime import datetime
import datetime as dt


class page1(object):
	"""docstring for app"""
	def __init__(self,master):
		self.app = master 
		self.app.title("ALGO-0.2MINI")	
		self.started = False
		
		self.epic= Var.epic
		self.timing="SECOND"

		ig = rest.ig()
		self.LStoken = ig.streamingToken(Var.data)
		self.lightstreamer_client = stream.LSClient(self.LStoken['addr'], "", self.LStoken['user'], self.LStoken['password'])
	
	def main(self):
		
		self.WidgetSetup()
		self.app.after(1, self.loop)
		self.app.mainloop()

	def loop(self):
		#create a infinite loop for text  
		self.textrefresh()
		self.app.update_idletasks()
		self.app.after(1, self.loop) 		
	
	def WidgetSetup(self):
		
		self.TextFrame = Text(self.app,height=20, width= 35,bg='light grey',undo= False)
		B1 = Button(self.app,text="Start",command=self.connection)
		B2 = Button(self.app,text="Stop", command=self.deconnection)
		
		self.TextFrame.pack()
		B1.pack(side=LEFT)
		B2.pack(side=LEFT)

	def textrefresh(self):
		space = "\n"
		EntryNum = len(Var.price["Time"])-1
		texte =(
			"Marché: "+self.epic,
			"Heure: "+Var.price["Time"][EntryNum],
			"Bid: "+Var.price["Bid"][EntryNum],
			"Ask: "+Var.price["Ask"][EntryNum],
			"Ema"+str(len(Var.ema["valeurs"]))+": "+str(Var.ema["valeurs"][len(Var.ema["valeurs"])-1]),
			"P/L: "+str(Var.PnL)+" pip \n",
			"FDEAL: "+str(Var.FakeDeal),
			"Clean: "+str(Var.CleanedDeal)
			)

		if self.started == True :
			self.TextFrame.delete(1.0,END)
			self.TextFrame.insert(END,space.join(texte))
		
	def connection(self):

		print(self.LStoken['addr'])
		
		Var.price["Date"] = str((datetime.now(dt.timezone.utc)).date()).replace('-','/')
		# a regrouper ces codes dans 1 fonctions communes avec streaming
		
		try:
			self.lightstreamer_client.connect()
		except :
			print("Unable to connect to Lightstreamer Server")
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
		
		# allowing text view
		self.started = True 

	def deconnection(self):

		# Cloture d'affichage
		self.started = False

		# Unsubscribing + Disconnecting
		self.lightstreamer_client.unsubscribe(self.sub_key)
		self.lightstreamer_client.disconnect()

		#Cloture Fenetre Tkinter 
		self.app.destroy()		

if __name__ == '__main__':
	root = Tk()
	page1(root).main()
