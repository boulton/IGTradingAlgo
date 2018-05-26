import csv
import datetime
import logging
import time

from Algorithme import Indicateur
from Algorithme import Strategie

import pandas as pd

import Var

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

file_handler = logging.FileHandler('activity.log', 'w', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def main(Date1, Date2):
    # rest.Backtest().Pull(Date1, Date2)
    histdataconverter()
    pass


class histdataconverter(object):
    """docstring for  csv to  from histdata.com"""

    spread = 2  # pip sur audjpy je crois 0.01

    def __init__(self):
        arg = "DAT_ASCII_AUDJPY_M1_201808"
        tab = self.csvreader(arg, self.spread)
        # pprint(bro["snapshotTimeUTC"])
        self.pricediscovery(tab)
        df = self.toDataframe(tab)

    def csvreader(self, arg, spread):  # cleaned

        sample0 = {"snapshotTimeUTC": [], "openPrice": [], "highPrice": [], "lowPrice": [], "closePrice": [],
                   "lastTradedVolume": []}
        with open("Data/histdata/{}.csv".format(arg), 'r+', encoding='utf-8') as outfile:
            reader = csv.reader(outfile, delimiter=';')
            for row in reader:
                #  date brut : "20180101 170000"
                tl = ([int(row[0][:4]), int(row[0][4:6]), int(row[0][6:8]), int(row[0][9:11]), int(row[0][11:13]),
                       int(row[0][13:15])])
                dt = datetime.datetime(tl[0], tl[1], tl[2], tl[3], tl[4], tl[5])

                sample0["snapshotTimeUTC"].append(dt.strftime("%Y-%m-%d %H:%M:%S"))
                sample0["openPrice"].append(row[1])
                sample0["highPrice"].append(row[2])
                sample0["lowPrice"].append(row[3])
                sample0["closePrice"].append(row[4])
                sample0["lastTradedVolume"].append(0)
        return sample0

    def pricediscovery(self, sample):  # cleaned

        t = sample["snapshotTimeUTC"][0]
        # print(t)
        Var.lastDatetime = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")

        for x in range(1, len(sample["snapshotTimeUTC"]) - 1):
            # logger.info(sample["closePrice"][x - 1])
            bidbefore = float(sample['closePrice'][x - 1]) - (0.01 * self.spread / 2)
            askbefore = float(sample.get('closePrice')[x - 1]) + (0.01 * self.spread / 2)
            bid = float(sample.get('closePrice')[x]) - (0.01 * self.spread / 2)
            ask = float(sample.get('closePrice')[x]) + (0.01 * self.spread / 2)

            t = sample["snapshotTimeUTC"][x]
            temps = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")

            Indicateur.indicateur(temps=temps, Midpoint=((bid + ask) / 2))
            Strategie.strategie(BidAsk=[bid, ask], Price_0=[bidbefore, askbefore], temps=temps,
                                backtest=Var.backtest)

            # logger.debug(" b: "+str(bid)+" a: "+str(round(ask,4))+" t:"+str(temps.strftime("%Y-%m-%d %H:%M:%S"))+" b0: "+str(bidbefore)+" a0: "+str(askbefore))
            time.sleep(Var.debugTime)  # Pour debug

    def toDataframe(self, sample):
        """	sample : dict object
            Retrieve dict to a object named df finalized """
        df = {"Time": [],
              "bidClose": [],
              "askClose": [],
              "TradedVolume": [],
              "ema": [],
              "MA": []
              }
        logger.debug(len(sample["snapshotTimeUTC"]))
        for x in range(0, len(sample["snapshotTimeUTC"])):
            df["Time"].append(sample["snapshotTimeUTC"][x])
            df["bidClose"].append(float(sample["closePrice"][x]) - (0.01 * self.spread / 2))  # bid
            df["askClose"].append(float(sample["closePrice"][x]) + (0.01 * self.spread / 2))  # ask
            df["TradedVolume"].append(sample["lastTradedVolume"][x])

        # boucle migrant deal vers priceclose.csv
        for z in range(1, len(Var.cleanedDeal["OpenTime"])):
            name = "Trade" + str(z)
            df[name] = []
        Tradetotal = len(Var.cleanedDeal["OpenTime"])
        logger.debug("TradeTotal {}".format(Tradetotal))
        # pprint(df)
        for x in range(0, len(df["Time"])):
            a = datetime.datetime.strptime(df["Time"][x], "%Y-%m-%d %H:%M:%S")

            # logger.info("correctif sur tableau")
            for y1 in range(1, len(Var.cleanedDeal["OpenTime"])):
                # date d'ouverture du deal
                t1 = Var.cleanedDeal["OpenTime"][y1]
                t2 = Var.cleanedDeal["CloseTime"][y1]
                up = datetime.datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
                down = datetime.datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
                colname = "Trade" + str(y1)

                if a >= up and a <= down:
                    df[colname].append(df["bidClose"][x])
                else:
                    df[colname].append(0)

        Var.emaBacktest[0] = Var.emaBacktest[1]  # corrige le premier 0
        df["ema"] = Var.emaBacktest
        df["MA"] = Var.maBacktest
        # arrange la taille du csv :
        dimension = len(df["bidClose"])

        if len(df["MA"]) != dimension:
            for x in range(0, dimension - len(df["MA"])):
                df["MA"].append(0)

        if len(df["ema"]) != dimension:
            logger.debug("EMA mal formaté :{}".format(len(df["ema"])))
            for x in range(0, dimension - len(df["ema"])):
                df["ema"].append(0)

        for x in range(1, Tradetotal):
            colname = "Trade" + str(x)
            if len(df[colname]) != dimension:
                logger.debug("manque {} données".format(len(df[colname])))
                for x in range(0, dimension - len(df[colname])):
                    df[colname].append(0)
            else:
                # logger.debug("{} filled".format(colname))
                pass

        logger.debug("Time:{} close,{} ma:{} autre: {}".format(len(df["Time"]), len(df["Trade2"]), len(df["MA"]),
                                                               len(df["bidClose"])))
        logger.debug("arrangement {}".format(len(df["Trade1"])))

        # ---- Excel part ----
        df = pd.DataFrame(df)
        collist = ["Time", "TradedVolume", "askClose", "bidClose", "ema", "MA"]
        for x in range(1, len(list(df)) - len(collist) - 1):
            collist.append("Trade" + str(x))
        frame = df[collist]
        frame = frame.replace(0, "")

        writer = pd.ExcelWriter('Backtest/resume{}.xlsx'.format(df["Time"][0][:10]))
        frame.to_excel(writer, 'Overview')
        pd.DataFrame(Var.cleanedDeal).to_excel(writer, "Deals")
        # pd.DataFrame(Var.FakeDeal).to_csv("openposition.csv", index=False)
        # df.to_csv("Backtest/resume"+DayF+".csv", index=False)
        writer.save()

        return pd.DataFrame(df)


if __name__ == '__main__':
    main(Var.D1, Var.D2)
