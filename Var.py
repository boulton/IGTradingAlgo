# -*- coding: utf-8 -*-

import id
import datetime

# ----//Variable connexion //----
login = id.login
password = id.password
epic = "CS.D.AUDJPY.MINI.IP"
authentified = False
backtest = True
data = {}
managerfirstrun = True  # Streamer Bug  fix (relaunch) ?

# ----//Variable de Backtest//----
DebugTime = 0
D1 = "2018-04-08"
D2 = "2018-04-09"
emaBacktest = [0, ]
mabacktest = []
marketId = ""
makeadeal = False

# ----//Variable Stratégie//----
Limit = 120
Stoploss = -50
sens = ""
PositionSimultanee = 3
AlgoInitialTime = (60 * 60)
ordrePassee = False
pauseordre = 60 * 10
starttime = datetime.datetime(int(D1[:4]),
                              int(D1[5:7]),
                              int(D1[8:10]),
                              23, 00, 00)

tempsaucross = starttime
minderniercross = 0


# ----//Variable indicateur et chrono //----
Minute = 1
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
DealDone = {"Time": [],
            "Id": [],
            "entry": [],
            "sens": []
            }
# Deal Fake, test de strategie
FakeDeal = {"Time": [],
            "Id": [],
            "entry": [],
            "sens": []
            }

# Deal Cloturé
CleanedDeal = {"CloseTime": [""],
               "OpenTime": [""],
               "profit": [""],
               "entrylevel": [""],
               "closelevel": [""]
               }

# ----//Autre variables//----
PnL = 0
