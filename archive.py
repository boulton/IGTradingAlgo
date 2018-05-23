class Sentiment(object):
	"""docstring for Sentiment"""
	def __init__(self):
		super(Sentiment, self).__init__()
		self.epic = "CS.D.EURUSD.MINI.IP"
		self.data = rest.ig().Auth(Var.login,Var.password)
		self.Thread1 = None
		self.dates = []	
		self.Position = {"Bull":[],"Bear":[]}
		self.fig = plt.figure()
		self.ax1 = self.fig.add_subplot(1,1,1)


	def follow(self):
		
		#THREAD
		while 1:
			Bullish, Bearish = strat.strat().ClientSentiment(self.epic)
			self.Position["Bull"].append(Bullish)
			self.Position["Bear"].append(Bearish)
			self.dates.append(datetime.now())
			print("Long: "+str(Bullish),"Short: "+str(Bearish))
			time.sleep(10)

	def animate(self):
		ax1.ylabel("Sentiment")
		ax1.xlabel("Temps")
		
		ax1.clear()
		ax1.plot_date(self.dates, self.Position["Bull"], 'r--', xdate=True, ydate=False)



	def main(self):

		self.Thread1 = threading.Thread(name="Sentiment", target=self.follow)
		self.Thread1.setDaemon(True)
		self.Thread1.start()
		time.sleep(3)
		
		
		ani = animation.FuncAnimation(self.fig, Sentiment.animate,interval=1000)
		plt.show()

		if sys.version_info[0] == 3 :
			input("Hit to Stop3")
			print("Fin")
			self.Thread1.join()
		else :
			raw_input("Hit to stop")
			self.Thread1.join()
		
		