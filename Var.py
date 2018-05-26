# -*- coding: utf-8 -*-

import datetime

from Broker import Id

# ----//Variable connexion //----
login = Id.login
password = Id.password
epic = "CS.D.AUDJPY.MINI.IP"
authentified = False
backtest = True
data = {}
managerFirstRun = True  # Streamer Bug  fix (relaunch) ?

# ----//Variable de Backtest//----
debugTime = 0
D1 = "2018-04-08"
D2 = "2018-04-09"
emaBacktest = [0, ]
maBacktest = []
marketId = ""
makeADeal = False

# ----//Variable Stratégie//----
limit = 120
stopLoss = -50
sens = ""
positionSimultanee = 3
algoInitialTime = (60 * 60)
ordrePassee = False
pauseOrdre = 60 * 10
startTime = datetime.datetime(int(D1[:4]),
                              int(D1[5:7]),
                              int(D1[8:10]),
                              23, 00, 00)

tempsaucross = startTime
minderniercross = 0

# ----//Variable indicateur et chrono //----
minute = 1
lastMinute = 0  # depécié
lastHeure = 0  # déprécié
lastDatetime = datetime.datetime

ema = {"Periode": "",
       "echelle": "",  # minutes, heure , seconde
       "valeurs": [0, ]
       }

prixpourma = []
ma = {"Periode": "",
      "echelle": "",
      "valeurs": []
      }

# ----// Interface/Affichage //----
price = {"Market": str(),
         "Date": str(),
         "Time": [""],
         "Bid": [""],
         "Ask": [""]
         }

# Deal en cours, validé sur plateforme
dealDone = {"Time": [],
            "Id": [],
            "entry": [],
            "sens": []
            }
# Deal Fake, test de strategie
fakeDeal = {"Time": [],
            "Id": [],
            "entry": [],
            "sens": []
            }

# Deal Cloturé
cleanedDeal = {"CloseTime": [""],
               "OpenTime": [""],
               "profit": [""],
               "entrylevel": [""],
               "closelevel": [""]
               }

# ----//Autre variables//----
PnL = 0
