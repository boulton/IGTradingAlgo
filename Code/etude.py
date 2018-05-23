# -*- coding: utf-8 -*-

from tkinter import *
import os
import Var

class indicateur(object):
	from collections import deque
	"""docstring for indic"""
	def __init__(self, arg):
		self.exp = list

	def ema(*prix):
		y = float 
		x = prix[1]
		t = prix[0]
		# n = nb de periode
		n = 14
		# poid alpha
		a = 2/(n+1)

		y = (a*x+(1-a)*t)
		
		print(y)

		return y

	def testEMA(l):
		j = list
		i 
		for i in len(l) :
			j.append(indicateur.ema(l[i],l[i+1]))
			i= i+1

		print(j)
		pass
	#self.exp.append(ema(x))

class Application(Frame):
	def say_hi(self):
		print("hi there, everyone!")

	def createWidgets(self):
		self.QUIT = Button(self)
		self.QUIT["text"] = "QUIT"
		self.QUIT["fg"]   = "red"
		self.QUIT["command"] =  self.quit

		self.QUIT.pack({"side": "left"})

		self.hi_there = Button(self)
		self.hi_there["text"] = "Hello",
		self.hi_there["command"] = self.say_hi

		self.hi_there.pack({"side": "left"})

		
	def __init__(self, master=None):
		Frame.__init__(self, master)
		
		self.pack()
		self.createWidgets()

class gui():
	"""docstring for gui"""

	def gui():
		
		root = Tk()
		app = Application(master=root)
		app.mainloop()
		root.destroy()

	if __name__== '__main__' :
		gui()

class term():

	def gui():
		root = Tk()

		termf = Frame(root, height=400, width=500)
		T = Text(root, height= 50,width=100)
		S = Scrollbar(root)
		S.pack(side=RIGHT, fill=Y)
		T.pack(side=LEFT, fill=Y)
		S.config(command=T.yview)
		T.config(yscrollcommand=S.set)
		
		
		termf.pack(fill=BOTH)
		wid = termf.winfo_id()
		T.insert(END,Var.price)
		#os.system('xterm -into %d -geometry 40x20 -sb &' % wid)
		root.mainloop()

	if __name__== '__main__' :
		gui()

class console(object):
	"""docstring for console"""
	def main(self):

		print("----Trading Bot----\n")
		reponse = input('Voulez vous entrer des params ? O/N :')
		if reponse == 'o' or reponse == 'O' :
			login = raw_input("login :")
			password = input('Mot de passe :')	
			pass
		else :
			login= Var.login
			password = Var.password

		data = rest.ig().Auth(login,password)
		p= Process(target=stream.streaming, args=(data,))
		
		p.start()
		p.join()
		
		# rest.ig().PnL(data)
	
if __name__== '__main__' :
		console.main()