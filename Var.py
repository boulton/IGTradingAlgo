# -*- coding: utf-8 -*-

import datetime


# ----//Variable connexion //----
login = str("fleuros")
password = str("Trade4Lyfe")
epic = "CS.D.EURUSD.MINI.IP"
authentified = False
backtest = True
data = {}

# ----//Variable de Backtest//----
DebugTime = 0.01
D1 = "2018-03-12"
D2 = "2018-03-13"
emaBacktest = [0,]

# ----//Variable Stratégie//----
Limit = 25
Stoploss = -10
PositionSimultanee = 3
AlgoInitialTime = (61 * 60)
ordrePassee = False
pauseordre = 60*10
starttime = datetime.datetime(int(D1[:4]),
							int(D1[5:7]),
							int(D1[8:10]),
							23,00,00)

# ----//Variable indicateur et chrono //----

Minute = 1
lastMinute = 0  # depécié
lastHeure = 0  # déprécié
lastDatetime = datetime.datetime



ema = {"Periode": "",
	   "echelle": "",  # minutes, heure , seconde
	   "valeurs": [0, ]
	   }

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
