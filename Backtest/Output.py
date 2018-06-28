import numpy
import datetime
import pandas as pd
import logging
import pprint
from xlsxwriter.workbook import Workbook


logger = logging.getLogger()

class excel:

    writer = None
    nomDuFichier = "essai"
    var1 =""
    var2=""
    df = {"Time": [],
              "bidClose": [],
              "askClose": [],
              "TradedVolume": [],
              var2: [],
              var1: []
              }

    def __init__(self, nom, sample, deal, strat):
        logger.debug("---EXCEL---")
        self.nomDuFichier = nom
        self.writer = pd.ExcelWriter('{}.xlsx'.format(self.nomDuFichier + deal["OpenTime"][0][:10]), engine='xlsxwriter')
        self.pnl(deal, strat)


    def priceColumns(self, sample, df):
        # logger.debug(len(sample["snapshotTimeUTC"]))
        for x in range(0, len(sample["snapshotTimeUTC"])):
            df["Time"].append(sample["snapshotTimeUTC"][x])
            df["bidClose"].append(float(sample["closePrice"][x]) - (self.spread / 2))  # bid
            df["askClose"].append(float(sample["closePrice"][x]) + (self.spread / 2))  # ask
            df["TradedVolume"].append(sample["lastTradedVolume"][x])

        return df

    def tradeColumns(self, sanmple, df):
        # All trade column
        for z in range(1, len(self.deal["OpenTime"])):
            name = "Trade" + str(z)
            df[name] = []
        Tradetotal = len(self.deal["OpenTime"])
        logger.debug("TradeTotal {}".format(Tradetotal))

        for x in range(0, len(df["Time"])):
            a = datetime.datetime.strptime(df["Time"][x], "%Y-%m-%d %H:%M:%S")

            # logger.info("correctif sur tableau")
            for y1 in range(1, len(self.deal["OpenTime"])):
                # date d'ouverture du self.deal
                t1 = self.deal["OpenTime"][y1]
                t2 = self.deal["CloseTime"][y1]
                up = datetime.datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
                down = datetime.datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
                colname = "Trade" + str(y1)

                if a >= up and a <= down:
                    df[colname].append(df["bidClose"][x])
                else:
                    df[colname].append(0)
        return df

    def colAdjust(self, df):
        # arrange la taille du csv :
        dimension = len(df["bidClose"])
        tradeTotal = len(self.deal["OpenTime"])

        if len(df["MA"]) != dimension:
            for x in range(0, dimension - len(df["MA"])):
                df["MA"].append(0)

        if len(df["ema"]) != dimension:
            logger.debug("EMA mal formaté :{}".format(len(df["ema"])))
            for x in range(0, dimension - len(df["ema"])):
                df["ema"].append(0)

        for x in range(1, tradeTotal):
            colname = "Trade" + str(x)
            if len(df[colname]) != dimension:
                logger.debug("manque {} données".format(len(df[colname])))
                for x in range(0, dimension - len(df[colname])):
                    df[colname].append(0)
            else:
                # logger.debug("{} filled".format(colname))
                pass
        logger.debug("Time:{} close,{} ma:{} autre: {}"
                     .format(len(df["Time"]), len(df["Trade1"]), len(df["MA"]), len(df["bidClose"])))
        logger.debug("arrangement: {}".format(len(df["Trade2"])))
        return df

    def simpleTradeResultExcel(self, df):

        # arrange la taille du csv :
        dimension = len(df["bidClose"])
        tradeTotal = len(self.deal["OpenTime"])

        if len(df["MA"]) != dimension:
            for x in range(0, dimension - len(df["MA"])):
                df["MA"].append(0)

        if len(df["ema"]) != dimension:
            logger.debug("EMA mal formaté :{}".format(len(df["ema"])))
            for x in range(0, dimension - len(df["ema"])):
                df["ema"].append(0)

        df = pd.DataFrame(df)
        writer = pd.ExcelWriter('resumeMois{}.xlsx'.format(df["Time"][0][:10]))
        pd.DataFrame(self.deal).to_excel(writer, "self.Deals")
        writer.save()

    def pnl(self, deal:dict, strat):
        # DONE
        deal['profit']= (numpy.asarray(deal['profit']) * strat.pipMultiplier)
        deal['sumPnl'] =  [ (deal['profit'][0]), ]
        dimension = len(deal['profit'])
        for i in range(1, dimension):
            deal['sumPnl'].append(float(deal['sumPnl'][i-1]) + float(deal['profit'][i]))


        pd.DataFrame(deal).to_excel(self.writer, sheet_name="Pnl", columns=["CloseTime", "OpenTime", "profit", "sumPnl",
                                                     "entrylevel", "closelevel", "stop", 'limit'])

        workbook = self.writer.book
        worksheet = self.writer.sheets['Pnl']
        logger.debug(' ')

        line_chart = workbook.add_chart({'type': 'line'})
        line_chart.add_series({
            'name': '=Pnl!E1',
            'categories': '=Pnl!A3:A{}'.format(dimension),
            'values': '=Pnl!E3:E{}'.format(dimension),
            'line': {'color': '#da7c30'},
        })

        column_chart = workbook.add_chart({'type': 'column'})
        column_chart.add_series({
            'name': '=Pnl!D1',
            'categories': '=Pnl!A3:A{}'.format(dimension),
            'values': '=Pnl!D3:D{}'.format(dimension),
            'fill':   {'color': '#7293cb'},
            'border': {'color': '#7293cb'},
            'y2_axis': True,
        })

        line_chart.combine(column_chart)
        line_chart.set_title({'name': 'Profit/Loss'})
        line_chart.set_x_axis({'name': 'number of trade'})
        line_chart.set_y_axis({'name': 'pip profit'})
        column_chart.set_y2_axis({'name': 'global pip profit'})

        # Insert the chart into the worksheet
        worksheet.insert_chart('E2', line_chart)

        workbook.close()

    def overview(self, sample, strat, df, var1, var2):

        # --- sheet formatting ---
        df = self.priceColumns(sample, df)
        df = self.tradeColumns(sample, df)
        df = self.colAdjust(df)

        a = numpy.array(strat.thiel_sen['mid']['medslope']).astype(float)
        b = numpy.array(strat.thiel_sen['mid']['medintercept']).astype(float)
        x = numpy.array(strat.thiel_sen['x']).astype(float)
        pprint.pprint(str(a.size) + " " + str(x.size) + " " + str(b.size))
        y = a * x + b
        df[var2] = y.tolist()
        df[var1] = []

        # ---- Excel part ----
        df = pd.DataFrame(df)
        writer = pd.ExcelWriter('{}.xlsx'.format(self.nomDuFichier+df["Time"][0][:10]))

        collist = ["Time", "TradedVolume", "askClose", "bidClose", "ema", self.var1]
        for x in range(1, len(list(df)) - len(collist) - 1):
            collist.append("Trade" + str(x))
        frame = df[collist]
        pprint.pprint(frame)
        frame = frame.replace(0, "")
        frame.to_excel(writer, 'Overview')
        pd.DataFrame(self.deal).to_excel(writer, "self.Deals")

        # pd.DataFrame(Var.Fakeself.Deal).to_csv("openposition.csv", index=False)
        # df.to_csv("Backtest/resume"+DayF+".csv", index=False)
        writer.save()

