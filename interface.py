# -*- coding: utf-8 -*-

import sys
from tkinter import *
import time
import rest
import stream
import Var
from datetime import datetime
import datetime as dt
#import numpy as np

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.dates as pld
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class page1(object):
	"""docstring for app"""
	def __init__(self,master):
		self.fresh= True
		self.data = rest.ig().Auth(Var.login,Var.password)
		self.epic="CS.D.EURUSD.MINI.IP"
		self.timing="SECOND"
		self.started = False
		self.firstrun = True
		self.LStoken = rest.ig().streamingToken(self.data)
		self.lightstreamer_client = stream.LSClient(self.LStoken['addr'],"",self.LStoken['user'],self.LStoken['password'])
		self.sub_key = int
		self.app = master 
		self.Windows2 = False

		self.app.title("ALGO-0.1a")
		self.T = Text
	
	
	def new_window(self):
		self.newWindow = Toplevel(self.app)
		self.app2 = page2(self.newWindow)
		

	def WidgetSetup(self):

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
		#"DeltaPip: "+str(round(float(Var.delta["Bid"][EntryNum-1]),1)),
		"P/L: "+str(Var.PnL)+" pip \n",
		"FDEAL: "+str(Var.FakeDeal),
		"Clean: "+str(Var.CleanedDeal))
		s = "\n"
		if self.started == True :
			self.T.delete(1.0,END)
			self.T.insert(END,s.join(a))
			#self.T.pack()
		
		
	def conn(self):
		
		print(self.LStoken['addr'])
		
		Var.price["Date"] = str((datetime.now(dt.timezone.utc)).date()).replace('-','/')
		# a regrouper ces codes dans 1 fonctions communes avec streaming
		try:
			self.lightstreamer_client.connect()
		except :
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
			Var.delta["Ask"].pop(0)
			self.firstrun = False
			self.Graph()
		else :
			#print(Var.delta["Ask"])
			self.graphed = True
			self.new_window()
			#ani = animation.FuncAnimation(self.fig,self.redraw,interval=10)
			#plt.show()
			

	def loopin(self):
		self.textrefresh()
		
		self.app.update_idletasks()
		self.app.update()
		if self.Windows2:
			self.app2.after(1,app2.loop)
		else:
			pass
		self.app.after(1,self.loopin)
	

	def main(self):
		
		# Popup login
		#self.newwindows = Toplevel(self.app) 
		#self.popup = login(self.newwindows)

		self.WidgetSetup()
		self.app.after(1,self.loopin)
		self.app.mainloop()
		#Mainloop	
		"""while self.fresh == True:
			self.textrefresh()
			self.app.update_idletasks()
			self.app.update()
		"""

class login(object):
	"""startup(popup) initialisant login/pass/market/backtest Value
		Under COnstruction"""
	def __init__(self, master):
		self.app = master 
		self.app.title("LOGIN :")

	def main(self):
		self.app.mainloop()
		

class page2(object):
	"""docstring for page2"""
	def __init__(self, master):
		self.app = master
		self.app.title("Graphique")
		self.frame = Frame(self.app)
		self.quitButton = Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
		self.fig = plt.figure(1)
		self.ax1 = self.fig.add_subplot(2,1,1)
		self.ax2 = self.fig.add_subplot(2,1,2)
		self.canvas = FigureCanvasTkAgg(self.fig, self.app)		

		self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=False)
		self.quitButton.pack()
		self.frame.pack()
		self.main()

	def loop(self):

		self.ax1.clear()
		self.ax2.clear()
		self.poppin()

		self.ax1.plot(Var.datePrix, Var.prix , 'b')
		self.ax1.plot(Var.emadate, Var.emachart, "r--")
		self.ax2.plot(Var.daties, Var.deltaaffiche,'g')
		#plt.ylabel("Prix")
		#plt.xlabel("Temps")
		self.canvas.show()
		self.app.update_idletasks()
		self.app.update()
		self.app.after(1,self.loop)
	
	def poppin(self):
		if len(Var.emachart) > Var.dim_affichage:
			Var.emachart.pop(0)
			Var.emadate.pop(0)	
			Var.prix.pop(0)
			Var.datePrix.pop(0)
		elif len(Var.lastMinIndice) > (Var.dim_affichage/60) :
			Var.daties.pop(0)
			Var.deltaaffiche.pop(0)
		
	def main(self):
		#self.prix.pop(0)
		self.app.after(1,self.loop)
		self.app.mainloop()

	def close_windows(self):
		plt.close(self.fig)
		self.app.destroy()	
					

if __name__ == '__main__':
	root = Tk()
	page1(root).main()
