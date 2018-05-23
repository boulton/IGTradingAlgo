# -*- coding: utf-8 -*-


import sys
import strat
import time
import rest
import pprint 
import Var
import threading
from datetime import datetime
import numpy as np
import matplotlib.dates as pld
import matplotlib.pyplot as plt
import matplotlib.animation as animation


epic = "CS.D.EURUSD.MINI.IP"
data = rest.ig().Auth(Var.login,Var.password)
Thread1 = None
Thread2 = None
dates = []	
Position = {"Bull":[],"Bear":[]}
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

class cafe(object):
	"""docstring for cafe"""
	def __init__(self):
		Thread1 = threading.Thread(name="Thread1", target=follow)
		Thread1.setDaemon(True)
		running = True
	def follow():
		#THREAD
		while self.running:
			Bullish, Bearish = strat.strat().ClientSentiment(epic)
			Position["Bull"].append(Bullish)
			Position["Bear"].append(Bearish)
			dates.append(datetime.now())
			#print("Long: "+str(Bullish),"Short: "+str(Bearish))
			time.sleep(10)

	def stop():
		self.running = False

def animate(i):
	ax1.ylabel("Sentiment")
	ax1.xlabel("Temps")
	
	ax1.clear()
	ax1.plot(dates, Position["Bull"], xdate=True, ydate=False)

def gui():
	pass
	



def main():
	
	cf = cafe()
	time.sleep(1)
	
	ani = animation.FuncAnimation(fig, animate,interval=1000)
	plt.show()

	input("Hit to Stop3")
	print("Fin")
	Thread1.join()
			
if __name__ == '__main__':
	main()
