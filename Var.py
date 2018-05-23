# -*- coding: utf-8 -*-

PositionSimultanee = 2
Ematempsinit = 4

Minute = 1
lastMinute = int
lastMinIndice = []

dim_affichage = 400
PnL = 0

delta = {"Bid":["0"],
		 "Ask":["0"],
		 "Time":["0"]
		}


ema = 	{"Periode":"",
		 "echelle":"", #minutes, heure , seconde
		 "valeurs":[0,]
		}

price = {"Market": str(),
		 "Date": str(),
		 "Time":[""],
		 "Bid" :[""],
		 "Ask" :[""]
		}

#Deal en cours, validé sur plateforme
DealDone = {"Time":[""],
			"Id"  :[""],
			"entry":[""],
			"sens":[""]}
#Deal Fake, test de strategie
FakeDeal ={"Time":[""],
			"Id"  :[""],
			"entry":[""],
			"sens":[""]}

#Deal Cloturé
CleanedDeal ={"Time": [""],
			  "Id":[""],
			  "profit":[""],
			  "entry":[""],
			  "close":[""],

			 }

prix =[]
datePrix =[]
daties = []
deltaaffiche =[]
# second updated 1min ema
emachart = []
emadate = []


login= str("YOUR-IG-LOGIN")
password = str("YOUR-IG-PASSWORD")

