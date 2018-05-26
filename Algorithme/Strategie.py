# -*- coding: utf-8 -*-

import datetime
import logging
import time

import Var
from Broker import Rest

logger = logging.getLogger()


class strategie():
    """	regroupe les strategie d'achat/vente
                                                                    temps = YYYY-MM-JJTHH:MM:SS(datetime)
    """

    def __init__(self, BidAsk, temps, Price_0, backtest):

        self.pauseordre(temps, backtest)
        self.maEmaCross1(BidAsk, Price_0, backtest, temps)

    # self.balai(BidAsk, Price_0, temps, Backtest)

    # print("strategie failed")

    def pauseordre(self, temps, backtest):
        """ Effectue une pause apres un ordre passé
        """
        if Var.ordrePassee:
            if not backtest:
                logger.info("Ordre passé,\n 2Min de pause")
                time.sleep(Var.pauseOrdre)
                Var.ordrePassee = False
            else:
                if len(Var.fakeDeal["Time"]) == 0:
                    # cas : cloture de toute position avant fin de délai
                    logger.debug("Cas ou y a plus de deal")
                    Var.ordrePassee = False
                else:
                    tnow = temps
                    DealT = Var.fakeDeal["Time"][len(Var.fakeDeal["Time"]) - 1]
                    tdeal = datetime.datetime(int(DealT[:4]), int(DealT[5:7]), int(
                        DealT[8:10]), int(DealT[11:13]), int(DealT[14:16]), int(DealT[17:19]))
                    if (tnow - tdeal) >= datetime.timedelta(0, Var.pauseOrdre):
                        # print(int((tnow-tdeal).seconds/60)," minutes depuis dernier trade")
                        Var.ordrePassee = False
        pass

    def simpleEmaCross0(self, BidAsk, Price_0, backtest, tempo):
        # Brouillon, ne prend pas en compte des limite
        # "n'utilise" pas le balai
        bid, ask = BidAsk
        bid0, ask0 = Price_0  # Prix précedent

        taille = len(Var.ema["valeurs"]) - 1  # <- delai de 5 periode
        EMAdecalee = float(Var.ema["valeurs"][taille])

        # Crosses condition
        c11 = float(ask0) <= EMAdecalee
        c1 = float(ask) > EMAdecalee
        c21 = float(bid0) >= EMAdecalee
        c2 = float(bid) < EMAdecalee

        initparam = (tempo - Var.startTime).seconds > Var.algoInitialTime
        condition1 = initparam and c1 and c11
        condition2 = initparam and c2 and c21

        if condition1:
            sens = "BUY"
            Var.sens = sens
            Var.makeADeal = True
            # print(sens + " \n", str(ask) + "\n EMA: " + str(Var.ema["valeurs"][taille]))
            # self.event(Backtest, sens, tempo, BidAsk, Price_0)
            Var.tempsaucross = tempo

        elif condition2:
            sens = "SELL"
            Var.sens = sens
            Var.makeADeal = True
            # print(sens + " \n", "prix: " + str(bid) + "\n EMA: " + str(Var.ema["valeurs"][taille]))
            # self.event(Backtest, sens, tempo, BidAsk, Price_0)
            Var.tempsaucross = tempo
        else:
            # Garde fou:
            autre = self.stopAndLimit(BidAsk, tempo, backtest, [])
            if backtest:
                Rest.backtest().closeFakeOrders(autre, BidAsk, tempo)
            else:
                # BUGGY
                Rest.ig().closeOrders(dealId=autre[0], orderType="MARKET")
            if Var.makeADeal and Var.minderniercross >= 2:
                Var.makeADeal = False
                self.event(backtest, Var.sens, tempo, BidAsk, Price_0)

        # -----------NEW-------
        Var.minderniercross = int((tempo - Var.tempsaucross).seconds / 60)

    # print(Var.minderniercross)

    def maEmaCross1(self, BidAsk, Price_0, backtest, tempo):
        """ Croisement entre MovingAvg 14 et EMA 500
        """
        bid, ask = BidAsk
        bid0, ask0 = Price_0  # Prix précedent
        MovingAvg = Var.ma["valeurs"][len(Var.ma["valeurs"]) - 1]
        MovingAvg0 = Var.ma["valeurs"][len(Var.ma["valeurs"]) - 2]

        taille = len(Var.ema["valeurs"]) - 1  # <- delai de 5 periode
        EMAdecalee = float(Var.ema["valeurs"][taille])

        # Crosses condition
        c11 = float(MovingAvg0) <= EMAdecalee
        c1 = float(MovingAvg) > EMAdecalee
        c21 = float(MovingAvg0) >= EMAdecalee
        c2 = float(MovingAvg) < EMAdecalee

        initparam = (tempo - Var.startTime).seconds > Var.algoInitialTime
        condition1 = initparam and c1 and c11
        condition2 = initparam and c2 and c21

        if condition1:
            sens = "BUY"
            Var.sens = sens
            Var.makeADeal = True
            # print(sens + " \n", str(ask) + "\n EMA: " + str(Var.ema["valeurs"][taille]))
            # self.event(Backtest, sens, tempo, BidAsk, Price_0)
            Var.tempsaucross = tempo

        elif condition2:
            sens = "SELL"
            Var.sens = sens
            Var.makeADeal = True
            # print(sens + " \n", "prix: " + str(bid) + "\n EMA: " + str(Var.ema["valeurs"][taille]))
            # self.event(Backtest, sens, tempo, BidAsk, Price_0)
            Var.tempsaucross = tempo
        else:
            # Garde fou:
            autre = self.stopAndLimit(BidAsk, tempo, backtest, [])
            if backtest:
                Rest.backtest().closeFakeOrders(autre, BidAsk, tempo)
            else:
                # BUGGY
                Rest.ig().closeOrders(dealId=autre[0], orderType="MARKET")
            if Var.makeADeal and Var.minderniercross >= 0:
                Var.makeADeal = False
                self.event(backtest, Var.sens, tempo, BidAsk, Price_0)

        # -----------NEW-------
        Var.minderniercross = int((tempo - Var.tempsaucross).seconds / 60)

    # print(Var.minderniercross)

    def simpleEmaCross(self, BidAsk, Price_0, backtest, tempo):
        """ Croisement PRIX et EMA a la periode j """
        bid, ask = BidAsk
        bid0, ask0 = Price_0  # Prix précedent a
        taille = len(Var.ema["valeurs"]) - 1  # <- delai de 5 periode
        EMAdecalee = Var.ema["valeurs"][taille]

        # Crosses condition
        c11 = float(ask0) <= EMAdecalee
        c1 = float(ask) > EMAdecalee and c11

        c21 = float(bid0) >= EMAdecalee
        c2 = float(bid) < EMAdecalee and c21

        sparam = (len(Var.fakeDeal["Id"])) < Var.positionSimultanee

        initparam = (tempo - Var.startTime).seconds > Var.algoInitialTime
        cparam = sparam and initparam
        condition1 = cparam and c1
        condition2 = cparam and c2

        if condition1:
            sens = "BUY"
            print(sens + " \n", "prix: " + str(ask) +
                  "\n EMA: " + str(Var.ema["valeurs"][taille]))

            if backtest is False:
                Rest.ig().createOrders(orderType="MARKET", direction=sens,
                                       stopDistance=Var.stopLoss, limitDistance=self.limit, epic=Var.epic)
            # rest.ig() crée une nouvelle instance -> overload de connection
            else:
                Rest.backtest().fakeOrders(BidAsk, sens, tempo)
            Var.ordrePassee = True

        elif condition2:
            sens = "SELL"
            print(sens + " \n", "prix: " + str(bid) +
                  "\n EMA: " + str(Var.ema["valeurs"][taille]))

            if backtest is False:
                Rest.ig().createOrders(orderType="MARKET", direction=sens,
                                       limitDistance=self.limit, stopDistance=self.stoploss, epic=Var.epic)
            # redondance rest.ig()
            else:
                Rest.backtest().fakeOrders(BidAsk=BidAsk, sens=sens, temps=tempo)

            Var.ordrePassee = True

        else:
            pass

    def event(self, backtest, sens, tempo, BidAsk, Price_0):
        """ Handle maxposition de Var et 1 seul sens de trade
        """
        maxposition = (len(Var.fakeDeal["Id"])) >= Var.positionSimultanee
        vague1 = self.ordresInv(BidAsk, Price_0, tempo, sens, backtest)
        suppr = self.stopAndLimit(BidAsk, tempo, backtest, vague1)
        if backtest:
            Rest.backtest().closeFakeOrders(suppr, BidAsk, tempo)
            if not maxposition:
                print(sens)
                Rest.backtest().fakeOrders(BidAsk, sens, tempo)
        else:
            # BUGGY
            Rest.ig().closeOrders(dealId=suppr[0], orderType="MARKET")
            if not maxposition:
                Rest.ig().createOrders(
                    orderType="MARKET",
                    direction=sens,
                    stopDistance=Var.stopLoss,
                    limitDistance=Var.limit,
                    epic=Var.epic)
            # rest.ig() crée une nouvelle instance -> overload de connection
        Var.ordrePassee = True

    def ordresInv(self, BidAsk, Price_0, temps, sens, backtest):
        """	groupe les INDEX des Deal inversé au sens du trade"""
        suppresion = []
        if backtest:
            dico = Var.fakeDeal
        else:
            dico = Var.dealDone
        for x in range(0, (len(dico["Id"]))):
            dealsens = dico["sens"][x]
            if dealsens != sens:
                # print("profit@close: ",self.profit(dico, x, BidAsk))
                suppresion.append(x)

        return suppresion

    def balai(self, BidAsk, Price_0, temps, backtest):
        """ 23/03/2018
                                        non testé
                                        cloture les deal existant
        """
        DealACloturer = []

        bid, ask = BidAsk
        bid0, ask0 = Price_0  # BidAsk précedent

        for x in range(0, (len(Var.fakeDeal["Id"]))):
            # x : index de l'id
            # condition de cross d'ema
            p = 0
            taille = len(Var.ema["valeurs"]) - 1
            # <- delai de 5 periode
            c11 = float(ask0) <= Var.ema["valeurs"][taille]
            c1 = float(ask) > Var.ema["valeurs"][taille] and c11

            c21 = float(bid0) >= Var.ema["valeurs"][taille]
            c2 = float(bid) < Var.ema["valeurs"][taille] and c21

            # Id existant
            prixentree = float(Var.fakeDeal["entry"][x])

            if Var.fakeDeal["sens"][x] == "SELL":
                prixactuel = float(ask)
                p = round((prixentree - prixactuel) * 10000, 2)
            # x100 caren pip
            # A modif selon l'instrument et son levier
            elif Var.fakeDeal["sens"][x] == "BUY":
                prixactuel = float(bid)
                p = round((prixactuel - prixentree) * 10000, 2)
            # x100 caren pip

            else:
                print("erreur: ", Var.fakeDeal["sens"][x])
                break

            # print("profit :", p)
            # cloture si stoploss/limit ou emacross
            if p > Var.limit or p < Var.stopLoss:
                print("stoploss")
                DealACloturer.append(x)  # x = index dans dict
            elif c1 and Var.fakeDeal["sens"][x] == "SELL":
                DealACloturer.append(x)
                print("Croisement vendeur invalidé")
            elif c2 and Var.fakeDeal["sens"][x] == "BUY":
                DealACloturer.append(x)
                print("Croisement acheteur invalidé")

        if backtest is False:
            # NOT WORKING , DealId bad behavior
            Rest.ig().closeOrders(dealId=DealACloturer[0], orderType="MARKET")

        else:
            Rest.backtest().closeFakeOrders(DealACloturer, BidAsk, temps)

    def clientSentiment(self, BidAsk, sens, temps, epic):
        """Strategie autour des Positions des clients IG """

        position = Rest.ig().igClientPositions(epic)
        Bullish = position["Bull"]
        Bearish = position["Bear"]

        c1 = Bullish > 89
        if c1:
            Id = Rest.fakeOrders(BidAsk, "sell", temps)
            return Id
        else:
            pass

    # self.archiveSentiment(position, epic)

    def profit(self, dico, i, BidAsk):
        profit = 0
        bid, ask = BidAsk
        sens = dico["sens"][i]
        prixentree = float(dico["entry"][i])
        # print("profit ;",dico["Id"][i])

        if sens == "SELL":
            prixactuel = float(ask)
            profit = round((prixentree - prixactuel) * 100, 2)
        else:
            prixactuel = float(bid)
            profit = round((prixactuel - prixentree) * 100, 2)
        # profit x100 caren pip
        # A modif selon l'instrument et son levier
        # print(profit)
        return profit

    def stopAndLimit(self, BidAsk, temps, backtest, suppresion):
        if backtest:
            dico = Var.fakeDeal
        else:
            dico = Var.dealDone

        for x in range(0, len(dico["Id"])):
            # DealT = dico["Time"][x]
            # tdeal = datetime.datetime(int(DealT[:4]), int(DealT[5:7]), int(DealT[8:10]), int(DealT[11:13]), int(DealT[14:16]), int(DealT[17:19]))
            # nighclose = datetime.datetime(int(DealT[:4]), int(DealT[5:7]), int(DealT[8:10]), 22, 50, 0)
            p = self.profit(dico, x, BidAsk)

            if p < Var.stopLoss:
                logger.info("stoploss")
                suppresion.append(x)  # x = index dans dict
            elif p > Var.limit:
                logger.info("Limit")
                suppresion.append(x)
            # elif temps > nighclose:
            # suppresion.append(x)
            else:
                pass
        return suppresion

    def closeAll(self, BidAsk, temps, backtest):
        """	Ferme tout les ordres
        """
        if backtest:
            dico = Var.fakeDeal
        else:
            dico = Var.dealDone
        toute = []
        for x in range(0, len(dico["entry"])):
            toute.append(x)

        if backtest:
            Rest.backtest().closeFakeOrders(toute, BidAsk, temps)
        else:
            Rest.ig().closeOrders(dealId=toute[0], orderType="MARKET")
