# -*- coding: utf-8 -*-

"""
Minimale app template :
	ON/OFF streamer
	ON/OFF strategy
	SEND order + GET confirm
"""
import datetime as dt
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from tkinter import *

import Var
from Broker import Rest, Stream
from Backtest import Backtest

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s :: %(asctime)s :: %(name)s :: %(message)s')

file_handler = RotatingFileHandler('activity.log', 'a', 3000, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


class Page1(object):
    """docstring for app"""

    def __init__(self, master):
        self.app = master
        self.app.title("ALGO-0.2MINI")
        self.started = False

        self.epic = Var.epic
        self.timing = "SECOND"

        ig = Rest.ig()
        self.LStoken = ig.streamingToken(Var.data)
        self.lightstreamer_client = Stream.LSClient(self.LStoken['addr'], "", self.LStoken['user'],
                                                    self.LStoken['password'])

    def main(self):

        self.widgetSetup()
        self.app.after(1, self.loop)
        self.app.mainloop()

    def loop(self):
        # create a infinite loop for text
        self.textRefresh()
        self.app.update_idletasks()
        self.app.after(1, self.loop)

    def widgetSetup(self):

        self.TextFrame = Text(self.app, height=20, width=35, bg='light grey', undo=False)
        B1 = Button(self.app, text="Start", command=self.connection)
        B2 = Button(self.app, text="Stop", command=self.deconnection)

        self.TextFrame.pack()
        B1.pack(side=LEFT)
        B2.pack(side=LEFT)

    def textRefresh(self):
        space = "\n"
        EntryNum = len(Var.price["Time"]) - 1
        texte = (
            "Marché: " + self.epic,
            "Temps: " + str(Var.price["Time"][EntryNum]),
            "Bid: " + Var.price["Bid"][EntryNum],
            "Ask: " + Var.price["Ask"][EntryNum],
            "Ema " + str(len(Var.ema["valeurs"])) + ": " + str(Var.ema["valeurs"][len(Var.ema["valeurs"]) - 1]),
            "P/L: " + str(Var.PnL) + " pip \n",
            "FDEAL: " + str(Var.fakeDeal),
            "Clean: " + str(Var.cleanedDeal)
        )

        if self.started == True:
            self.TextFrame.delete(1.0, END)
            self.TextFrame.insert(END, space.join(texte))

    def connection(self) :

        logger.info(self.LStoken['addr'])

        Var.price["Date"] = str((datetime.now(dt.timezone.utc)).date()).replace('-', '/')
        # TODO regrouper ces codes dans 1 fonctions communes avec streaming

        try:
            self.lightstreamer_client.connect()
        except Exception as e:
            logger.error("Unable to connect to Lightstreamer Server")
            logger.error(e)
            exit(1)

        # Making a new Subscription in MERGE mode
        subscription = Stream.Subscription(
            mode="MERGE",
            items=["CHART:" + self.epic + ":" + self.timing],
            fields=["BID_CLOSE", "OFR_CLOSE", "UTM"],
            adapter="DEFAULT")

        # Ajoute le "on_item_update" function a Subscription
        subscription.addlistener(Stream.on_item_update)

        # Enregistre lq Subscription
        self.sub_key = self.lightstreamer_client.subscribe(subscription)

        # autorise l'affichage
        self.started = True

    def deconnection(self):

        # Cloture d'affichage
        self.started = False

        # Unsubscribing + Disconnecting
        try :
            self.lightstreamer_client.unsubscribe(self.sub_key)
            self.lightstreamer_client.disconnect()
            self.app.destroy()
        except:
            # Cloture Fenetre Tkinter
            self.app.destroy()

class Console(): #TODO a perfectionné

    def __init__(self):

        self.started = False
        self.epic = Var.epic
        self.timing = "SECOND"


        print("----Trading Console----")
        ep =input("On change l'épic ?")
        if(ep == "y" or ep == "Y"):
            epic = input("L'épic : ")
            self.epic = epic

        rep = input("Start Lightstream ?")

        if(rep == "y" or rep == "yes" or rep =="Y"):
            self.connection()

        logger.info("END")

    def connection(self):
        ig = Rest.ig()
        self.LStoken = ig.streamingToken(Var.data)
        self.lightstreamer_client = Stream.LSClient(self.LStoken['addr'], "", self.LStoken['user'],
                                                    self.LStoken['password'])
        logger.info(self.LStoken['addr'])

        Var.price["Date"] = str((datetime.now(dt.timezone.utc)).date()).replace('-', '/')
        # TODO regrouper ces codes dans 1 fonctions communes avec streaming

        try:
            self.lightstreamer_client.connect()
        except Exception as e:
            logger.error("Unable to connect to Lightstreamer Server")
            logger.error(e)
            exit(1)

        # Making a new Subscription in MERGE mode
        subscription = Stream.Subscription(
            mode="MERGE",
            items=["CHART:" + self.epic + ":" + self.timing],
            fields=["BID_CLOSE", "OFR_CLOSE", "UTM"],
            adapter="DEFAULT")

        # Ajoute le "on_item_update" function a Subscription
        subscription.addlistener(Stream.on_item_update)

        # Enregistre lq Subscription
        self.sub_key = self.lightstreamer_client.subscribe(subscription)

        # autorise l'affichage
        self.started = True

if __name__ == '__main__':

    # Backtest.main(Var.D1, Var.D2)
    root = Tk()
    Page1(root).main()

    # Console()