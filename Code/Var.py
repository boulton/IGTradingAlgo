# -*- coding: utf-8 -*-

from tkinter import *


delta = {"Bid":["0"],
		 "Ask":["0"],
		 "Time":["0"]
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

daties = []

login= str("MY-IG-LOGIN")
password = str("MY-IG-PASSWORD")

